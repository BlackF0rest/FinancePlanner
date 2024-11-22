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

    self.update_accounts()
    self.update_pt_one()
    self.update_pt_two()
    self.update_pt_three()
    self.update_pt_four()
    self.update_pt_five()
    self.update_pt_six()
    self.update_pt_seven()
    #self.update_pie_where_went()
    # Any code you write here will run before the form opens.

  def pt_one_show(self, **event_args):
    """This method is called when the Plot is shown on the screen"""
    pass
    
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
        if account['id'] == anvil.server.call('get_current_account_id', anvil.users.get_user()):
          self.dp_accounts.selected_value = account['id']

  def update_charts(self):
    self.update_pt_one()

  def update_pie_where_went(self):
    data = anvil.server.call('is_get_expense_data')
    labels = list(data.keys())
    sizes = list(data.values())

    self.pt_pie_where_went_money.data = go.Pie(
      labels=labels,
      values=sizes
    )

  def update_pt_one(self):
    data = anvil.server.call('is_1_get_fix_month')
    labels = list(data.keys())
    sizes = list(data.values())

    self.pt_one.data = go.Bar(
      x=labels,
      y=sizes,
      text=sizes,
      textposition='auto',
    )
    self.pt_one.layout = go.Layout(
      title='Fix Costs per Month',
      xaxis=dict(title='Month'),
      yaxis=dict(title='Amount'),
      paper_bgcolor='rgba(0,0,0,0.2)',
      plot_bgcolor='rgba(255,255,255,0)',
      )

  def update_pt_two(self):
    data = anvil.server.call('is_2_ic_oc_month')

    incomes = [item['income'] for item in data]
    outcomes = [item['expense'] for item in data]

    months = ['1','2','3','4','5','6','7','8','9','10','11','12']

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
      yaxis=dict(title='Amount'),
      paper_bgcolor='rgba(0,0,0,0.2)',
      plot_bgcolor='rgba(255,255,255,0)',
      )

  def update_pt_three(self):
    data = anvil.server.call('is_3_get_expense_data')

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

  def update_pt_four(self):
    pass

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
      yaxis=dict(title='Amount'),
      paper_bgcolor='rgba(0,0,0,0.2)',
      plot_bgcolor='rgba(255,255,255,0)',
      )

  def update_pt_six(self):
    self.six_data = anvil.server.call('is_6_saving_goal')
    currency = anvil.server.call('get_currency')

    items = [goal['name'] for goal in self.six_data]
    print(self.lb_progress.width)

    self.dp_six.items = items
    self.lb_progress.width = str(self.six_data[0]['perc_done'])+'%'
    self.img_six.source = self.six_data[0]['icon']
    self.lb_name.text = self.six_data[0]['name']
    self.lb_amount.text = str(self.six_data[0]['amount']) + currency
    self.lb_amount_payed.text = str(self.six_data[0]['amount_payed']) + currency
    self.lb_days_to_go.text = str(-self.six_data[0]['to_go']) + ' Days to go'

  def dp_six_change(self, **event_args):
    """This method is called when an item is selected"""
    currency = anvil.server.call('get_currency')
    for goal in self.six_data:
      if goal['name'] == self.dp_six.selected_value:
        self.lb_name.text = goal['name']
        self.lb_amount.text = str(goal['amount']) + currency
        self.lb_days_to_go.text = str(-goal['to_go']) + ' Days to go'
        self.lb_progress.width = str(goal['perc_done'])+'%'
        self.img_six.source = goal['icon']
        self.lb_amount_payed.text = str(goal['amount_payed']) + currency

  def update_pt_seven(self):
    data = anvil.server.call('is_7_perc_pm')
    sizes = list(data.values())
    labels = list(data.keys())

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
      )

  def dp_accounts_change(self, **event_args):
    """This method is called when an item is selected"""
    if sstomelf.dp_accounts.
