import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

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
def get_daily_total_data(account_name=None):
  filters = {}
  if account_name:
    filters['account'] = account_name
      
  daily_totals = app_tables.dailytotals.search(**filters)

  # Preparation for plotting
  dates = []
  net_totals = []

  for day in daily_totals:
    dates.append(day['date'])
    net_totals.append(day['net_total'])

  return {"dates": dates, "net_totals" : net_totals}

@anvil.server.callable
def get_pt_data(**kwargs):
  #class to get data from server
  pass

@anvil.server.callable
def write_transaction(type, category, amount, name, account, to_account=None):
  # Write the transaction different, depending on what it is.
  print("writing transactions")
  pass

def update_daily_totals(account, change_date):
  # Update the Daily Totals for a certain account from the date of change until a user setting.
  pass