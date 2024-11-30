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
import calendar

@anvil.server.callable
def get_daily_total_data():
  """Get data from Daily Total Database yesterday, today and tomorrow to display on the main Graph."""
  
  account = app_tables.settings.get(user=anvil.users.get_user())['current_account'] # get the current account

  # get Dates from yesterday, today and tomorrow
  today = datetime.now().date()
  yesterday =   today - timedelta(days=1)
  tomorrow =   today + timedelta(days=1)

  # create Lists
  dates = []
  net_totals = []

  # check if yesterday exists in the database, io not return 0
  net_yesterday = app_tables.dailytotals.get(account=account, date=yesterday)
  dates.append(yesterday)
  if net_yesterday is not None:
    net_totals.append(net_yesterday['net_total'])
  else:
    net_totals.append(0)
  # check if today exists in the database, io not return 0
  net_today =  app_tables.dailytotals.get(account=account, date=today)
  dates.append(today)
  if net_today is not None:
    net_totals.append(net_today['net_total'])
  else:
    net_totals.append(0)
  # check if tomorrow exists in the database, io not return 0
  net_tomorrow =  app_tables.dailytotals.get(account=account, date=tomorrow)
  dates.append(tomorrow)
  if net_tomorrow is not None:
    net_totals.append(net_tomorrow['net_total'])
  else:
    net_totals.append(0)

  return {"dates": dates, "net_totals" : net_totals}
  
@anvil.server.callable
def is_1_get_fix_month(accounts=None):
  # every (actual) Month not theoretical with 30.xx days
  month_range = get_month_range()
  if accounts != []:
    return_dict = {}
    month_list = []
    i=0
    for account in accounts:
      for first_day, last_day in month_range:
        month = first_day.month
        transactions = app_tables.transactions.search(
        type='expense',
        recurring=True,
        spread_out=False,
        date=q.less_than_or_equal_to(last_day),
        end_date=q.greater_than_or_equal_to(first_day),
        account=app_tables.accounts.get_by_id(account))
        if i==0:
          month_list.append(first_day.month)

        if str(month) in return_dict.keys():
          return_dict[str(month)] += sum(transaction['amount'] for transaction in transactions)
        else:
          return_dict[str(month)] = sum(transaction['amount'] for transaction in transactions)
      i = 1
  else:
    month_range = get_month_range()
    return_dict = {}
    month_list = []
    
    for first_day, last_day in month_range:
      month = first_day.month
        
      transactions = app_tables.transactions.search(
        type='expense',
        recurring=True,
        spread_out=False,
        date=q.less_than_or_equal_to(last_day),
        end_date=q.greater_than_or_equal_to(first_day),
        account=app_tables.settings.get(user=anvil.users.get_user())['current_account']
      )
      

      return_dict[str(month)] = sum(transaction['amount'] for transaction in transactions)
      month_list.append(first_day.month)

  return return_dict, month_list

@anvil.server.callable
def is_2_ic_oc_month(accounts=[]):
  #total income vs outcome everey month (real month values)
  month_range = get_month_range()
  return_dict = {}
  month_list = []
  i = 0
  if accounts != []:
    for account in accounts:
      for first_day, last_day in month_range:
        if i==0:
          month_list.append(first_day.month)
        month = first_day.month
        daily_rows = app_tables.dailytotals.search(
          account=app_tables.accounts.get_by_id(account),
          date=q.all_of(q.between(first_day-timedelta(days=1), last_day+timedelta(days=1), min_inclusive=False ,max_inclusive=False))
        )
        month_dict = {}
    
        month_dict['income'] = round(sum(daily_row['total_income'] for daily_row in daily_rows),2)
        month_dict['expense'] = round(sum(daily_row['total_outcome'] for daily_row in daily_rows),2)

        if str(month) in return_dict.keys():
          for key in month_dict.keys():
            return_dict[str(month)][key] += month_dict[key]
        else:
          return_dict[str(month)] = month_dict

      i = 1
  else:
    for first_day, last_day in month_range:
        month_list.append(first_day.month)
        month = first_day.month
        daily_rows = app_tables.dailytotals.search(
          account=app_tables.settings.get(user=anvil.users.get_user())['current_account'],
          date=q.all_of(q.between(first_day-timedelta(days=1), last_day+timedelta(hours=23, minutes=59), min_inclusive=False ,max_inclusive=False))
        )
      
        month_dict = {}

        month_dict['income'] = round(sum(daily_row['total_income'] for daily_row in daily_rows),2)
        month_dict['expense'] = round(sum(daily_row['total_outcome'] for daily_row in daily_rows),2)

        return_dict[str(month)] = month_dict
  return return_dict, month_list

