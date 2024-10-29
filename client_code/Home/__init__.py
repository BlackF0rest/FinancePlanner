from ._anvil_designer import HomeTemplate
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import plotly.graph_objects as go


class Home(HomeTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def plot_now_show(self, **event_args):
    """This method is called when the Plot is shown on the screen"""
    pass

  def button_now_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Home')

  def button_logs_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('InOut')

  def button_insights_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Insights')

  def button_setting_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Settings')

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Income')

  def button_3_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Transfer')

  def button_2_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Expense')
