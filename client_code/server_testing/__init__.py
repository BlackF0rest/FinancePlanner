from ._anvil_designer import server_testingTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime


class server_testing(server_testingTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def recalc_daily_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call('recalc_daily_totals', datetime.now().date(), anvil.server.call('get_current_account_id', anvil.users.get_user()))
    print('done')