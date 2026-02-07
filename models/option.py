from models.black_scholes import BlackScholes

class Option:
    """
    Represents a European option position.

    Attributes:
        type : str
            Option type: "Call" or "Put"
        side : str
            Position side: "BUY" or "SELL"
        strike : float
            Strike price of the option
        qty : int
            Quantity of options held
        vol : float
            Volatility used for pricing
        rate : float
            Risk-free interest rate
        maturity : float
            Time to maturity in years
        price_entry : float
            Entry price of the option (rounded to 2 decimals)
        prime : float
            Total initial cash outflow/inflow for the position
            (negative for BUY, positive for SELL)
    """

    def __init__(self, type_, side, strike, qty, vol, rate, maturity, price_entry):
        """
        Initializes an Option instance.

        Parameters:
            type_ : str
                Option type ("Call" or "Put")
            side : str
                "BUY" or "SELL"
            strike : float
                Strike price of the option
            qty : int
                Number of option contracts
            vol : float
                Volatility used for pricing
            rate : float
                Risk-free interest rate
            maturity : float
                Time to maturity in years
            price_entry : float
                Price at which the option was entered
        """
        self.type = type_
        self.side = side
        self.strike = strike
        self.qty = qty
        self.vol = vol
        self.rate = rate
        self.maturity = maturity
        self.price_entry = round(price_entry, 2)
        # Initial cash flow: negative for BUY, positive for SELL
        self.prime = round(qty * price_entry * (-1 if side == "BUY" else 1), 2)

    def pnl(self, spot):
        """
        Calculates the profit and loss (PnL) of the option at a given spot price.

        Parameters:
            spot : float
                Current price of the underlying asset

        @Returns:
            float : PnL of the option position (rounded to 2 decimals)
        """
        # Determine position sign: +1 for BUY, -1 for SELL
        sign = 1 if self.side == "BUY" else -1
        # Calculate PnL using Black-Scholes pricing
        current_price = BlackScholes.price(
            spot, self.strike, self.maturity, self.rate, self.vol, self.type
        )
        return round(sign * self.qty * (current_price - self.price_entry), 2)
