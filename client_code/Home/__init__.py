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
    anvil.users.login_with_form()

    if anvil.server.call('is_first_login'): # Handle First Login
      t = anvil.TextBox(placeholder='Account Name')
      anvil.alert(content=t, title='Hi, please enter the Name of your first Account :)', dismissible=False, buttons=[('Create')], large=True) # Get Name of first Account
      anvil.server.call('setup_user', t.text) # Call setup function on Server
      
      
    
    # get Users accounts
    self.update_accounts()
    # initialize main graph
    self.update_main_graph()

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

  def dp_accounts_change(self, **event_args):
    """This method is called when a different account is selected in the Dropdown"""
    selected_account_id = self.dp_accounts.selected_value
    anvil.server.call('set_account_setting', selected_account_id) # set new account id in Server
    self.update_main_graph() # Update the Main Graph


  def update_accounts(self):
    """Update the main Graph with new Data. This automatically uses the Account which is set in the """
    self.accounts = anvil.server.call('get_user_accounts') # get all accounts of the user

    self.drop_down_1.items = [(account['name'], account['id']) for account in self.accounts] # set the Dropdown to the names and ids of the accounts

    if self.accounts:
      for account in self.accounts:
        if account['id'] == anvil.server.call('get_current_account_id'):
          self.dp_accounts.selected_value = account['id'] # Set selected Account to the global selected account

  def update_main_graph(self):
    """Upadte Main Graph with daily Totals from yesterday, today and tomorrow."""
    data = anvil.server.call('get_daily_total_data') # Get data from Server
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
      paper_bgcolor='rgba(0,0,0,0.2)',
    )

    self.plot_now.interactive = False # don't allow user interaction 