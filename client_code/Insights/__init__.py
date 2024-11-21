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
      textposition='auto'
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

  def update_pt_three(self):
    data = anvil.server.call('is_3_get_expense_data')

    categories = list(data.keys())
    amounts = list(data.values())

    self.pt_three.data = go.Pie(
      labels=categories,
      values=amounts
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

  def update_pt_six(self):
    data = anvil.server.call('is_6_saving_goal')

    self.lb_name.text = data[0]['name']
    self.lb_amount.text = data[0]['amount']
    self.lb_days_to_go.text = f'{days} To Go', data[0]['to_go']
    

  def update_pt_seven(self):
    pass