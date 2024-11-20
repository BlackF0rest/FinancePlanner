import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime, timedelta, date
import random
import itertools

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
def is_get_fixcosts_month(all_accounts=False):
  # Sum of all recurring expenses in a month
  if all_accounts:
    pass
  else:
    pass

@anvil.server.callable
def is_1_get_fix_month():
  # every (actual) Month not theoretical with 30.xx days
  year = datetime.now().year
  return_dict = []
  
  for month in range(1, 13):
    first_day = datetime(year, month, 1)
    if month == 12:
      last_day = datetime(year+1, 1, 1) - timedelta(days=1)
    else:
      last_day = datetime(year, month+1, 1) - timedelta(days=1)
      
    transactions = app_tables.transactions.search(
    Type='expense',
    recurring=True,
    spread_out=False,
    date=q.less_than_or_equal_to(last_day),
    end_date=q.greater_than_or_equal_to(first_day))

    return_dict[month] = sum(transaction['Amount'] for transaction in transactions)

  print(return_dict)
  return return_dict

@anvil.server.callable
def is_2_ic_oc_month():
  #total income vs outcome everey month (real month values)
  year = datetime.now().year
  return_list = []
  
  for month in range(1, 13):
    first_day = datetime(year, month, 1)
    if month == 12:
      last_day = datetime(year+1, 1, 1) - timedelta(days=1)
    else:
      last_day = datetime(year, month+1, 1) - timedelta(days=1)

    daily_rows = app_tables.dailytotals.search(
      account=app_tables.settings.get(user=anvil.users.get_user())['current_account'],
      date=q.between(first_day, last_day)
    )
    month_dict = {}

    month_dict['income'] = sum(daily_row['total_income'] for daily_row in daily_rows)
    month_dict['expense'] = sum(daily_row['total_outcome'] for daily_row in daily_rows)

  return_list.append(month_dict)
  print(return_list)
  return return_list

@anvil.server.callable
def is_3_get_expense_data(all_accounts = None):
  year = datetime.now().year
  month = datetime.now().month

  first_day = datetime(year, month, 1)
  if month == 12:
    last_day = datetime(year+1, 1, 1) - timedelta(days=1)
  else:
    last_day = datetime(year, month+1, 1) - timedelta(days=1)
  
  if all_accounts:
    pass
  else:
    transactions = app_tables.transactions.search(
      Type='expense', 
      date=q.between(first_day.date(), last_day.date()))

  category_counts = {}

  for transaction in transactions:
      category = transaction['Category']['category']
      if category in category_counts:
        category_counts[category] += transaction['Amount']
      else:
        category_counts[category] = transaction['Amount']

  return category_counts

@anvil.server.callable
def is_5_costs_qt():
  year = datetime.now().year
  qt_starts = [datetime.date(year,1,1), datetime.date(year,4,1), datetime.date(year,7,1), datetime.date(year,10,1)]
  return_list = []
  
  for qt in range(4):
    first_day = qt_starts[qt]
    if qt == 3:
      last_day = datetime.date(year,12,31)
    else:
      last_day = qt_starts[(qt+1)] - timedelta(days=1)
  
    dailies = app_tables.dailytotals.search(account=app_tables.settings.get(current_account=anvil.users.get_user()), date=q.between(first_day, last_day))
    return_list.append(sum(daily['total_outcome'] for daily in dailies))

  print(return_list)
  return return_list

@anvil.server.callable
def is_6_saving_goal():
  last_day = datetime.now().date() - timedelta(days=30)
  results = app_tables.transactions.search(account=app_tables.settings.get(user=anvil.users.get_user())['current_account'], Type=q.any_of('expense','transfer'), spread_out=True, end_date=q.greater_than_or_equal_to(last_day))

  return_list = []
  
  pass
    
    
@anvil.server.callable
def get_icon_categories():
  return app_tables.icons.search()

@anvil.server.callable
def write_transaction(type, category, amount, name, account_id, date=datetime.now().date(), to_account=None, recurring=False, end_date=None, spread_out=False):
  # Write the transaction different, depending on what it is.
  print("writing transactions")
  app_tables.transactions.add_row(
    Type=type, 
    Category=app_tables.icons.get(category=category), 
    Amount=amount, 
    name=name, 
    account=app_tables.accounts.get_by_id(account_id), 
    date=date,To_Account=to_account, 
    recurring=recurring, 
    end_date=end_date, 
    spread_out=spread_out)
  recalc_daily_totals(date, get_current_account_id(anvil.users.get_user()))
  if type == 'transfer':
    recalc_daily_totals(date, to_account)

@anvil.server.callable
def test_recalc():
  recalc_daily_totals(datetime.now().date(), anvil.users.get_user())

