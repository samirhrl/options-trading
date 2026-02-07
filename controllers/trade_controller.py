from dash import Input, Output, State, html, dcc
import dash
import numpy as np
from models.option import Option
from models.portfolio import Portfolio
from models.black_scholes import BlackScholes
from views.graph_panel import GraphPanel
from views.book_table import BookTable

class TradeController:
    """
    Controller class to handle trading actions, portfolio updates, and 
    dashboard rendering in a Dash application.

    Attributes:
        portfolio : Portfolio
            The user's portfolio containing option positions
        view : object
            The Dash view object that contains the app and layout
        app : dash.Dash
            Reference to the Dash app instance from the view
    """

    def __init__(self, portfolio: Portfolio, view):
        """
        Initializes the TradeController and registers Dash callbacks.

        Parameters:
            portfolio : Portfolio
                The portfolio instance to manage
            view : object
                Dash view object containing the app
        """
        self.portfolio = portfolio
        self.view = view
        self.app = view.app
        self.register_callbacks()

    def register_callbacks(self):
        """
        Registers all Dash callbacks for tab switching, portfolio trades,
        flattening, and updating the right-hand panel with graphs and tables.
        """

        # -------------------------
        # Tab switching
        # -------------------------
        @self.app.callback(
            Output("active-tab","data"),
            Output("tab-equity","style"),
            Output("tab-bonds","style"),
            Output("tab-credit","style"),
            Input("tab-equity","n_clicks"),
            Input("tab-bonds","n_clicks"),
            Input("tab-credit","n_clicks")
        )
        def switch_tab(equity, bonds, credit):
            """
            Switches between dashboard tabs and applies active styles.

            @Returns:
                tuple:
                    - active tab name ("Equity", "Bonds", or "Credit")
                    - style for equity tab
                    - style for bonds tab
                    - style for credit tab
            """
            tab_style_default = {"flex":1,"textAlign":"center","lineHeight":"42px",
                                 "fontWeight":"bold","cursor":"pointer","background":"#111"}
            tab_style_active = {"flex":1,"textAlign":"center","lineHeight":"42px",
                                "fontWeight":"bold","cursor":"pointer","background":"#222"}

            ctx = dash.callback_context
            clicked_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else "tab-equity"

            if clicked_id == "tab-equity":
                return "Equity", tab_style_active, tab_style_default, tab_style_default
            elif clicked_id == "tab-bonds":
                return "Bonds", tab_style_default, tab_style_active, tab_style_default
            elif clicked_id == "tab-credit":
                return "Credit", tab_style_default, tab_style_default, tab_style_active
            else:
                return "Equity", tab_style_active, tab_style_default, tab_style_default

        # -------------------------
        # Trade / Flatten Portfolio
        # -------------------------
        @self.app.callback(
            Output("book-data","data"),
            Output("risk-strip","children"),
            Output("prime-error","displayed"),
            Input("trade","n_clicks"),
            Input("flatten","n_clicks"),
            State("type","value"),
            State("side","value"),
            State("strike","value"),
            State("qty","value"),
            State("spot","value"),
            State("vol","value"),
            State("rate","value"),
            State("maturity","value"),
            State("price_entry_input","value")
        )
        def update_book(trade, flatten, opt, side, strike, qty, spot, vol, rate, maturity, price_input):
            """
            Handles trading and flattening actions:
                - Adds a new option to the portfolio
                - Flattens the portfolio
                - Computes updated PnL and Greeks for risk display

            @Returns:
                - book_data : list of dicts with option details and PnL
                - risk : list of html.Div representing portfolio PnL and Greeks
                - show_error : bool, whether to display price input error
            """
            # Set defaults for missing inputs
            spot = spot if spot is not None else 100
            qty = qty if qty is not None else 1
            strike = strike if strike is not None else spot
            vol = vol if vol is not None else 0.2
            rate = rate if rate is not None else 0.01
            maturity = maturity if maturity is not None else 0.5
            price_input = price_input if price_input is not None else 0
            opt = opt if opt in ["Call","Put"] else "Call"
            side = side if side in ["BUY","SELL"] else "BUY"

            show_error = False
            triggered_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0] \
                           if dash.callback_context.triggered else None

            if triggered_id == "flatten":
                self.portfolio.flatten()
            elif triggered_id == "trade":
                if price_input < 0:
                    show_error = True
                if show_error:
                    return dash.no_update, dash.no_update, True

                # Use provided price or Black-Scholes model price
                price_entry = price_input if price_input > 0 else BlackScholes.price(spot, strike, maturity, rate, vol, opt)
                self.portfolio.add_option(Option(opt, side, strike, qty, vol, rate, maturity, price_entry))

            # Compute portfolio metrics
            pnl, delta, gamma, vega, theta, rho = self.portfolio.portfolio_curves()

            # Get PnL at current spot
            try:
                spot_idx = np.searchsorted(Portfolio.spot_grid, spot)
                current_pnl = pnl[spot_idx] if len(pnl) > 0 else 0
            except Exception:
                current_pnl = 0
            pnl_color = "lime" if current_pnl >= 0 else "red"

            # Build risk strip display
            risk = [
                html.Div(f"P&L: {current_pnl:.2f}", style={"color": pnl_color,"fontWeight":"bold"}),
                html.Div(f"Δ: {delta.sum():.2f}" if delta is not None else "Δ: 0.0"),
                html.Div(f"Γ: {gamma.sum():.2f}" if gamma is not None else "Γ: 0.0"),
                html.Div(f"V: {vega.sum():.2f}" if vega is not None else "V: 0.0"),
                html.Div(f"Θ: {theta.sum():.2f}" if theta is not None else "Θ: 0.0"),
                html.Div(f"Ρ: {rho.sum():.2f}" if rho is not None else "Ρ: 0.0"),
            ]

            # Build book data for table
            book_data = []
            for o in self.portfolio.book:
                pnl_value = o.pnl(spot) if o.pnl(spot) is not None else 0
                book_data.append({
                    "type": o.type,
                    "side": o.side,
                    "strike": o.strike,
                    "qty": o.qty,
                    "vol": o.vol,
                    "rate": o.rate,
                    "maturity": o.maturity,
                    "price_entry": o.price_entry,
                    "prime": o.prime,
                    "pnl": pnl_value
                })

            return book_data, risk, show_error

        # -------------------------
        # Render Right Panel (Graphs + Table)
        # -------------------------
        @self.app.callback(
            Output("right-panel","children"),
            Input("active-tab","data"),
            Input("book-data","data"),
            Input("spot","value"),
        )
        def render_right_panel(tab, book_data, spot):
            """
            Updates the right-hand panel with portfolio graphs and book table.

            Parameters:
                tab : str
                    Currently active tab
                book_data : list of dict
                    Current portfolio book data
                spot : float
                    Current underlying spot price

            @Returns:
                list of html.Div : Graphs and table for display
            """
            spot = spot if spot is not None else 100

            if tab != "Equity":
                return html.Div(
                    "Nothing to print for the moment",
                    style={"color":"white","fontSize":"20px","textAlign":"center","marginTop":"20px"}
                )

            # Compute portfolio curves
            pnl, delta, gamma, vega, theta, rho = self.portfolio.portfolio_curves()
            strikes = [o.strike for o in self.portfolio.book]

            # Build graphs for each Greek and PnL
            graphs = [
                html.Div(dcc.Graph(figure=GraphPanel("Portfolio P&L").make_fig(pnl, spot, strikes)), style={"height":"100%"}),
                html.Div(dcc.Graph(figure=GraphPanel("Portfolio Delta").make_fig(delta, spot, strikes)), style={"height":"100%"}),
                html.Div(dcc.Graph(figure=GraphPanel("Portfolio Gamma").make_fig(gamma, spot, strikes)), style={"height":"100%"}),
                html.Div(dcc.Graph(figure=GraphPanel("Portfolio Vega").make_fig(vega, spot, strikes)), style={"height":"100%"}),
                html.Div(dcc.Graph(figure=GraphPanel("Portfolio Theta").make_fig(theta, spot, strikes)), style={"height":"100%"}),
                html.Div(dcc.Graph(figure=GraphPanel("Portfolio Rho").make_fig(rho, spot, strikes)), style={"height":"100%"}),
            ]

            # Build portfolio table
            table = html.Div([
                html.Div("BOOK", style={"height":"28px","lineHeight":"28px","borderBottom":"1px solid #333","fontWeight":"bold"}),
                BookTable().make_table(book_data)
            ], style={"flex":1,"marginTop":"8px","overflowY":"auto"})

            # Layout the graphs in a 2x3 grid
            graph_grid = html.Div(
                style={
                    "display":"grid",
                    "gridTemplateColumns":"1fr 1fr",
                    "gridTemplateRows":"repeat(3,1fr)",
                    "gap":"10px",
                    "flex":"0 0 60%",
                    "overflow":"hidden"
                },
                children=graphs
            )

            return [graph_grid, table]