@anvil.server.callable
def is_3_get_expense_data(accounts = []):
  year = datetime.now().year
  month = datetime.now().month

  first_day = datetime(year, month, 1)
  if month == 12:
    last_day = datetime(year+1, 1, 1) - timedelta(days=1)
  else:
    last_day = datetime(year, month+1, 1) - timedelta(days=1)
  
  if accounts != []:
    transactions = itertools.chain.from_iterable(
      app_tables.transactions.search(
        type='expense', 
        date=q.between(first_day-timedelta(days=1), last_day, min_inclusive=False ,max_inclusive=True),
        account=app_tables.accounts.get_by_id(account)
    ) for account in accounts
  )
  else:
    transactions = app_tables.transactions.search(
      type='expense', 
      date=q.between(first_day-timedelta(days=1), last_day, min_inclusive=False ,max_inclusive=True),
      account=app_tables.settings.get(user=anvil.users.get_user())['current_account'])

  category_counts = {}

  for transaction in transactions:
      category = transaction['category']['category']
      if category in category_counts.keys():
        category_counts[category] += transaction['amount']
      else:
        category_counts[category] = transaction['amount']

  return category_counts

@anvil.server.callable
def is_5_costs_qt():
  year = datetime.now().year
  qt_starts = [date(year,1,1), date(year,4,1), date(year,7,1), date(year,10,1)]
  return_list = []
  
  for qt in range(4):
    first_day = qt_starts[qt]
    if qt == 3:
      last_day = date(year,12,31)
    else:
      last_day = qt_starts[(qt+1)] - timedelta(days=1)
  
    dailies = app_tables.dailytotals.search(account=app_tables.settings.get(user=anvil.users.get_user())['current_account'], date=q.between(first_day, last_day))
    return_list.append(sum(daily['total_outcome'] for daily in dailies))

  return return_list

@anvil.server.callable
def is_6_saving_goal():
  last_day = datetime.now().date() - timedelta(days=30)
  results = app_tables.transactions.search(account=app_tables.settings.get(user=anvil.users.get_user())['current_account'], type=q.any_of('expense','transfer'), spread_out=True, end_date=q.greater_than_or_equal_to(last_day))

  return_list = []

  for result in results:
    total_amount = (result['end_date'] - result['date']).days * result['amount']
    if result['end_date'] <= datetime.now().date():
      perc_done = 100
      to_go = (result['end_date']-result['date']).days
      amount_payed = total_amount
    elif result['date'] > datetime.now().date():
      perc_done = 0
      to_go = 'Done'
      amount_payed = 0
    else:
      perc_done = round((((datetime.now().date() - result['date']).days / (result['end_date'] - result['date']).days) * 100), 0)
      to_go = (result['end_date']-datetime.now().date()).days
      amount_payed = amount_payed = (datetime.now().date() - result['date']).days * result['amount']
    return_list.append({
      'name':result['name'],
      'amount':total_amount,
      'amount_payed':amount_payed,
      'to_date':result['end_date'],
      'to_go':to_go,
      'perc_done': perc_done,
      'icon':result['category']['icon']
    })
    
  return_list.sort(key= lambda x: x['to_date'], reverse=True)

  return return_list

