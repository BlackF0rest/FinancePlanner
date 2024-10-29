from ._anvil_designer import Form1_copy_copy_copyTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import plotly.graph_objects as go


class Form1_copy_copy_copy(Form1_copy_copy_copyTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def plot_now_show(self, **event_args):
    """This method is called when the Plot is shown on the screen"""
    pass
