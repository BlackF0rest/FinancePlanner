from ._anvil_designer import HomeTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import plotly.graph_objects as go

class Home(HomeTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Initialize accounts dict
    self.accounts = None

    # Handle Login
    self.user = anvil.users.login_with_form()

    #anvil.server.call('update_daily_totals')
    
    # get Users accounts
    self.update_accounts()
    # initialize main graph
    self.update_main_graph(anvil.server.call('get_current_account_id', anvil.users.get_user()))

  def button_now_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Home')

  def button_transaction_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Transactions')

  def button_insights_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Insights')

  def button_setting_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Settings')

  def button_income_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Income')

  def button_transfer_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Transfer')

  def button_expense_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Expense')

  def drop_down_1_change(self, **event_args):
    """This method is called when an item is selected"""
    selected_account_id = self.drop_down_1.selected_value
    anvil.server.call('set_account_setting', selected_account_id, anvil.users.get_user())
    self.update_main_graph(selected_account_id)


  def update_accounts(self):
    self.accounts = anvil.server.call('get_user_accounts')

    self.drop_down_1.items = [(account['name'], account['id']) for account in self.accounts]

    if self.accounts:
      self.drop_down_1.selected_value = self.accounts[0]['id']

  def update_main_graph(self, account_id):
    data = anvil.server.call('get_daily_total_data', account_id)
    dates = data['dates']
    totals = data['net_totals']

    self.plot_now.data = [go.Scatter(x=dates, y=totals, mode='lines+markers')]
 