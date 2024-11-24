from ._anvil_designer import SettingsTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import plotly.graph_objects as go


class Settings(SettingsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.selected_currency = None
    self.selected_days = None
    self.accounts = None
    self.update_days()
    self.update_currency()
    self.update_accounts()
    
  def plot_now_show(self, **event_args):
    """This method is called when the Plot is shown on the screen"""
    pass
    
  def button_now_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Home')

  def button_logs_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Transactions')

  def button_insights_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Insights')

  def update_days(self):
    self.selected_days = anvil.server.call('get_settings')['max_days_ahead_from_today']
    self.lb_days_future.text = self.selected_days

  def update_currency(self):
    self.selected_currency =  anvil.server.call('get_currency')
    if self.selected_currency == '€':
      self.rd_euro.selected = True
    else:
      self.rd_dollar.selected = True

  def update_accounts(self):
    self.accounts = anvil.server.call('get_user_accounts')

    self.dp_accounts.items = [(account['name'], account['id']) for account in self.accounts]

    if self.accounts:
      for account in self.accounts:
        if account['id'] == anvil.server.call('get_current_account_id'):
          self.dp_accounts.selected_value = account['id']

  def bt_plus_days_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.selected_days += 1
    self.lb_days_future.text = self.selected_days

  def bt_minus_days_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.selected_days -= 1
    self.lb_days_future.text = self.selected_days

  def rd_dollar_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.selected_currency = '$'

  def rd_euro_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.selected_currency = '€'

  def bt_cancel_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.update_currency()
    self.update_days()

  def bt_apply_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call('set_days_into_future', self.selected_days)
    anvil.server.call('set_currency', self.selected_currency)

  def rd_create_account_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.bt_create_account.visible = self.rd_create_account.selected
    self.tb_acc_name.visible = self.rd_create_account.selected
    self.bt_delete_account.visible = self.rd_delete_account.selected
    self.dp_accounts.visible = self.rd_delete_account.selected

  def rd_delete_account_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.bt_create_account.visible = self.rd_create_account.selected
    self.tb_acc_name.visible = self.rd_create_account.selected
    self.bt_delete_account.visible = self.rd_delete_account.selected
    self.dp_accounts.visible = self.rd_delete_account.selected

  def bt_create_account_click(self, **event_args):
    """This method is called when the button is clicked"""
    if not self.tb_acc_name.text:
      self.tb_acc_name.border = 'solid red'
    else:
      anvil.server.call('create_account', self.tb_acc_name.text)
      alert('Account Created')
      open_form('Settings')

  def bt_delete_account_click(self, **event_args):
    """This method is called when the button is clicked"""
    if confirm('Do you want to delete this account?'):
      anvil.server.call('delete_account', self.dp_accounts.selected_value)
      alert('Account Deleted')
      open_form('Settings')

  def bt_delete_user_click(self, **event_args):
    """This method is called when the button is clicked"""
    if confirm('Do you want to delete your Account on this Website?'):
      alert('Thank you - Goodbye')
      anvil.server.call('delete_user')
      anvil.users.logout()

  def bt_logout_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.users.logout()
    open_form('Home')
