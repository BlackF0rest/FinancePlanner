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

  def bt_add_click(self, **event_args):
    """This method is called when the button is clicked"""
    if not self.input_numb.text :
      self.input_numb.border = "2px solid red"
    elif not self.input_name.text:
      self.input_name.border = "2px solid red"
    elif not self.selected_icon:
      self.img_icon.border = "2px solid red"
    else: 
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
    self.rppn_icons.visible = False
    self.img_icon.source = anvil.server.call('get_icon', event_args['icon_category'])
    self.img_icon.border = ""

  def bt_set_icon_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.rppn_icons.visible = True

  def rd_recurring_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.rd_recurring.selected != self.rd_recurring.selected
    self.dt_spreadout.visible = False
    self.dt_recurring.visible = self.rd_recurring.selected

  def rd_spreadout_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.rd_spreadout.selected != self.rd_spreadout.selected
    self.dt_recurring.visible = False
    self.dt_spreadout.visible = self.rd_spreadout.selected

  def rd_one_time_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.dt_recurring.visible = False
    self.dt_spreadout.visible = False

  def input_numb_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    if self.input_numb.border != 