@anvil.server.callable
def is_7_perc_pm(accounts = []):
  return_dict = {}
  month_range = get_month_range()
  month_list = []
  if accounts != []:
    for start_day, end_day in month_range:
      month_list.append(start_day.month)
      acc_total_income = 0
      acc_total_outcome = 0
      for account in accounts:
        results = app_tables.dailytotals.search(
          account=app_tables.settings.get(user=anvil.users.get_user())['current_account'],
          date=q.between(start_day, end_day)
        )
        monthly_income = 0
        monthly_outcome = 0
    
        for day in results:
          monthly_income += day['total_income']
          monthly_outcome += day['total_outcome']

        acc_total_income += monthly_income
        acc_total_outcome += monthly_outcome
    
      total_month = acc_total_income + acc_total_outcome
    
      if total_month == 0:
        ratio = 0
      else:
        ratio = round(((acc_total_income*100/total_month)-(acc_total_outcome*100/total_month)),1)
  
      return_dict[f'{start_day.month}']=ratio
  else:
    for start_day, end_day in month_range:
      month_list.append(start_day.month)
      results = app_tables.dailytotals.search(
        account=app_tables.settings.get(user=anvil.users.get_user())['current_account'],
        date=q.between(start_day, end_day)
      )
      monthly_income = 0
      monthly_outcome = 0
  
      for day in results:
        monthly_income += day['total_income']
        monthly_outcome += day['total_outcome']
  
      total_month = monthly_income + monthly_outcome
  
      if total_month == 0:
        ratio = 0
      else:
        ratio = round(((monthly_income*100/total_month)-(monthly_outcome*100/total_month)),1)
  
      return_dict[f'{start_day.month}']=ratio

  return return_dict, month_list
    
@anvil.server.callable
def get_icon_categories():
  return app_tables.icons.search()

@anvil.server.callable
def write_transaction(type, category, amount, name, account_id, date=datetime.now().date(), to_account=None, recurring=False, end_date=None, spread_out=False):
  # Write the transaction different, depending on what it is.
  app_tables.transactions.add_row(
    type=type, 
    category=app_tables.icons.get(category=category), 
    amount=amount, 
    name=name, 
    account=app_tables.accounts.get_by_id(account_id), 
    date=date,to_account=to_account, 
    recurring=recurring, 
    end_date=end_date, 
    spread_out=spread_out)
  recalc_daily_totals(date, get_current_account_id())
  if type == 'transfer':
    recalc_daily_totals(date, to_account.get_id())

def recalc_daily_totals(from_date, account_id):
  account = app_tables.accounts.get_by_id(account_id)
  days_ahead_from_today = app_tables.settings.get(user=anvil.users.get_user())['calculate_days_ahead']
  if from_date != datetime.now().date():
    days_to_calc = ((datetime.now().date() + timedelta(days=days_ahead_from_today)) - from_date).days
  else:
    days_to_calc = days_ahead_from_today
  
  daterange = [from_date + timedelta(days=x) for x in range((days_to_calc+1))]
  
  for day in daterange:
    daily_expense = (sum(transaction['amount'] for transaction in app_tables.transactions.search(type=q.any_of('expense', 'transfer'), 
                                                                                                 date=day, 
                                                                                                 account=account))
                     + sum(transaction['amount'] for transaction in app_tables.transactions.search(end_date=q.any_of(None, q.greater_than_or_equal_to(day)), 
                                                                                                   date=q.less_than(day),
                                                                                                   type=q.any_of('expense', 'transfer'), 
                                                                                                   recurring=True, 
                                                                                                   account=account)))
    daily_income = (sum(transaction['amount'] for transaction in app_tables.transactions.search(type='income', 
                                                                                                date=day, 
                                                                                                account=account)) 
                    + sum(transaction['amount'] for transaction in app_tables.transactions.search(type='transfer', 
                                                                                                  date=day, 
                                                                                                  to_account=account))
                    + sum(transaction['amount'] for transaction in app_tables.transactions.search(end_date=q.any_of(None, q.greater_than_or_equal_to(day)), 
                                                                                                  date=q.less_than(day),
                                                                                                  type='income', 
                                                                                                  recurring=True, 
                                                                                                  account=account))
                    + sum(transaction['amount'] for transaction in app_tables.transactions.search(end_date=q.any_of(None, q.greater_than_or_equal_to(day)), 
                                                                                                  date=q.less_than(day),
                                                                                                  type='transfer', 
                                                                                                  recurring=True, 
                                                                                                  to_account=account)))
    
    if app_tables.dailytotals.get(date=(day - timedelta(days=1)), account=account) is not None:
      daily_total = app_tables.dailytotals.get(date=(day - timedelta(days=1)), account=account)['net_total'] + daily_income - daily_expense
    else:
      daily_total = daily_income - daily_expense
      
    if app_tables.dailytotals.get(date=day, account=account) is not None:
      app_tables.dailytotals.get(date=day, account=account).update(total_income=round(daily_income,2), total_outcome=round(daily_expense,2), net_total=round(daily_total,2))
    else:
      app_tables.dailytotals.add_row(account=account, date=day, total_income=round(daily_income,2), total_outcome=round(daily_expense,2), net_total=round(daily_total,2))

