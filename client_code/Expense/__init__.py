from ._anvil_designer import ExpenseTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Expense(ExpenseTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    self.set_event_handler('x-set-icon', self.set_selected_icon)

    self.rppn_icons.items = anvil.server.call('get_all_icons')

    self.selected_icon = None

    # Any code you write here will run before the form opens.

  def bt_add_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call('write_transaction', type='expense', category=self.selected_icon, amount=float(self.input_numb.text), name=self.input_name.text, account_id=anvil.server.call('get_current_account_id', anvil.users.get_user()))
    open_form('Home')

  def outlined_button_2_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Home')

  def rd_recurring_change(self, **event_args):
    """This method is called when this radio button is selected (but not deselected)"""
    pass

  def set_selected_icon(self, **event_args):
    self.selected_icon = event_args['icon_category']
    self.raise_event_on_children('x-set-visible')