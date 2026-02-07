"""
Main entry point for the Options Trading Dashboard.

This script initializes the portfolio, sets up the Dash application view,
registers the trade controller, and runs the Dash server.
"""

from models.portfolio import Portfolio
from views.dash_app import DashApp
from controllers.trade_controller import TradeController

if __name__ == "__main__":
    # Initialize an empty portfolio
    portfolio = Portfolio()

    # Initialize the Dash application view with the portfolio
    app_view = DashApp(portfolio)

    # Attach the trade controller to manage trades and callbacks
    TradeController(portfolio, app_view)

    # Run the Dash app
    app_view.run()