@anvil.server.callable
def get_account_from_id(account_id):
  return app_tables.accounts.get_by_id(account_id)

@anvil.server.callable
def get_user_accounts():
  user = anvil.users.get_user()

  if user:
    accounts = tables.app_tables.accounts.search(user=user)
    return [{'id': account.get_id(), 'name': account['name']} for account in accounts]
  else:
    return []

@anvil.server.callable
def set_account_setting(account_id):
  app_tables.settings.get(user=anvil.users.get_user()).update(current_account=app_tables.accounts.get_by_id(account_id))

@anvil.server.callable
def get_current_account_id():
  return app_tables.settings.get(user=anvil.users.get_user())['current_account'].get_id()

@anvil.server.callable
def get_transactions(date=datetime.now().date()):
  curr_account = app_tables.settings.get(user=anvil.users.get_user())['current_account']
  incomes = app_tables.transactions.search(type='income', 
                                           date=date, 
                                           recurring=False, 
                                           account=curr_account)
  extra_incomes = app_tables.transactions.search(type='income',
                                                date=q.less_than_or_equal_to(date),
                                                recurring=True,
                                                account=curr_account,
                                                end_date=q.any_of(None, q.greater_than_or_equal_to(date)))
  expenses = app_tables.transactions.search(type='expense', 
                                            date=date,
                                            recurring=False,
                                            account=curr_account
                                           )
  extra_expenses = app_tables.transactions.search(type='expense',
                                                date=q.less_than_or_equal_to(date),
                                                recurring=True,
                                                account=curr_account,
                                                end_date=q.any_of(None, q.greater_than_or_equal_to(date)))
  expense_transfers = app_tables.transactions.search(type='transfer', 
                                            date=date,
                                            recurring=False,
                                            account=curr_account,
                                            )
  expense_extra_transfers = app_tables.transactions.search(type='transfer',
                                                  date=q.less_than_or_equal_to(date),
                                                  recurring=True,
                                                  account=curr_account,
                                                  end_date=q.any_of(None, q.greater_than_or_equal_to(date))
                                                  )
  income_transfers = app_tables.transactions.search(type='transfer', 
                                              date=date,
                                              recurring=False,
                                              to_account=curr_account,
                                              )
  income_extra_transfers = app_tables.transactions.search(type='transfer',
                                                  date=q.less_than_or_equal_to(date),
                                                  recurring=True,
                                                  to_account=curr_account,
                                                  end_date=q.any_of(None, q.greater_than_or_equal_to(date))
                                                  )
  
  income_data = []
  expense_data = []
  transfer_data = []
  
  for income in itertools.chain(incomes, extra_incomes):
    income_data.append({
      'name': income['name'],
      'category': income['category'],
      'amount': income['amount'],
      'id':income.get_id()
    })
  for expense in itertools.chain(expenses, extra_expenses):
    expense_data.append({
      'name': expense['name'],
      'category': expense['category'],
      'amount': expense['amount'],
      'id':expense.get_id()
    })
  for transfer in itertools.chain(expense_transfers, expense_extra_transfers):
    transfer_data.append({
      'name': transfer['name'],
      'category': transfer['category'],
      'amount': (0 - transfer['amount']),
      'to': transfer['to_account']['name'],
      'id':transfer.get_id()
    })
  for transfer in itertools.chain(income_transfers, income_extra_transfers):
    transfer_data.append({
      'name': transfer['name'],
      'category': transfer['category'],
      'amount': transfer['amount'],
      'from': transfer['account']['name'],
      'id':transfer.get_id()
    })

  return income_data, expense_data, transfer_data

