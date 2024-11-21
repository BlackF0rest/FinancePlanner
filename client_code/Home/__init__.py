from ._anvil_designer import HomeTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import plotly.graph_objects as go

class Home(HomeTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Initialize accounts dict
    self.accounts = None

    # Handle Login
    self.user = anvil.users.login_with_form()

    #anvil.server.call('update_daily_totals')
    
    # get Users accounts
    self.update_accounts()
    # initialize main graph
    self.update_main_graph(anvil.server.call('get_current_account_id', anvil.users.get_user()))

  def button_now_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Home')

  def button_transaction_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Transactions')

  def button_insights_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Insights')

  def button_setting_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Settings')

  def button_income_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Transaction_Form', type='income')

  def button_transfer_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Transaction_Form', type='transfer')

  def button_expense_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Transaction_Form', type='expense')

  def drop_down_1_change(self, **event_args):
    """This method is called when an item is selected"""
    selected_account_id = self.drop_down_1.selected_value
    anvil.server.call('set_account_setting', selected_account_id, anvil.users.get_user())
    self.update_main_graph(selected_account_id)


  def update_accounts(self):
    self.accounts = anvil.server.call('get_user_accounts')

    self.drop_down_1.items = [(account['name'], account['id']) for account in self.accounts]

    if self.accounts:
      for account in self.accounts:
        if account['id'] == anvil.server.call('get_current_account_id', anvil.users.get_user()):
          self.drop_down_1.selected_value = account['id']

  def update_main_graph(self, account_id):
    data = anvil.server.call('get_daily_total_data', account_id)
    dates = data['dates']
    totals = data['net_totals']

    totals = [int(round(total)) for total in totals]

    # Initialize a list for marker colors
    marker_colors = []
    
    # Determine colors for each marker based on the specified conditions
    for i in range(len(totals)):    
        if i == 0:  # First marker
            if totals[i] < 0:  
                marker_colors.append('red')   
            else: 
                marker_colors.append('black')
        elif i == 1:  # Second marker
            if totals[i] > totals[i - 1]:   
                marker_colors.append('green')   
            elif totals[i] == totals[i - 1]: 
                marker_colors.append('black')
            else:
                marker_colors.append('red')
        elif i == 2:  # Third marker
            if totals[i] > totals[i - 1]:
                marker_colors.append('green')
            elif totals[i] == totals[i - 1]:
                marker_colors.append('black')
            else:
                marker_colors.append('red')
              
    self.plot_now.data = [go.Scatter(
      x=dates, 
      y=totals, 
      text=totals, 
      textposition='center', 
      textfont=dict(
        size=18,
        color='white',
      ), 
      marker=dict(size=40, color=marker_colors), 
      mode='lines+markers+text')]

    self.plot_now.layout = go.Layout(
    showlegend=False,  # Hide the legend if not needed
    xaxis=dict(
        showgrid=False,   # Hide grid lines
        zeroline=False,   # Hide the zero line
        showline=False,   # Hide the axis line
        title='',         # Optionally remove the title
        tickvals=dates,
        ticktext=dates,
        ticks='outside',
      ),
      yaxis=dict(
        showgrid=False,   # Hide grid lines
        zeroline=False,   # Hide the zero line
        showline=False,   # Hide the axis line
        title='',         # Optionally remove the title
        showticklabels=False,
      ),
      plot_bgcolor='rgba(255,255,255,0)',  # Optional: Set background color to transparent
      paper_bgcolor='rgba(255,255,255,0)',
    )

    self.plot_now.interactive = False

  def plot_now_show(self, **event_args):
    """This method is called when the Plot is shown on the screen"""
    pass

  def recalc_daily_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call('test_recalc')

  def tst_bttn_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call('is_1_get_fix_month')
    anvil.server.call('is_2_ic_oc_month')
    anvil.server.call('is_3_get_expense_data')
    anvil.server.call('is_5_costs_qt')
    anvil.server.call('is_6_saving_goal')
    anvil.server.call('is_7_perc_pm')
    print('all went good')
 