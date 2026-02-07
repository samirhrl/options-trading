import plotly.graph_objects as go
from models.portfolio import Portfolio

class GraphPanel:
    """
    Represents a panel for plotting portfolio metrics (PnL or Greeks) using Plotly.

    Attributes:
        title : str
            Title of the graph panel (e.g., "Portfolio P&L", "Portfolio Delta")
    """

    def __init__(self, title: str):
        """
        Initializes the GraphPanel with a title.

        Parameters:
            title : str
                The title to display on the graph
        """
        self.title = title

    def make_fig(self, y, spot: float, strikes: list):
        """
        Creates a Plotly Figure displaying a portfolio metric across spot prices.

        Features:
            - Line plot of metric vs underlying spot price
            - Vertical dashed line at current spot
            - Vertical dash-dot lines at option strikes
            - Dark theme layout with minimal margins

        Parameters:
            y : np.ndarray or list
                Array of metric values (e.g., PnL, Delta, Gamma)
            spot : float
                Current spot price of the underlying asset
            strikes : list of floats
                List of option strike prices to highlight on the graph

        @Returns:
            plotly.graph_objects.Figure : Plotly figure ready to render in Dash
        """
        fig = go.Figure(go.Scatter(
            x=Portfolio.spot_grid,
            y=y,
            mode="lines",
            line=dict(width=2)
        ))

        # Highlight current spot price
        fig.add_vline(x=spot, line_dash="dash", line_color="orange",
                      line_width=2.5, opacity=0.9)

        # Highlight option strikes
        for k in strikes:
            fig.add_vline(x=k, line_dash="dashdot", line_color="cyan",
                          line_width=2, opacity=0.85)

        # Update layout
        fig.update_layout(
            template="plotly_dark",
            title=self.title,
            margin=dict(l=10, r=10, t=30, b=10),
            height=180
        )

        return fig
