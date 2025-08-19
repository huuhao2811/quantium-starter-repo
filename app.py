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
df = df.dropna(subset=["Date", "Sales", "Region"]).sort_values("Date")

regions = sorted(df["Region"].unique().tolist())
region_options = [{"label": "All regions", "value": "__ALL__"}] + [
    {"label": r.title(), "value": r} for r in regions
]

app = Dash(__name__)
app.title = "Pink Morsel Sales Visualiser"

bg_layer = html.Div(
    style={
        "position": "fixed",
        "inset": "0",
        "background": "radial-gradient(80% 60% at 50% 20%, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.92) 60%, rgba(0,0,0,1) 100%)",
        "backdropFilter": "blur(10px)",
        "WebkitBackdropFilter": "blur(10px)",
        "zIndex": 0,
    }
)

content = html.Div(
    style={
        "position": "relative",
        "zIndex": 1,
        "maxWidth": "1500px",
        "margin": "40px auto",
        "fontFamily": "Inter, Arial, sans-serif",
        "color": "#fff", 

        "border": "2px solid rgba(255,255,255,0.25)",  
        "borderRadius": "12px",                       
        "padding": "24px",                            
        "boxShadow": "0 0 20px rgba(0,255,255,0.15)",  
        "backgroundColor": "rgba(0,0,0,0.4)",          
        "backdropFilter": "blur(6px)",
        "WebkitBackdropFilter": "blur(6px)",
        "backgroundColor": "rgba(0,0,0,0.4)", 
    },
    children=[
        html.H1(
            "Pink Morsel Sales Over Time",
            style={"marginBottom": "8px", "fontWeight": 800}
        ),
        html.Div(
            "Does the price increase on Jan 15, 2021 change total sales?",
            style={"color": "rgba(255,255,255,0.75)", "marginBottom": "20px"}
        ),

        html.Div(
            style={"display": "flex", "gap": "12px", "alignItems": "center", "marginBottom": "14px"},
            children=[
                html.Label("Region:", style={"fontWeight": 600}),
                dcc.Dropdown(
                    id="region-dd",
                    options=region_options,
                    value="__ALL__",
                    clearable=False,
                    style={"width": "260px", "color": "#000"}, 
                ),
            ],
        ),

        dcc.Graph(id="sales-line"),
        html.Div(
            "Note: Vertical line indicates Pink Morsel price increase on 2021-01-15.",
            style={"color": "rgba(255,255,255,0.7)", "fontSize": "0.9rem", "marginTop": "8px"},
        ),
    ],
)

app.layout = html.Div([bg_layer, content])

@app.callback(
    Output("sales-line", "figure"),
    Input("region-dd", "value"),
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
        line=dict(width=2, dash="dash", color="red"),
    )
    fig.add_annotation(
        x=PRICE_HIKE_DATE, y=1.02,
        xref="x", yref="paper",
        text="Price hike (2021-01-15)",
        showarrow=False,
        font=dict(color="red")
    )
    return fig

if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8050)
