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
  print(type + ' ' + str(category) +' ' + str(amount) + ' ' + name + ' ' + account_id + ' ' + str(to_account) + ' ' + str(date))
  app_tables.transactions.add_row(Type=type, Category=category, Amount=amount, name=name, account=app_tables.accounts.get_by_id(account_id), date=date,To_Account=to_account)

@anvil.server.callable
def get_user_accounts():
  user = anvil.users.get_user()

  if user:
    accounts = tables.app_tables.accounts.search(user=user)
    return [{'id': account.get_id(), 'name': account['account_name']} for account in accounts]
  else:
    return []

@anvil.server.callable
def update_daily_totals(account=None, change_date=None):
  # Update the Daily Totals for a certain account from the date of change until a user setting.
  #TODO FOR REAL ONLY FOR TESTING
  # Get today's date and the dates for yesterday and tomorrow

    today = datetime.now().date()

    yesterday = today - timedelta(days=1)

    tomorrow = today + timedelta(days=1)


    # Retrieve all accounts

    accounts = app_tables.accounts.search()


    # Loop through each account to check for daily totals

    for account in accounts:

        # Check if daily totals exist for yesterday, today, and tomorrow

        totals_exist = {

            'yesterday': app_tables.dailytotals.search(

                account=account,

                date=yesterday

            ),

            'today': app_tables.dailytotals.search(

                account=account,

                date=today

            ),

            'tomorrow': app_tables.dailytotals.search(

                account=account,

                date=tomorrow

            )

        }


        # Check for missing totals and generate new rows if necessary

        for date, total in totals_exist.items():

            if not total:  # If no totals exist for this date

                # Generate random values for total_income, total_outcome, and net_total

                total_income = random.randint(100, 1000)  # Example range for income

                total_outcome = random.randint(50, 500)    # Example range for outcome

                net_total = total_income - total_outcome


                # Create a new row in the dailytotals table

                app_tables.dailytotals.add_row(

                    account=account,

                    date=eval(date),  # Use eval to get the date variable

                    total_income=total_income,

                    total_outcome=total_outcome,

                    net_total=net_total

                )

                print(f"Added total for {date} for account {account['id']}: "

                      f"Income={total_income}, Outcome={total_outcome}, Net={net_total}")

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
      'amount': transfer['Amount']
    })

  return income_data, expense_data, transfer_data