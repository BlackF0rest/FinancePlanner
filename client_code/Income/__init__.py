from ._anvil_designer import IncomeTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Income(IncomeTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def outlined_button_2_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Home')

  def bt_add_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call('write_transaction', type='income', amount=self.input_numb.text, name=self.input_name.text)
    open_form('Home')
