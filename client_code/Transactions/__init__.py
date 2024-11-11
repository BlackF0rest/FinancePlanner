from ._anvil_designer import TransactionsTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import plotly.graph_objects as go


class Transactions(TransactionsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.update_accounts()
    self.update_transactions()

  def plot_now_show(self, **event_args):
    """This method is called when the Plot is shown on the screen"""
    pass

  def button_now_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Home')

  def button_logs_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('InOut')

  def button_insights_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Insights')

  def button_setting_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Settings')

  def update_transactions(self):
    incomes, expenses, transfers = anvil.server.call('get_transactions', anvil.server.call('get_current_account_id', anvil.users.get_user()))
    self.prppn_income.items = incomes

  def dd_account_change(self, **event_args):
    """This method is called when an item is selected"""
    selected_account_id = self.drop_down_1.selected_value
    anvil.server.call('set_account_setting', selected_account_id, anvil.users.get_user())
    self.update_main_graph(selected_account_id)

  def update_accounts(self):
      self.accounts = anvil.server.call('get_user_accounts')
  
      self.dd_account.items = [(account['name'], account['id']) for account in self.accounts]
  
      if self.accounts:
        self.dd_account.selected_value = self.accounts[0]['id']

