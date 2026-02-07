from dash import html, dcc
from views.graph_panel import GraphPanel
from views.book_table import BookTable

class DashApp:
    """
    Initializes and runs a Dash-based trading dashboard for an option portfolio.

    Attributes:
        app : dash.Dash
            The Dash application instance
        portfolio : Portfolio
            Portfolio object containing option positions
        graph_panels : dict
            Dictionary mapping Greek/PnL names to GraphPanel instances
        book_table : BookTable
            Table component for displaying the portfolio book
    """

    def __init__(self, portfolio):
        """
        Initializes the Dash app, creates graph panels and book table,
        and sets up the layout.

        Parameters:
            portfolio : Portfolio
                The portfolio instance to display and manage
        """
        import dash
        self.app = dash.Dash(__name__)
        self.portfolio = portfolio

        # Initialize graph panels for portfolio metrics
        self.graph_panels = {
            "P&L": GraphPanel("Portfolio P&L"),
            "Delta": GraphPanel("Portfolio Delta"),
            "Gamma": GraphPanel("Portfolio Gamma"),
            "Vega": GraphPanel("Portfolio Vega"),
            "Theta": GraphPanel("Portfolio Theta"),
            "Rho": GraphPanel("Portfolio Rho"),
        }

        # Initialize the book table component
        self.book_table = BookTable()

        # Setup the layout
        self._init_layout()

    def _init_layout(self):
        """
        Defines the Dash app layout including:
            - Tabs for Equity, Bonds, and Credit
            - Stores for active tab and book data
            - Risk strip display for portfolio Greeks
            - Left panel for trade inputs
            - Right panel for graphs and book table
        """
        self.app.layout = html.Div(
            style={"height": "100vh", "display": "flex", "flexDirection": "column",
                   "background": "#111", "color": "white"},
            children=[
                # Top tabs
                html.Div(
                    style={"height": "42px", "display": "flex", "borderBottom": "1px solid #333"},
                    children=[
                        html.Div("Equity", id="tab-equity", n_clicks=0,
                                 style={"flex": 1, "textAlign": "center", "lineHeight": "42px",
                                        "fontWeight": "bold", "cursor": "pointer", "background": "#222"}),
                        html.Div("Bonds", id="tab-bonds", n_clicks=0,
                                 style={"flex": 1, "textAlign": "center", "lineHeight": "42px",
                                        "fontWeight": "bold", "cursor": "pointer", "background": "#111"}),
                        html.Div("Credit", id="tab-credit", n_clicks=0,
                                 style={"flex": 1, "textAlign": "center", "lineHeight": "42px",
                                        "fontWeight": "bold", "cursor": "pointer", "background": "#111"}),
                    ]
                ),
                # Stores for active tab and book data
                dcc.Store(id="active-tab", data="Equity"),
                dcc.Store(id="book-data", data=[]),
                # Risk strip display (PnL & Greeks)
                html.Div(
                    id="risk-strip",
                    style={"display": "grid", "gridTemplateColumns": "repeat(6,1fr)",
                           "borderBottom": "1px solid #333", "textAlign": "center",
                           "height": "36px", "lineHeight": "36px"}
                ),
                # Main content: left panel (inputs) and right panel (graphs & table)
                html.Div(
                    style={"flex": 1, "display": "grid", "gridTemplateColumns": "280px 1fr",
                           "overflow": "hidden"},
                    children=[
                        # Left panel: trading inputs and buttons
                        html.Div(
                            style={"padding": "12px", "borderRight": "1px solid #333",
                                   "overflowY": "auto"},
                            children=[
                                html.Label("Spot"),
                                dcc.Slider(50, 150, 1, value=100, id="spot",
                                           marks={i: {'label': str(i), 'style': {'color': 'white'}}
                                                  for i in range(50, 151, 20)}),
                                html.Br(), html.Label("Strike"),
                                dcc.Input(id="strike", type="number", value=100,
                                          style={"width": "100%", "color": "black"}),
                                html.Br(), html.Br(), html.Label("Type"),
                                dcc.Dropdown(["Call", "Put"], "Call", id="type",
                                             style={"color": "black"}),
                                html.Br(), html.Label("Side"),
                                dcc.Dropdown(["BUY", "SELL"], "BUY", id="side",
                                             style={"color": "black"}),
                                html.Br(), html.Label("Qty"),
                                dcc.Input(id="qty", type="number", value=1,
                                          style={"width": "100%", "color": "black"}),
                                html.Br(), html.Br(), html.Label("Volatility"),
                                dcc.Input(id="vol", type="number", value=0.2, step=0.01,
                                          style={"width": "100%", "color": "black"}),
                                html.Br(), html.Br(), html.Label("Risk-free Rate"),
                                dcc.Input(id="rate", type="number", value=0.01, step=0.001,
                                          style={"width": "100%", "color": "black"}),
                                html.Br(), html.Br(), html.Label("Maturity (yrs)"),
                                dcc.Input(id="maturity", type="number", value=0.5, step=0.01,
                                          style={"width": "100%", "color": "black"}),
                                html.Br(), html.Br(), html.Label("Premium (optional)"),
                                dcc.Input(id="price_entry_input", type="number", value=0, step=0.01,
                                          style={"width": "100%", "color": "black"}),
                                html.Br(), html.Br(), html.Br(),
                                html.Button("EXECUTE TRADE", id="trade", style={"width": "100%"}),
                                html.Br(), html.Br(),
                                html.Button("FLATTEN PORTFOLIO", id="flatten", style={"width": "100%"}),
                                dcc.ConfirmDialog(id="prime-error",
                                                  message="Error: inconsistent premium for this trade!")
                            ]
                        ),
                        # Right panel: graphs and table
                        html.Div(
                            id="right-panel",
                            style={"padding": "10px", "display": "flex",
                                   "flexDirection": "column", "overflow": "hidden"}
                        )
                    ]
                )
            ]
        )

    def run(self):
        """
        Runs the Dash app in debug mode.
        """
        self.app.run(debug=True)
