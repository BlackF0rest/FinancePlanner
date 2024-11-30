from ._anvil_designer import InsightsTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import plotly.graph_objects as go


class Insights(InsightsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    self.accounts = None
    self.selected_accounts = []
    self.currency = anvil.server.call('get_currency')
    
    self.update_accounts()
    self.update_all_pt()
    self.update_grid_panel()

  def update_all_pt(self):
    self.update_pt_one()
    self.update_pt_two()
    self.update_pt_three()
    self.update_pt_five()
    self.update_pt_six()
    self.update_pt_seven()
    
  def button_now_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Home')

  def button_logs_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Transactions')

  def button_insights_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  def button_setting_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Settings')

  def update_accounts(self):
    self.accounts = anvil.server.call('get_user_accounts')

    self.dp_accounts.items = [(account['name'], account['id']) for account in self.accounts]

    if self.accounts:
      for account in self.accounts:
        if account['id'] == anvil.server.call('get_current_account_id'):
          self.dp_accounts.selected_value = account['id']

  def update_pt_one(self):
    data, labels = anvil.server.call('is_1_get_fix_month', self.selected_accounts)
    sizes = []

    for month in labels:
      sizes.append(data[str(month)])

    self.pt_one.data = []
    self.pt_one.layout = None
    
    self.pt_one.data = go.Bar(
      x=labels,
      y=sizes,
      text=sizes,
      textposition='auto',
      marker_color='red'
    )
    self.pt_one.layout = go.Layout(
      title='Fix Costs per Month',
      xaxis=dict(title='Month'),
      yaxis=dict(title=f'Amount in {self.currency}'),
      paper_bgcolor='rgba(0,0,0,0.2)',
      plot_bgcolor='rgba(255,255,255,0)',
      xaxis_type='category',
      )

  def update_pt_two(self):
    data, months = anvil.server.call('is_2_ic_oc_month', self.selected_accounts)
    incomes = []
    outcomes = []
    
    for month in months:
      incomes.append(data[str(month)]['income'])
      outcomes.append(data[str(month)]['expense'])

    self.pt_two.data = [
      go.Bar(
        x=months,
        y=incomes,
        name='Income',
        marker_color='blue',
        text=incomes,
        textposition='auto'
      ),
      go.Bar(
        x=months,
        y=outcomes,
        name='Outcome',
        marker_color='red',
        text=outcomes,
        textposition='auto'
      )
    ]
    self.pt_two.layout = go.Layout(
      title='Income vs. Expenses',
      xaxis=dict(title='Month'),
      yaxis=dict(title=f'Amount in {self.currency}'),
      paper_bgcolor='rgba(0,0,0,0.2)',
      plot_bgcolor='rgba(255,255,255,0)',
      xaxis_type='category'
      )

  def update_pt_three(self):
    data = anvil.server.call('is_3_get_expense_data', self.selected_accounts)

    categories = list(data.keys())
    amounts = list(data.values())

    self.pt_three.data = go.Pie(
      labels=categories,
      values=amounts
    )
    self.pt_three.layout = go.Layout(
      title='Portion per Category this Month',
      paper_bgcolor='rgba(0,0,0,0.2)',
      plot_bgcolor='rgba(255,255,255,0)',
      )

  def update_pt_five(self):
    data = anvil.server.call('is_5_costs_qt')

    labels = ['1','2','3','4']
    sizes = data

    self.pt_five.data = go.Scatter(
      x=labels, 
      y=sizes)
    self.pt_five.layout = go.Layout(
      title='Costs per quarter',
      xaxis=dict(title='Quarter'),
      yaxis=dict(title=f'Amount in {self.currency}'),
      paper_bgcolor='rgba(0,0,0,0.2)',
      plot_bgcolor='rgba(255,255,255,0)',
      xaxis_type='category'
      )

  def update_pt_six(self):
    self.six_data = anvil.server.call('is_6_saving_goal')
    currency = anvil.server.call('get_currency')

    if self.six_data:
    
      items = [goal['name'] for goal in self.six_data]
  
      self.dp_six.items = items
      self.lb_progress.width = str(self.six_data[0]['perc_done'])+'%'
      self.img_six.source = self.six_data[0]['icon']
      self.lb_name.text = self.six_data[0]['name']
      self.lb_amount.text = str(self.six_data[0]['amount']) + currency
      self.lb_amount_payed.text = str(self.six_data[0]['amount_payed']) + currency
      self.lb_days_to_go.text = str(self.six_data[0]['to_go']) + ' Days to go'
    else:
      self.dp_six.items = []
      self.lb_progress.width = 0
      self.img_six.source = None
      self.lb_name.text = None
      self.lb_amount.text = None
      self.lb_amount_payed.text = None
      self.lb_days_to_go.text = None
  
  def dp_six_change(self, **event_args):
    """This method is called when an item is selected"""
    currency = anvil.server.call('get_currency')
    for goal in self.six_data:
      if goal['name'] == self.dp_six.selected_value:
        self.lb_name.text = goal['name']
        self.lb_amount.text = str(goal['amount']) + currency
        self.lb_days_to_go.text = str(goal['to_go']) + ' Days to go'
        self.lb_progress.width = str(goal['perc_done'])+'%'
        self.img_six.source = goal['icon']
        self.lb_amount_payed.text = str(goal['amount_payed']) + currency

  def update_pt_seven(self):
    data, labels = anvil.server.call('is_7_perc_pm')

    sizes = []
    for month in labels:
      sizes.append(data[str(month)])

    self.pt_seven.data = go.Scatter(
      x=labels,
      y=sizes
    )
    self.pt_seven.layout = go.Layout(
      title='Percent of Change per Month',
      xaxis=dict(title='Month'),
      yaxis=dict(title='Change in %'),
      paper_bgcolor='rgba(0,0,0,0.2)',
      plot_bgcolor='rgba(255,255,255,0)',
      xaxis_type='category'
      )

  def dp_accounts_change(self, **event_args):
    """This method is called when an item is selected"""
    if self.dp_accounts.selected_value is None:
      self.grid_panel_1.visible = True
    else:
      self.grid_panel_1.visible = False
      self.selected_accounts = []
      anvil.server.call('set_account_setting', self.dp_accounts.selected_value)
      self.update_all_pt()

  def update_grid_panel(self):
    """This method is called when the grid panel is shown on the screen"""
    col = 0
    row = 0
    for account in self.accounts:
      check_box = anvil.CheckBox(text=account['name'])
      check_box.add_event_handler('change', self.on_change_grid_check_boxes)
      self.grid_panel_1.add_component(check_box, row=row, width_xs=3)
      col += 1
      if col == 3:
        col = 0
        row += 1

  def on_change_grid_check_boxes(self, **event_args):
    for account in self.accounts:
      if event_args['sender'].text == account['name']:
        if account['id'] in self.selected_accounts:
          self.selected_accounts.remove(account['id'])
        else:
          self.selected_accounts.append(account['id'])

    self.update_all_pt()