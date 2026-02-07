import numpy as np
from models.option import Option
from models.black_scholes import BlackScholes

class Portfolio:
    """
    Represents a portfolio of European option positions and computes
    portfolio-level PnL and Greeks across a range of spot prices.

    Attributes:
        spot_grid : np.ndarray
            Array of underlying prices used to evaluate portfolio curves
        book : list
            List of Option objects currently in the portfolio
    """

    # Define a fixed spot price grid for portfolio evaluation
    spot_grid = np.linspace(50, 150, 200)

    def __init__(self):
        """
        Initializes an empty portfolio.
        """
        self.book = []

    def add_option(self, opt: Option):
        """
        Adds an Option to the portfolio.

        Parameters:
            opt : Option
                An instance of the Option class to add to the portfolio
        """
        self.book.append(opt)

    def flatten(self):
        """
        Removes all options from the portfolio.
        """
        self.book.clear()

    def portfolio_curves(self):
        """
        Computes portfolio-level PnL and Greeks over the spot price grid.

        @Returns:
            tuple of np.ndarray:
                - pnl : array of portfolio PnL across spot_grid
                - delta : array of portfolio Delta across spot_grid
                - gamma : array of portfolio Gamma across spot_grid
                - vega : array of portfolio Vega across spot_grid
                - theta : array of portfolio Theta across spot_grid
                - rho : array of portfolio Rho across spot_grid
        """
        # Initialize arrays for portfolio metrics
        pnl = np.zeros_like(Portfolio.spot_grid)
        delta = np.zeros_like(Portfolio.spot_grid)
        gamma = np.zeros_like(Portfolio.spot_grid)
        vega = np.zeros_like(Portfolio.spot_grid)
        theta = np.zeros_like(Portfolio.spot_grid)
        rho = np.zeros_like(Portfolio.spot_grid)

        # Sum contributions from each option in the portfolio
        for opt in self.book:
            sign = 1 if opt.side == "BUY" else -1
            pnl += sign * opt.qty * (
                BlackScholes.price(
                    Portfolio.spot_grid, opt.strike, opt.maturity, opt.rate, opt.vol, opt.type
                )
                - opt.price_entry
            )
            delta += sign * opt.qty * BlackScholes.delta(
                Portfolio.spot_grid, opt.strike, opt.maturity, opt.rate, opt.vol, opt.type
            )
            gamma += sign * opt.qty * BlackScholes.gamma(
                Portfolio.spot_grid, opt.strike, opt.maturity, opt.rate, opt.vol
            )
            vega += sign * opt.qty * BlackScholes.vega(
                Portfolio.spot_grid, opt.strike, opt.maturity, opt.rate, opt.vol
            )
            theta += sign * opt.qty * BlackScholes.theta(
                Portfolio.spot_grid, opt.strike, opt.maturity, opt.rate, opt.vol, opt.type
            )
            rho += sign * opt.qty * BlackScholes.rho(
                Portfolio.spot_grid, opt.strike, opt.maturity, opt.rate, opt.vol, opt.type
            )

        return pnl, delta, gamma, vega, theta, rho