def recalc_daily_totals(from_date, account_id):
  account = app_tables.accounts.get_by_id(account_id)
  days_ahead_from_today = app_tables.settings.get(user=anvil.users.get_user())['max_days_ahead_from_today']
  if from_date != datetime.now().date():
    days_to_calc = ((datetime.now().date() + timedelta(days=days_ahead_from_today)) - from_date).days
  else:
    days_to_calc = days_ahead_from_today
  
  daterange = [from_date + timedelta(days=x) for x in range(days_to_calc)]
  
  for day in daterange:
    daily_expense = (sum(transaction['Amount'] for transaction in app_tables.transactions.search(Type=q.any_of('expense', 'transfer'), date=day, account=account))
                     + sum(transaction['Amount'] for transaction in app_tables.transactions.search(end_date=q.any_of(None, q.greater_than(day)), date=q.not_(day),Type=q.any_of('expense', 'transfer'), recurring=True, account=account)))
    daily_income = (sum(transaction['Amount'] for transaction in app_tables.transactions.search(Type='income', date=day, account=account)) 
                    + sum(transaction['Amount'] for transaction in app_tables.transactions.search(Type='transfer', date=day, To_Account=account))
                    + sum(transaction['Amount'] for transaction in app_tables.transactions.search(end_date=q.any_of(None, q.greater_than(day)), date=q.not_(day),Type='income', recurring=True, account=account))
                    + sum(transaction['Amount'] for transaction in app_tables.transactions.search(end_date=q.any_of(None, q.greater_than(day)), date=q.not_(day),Type='transfer', recurring=True, To_Account=account)))
    
    if app_tables.dailytotals.get(date=(day - timedelta(days=1)), account=account) is not None:
      daily_total = app_tables.dailytotals.get(date=(day - timedelta(days=1)), account=account)['net_total'] + daily_income - daily_expense
    else:
      daily_total = daily_income - daily_expense
      
    if app_tables.dailytotals.get(date=day, account=account) is not None:
      print('edited Row')
      app_tables.dailytotals.get(date=day, account=account).update(total_income=daily_income, total_outcome=daily_expense, net_total=daily_total)
    else:
      app_tables.dailytotals.add_row(account=account, date=day, total_income=daily_income, total_outcome=daily_expense, net_total=daily_total)
      print('added Row')

@anvil.server.callable
def get_account_from_id(account_id):
  return app_tables.accounts.get_by_id(account_id)

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
def get_transactions(date=datetime.now().date()):
  curr_account = app_tables.settings.get(user=anvil.users.get_user())['current_account']
  incomes = app_tables.transactions.search(Type='income', 
                                           date=date, 
                                           recurring=False, 
                                           account=curr_account)
  extra_incomes = app_tables.transactions.search(Type='income',
                                                date=q.less_than_or_equal_to(datetime.now().date()),
                                                recurring=True,
                                                account=curr_account,
                                                end_date=q.any_of(None, q.greater_than_or_equal_to(date)))
  expenses = app_tables.transactions.search(Type='expense', 
                                            date=date,
                                            recurring=False,
                                            account=curr_account
                                           )
  extra_expenses = app_tables.transactions.search(Type='expense',
                                                date=q.less_than_or_equal_to(datetime.now().date()),
                                                recurring=True,
                                                account=curr_account,
                                                end_date=q.any_of(None, q.greater_than_or_equal_to(date)))
  expense_transfers = app_tables.transactions.search(Type='transfer', 
                                            date=date,
                                            recurring=False,
                                            account=curr_account,
                                            )
  expense_extra_transfers = app_tables.transactions.search(Type='transfer',
                                                  date=q.less_than_or_equal_to(datetime.now().date()),
                                                  recurring=True,
                                                  account=curr_account,
                                                  end_date=q.any_of(None, q.greater_than_or_equal_to(date))
                                                  )
  income_transfers = app_tables.transactions.search(Type='transfer', 
                                              date=date,
                                              recurring=False,
                                              To_Account=curr_account,
                                              )
  income_extra_transfers = app_tables.transactions.search(Type='transfer',
                                                  date=q.less_than_or_equal_to(datetime.now().date()),
                                                  recurring=True,
                                                  To_Account=curr_account,
                                                  end_date=q.any_of(None, q.greater_than_or_equal_to(date))
                                                  )
  
  income_data = []
  expense_data = []
  transfer_data = []
  
  for income in (incomes and extra_incomes):
    income_data.append({
      'name': income['name'],
      'category': income['Category'],
      'amount': income['Amount']
    })
  for expense in itertools:
    expense_data.append({
      'name': expense['name'],
      'category': expense['Category'],
      'amount': expense['Amount']
    })
  for transfer in expense_transfers and expense_extra_transfers:
    transfer_data.append({
      'name': transfer['name'],
      'category': transfer['Category'],
      'amount': (0 - transfer['Amount']),
      'to': transfer['To_Account']['account_name']
    })
  for transfer in income_transfers and income_extra_transfers:
    transfer_data.append({
      'name': transfer['name'],
      'category': transfer['Category'],
      'amount': transfer['Amount'],
      'from': transfer['account']['account_name']
    })

  return income_data, expense_data, transfer_data

@anvil.server.callable
def get_icon(icon_category):
  return app_tables.icons.get(category=icon_category)['Icon']

@anvil.server.callable
def get_all_icons():
  rows = app_tables.icons.search()
  icon_list = []
  for row in rows:
    icon_list.append({row['category']:row['Icon']})
    
  return icon_list

@anvil.server.callable
def get_settings(user):
  return app_tables.settings.get(user=user)

@anvil.server.callable
def set_days_into_future(user, days):
  app_tables.settings.get(user=user).update(max_days_ahead_from_today=days)

@anvil.server.callable
def get_time_values():
  data = app_tables.time_values.search()
  time_dict = []
  for row in data:
    time_dict[row['name']] = row['value']

  return time_dict