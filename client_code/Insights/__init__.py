from ._anvil_designer import InsightsTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import plotly.graph_objects as go


class Insights(InsightsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    self.accounts = None

    self.update_accounts()

    # Any code you write here will run before the form opens.

  def pt_fixcosts_show(self, **event_args):
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
    pass

  def button_setting_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Settings')

  def update_accounts(self):
    self.accounts = anvil.server.call('get_user_accounts')

    self.dp_accounts.items = [(account['name'], account['id']) for account in self.accounts]

  def update_charts(self):
    pass