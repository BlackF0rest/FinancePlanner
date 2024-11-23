from ._anvil_designer import SettingsTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import plotly.graph_objects as go


class Settings(SettingsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.settings = None
    self.update_days()
    
    selected_currency = anvil.server.call('get_currency')
    if selected_currency == '€':
      self.rd_euro.selected = True
    else:
      self.rd_dollar.selected = True
    
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

  def bt_plus_days_click(self, **event_args):
    """This method is called when the button is clicked"""
    days = self.settings['max_days_ahead_from_today'] + 1
    anvil.server.call('set_days_into_future', anvil.users.get_user(), days)
    self.update_days()

  def update_days(self):
    self.settings = anvil.server.call('get_settings', user=anvil.users.get_user())
    self.lb_days_future.text = self.settings['max_days_ahead_from_today']

  def bt_minus_days_click(self, **event_args):
    """This method is called when the button is clicked"""
    days = self.settings['max_days_ahead_from_today'] - 1
    anvil.server.call('set_days_into_future', anvil.users.get_user(), days)
    self.update_days()

  def rd_dollar_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    anvil.server.call('set_currency', '$')

  def rd_euro_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    anvil.server.call('set_currency', '€')

  def bt_request_feature_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
