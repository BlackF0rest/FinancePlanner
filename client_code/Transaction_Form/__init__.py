from ._anvil_designer import Transaction_FormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime, timedelta, date


class Transaction_Form(Transaction_FormTemplate):
  def __init__(self, type, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.type = type

    self.set_event_handler("x-set-icon", self.set_selected_icon)

    self.rppn_icons.items = anvil.server.call("get_all_icons")

    self.dt_main.date = datetime.now().date()
    self.dt_spreadout.min_date = self.dt_main.date + timedelta(days=1)

    self.selected_icon = None

    self.accounts = None

    self.intervalls = anvil.server.call('get_time_values')
    self.dp_recurring.items = [(intervall, self.intervalls[intervall]) for intervall in self.intervalls]

    if self.type == 'transfer':
      self.dp_accounts.visible = True
      self.dp_accounts.enabled = True
      self.update_accounts()

  def update_accounts(self):
    """
    Updates the accounts list by fetching user accounts from the server and excluding a specific account.
    This method performs the following steps:
    1. Calls the server to get the list of user accounts and assigns it to `self.accounts`.
    2. Calls the server to get the current account ID that needs to be excluded.
    3. Filters out the account with the excluded ID from the list of accounts.
    4. Updates `self.dp_accounts.items` with the filtered list of account names and IDs.
    Note:
      The server functions `get_user_accounts` and `get_current_account_id` must be defined on the server side.
    """
    self.accounts = anvil.server.call("get_user_accounts")

    excluded_account_id = anvil.server.call("get_current_account_id")  # Replace with the account ID you want to exclude

    self.dp_accounts.items = [
      (account["name"], account["id"])
      for account in self.accounts
      if account["id"] != excluded_account_id
    ]

  def bt_add_click(self, **event_args):
    """
    This method is called when the button is clicked. It performs validation on various input fields and 
    then processes the transaction based on the type and recurrence settings.

    Validations:
    - Checks if the input number is provided and greater than 0.01.
    - Checks if the input name is provided.
    - Checks if an icon is selected.
    - Checks if the date is provided.
    - For 'transfer' type, checks if an account is selected.
    - For recurring transactions, checks if recurrence settings are provided and valid.
    - For spread out transactions, checks if the end date is provided.

    Actions:
    - If the transaction is a transfer, retrieves the target account.
    - If the transaction is recurring, calculates the daily value and adjusts the end date if necessary.
    - If the transaction is spread out, calculates the daily value based on the date range.
    - Calls the server to write the transaction with the appropriate details.
    - Opens the "Home" form after processing the transaction.
    """
    """This method is called when the button is clicked"""
    if not self.input_numb.text or float(self.input_numb.text)<0.01:
      self.input_numb.border = "2px solid red"
    elif not self.input_name.text:
      self.input_name.border = "2px solid red"
    elif not self.selected_icon:
      self.img_icon.border = "2px solid red"
    elif not self.dt_main.date:
      self.dt_main.border = "2px solid red"
    elif self.type == 'transfer' and not self.dp_accounts.selected_value:
      self.dp_accounts.border = "2px solid red"
    else:
      if self.type == 'transfer':
        to_account = anvil.server.call("get_account_from_id", self.dp_accounts.selected_value)
      else:
        to_account = None
      if self.rd_recurring.selected:
        if not self.dp_recurring.selected_value:
          self.dp_recurring.border = "2px solid red"
        if self.dp_recurring.selected_value == 0 and not self.tb_days.text:
          self.tb_days.border = '2px solid red'
        else:
          if self.dp_recurring.selected_value == 0:
            recurring_days = round(float(self.tb_days.text), 0)
          else:
            recurring_days = self.dp_recurring.selected_value
          today = self.dt_main.date
          total_value = float(self.input_numb.text)
          daily_value = round((total_value / recurring_days), 2)
          end_date = self.dt_end_recurring.date
          print (end_date)
          if end_date is not None:
            rest_days = ((end_date - today).days % recurring_days)
            print(rest_days)
            if rest_days == 0:
              pass
            else:
              end_date -= timedelta(days=rest_days) # rest tage abziehen
              end_date += timedelta(days=recurring_days) # periode drauf rechnen
            print(end_date)
          anvil.server.call(
            "write_transaction",
            type=self.type,
            date=today,
            category=self.selected_icon,
            amount=daily_value,
            name=self.input_name.text,
            recurring=True,
            end_date=end_date,
            account_id=anvil.server.call("get_current_account_id"),
            to_account=to_account,
          )
      elif self.rd_spreadout.selected:
        if not self.dt_spreadout.date:
          self.rd_spreadout.border = "2px solid red"
        else:
          today = self.dt_main.date
          end_date = self.dt_spreadout.date
          total_value = float(self.input_numb.text)
          daily_value = round((total_value / (end_date - today).days), 2)
          anvil.server.call(
            "write_transaction",
            type=self.type,
            date=today,
            category=self.selected_icon,
            amount=daily_value,
            name=self.input_name.text,
            recurring=True,
            end_date=end_date,
            account_id=anvil.server.call("get_current_account_id"),
            to_account=to_account,
            spread_out=True
          )
      else:
        today = self.dt_main.date
        anvil.server.call(
          "write_transaction",
          type=self.type,
          date=today,
          category=self.selected_icon,
          amount=float(self.input_numb.text),
          name=self.input_name.text,
          account_id=anvil.server.call("get_current_account_id"),
          to_account=to_account,
        )
      open_form("Home")

  def bt_cancel_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form("Home")

  def set_selected_icon(self, **event_args):
    """
    Sets the selected icon based on the provided event arguments.

    Args:
      event_args (dict): A dictionary containing event arguments. 
                 Expected key is "icon_category" which specifies the category of the icon.

    Returns:
      None
    """
    self.selected_icon = event_args["icon_category"]
    self.rppn_icons.visible = False
    self.img_icon.source = anvil.server.call("get_icon", event_args["icon_category"])
    self.img_icon.border = ""

  def bt_set_icon_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.rppn_icons.visible = True

  def rd_recurring_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.rd_recurring.selected != self.rd_recurring.selected
    self.dt_spreadout.visible = False
    self.lb_spreadout.visible = False
    self.dp_recurring.visible = self.rd_recurring.selected
    self.lb_recurring.visible = self.rd_recurring.selected
    self.dt_end_recurring.visible = self.rd_recurring.selected
    self.lb_end_recurring.visible = self.rd_recurring.selected

  def rd_spreadout_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.rd_spreadout.selected != self.rd_spreadout.selected
    self.dp_recurring.visible = False
    self.lb_recurring.visible = False
    self.dt_end_recurring.visible = False
    self.lb_end_recurring.visible = False
    self.tb_days.visible =False
    self.dt_spreadout.visible = self.rd_spreadout.selected
    self.lb_spreadout.visible = self.rd_spreadout.selected

  def rd_one_time_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.dp_recurring.visible = False
    self.lb_recurring.visible = False
    self.dt_spreadout.visible = False
    self.lb_spreadout.visible = False
    self.dt_end_recurring.visible = False
    self.lb_end_recurring.visible = False
    self.tb_days.visible = False

  def input_numb_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    if self.input_numb.border != "":
      self.input_numb.border = ""

  def input_name_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    if self.input_name.border != "":
      self.input_name.border = ""

  def dt_main_change(self, **event_args):
    """This method is called when the selected date changes"""
    self.dt_spreadout.min_date = self.dt_main.date + timedelta(days=1)
    if self.dt_main.border != "":
      self.dt_main.border = ""

  def dp_recurring_change(self, **event_args):
    """This method is called when the selected date changes"""
    if self.dp_recurring.border != "":
      self.dp_recurring.border = ""
    if self.dp_recurring.selected_value == 0:
      self.tb_days.visible = True
    else:
      self.tb_days.visible = False

  def dt_spreadout_change(self, **event_args):
    """This method is called when the selected date changes"""
    if self.dt_spreadout.border != "":
      self.dt_spreadout.border = ""

  def dp_accounts_change(self, **event_args):
    """This method is called when an item is selected"""
    if self.dp_accounts.border != "":
      self.dp_accounts.border = ""

  def tb_days_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    if self.tb_days.border != "":
      self.tb_days.border = ""
