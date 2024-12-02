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
from datetime import datetime


class Transactions(TransactionsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.accounts = None
    
    self.init_components(**properties)
    self.update_accounts() # Update Account Dropdown
    self.update_transactions() # Load and show all transactions of current account

    self.date_transactions.date = datetime.now().date()

  def button_now_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Home')

  def button_logs_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  def button_insights_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Insights')

  def button_setting_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Settings')

  def update_transactions(self, date=datetime.now().date()):
    """
    Updates the transactions for the given date by loading them from the server
    and assigning them to the respective repeating panels.

    Args:
      date (datetime.date, optional): The date for which to load transactions.
                       Defaults to the current date.

    Returns:
      None
    """
    incomes, expenses, transfers = anvil.server.call('get_transactions', date)
    self.rppn_income.items = incomes
    self.rppn_transfers.items = transfers
    self.rppn_expense.items = expenses

  def dd_account_change(self, **event_args):
    """This method is called when the """
    selected_account_id = self.dd_account.selected_value
    anvil.server.call('set_account_setting', selected_account_id)
    self.update_transactions()

  def update_accounts(self):
      """
      Updates the accounts information for the client.
      This method retrieves the user's accounts from the server and updates the
      dropdown menu items with the account names and IDs. It also sets the selected
      value of the dropdown to the current account ID if it exists.
      Returns:
        None
      """
      self.accounts = anvil.server.call('get_user_accounts')
      self.dd_account.items = [(account['name'], account['id']) for account in self.accounts]
    
      if self.accounts:
        for account in self.accounts:
          if account['id'] == anvil.server.call('get_current_account_id'):
            self.dd_account.selected_value = account['id']

  def date_transactions_change(self, **event_args):
    """This method is called when the selected date changes"""
    selected_date = self.date_transactions.date
    self.update_transactions(selected_date)

