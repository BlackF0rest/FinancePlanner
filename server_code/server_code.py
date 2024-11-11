import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime, timedelta
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
  filters = []
  if account_id:
    account = app_tables.accounts.get_by_id(account_id)
    if account:
        filters.append('account' == account)
  
  today = datetime.now().date()
  yesterday = today - timedelta(days=1)
  tomorrow = today + timedelta(days=1)

  date_filter = q.any_of(
        'date' == today,
        'date' == yesterday,
        'date' == tomorrow

    )

  combined_filter = q.all_of(*filters, date_filter)

  print(combined_filter)

  daily_totals = app_tables.dailytotals.search(combined_filter)

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
def write_transaction(type, category, amount, name, account, to_account=None):
  # Write the transaction different, depending on what it is.
  print("writing transactions")
  app_tables.transactions.add_row(account=app_tables.settings.get(user=anvil.users.get_user()))

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
    