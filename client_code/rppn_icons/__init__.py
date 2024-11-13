from ._anvil_designer import rppn_iconsTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class rppn_icons(rppn_iconsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.category = list(self.item.keys())[0]
    self.lnk_lb.text = self.category
    self.lnk_img.source = self.item[self.category]
    self.set_event_handler('x-set-visibile', self.set_visible)

  def lnk_1_click(self, **event_args):
    """This method is called when the link is clicked"""
    print('clicked') 
    self.parent.parent.raise_event('x-set-icon', icon_category=self.category)
    self.lnk_1.visible = True

  def set_visible(self):
    self.lnk_1.visible = True