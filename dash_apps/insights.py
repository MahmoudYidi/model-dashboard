from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

def init_insights_app(server):
    dash_app = Dash(
        __name__, server=server, url_base_pathname='/insights/',
        external_stylesheets=[dbc.themes.BOOTSTRAP, "https://use.fontawesome.com/releases/v5.15.4/css/all.css"],
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
    )

    dash_app.layout = html.Div(style={
        "background": "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
        "minHeight": "100vh",
        "padding": "20px"
    }, children=[

        # Header
        html.Div(className="text-center mb-4", children=[
            html.H1("Insights", style={
                "color": "#2c3e50",
                "textShadow": "1px 1px 2px rgba(0,0,0,0.1)",
                "fontWeight": "bold"
            }),
            html.Small("Coming Soon", className="text-muted")
        ])

    ])
        
    return dash_app
