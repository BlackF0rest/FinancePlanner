from ._anvil_designer import SettingsTemplate
from anvil import *
import anvil.google.auth
import anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import plotly.graph_objects as go

class Settings(SettingsTemplate):
    def __init__(self, **properties):
        """Initialize the Settings form and set up initial properties."""
        self.init_components(**properties)
        self.selected_currency = None
        self.selected_days = None
        self.accounts = None
        
        # Update settings on initialization
        self.update_days()
        self.update_currency()
        self.update_accounts()

    def plot_now_show(self, **event_args):
        """Called when the Plot is shown on the screen."""
        pass

    def button_now_click(self, **event_args):
        """Navigate to the Home form when the button is clicked."""
        open_form('Home')

    def button_logs_click(self, **event_args):
        """Navigate to the Transactions form when the button is clicked."""
        open_form('Transactions')

    def button_insights_click(self, **event_args):
        """Navigate to the Insights form when the button is clicked."""
        open_form('Insights')

    def update_days(self):
        """Fetch and update the maximum days ahead from today."""
        self.selected_days = anvil.server.call('get_settings')['max_days_ahead_from_today']
        self.lb_days_future.text = self.selected_days

    def update_currency(self):
        """Fetch and update the selected currency."""
        self.selected_currency = anvil.server.call('get_currency')
        self.rd_euro.selected = (self.selected_currency == '€')
        self.rd_dollar.selected = (self.selected_currency == '$')

    def update_accounts(self):
        """Fetch and update the user's accounts."""
        self.accounts = anvil.server.call('get_user_accounts')
        self.dp_accounts.items = [(account['name'], account['id']) for account in self.accounts]

        # Set the currently selected account
        if self.accounts:
            current_account_id = anvil.server.call('get_current_account_id')
            for account in self.accounts:
                if account['id'] == current_account_id:
                    self.dp_accounts.selected_value = account['id']

    def bt_plus_days_click(self, **event_args):
        """Increment the selected days by 1."""
        self.selected_days += 1
        self.lb_days_future.text = self.selected_days

    def bt_minus_days_click(self, **event_args):
        """Decrement the selected days by 1."""
        self.selected_days -= 1
        self.lb_days_future.text = self.selected_days

    def rd_dollar_clicked(self, **event_args):
        """Set the selected currency to dollars when the radio button is clicked."""
        self.selected_currency = '$'

    def rd_euro_clicked(self, **event_args):
        """Set the selected currency to euros when the radio button is clicked."""
        self.selected_currency = '€'

    def bt_cancel_click(self, **event_args):
        """Reset the currency and days to their original values."""
        self.update_currency()
        self.update_days()

    def bt_apply_click(self, **event_args):
        """Apply the selected settings for days and currency."""
        anvil.server.call('set_days_into_future', self.selected_days)
        anvil.server.call('set_currency', self.selected_currency)

    def rd_create_account_clicked(self, **event_args):
        """Show/hide account creation controls based on the selected radio button."""
        self.bt_create_account.visible = self.rd_create_account.selected
        self.tb_acc_name.visible = self.rd_create_account.selected
        self.bt_delete_account.visible = self.rd_delete_account.selected
        self.dp_accounts.visible = self.rd_delete_account.selected

    def rd_delete_account_clicked(self, **event_args):
        """Show/hide account deletion controls based on the selected radio button."""
        self.bt_create_account.visible = self.rd_create_account.selected
        self.tb_acc_name.visible = self.rd_create_account.selected
        self.bt_delete_account.visible = self.rd_delete_account.selected
        self.dp_accounts.visible = self.rd_delete_account.selected

    def bt_create_account_click(self, **event_args):
        """Create a new account with the specified name."""
        if not self.tb_acc_name.text:
            self.tb_acc_name.border = 'solid red'  # Highlight the input field if empty
        else:
            anvil.server.call('create_account', self.tb_acc_name.text)
            alert('Account Created')
            open_form('Settings')

    def bt_delete_account_click(self, **event_args):
        """Delete the selected account after user confirmation."""
        if confirm('Do you want to delete this account?'):
            anvil.server.call('delete_account', self.dp_accounts.selected_value)
            alert('Account Deleted')
            open_form('Settings')

    def bt_delete_user_click(self, **event_args):
        """Delete the user's account on the website after confirmation."""
        if confirm('Do you want to delete your Account on this Website?'):
            alert('Thank you - Goodbye')
            anvil.server.call('delete_user')
            anvil.users.logout()

    def bt_logout_click(self, **event_args):
        """Log out the user and navigate to the Home form."""
        anvil.users.logout()
        open_form('Home')