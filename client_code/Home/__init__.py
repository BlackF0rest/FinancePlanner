from ._anvil_designer import HomeTemplate
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

class Home(HomeTemplate):
    """
    The Home class represents the main user interface of the application..
    """

    def __init__(self, **properties):
        """
        Initialize the Home form. Handle login, setup user accounts,
        and render the main graph.
        """
        # Set Form properties and Data Bindings
        self.init_components(**properties)

        # Initialize accounts dictionary
        self.accounts = None

        # Handle user login
        anvil.users.login_with_form()

        # Perform first-time user setup if applicable
        if anvil.server.call('is_first_login'):
            account_name_input = TextBox(placeholder='Account Name')
            anvil.alert(
                content=account_name_input,
                title='Welcome! Please enter the name of your first account:',
                dismissible=False,
                buttons=[('Create')],
                large=True,
            )
            anvil.server.call('setup_user', account_name_input.text)

        # Retrieve and display user's accounts
        self.update_accounts()

        # Initialize the main graph
        self.update_main_graph()

    def button_now_click(self, **event_args):
        """Navigate to the Home form."""
        open_form('Home')

    def button_transaction_click(self, **event_args):
        """Navigate to the Transactions form."""
        open_form('Transactions')

    def button_insights_click(self, **event_args):
        """Navigate to the Insights form."""
        open_form('Insights')

    def button_setting_click(self, **event_args):
        """Navigate to the Settings form."""
        open_form('Settings')

    def button_income_click(self, **event_args):
        """Open the Transaction_Form with the 'income' type."""
        open_form('Transaction_Form', type='income')

    def button_transfer_click(self, **event_args):
        """Open the Transaction_Form with the 'transfer' type."""
        open_form('Transaction_Form', type='transfer')

    def button_expense_click(self, **event_args):
        """Open the Transaction_Form with the 'expense' type."""
        open_form('Transaction_Form', type='expense')

    def dp_accounts_change(self, **event_args):
        """
        Update the current account setting when the user selects
        a different account from the dropdown menu.
        """
        selected_account_id = self.dp_accounts.selected_value
        anvil.server.call('set_account_setting', selected_account_id)
        self.update_main_graph()

    def update_accounts(self):
        """
        Fetch and update the user's accounts in the dropdown menu.
        Set the currently selected account.
        """
        self.accounts = anvil.server.call('get_user_accounts')
        self.dp_accounts.items = [(account['name'], account['id']) for account in self.accounts]

        if self.accounts:
            current_account_id = anvil.server.call('get_current_account_id')
            for account in self.accounts:
                if account['id'] == current_account_id:
                    self.dp_accounts.selected_value = account['id']

    def update_main_graph(self):
        """
        Update the main graph with daily total data.
        The graph displays net totals with color-coded markers
        indicating changes in values.
        """
        data = anvil.server.call('get_daily_total_data')
        dates = data['dates']
        totals = [int(round(total)) for total in data['net_totals']]

        # Determine marker colors based on total trends
        marker_colors = []
        for i, total in enumerate(totals):
            if i == 0:
                marker_colors.append('red' if total < 0 else 'black')
            else:
                marker_colors.append(
                    'green' if total > totals[i - 1] else
                    'red' if total < totals[i - 1] else
                    'black'
                )

        # Update Plotly graph data
        self.plot_now.data = [
            go.Scatter(
                x=dates,
                y=totals,
                text=totals,
                textposition='center',
                textfont=dict(size=18, color='white'),
                marker=dict(size=40, color=marker_colors),
                mode='lines+markers+text',
            )
        ]

        # Configure graph layout
        self.plot_now.layout = go.Layout(
            showlegend=False,
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showline=False,
                tickvals=dates,
                ticktext=dates,
                ticks='outside',
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showline=False,
                showticklabels=False,
            ),
            plot_bgcolor='rgba(255,255,255,0)',
            paper_bgcolor='rgba(0,0,0,0.2)',
        )
        self.plot_now.interactive = False

    def recalc_daily_click(self, **event_args):
        """Trigger a recalculation of daily totals on the server."""
        anvil.server.call('test_recalc')
