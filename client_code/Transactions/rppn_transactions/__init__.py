from ._anvil_designer import rppn_transactionsTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class rppn_transactions(rppn_transactionsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.currency = anvil.server.call('get_currency')

    self.lb_name.text = self.item['name']
    self.lb_amount.text = f"${self.item['amount']:.2f}{self.currency}"
    self.img_icon.source = self.item['category']['icon']
    
    if 'to' in self.item :
      self.lb_to.visible = True
      self.lb_to.text = self.item['to']
    if 'from' in self.item:
      self.lb_to.visible = True
      self.lb_to.text = self.item['from']

  def bt_delete_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call('delete_transaction', self.item['id'])
    open_form('Transactions')
    