@anvil.server.callable
def get_icon(icon_category):
  return app_tables.icons.get(category=icon_category)['icon']

@anvil.server.callable
def get_all_icons():
  rows = app_tables.icons.search()
  icon_list = []
  for row in rows:
    icon_list.append({row['category']:row['icon']})
    
  return icon_list

@anvil.server.callable
def get_settings():
  return app_tables.settings.get(user=anvil.users.get_user())

@anvil.server.callable
def set_days_into_future(days):
  app_tables.settings.get(user=anvil.users.get_user()).update(calculate_days_ahead=days)

@anvil.server.callable
def get_time_values():
  data = app_tables.time_values.search()
  time_dict = {}
  for row in data:
    time_dict[row['name']] = row['value']

  return time_dict

@anvil.server.callable
def get_currency():
  return app_tables.settings.get(user=anvil.users.get_user())['currency']

@anvil.server.callable
def set_currency(currency):
  app_tables.settings.get(user=anvil.users.get_user()).update(currency=currency)

def get_month_range():
    # Get the current date
    current_date = datetime.now()

    # Calculate the start and end months
    start_month = current_date.month - 6
    start_year = current_date.year
    end_month = current_date.month + 5
    end_year = current_date.year
  
    # Adjust start year and month if needed
    if start_month <= 0:
        start_year -= 1
        start_month += 12

    # Adjust end year and month if needed
    if end_month > 12:
        end_year += 1
        end_month -= 12

    # Create a list to hold the first and last days of each month
    month_ranges = []

    # Loop through the range of months
    for i in range(-6, 5):  # From -6 to +5
        # Calculate the month and year
        month = (current_date.month + i - 1) % 12 + 1
        year = current_date.year + (current_date.month + i - 1) // 12
        # Get the first day of the month
        first_day = datetime(year, month, 1)
        # Get the last day of the month
        last_day = datetime(year, month, calendar.monthrange(year, month)[1])
        month_ranges.append(((first_day), (last_day)))
    return month_ranges

@anvil.server.callable
def delete_transaction(transaction_id):
  transaction = app_tables.transactions.get_by_id(transaction_id)
  account = transaction['account']
  from_date = transaction['date']
  transaction.delete()
  recalc_daily_totals(from_date, account.get_id())

@anvil.server.callable
def create_account(name):
  app_tables.accounts.add_row(name=name, user=anvil.users.get_user())

@anvil.server.callable
def delete_account(account_id):
  account = app_tables.accounts.get_by_id(account_id)

  for day in app_tables.dailytotals.search(account=account):
    day.delete()

  for transaction in app_tables.transactions.search(account=account, type=q.not_('transfer')):
    transaction.delete()

  account.update(user=None) # don't Delete account name, so transfers still show the name of the account

@anvil.server.callable
def delete_user():
  for account in app_tables.accounts.search(user=anvil.users.get_user()):
    for transaction in app_tables.transactions.search(account=account):
      transaction.delete()
    for daily_total in app_tables.dailytotals.search(account=account):
      daily_total.delete()
    account.delete()
  app_tables.settings.get(user=anvil.users.get_user()).delete()
  app_tables.users.get_by_id(anvil.users.get_user().get_id()).delete()
  
@anvil.server.callable
def setup_user(name):
  curr_account = app_tables.accounts.add_row(user=anvil.users.get_user(), name=name)
  app_tables.settings.add_row(currency='$', current_account=curr_account, calculate_days_ahead=15, user=anvil.users.get_user())

@anvil.server.callable
def is_first_login():
  if not app_tables.settings.get(user=anvil.users.get_user()):
    return True
  else:
    return False