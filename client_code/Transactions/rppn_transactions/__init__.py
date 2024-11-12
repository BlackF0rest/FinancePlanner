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

    self.lb_name.text = self.item['name']
    self.lb_amount.text = f"${self.item['amount']:.2f}"
    
    if self.item['to']:
      self.lb_to.visible = True
      self.lb_arrow.visible = True
      self.lb_to.text = self.item['to']
