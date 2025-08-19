from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
from datetime import datetime

DATA_PATH = Path("data/processed_sales.csv")
PRICE_HIKE_DATE = datetime(2021, 1, 15)

df = pd.read_csv(DATA_PATH)
df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
df["Date"]  = pd.to_datetime(df["Date"], errors="coerce")

df["Region"] = df["Region"].astype(str).str.strip().str.lower()
df = df.dropna(subset=["Date", "Sales", "Region"]).sort_values("Date")

RADIO_OPTIONS = [
    {"label": "North", "value": "north"},
    {"label": "East",  "value": "east"},
    {"label": "South", "value": "south"},
    {"label": "West",  "value": "west"},
    {"label": "All",   "value": "__ALL__"},
]

app = Dash(__name__)
app.title = "Pink Morsel Sales Visualiser"

bg_layer = html.Div(
    className="bg-space",
    style={
        "position": "fixed",
        "inset": "0",
        "zIndex": 0,
    }
)

content = html.Div(
    className="galaxy-card",
    style={
        "position": "relative",
        "zIndex": 1,
        "maxWidth": "1500px",
        "margin": "110px auto",
        "fontFamily": "Inter, Arial, sans-serif",
        "color": "#fff",
        "padding": "24px",
    },
    children=[
        html.H1(
            "Pink Morsel Sales Over Time",
            className="title"
        ),
        html.Div(
            "Does the price increase on Jan 15, 2021 change total sales?",
            className="subtitle"
        ),
        html.Div(
            className="control-bar galaxy-card--soft",
            children=[
                html.Label("Region:", className="label"),
                dcc.RadioItems(
                    id="region-radio",
                    options=RADIO_OPTIONS,
                    value="__ALL__",
                    className="galaxy-radio",           
                    inputClassName="radio-input",      
                    labelClassName="radio-label",        
                ),
            ],
        ),

        html.Div(
            className="chart-wrap galaxy-card--soft",
            children=[dcc.Graph(id="sales-line", className="chart")]
        ),
        html.Div(
            "Note: Vertical line indicates Pink Morsel price increase on 2021-01-15.",
            className="note"
        ),
    ],
)

app.layout = html.Div([bg_layer, content], className="root")

@app.callback(
    Output("sales-line", "figure"),
    Input("region-radio", "value"),
)
def update_chart(region_value):
    if region_value == "__ALL__":
        df_plot = df.groupby("Date", as_index=False)["Sales"].sum()
        line_name = "All regions"
    else:
        dff = df[df["Region"] == region_value]
        df_plot = dff.groupby("Date", as_index=False)["Sales"].sum()
        line_name = region_value.title()

    df_plot = df_plot.sort_values("Date")

    fig = px.line(
        df_plot,
        x="Date",
        y="Sales",
        markers=False,
        title=None,
        labels={"Date": "Date", "Sales": "Sales (currency units)"},
        template="plotly_dark",
    )
    if fig.data:
        fig.update_traces(
            name=line_name,
            hovertemplate="Date=%{x|%Y-%m-%d}<br>Sales=%{y:.2f}"
        )

    fig.update_layout(
        margin=dict(l=40, r=20, t=20, b=40),
        xaxis_title="Date",
        yaxis_title="Sales (currency units)",
        legend_title_text="",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#fff"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.15)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.15)"),
    )

    fig.add_shape(
        type="line",
        x0=PRICE_HIKE_DATE, x1=PRICE_HIKE_DATE,
        y0=0, y1=1,
        xref="x", yref="paper",
        line=dict(width=2, dash="dash", color="#ff5c5c"),
    )
    fig.add_annotation(
        x=PRICE_HIKE_DATE, y=1.02,
        xref="x", yref="paper",
        text="Price hike (2021-01-15)",
        showarrow=False,
        font=dict(color="#ff5c5c")
    )
    return fig

if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8050)
