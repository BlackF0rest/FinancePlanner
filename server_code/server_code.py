import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime, timedelta, date
import random

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#

@anvil.server.callable
def get_daily_total_data(account_id):
  filters = {}
  if account_id:
    account = app_tables.accounts.get_by_id(account_id)
    if account:
        filters['account'] = account

  today = date(2024,11,7) #datetime.now().date()
  yesterday =   today - timedelta(days=1)
  tomorrow =   today + timedelta(days=1)

  filters['date'] = q.any_of(*[today, yesterday, tomorrow])
  
  daily_totals = app_tables.dailytotals.search(**filters)

  # Preparation for plotting
  dates = []
  net_totals = []

  for day in daily_totals:
    dates.append(day['date'])
    net_totals.append(day['net_total'])

  return {"dates": dates, "net_totals" : net_totals}

@anvil.server.callable
def get_pt_data(account, **kwargs):
  #class to get data from server
  pass

@anvil.server.callable
def get_icon_categories():
  return app_tables.icons.search()

@anvil.server.callable
def write_transaction(type, category, amount, name, account_id, date=datetime.now().date(), to_account=None):
  # Write the transaction different, depending on what it is.
  print("writing transactions")
  app_tables.transactions.add_row(Type=type, Category=category, Amount=amount, name=name, account=app_tables.accounts.get_by_id(account_id), date=date,To_Account=to_account)
  recalc_daily_totals(date)

def recalc_daily_totals(from_date, account_id):
  account = app_tables.accounts.get_by_id(account_id)
  days_ahead_from_today = app_tables.settings.get(user=anvil.users.get_user())['max_days_ahead_from_today']
  if from_date != datetime.now().date():
    days_to_calc = ((datetime.now().date() + timedelta(days=days_ahead_from_today)) - from_date).days
  else:
    days_to_calc = days_ahead_from_today
  
  daterange = [from_date + timedelta(days=x) for x in range(days_to_calc)]
  print(daterange)

  for day in daterange:
    daily_expense = (sum(transaction['Amount'] for transaction in app_tables.transactions.search(Type='expense', date=day, account=account)) + sum(transaction['Amount'] for transaction in app_tables.transactions.search(Type='transfer', date=day, account=account)))
    daily_income = (sum(transaction['Amount'] for transaction in app_tables.transactions.search(Type='income', date=day, account=account)) + sum(transaction['Amount'] for transaction in app_tables.transactions.search(Type='transfer', date=day, To_Account=account)))
    print((day - timedelta(days=1)))
    daily_total = app_tables.dailytotals.get(date=(day - timedelta(days=1)), account=account)['net_total'] + daily_income - daily_expense
    
    if app_tables.dailytotals.get(date=day, account=account) is not None:
      print('edited Row')
      app_tables.dailytotals.get(date=day, account=account).update(total_income=daily_income, total_outcome=daily_expense, net_total=daily_total)
    else:
      app_tables.dailytotals.add_row(account=account, date=day, total_income=daily_income, total_outcome=daily_expense, net_total=daily_total)
      print('added Row')

@anvil.server.callable
def get_user_accounts():
  user = anvil.users.get_user()

  if user:
    accounts = tables.app_tables.accounts.search(user=user)
    return [{'id': account.get_id(), 'name': account['account_name']} for account in accounts]
  else:
    return []

@anvil.server.callable
def set_account_setting(account_id, user):
  app_tables.settings.get(user=user).update(current_account=app_tables.accounts.get_by_id(account_id))

@anvil.server.callable
def get_current_account_id(user):
  return app_tables.settings.get(user=user)['current_account'].get_id()

@anvil.server.callable
def get_transactions(account_id, date=datetime.now().date()):
  incomes = app_tables.transactions.search(Type='income', date=date)
  expenses = app_tables.transactions.search(Type='expense', date=date)
  transfers = app_tables.transactions.search(Type='transfer', date=date)

  income_data = []
  expense_data = []
  transfer_data = []
  
  for income in incomes:
    income_data.append({
      'name': income['name'],
      'category': income['Category'],
      'amount': income['Amount']
    })
  for expense in expenses:
    expense_data.append({
      'name': expense['name'],
      'category': expense['Category'],
      'amount': expense['Amount']
    })
  for transfer in transfers:
    transfer_data.append({
      'name': transfer['name'],
      'category': transfer['Category'],
      'amount': transfer['Amount'],
      'to': transfer['To_Account']['account_name']
    })

  return income_data, expense_data, transfer_data

@anvil.server.callable
def get_icon(icon_category):
  return app_tables.icons.get(category=icon_category)['Icon']