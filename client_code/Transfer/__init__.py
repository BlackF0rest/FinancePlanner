from ._anvil_designer import TransferTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Transfer(TransferTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def outlined_button_2_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Home')

  def outlined_button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Home')

  def radio_button_1_change(self, **event_args):
    """This method is called when this radio button is selected (but not deselected)"""
     self.date_picker_1.visible = self.radio_button_1.selected
     self.date_picker_1.visible = self.radio_button_1.selected
