from ._anvil_designer import rppn_incomeTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class rppn_income(rppn_incomeTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    self.lb_name.text = self.item['name']
    self.lb_amount.text = f"${self.item['amount']:.2f}"
