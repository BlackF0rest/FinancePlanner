from ._anvil_designer import TransferTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime, timedelta, date


class Transfer(TransferTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    self.set_event_handler("x-set-icon", self.set_selected_icon)

    self.rppn_icons.items = anvil.server.call("get_all_icons")

    self.dt_main.date = datetime.now().date()
    self.dt_recurring.min_date = self.dt_main.date + timedelta(days=1)
    self.dt_spreadout.min_date = self.dt_main.date + timedelta(days=1)

    self.selected_icon = None

    self.accounts = None

    self.update_accounts()

  def update_accounts(self):
    self.accounts = anvil.server.call('get_user_accounts')

    excluded_account_id = anvil.server.call('get_current_account_id')  # Replace with the account ID you want to exclude

    self.dp_accounts.items = [

        (account['name'], account['id']) for account in self.accounts
    
            if account['id'] != excluded_account_id
    
    ]
  
  def bt_add_click(self, **event_args):
    """This method is called when the button is clicked"""
    if not self.input_numb.text:
      self.input_numb.border = "2px solid red"
    elif not self.input_name.text:
      self.input_name.border = "2px solid red"
    elif not self.selected_icon:
      self.img_icon.border = "2px solid red"
    elif not self.dt_main.date:
      self.dt_main.border = "2px solid red"
    else:
      if self.rd_recurring.selected:
        if not self.dt_recurring.date:
          self.dt_recurring.border = "2px solid red"
        else:
          today = self.dt_main.date
          recurring_days = (self.dt_recurring.date - today).days
          total_value = float(self.input_numb.text)
          daily_value = round((total_value / recurring_days), 2)
          end_date = self.dt_end_recurring.date
          anvil.server.call(
            "write_transaction",
            type="expense",
            date=today,
            category=self.selected_icon,
            amount=daily_value,
            name=self.input_name.text,
            recurring=True,
            end_date=end_date,
            account_id=anvil.server.call(
              "get_current_account_id", anvil.users.get_user()
            ),
          )
      elif self.rd_spreadout.selected:
        if not self.rd_spreadout.date:
          self.rd_spreadout.border = "2px solid red"
        else:
          today = self.dt_main.date
          end_date = self.dt_spreadout.date
          total_value = float(self.input_numb.text)
          daily_value = round((total_value / (end_date - today).days), 2)
          anvil.server.call(
            "write_transaction",
            type="expense",
            date=today,
            category=app_tables.icons.get(category=self.selected_icon),
            amount=daily_value,
            name=self.input_name.text,
            recurring=True,
            end_date=end_date,
            account_id=anvil.server.call(
              "get_current_account_id", anvil.users.get_user()
            ),
          )
      else:
        anvil.server.call(
          "write_transaction",
          type="expense",
          date=today,
          category=app_tables.icons.get(category=self.selected_icon),
          amount=float(self.input_numb.text),
          name=self.input_name.text,
          account_id=anvil.server.call(
            "get_current_account_id", anvil.users.get_user()
          ),
        )
      open_form("Home")

  def outlined_button_2_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form("Home")

  def rd_recurring_change(self, **event_args):
    """This method is called when this radio button is selected (but not deselected)"""
    pass

  def set_selected_icon(self, **event_args):
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
    self.dt_recurring.visible = self.rd_recurring.selected
    self.lb_recurring.visible = self.rd_recurring.selected
    self.dt_end_recurring.visible = self.rd_recurring.selected
    self.lb_end_recurring.visible = self.rd_recurring.selected

  def rd_spreadout_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.rd_spreadout.selected != self.rd_spreadout.selected
    self.dt_recurring.visible = False
    self.lb_recurring.visible = False
    self.dt_end_recurring.visible = False
    self.lb_end_recurring.visible = False
    self.dt_spreadout.visible = self.rd_spreadout.selected
    self.lb_spreadout.visible = self.rd_spreadout.selected

  def rd_one_time_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.dt_recurring.visible = False
    self.lb_recurring.visible = False
    self.dt_spreadout.visible = False
    self.lb_spreadout.visible = False
    self.dt_end_recurring.visible = False
    self.lb_end_recurring.visible = False

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
    self.dt_recurring.min_date = self.dt_main.date + timedelta(days=1)
    self.dt_spreadout.min_date = self.dt_main.date + timedelta(days=1)
    if self.dt_main.border != "":
      self.dt_main.border = ""

  def dt_recurring_change(self, **event_args):
    """This method is called when the selected date changes"""
    self.dt_end_recurring.min_date = self.dt_recurring.date + timedelta(days=1)
    if self.dt_recurring.border != "":
      self.dt_recurring.border = ""

  def dt_spreadout_change(self, **event_args):
    """This method is called when the selected date changes"""
    if self.dt_spreadout.border != "":
      self.dt_spreadout.border = ""
