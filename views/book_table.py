from dash import dash_table, html

class BookTable:
    """
    Generates a Dash DataTable for displaying the portfolio book.

    The table highlights key fields like 'pnl' and 'prime' using color coding:
        - Red for negative values
        - Lime for positive values
    """

    def make_table(self, book_data):
        """
        Creates a Dash DataTable from the provided book data.

        Parameters:
            book_data : list of dict
                Each dict represents an option in the portfolio with keys:
                ["type","side","strike","qty","vol","rate","maturity","price_entry","prime","pnl"]

        @Returns:
            dash_table.DataTable : Dash component ready to render
        """
        return dash_table.DataTable(
            # Table styling
            style_table={"height": "calc(100% - 28px)", "overflowY": "auto"},
            style_cell={
                "backgroundColor": "#111",
                "color": "white",
                "border": "1px solid #333",
                "fontSize": "12px",
                "textAlign": "center"
            },
            style_header={"backgroundColor": "#1e1e1e"},
            # Conditional formatting for PnL and Prime
            style_data_conditional=[
                {"if": {"filter_query": "{pnl} < 0", "column_id": "pnl"}, "color": "red"},
                {"if": {"filter_query": "{pnl} > 0", "column_id": "pnl"}, "color": "lime"},
                {"if": {"filter_query": "{prime} < 0", "column_id": "prime"}, "color": "red"},
                {"if": {"filter_query": "{prime} > 0", "column_id": "prime"}, "color": "lime"}
            ],
            # Define columns in table
            columns=[{"name": c, "id": c} for c in [
                "type", "side", "strike", "qty", "vol", "rate", "maturity", "price_entry", "prime", "pnl"
            ]],
            # Populate table with book data
            data=book_data
        )
