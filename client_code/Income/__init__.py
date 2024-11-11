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

    categories = anvil.server.call('get_icon_categories')
    #self.icons_repeater.items = categories
    self.selected_category = None

    print()

  def outlined_button_2_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Home')

  def bt_add_click(self, **event_args):
    """This method is called when the button is clicked"""
    #anvil.server.call('write_transaction', type='income', amount=float(self.input_numb.text), name=self.input_name.text, accoung=)
    open_form('Home')

  def radio_button_1_change(self, **event_args):
    """This method is called when this radio button is selected (but not deselected)"""
    self.date_picker_1.visible = self.radio_button_1.selected
    self.date_picker_1_copy.visible = False
    self. radio_button_2.selected != self.radio_button_1.selected

  def radio_button_2_change(self, **event_args):
    """This method is called when this radio button is selected (but not deselected)"""
    self.date_picker_1_copy.visible = self.radio_button_2.selected
    self.date_picker_1.visible = False
    self. radio_button_1.selected != self.radio_button_2.selected
