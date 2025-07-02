from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

def init_analytics_app(server):
    dash_app = Dash(__name__, server=server, url_base_pathname='/analytics/', 
                  external_stylesheets=[dbc.themes.BOOTSTRAP],
                  meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])
    
    THRESHOLD = 8
    weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    anomalies = [12, 3, 19, 5]

    # Create 3D bar chart data
    colors = ['#4CAF50' if val <= THRESHOLD else '#F44336' for val in anomalies]
    annotations = [
        dict(
            x=week,
            y=val,
            text=str(val),
            xanchor='center',
            yanchor='bottom',
            showarrow=False,
            font=dict(color='white', size=12)
        ) for week, val in zip(weeks, anomalies)
    ]

    # Gradient background for the whole app
    app_style = {
        'background': 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
        'min-height': '100vh',
        'padding': '20px'
    }

    # Metric tiles data
    metrics = {
        'scanned': {'value': '1,248', 'change': '+12%', 'trend': 'up'},
        'anomaly_rate': {'value': '3.2%', 'change': '-0.5%', 'trend': 'down'},
        'top_anomaly': {'value': 'Split', 'count': '28', 'trend': 'steady'},
        'yield_forecast': {'value': '96.5%', 'change': '+1.2%', 'trend': 'up'},
        'recent_anomaly': {'value': 'Crack', 'count': '9', 'trend': 'up'},
        'camera_health': {'value': '92%', 'status': 'good'}
    }

    def create_metric_card(title, value, change=None, icon=None, color="primary"):
        """Create stylish metric cards with 3D effect"""
        trend_icon = "fa-arrow-up" if change and '+' in change else "fa-arrow-down" if change else "fa-equals"
        trend_color = "success" if trend_icon == "fa-arrow-up" else "danger" if trend_icon == "fa-arrow-down" else "secondary"
        
        return dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H6(title, className="card-title mb-1"),
                    html.I(className=f"fas {icon} float-end fa-2x opacity-25")
                ], className="d-flex justify-content-between"),
                html.H4(value, className="mb-1 mt-2"),
                html.Small([
                    html.I(className=f"fas {trend_icon} me-1 text-{trend_color}"),
                    html.Span(change if change else "Steady", className=f"text-{trend_color}")
                ])
            ]),
            className=f"mb-3 border-0 shadow-lg h-100",
            style={
                'background': 'linear-gradient(145deg, #ffffff, #f0f0f0)',
                'border-radius': '15px',
                'transform': 'perspective(500px) rotateX(5deg)',
                'transition': 'transform 0.3s',
                'box-shadow': '0 10px 20px rgba(0,0,0,0.1), 0 6px 6px rgba(0,0,0,0.05)'
            }
        )

    # Create main 3D bar chart
    main_chart = dcc.Graph(
        figure={
            'data': [go.Bar(
                x=weeks,
                y=anomalies,
                marker_color=colors,
                text=anomalies,
                textposition='outside',
                hoverinfo='y'
            )],
            'layout': {
                'title': {'text': 'ANOMALIES DETECTED PER WEEK', 'font': {'size': 18}},
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'shapes': [{
                    'type': 'line',
                    'x0': -0.5,
                    'x1': len(weeks)-0.5,
                    'y0': THRESHOLD,
                    'y1': THRESHOLD,
                    'line': {'color': '#FF9800', 'width': 3, 'dash': 'dot'}
                }],
                'annotations': annotations + [{
                    'x': len(weeks)-0.5,
                    'y': THRESHOLD,
                    'text': f'THRESHOLD ({THRESHOLD})',
                    'showarrow': False,
                    'font': {'size': 12, 'color': '#FF9800'},
                    'bgcolor': 'rgba(255,255,255,0.8)',
                    'bordercolor': '#FF9800'
                }],
                'margin': {'l': 50, 'r': 30, 't': 80, 'b': 60},
                'height': 400,
                'hovermode': 'closest'
            }
        },
        config={'displayModeBar': False},
        style={'height': '100%', 'border-radius': '15px'}
    )

    # Create pie chart with 3D effect
    pie_chart = dcc.Graph(
        figure={
            'data': [go.Pie(
                labels=['Split', 'Crack', 'Deformation', 'Other'],
                values=[45, 30, 15, 10],
                hole=0.5,
                marker_colors=['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'],
                textinfo='percent',
                insidetextorientation='radial'
            )],
            'layout': {
                'title': {'text': 'ANOMALY TYPE DISTRIBUTION', 'font': {'size': 16}},
                'showlegend': False,
                'margin': {'l': 20, 'r': 20, 't': 60, 'b': 20},
                'height': 350,
                'paper_bgcolor': 'rgba(0,0,0,0)'
            }
        },
        config={'displayModeBar': False},
        style={'height': '100%', 'border-radius': '15px'}
    )

    # Create line chart with smooth style
    line_chart = dcc.Graph(
        figure={
            'data': [go.Scatter(
                x=weeks,
                y=[5, 3, 7, 4],
                mode='lines+markers',
                name='False Positives',
                line={'color': '#FFA500', 'width': 3, 'shape': 'spline'},
                marker={'size': 10}
            ), go.Scatter(
                x=weeks,
                y=[1, 0, 2, 1],
                mode='lines+markers',
                name='False Negatives',
                line={'color': '#FF4500', 'width': 3, 'shape': 'spline'},
                marker={'size': 10}
            )],
            'layout': {
                'title': {'text': 'DETECTION ACCURACY TRENDS', 'font': {'size': 16}},
                'showlegend': False,
                'plot_bgcolor': 'rgba(240,240,240,0.8)',
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'margin': {'l': 50, 'r': 30, 't': 60, 'b': 50},
                'height': 350
            }
        },
        config={'displayModeBar': False},
        style={'height': '100%', 'border-radius': '15px'}
    )

    dash_app.layout = html.Div(style=app_style, children=[
        # Header with 3D effect
        html.Div(className='text-center mb-4', children=[
            html.H1('ANALYTICS', 
                   style={
                       'color': '#2c3e50',
                       'textShadow': '2px 2px 4px rgba(0,0,0,0.1)',
                       'fontWeight': 'bold'
                   }),
            html.Div(f"Threshold: {THRESHOLD} anomalies/week", 
                    className='badge bg-warning text-dark p-2',
                    style={
                        'fontSize': '1rem',
                        'boxShadow': '0 4px 8px rgba(0,0,0,0.1)'
                    })
        ]),
        
        # Metrics tiles with 3D effect
        dbc.Row([
            dbc.Col(create_metric_card(
                "Units Scanned", metrics['scanned']['value'],
                metrics['scanned']['change'], icon="fa-search", color="primary"
            ), lg=2, md=4, sm=6, xs=6),
            
            dbc.Col(create_metric_card(
                "Anomaly Rate", metrics['anomaly_rate']['value'],
                metrics['anomaly_rate']['change'], icon="fa-exclamation-triangle", color="warning"
            ), lg=2, md=4, sm=6, xs=6),
            
            dbc.Col(create_metric_card(
                "Top Anomaly", f"{metrics['top_anomaly']['value']} ({metrics['top_anomaly']['count']})",
                None, icon="fa-chart-pie", color="info"
            ), lg=2, md=4, sm=6, xs=6),
            
            dbc.Col(create_metric_card(
                "Yield Forecast", metrics['yield_forecast']['value'],
                metrics['yield_forecast']['change'], icon="fa-chart-line", color="success"
            ), lg=2, md=4, sm=6, xs=6),
            
            dbc.Col(create_metric_card(
                "Recent Anomaly", f"{metrics['recent_anomaly']['value']} ({metrics['recent_anomaly']['count']})",
                None, icon="fa-clock", color="danger"
            ), lg=2, md=4, sm=6, xs=6),
            
            dbc.Col(create_metric_card(
                "Camera Health", metrics['camera_health']['value'],
                None, icon="fa-camera", color="secondary"
            ), lg=2, md=4, sm=6, xs=6),
        ], className="g-3 mb-4"),
        
        # Main content area
        dbc.Row(className="g-4", children=[
            # Main chart with 3D effect container
            dbc.Col(html.Div(
                main_chart,
                style={
                    'background': 'linear-gradient(145deg, #ffffff, #f8f9fa)',
                    'padding': '20px',
                    'border-radius': '15px',
                    'box-shadow': '0 10px 30px rgba(0,0,0,0.1)',
                    'height': '100%'
                }
            ), xl=8, lg=7, md=12),
            
            # Stats card with glass morphism effect
            dbc.Col(html.Div(
                dbc.Card([
                    dbc.CardHeader(
                        "SUMMARY STATISTICS",
                        className="text-center fw-bold",
                        style={'background': 'rgba(255,255,255,0.2)', 'border-bottom': '1px solid rgba(0,0,0,0.1)'}
                    ),
                    dbc.CardBody([
                        dbc.ListGroup([
                            dbc.ListGroupItem([
                                html.Div("Total Anomalies", className="fw-bold"),
                                html.Div("39", className="badge bg-primary rounded-pill")
                            ], className="d-flex justify-content-between align-items-center py-2 border-0"),
                            dbc.ListGroupItem([
                                html.Div("Above Threshold", className="fw-bold"),
                                html.Div("2 weeks", className="badge bg-danger rounded-pill")
                            ], className="d-flex justify-content-between align-items-center py-2 border-0"),
                            dbc.ListGroupItem([
                                html.Div("Most Common Type", className="fw-bold"),
                                html.Div("Split", className="badge bg-info rounded-pill")
                            ], className="d-flex justify-content-between align-items-center py-2 border-0"),
                            dbc.ListGroupItem([
                                html.Div("Detection Accuracy", className="fw-bold"),
                                html.Div("92.5%", className="badge bg-success rounded-pill")
                            ], className="d-flex justify-content-between align-items-center py-2 border-0"),
                        ], flush=True, style={'background': 'transparent'})
                    ], style={'background': 'rgba(255,255,255,0.1)'})
                ], className="border-0 h-100", style={
                    'background': 'rgba(255,255,255,0.3)',
                    'backdrop-filter': 'blur(10px)',
                    'box-shadow': '0 8px 32px 0 rgba(31, 38, 135, 0.1)',
                    'border-radius': '15px',
                    'border': '1px solid rgba(255,255,255,0.2)'
                })
            ), xl=4, lg=5, md=12),
        ]),
        
        # Secondary charts row
        dbc.Row(className="g-4 mt-2", children=[
            dbc.Col(html.Div(
                pie_chart,
                style={
                    'background': 'linear-gradient(145deg, #ffffff, #f8f9fa)',
                    'padding': '20px',
                    'border-radius': '15px',
                    'box-shadow': '0 10px 30px rgba(0,0,0,0.1)',
                    'height': '100%'
                }
            ), lg=6, md=12),
            
            dbc.Col(html.Div(
                line_chart,
                style={
                    'background': 'linear-gradient(145deg, #ffffff, #f8f9fa)',
                    'padding': '20px',
                    'border-radius': '15px',
                    'box-shadow': '0 10px 30px rgba(0,0,0,0.1)',
                    'height': '100%'
                }
            ), lg=6, md=12),
        ]),
        
        # System status with modern design
        html.Div(className="mt-4 p-4", style={
            'background': 'linear-gradient(145deg, #ffffff, #f8f9fa)',
            'border-radius': '15px',
            'box-shadow': '0 10px 30px rgba(0,0,0,0.1)'
        }, children=[
            html.H4("SYSTEM STATUS", className="text-center mb-4", style={'color': '#2c3e50'}),
            dbc.Row(className="g-3", children=[
                dbc.Col(html.Div([
                    html.Div(className="d-flex justify-content-between mb-2", children=[
                        html.Span("Camera 1", className="fw-bold"),
                        html.Span("Online", className="badge bg-success")
                    ]),
                    dbc.Progress(value=95, label="95%", style={
                        'height': '15px',
                        'background': 'linear-gradient(to right, #4facfe 0%, #00f2fe 100%)',
                        'border-radius': '10px'
                    })
                ]), lg=4, md=6, sm=12),
                
                dbc.Col(html.Div([
                    html.Div(className="d-flex justify-content-between mb-2", children=[
                        html.Span("Camera 2", className="fw-bold"),
                        html.Span("Online", className="badge bg-success")
                    ]),
                    dbc.Progress(value=88, label="88%", style={
                        'height': '15px',
                        'background': 'linear-gradient(to right, #4facfe 0%, #00f2fe 100%)',
                        'border-radius': '10px'
                    })
                ]), lg=4, md=6, sm=12),
                
                dbc.Col(html.Div([
                    html.Div(className="d-flex justify-content-between mb-2", children=[
                        html.Span("Processing", className="fw-bold"),
                        html.Span("Normal", className="badge bg-success")
                    ]),
                    dbc.Progress(value=92, label="92%", style={
                        'height': '15px',
                        'background': 'linear-gradient(to right, #4facfe 0%, #00f2fe 100%)',
                        'border-radius': '10px'
                    })
                ]), lg=4, md=6, sm=12),
            ])
        ])
    ])
    
    return dash_app.server