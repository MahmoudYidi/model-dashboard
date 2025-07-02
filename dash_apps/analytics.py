from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from flask import current_app

def init_analytics_app(server):
    dash_app = Dash(
        __name__,
        server=server,
        url_base_pathname='/analytics/', 
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
    )
    
    # Static configuration
    THRESHOLD = 8
    weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    
    # Create initial layout
    dash_app.layout = create_layout(dash_app, THRESHOLD, weeks)
    
    # Register all callbacks
    register_callbacks(dash_app, server, THRESHOLD, weeks)
    
    return dash_app.server

def create_layout(dash_app, threshold, weeks):
    """Create the complete Dash layout with all components"""
    return html.Div(style={
        'background': 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
        'min-height': '100vh',
        'padding': '20px'
    }, children=[
        # Update interval and loading component
        dcc.Interval(id='interval-component', interval=5000),
        dcc.Store(id='metrics-store'),
        
        # Header
        html.Div(className='text-center mb-4', children=[
            html.H1('ANALYTICS', style={
                'color': '#2c3e50',
                'textShadow': '2px 2px 4px rgba(0,0,0,0.1)',
                'fontWeight': 'bold'
            }),
            html.Div(f"Threshold: {threshold} anomalies/week", 
                    className='badge bg-warning text-dark p-2',
                    style={'fontSize': '1rem', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)'})
        ]),
        
        # Metrics tiles row
        dbc.Row([
            dbc.Col(id='scanned-metric', lg=2, md=4, sm=6, xs=6),
            dbc.Col(id='anomaly-rate-metric', lg=2, md=4, sm=6, xs=6),
            dbc.Col(id='top-anomaly-metric', lg=2, md=4, sm=6, xs=6),
            dbc.Col(id='yield-forecast-metric', lg=2, md=4, sm=6, xs=6),
            dbc.Col(id='recent-anomaly-metric', lg=2, md=4, sm=6, xs=6),
            dbc.Col(id='camera-health-metric', lg=2, md=4, sm=6, xs=6),
        ], className="g-3 mb-4"),
        
        # Main content area
        dbc.Row(className="g-4", children=[
            # Main chart
            dbc.Col(html.Div(
                dcc.Graph(id='main-chart'),
                style={
                    'background': 'linear-gradient(145deg, #ffffff, #f8f9fa)',
                    'padding': '20px',
                    'border-radius': '15px',
                    'box-shadow': '0 10px 30px rgba(0,0,0,0.1)',
                    'height': '100%'
                }
            ), xl=8, lg=7, md=12),
            
            # Stats card
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
                                html.Div(id='total-anomalies', className="badge bg-primary rounded-pill")
                            ], className="d-flex justify-content-between align-items-center py-2 border-0"),
                            dbc.ListGroupItem([
                                html.Div("Above Threshold", className="fw-bold"),
                                html.Div(id='above-threshold', className="badge bg-danger rounded-pill")
                            ], className="d-flex justify-content-between align-items-center py-2 border-0"),
                            dbc.ListGroupItem([
                                html.Div("Most Common Type", className="fw-bold"),
                                html.Div(id='common-anomaly', className="badge bg-info rounded-pill")
                            ], className="d-flex justify-content-between align-items-center py-2 border-0"),
                            dbc.ListGroupItem([
                                html.Div("Detection Accuracy", className="fw-bold"),
                                html.Div(id='detection-accuracy', className="badge bg-success rounded-pill")
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
                dcc.Graph(id='pie-chart'),
                style={
                    'background': 'linear-gradient(145deg, #ffffff, #f8f9fa)',
                    'padding': '20px',
                    'border-radius': '15px',
                    'box-shadow': '0 10px 30px rgba(0,0,0,0.1)',
                    'height': '100%'
                }
            ), lg=6, md=12),
            
            dbc.Col(html.Div(
                dcc.Graph(id='line-chart'),
                style={
                    'background': 'linear-gradient(145deg, #ffffff, #f8f9fa)',
                    'padding': '20px',
                    'border-radius': '15px',
                    'box-shadow': '0 10px 30px rgba(0,0,0,0.1)',
                    'height': '100%'
                }
            ), lg=6, md=12),
        ]),
        
        # System status
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
                        html.Span(id='camera-1-status', className="badge bg-success")
                    ]),
                    dbc.Progress(id='camera-1-progress', style={
                        'height': '15px',
                        'background': 'linear-gradient(to right, #4facfe 0%, #00f2fe 100%)',
                        'border-radius': '10px'
                    })
                ]), lg=4, md=6, sm=12),
                
                dbc.Col(html.Div([
                    html.Div(className="d-flex justify-content-between mb-2", children=[
                        html.Span("Camera 2", className="fw-bold"),
                        html.Span(id='camera-2-status', className="badge bg-success")
                    ]),
                    dbc.Progress(id='camera-2-progress', style={
                        'height': '15px',
                        'background': 'linear-gradient(to right, #4facfe 0%, #00f2fe 100%)',
                        'border-radius': '10px'
                    })
                ]), lg=4, md=6, sm=12),
                
                dbc.Col(html.Div([
                    html.Div(className="d-flex justify-content-between mb-2", children=[
                        html.Span("Processing", className="fw-bold"),
                        html.Span(id='processing-status', className="badge bg-success")
                    ]),
                    dbc.Progress(id='processing-progress', style={
                        'height': '15px',
                        'background': 'linear-gradient(to right, #4facfe 0%, #00f2fe 100%)',
                        'border-radius': '10px'
                    })
                ]), lg=4, md=6, sm=12),
            ])
        ])
    ])

def register_callbacks(dash_app, server, threshold, weeks):
    """Register all Dash callbacks for dynamic updates"""
    
    # Main metrics cards update
    @dash_app.callback(
        [Output('scanned-metric', 'children'),
         Output('anomaly-rate-metric', 'children'),
         Output('top-anomaly-metric', 'children'),
         Output('yield-forecast-metric', 'children'),
         Output('recent-anomaly-metric', 'children'),
         Output('camera-health-metric', 'children')],
        [Input('interval-component', 'n_intervals')]
    )
    def update_metrics_cards(n):
        with server.metrics_lock:
            metrics = server.metrics
        
        def create_card(title, metric_data, icon, color):
            trend_icon = ("fa-arrow-up" if '+' in metric_data.get('change', '') 
                         else "fa-arrow-down" if '-' in metric_data.get('change', '') 
                         else "fa-equals")
            trend_color = ("success" if trend_icon == "fa-arrow-up" 
                          else "danger" if trend_icon == "fa-arrow-down" 
                          else "secondary")
            
            value = (f"{metric_data['value']} ({metric_data['count']})" 
                    if 'count' in metric_data else metric_data['value'])
            
            return dbc.Card(
                dbc.CardBody([
                    html.Div([
                        html.H6(title, className="card-title mb-1"),
                        html.I(className=f"fas {icon} float-end fa-2x opacity-25")
                    ], className="d-flex justify-content-between"),
                    html.H4(value, className="mb-1 mt-2"),
                    html.Small([
                        html.I(className=f"fas {trend_icon} me-1 text-{trend_color}"),
                        html.Span(metric_data.get('change', 'Steady'), className=f"text-{trend_color}")
                    ]) if 'change' in metric_data else None
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
        
        return (
            create_card("Units Scanned", metrics['scanned'], "fa-search", "primary"),
            create_card("Anomaly Rate", metrics['anomaly_rate'], "fa-exclamation-triangle", "warning"),
            create_card("Top Anomaly", metrics['top_anomaly'], "fa-chart-pie", "info"),
            create_card("Yield Forecast", metrics['yield_forecast'], "fa-chart-line", "success"),
            create_card("Recent Anomaly", metrics['recent_anomaly'], "fa-clock", "danger"),
            create_card("Camera Health", metrics['camera_health'], "fa-camera", "secondary")
        )
    
    # Charts and stats updates
    @dash_app.callback(
        [Output('main-chart', 'figure'),
         Output('pie-chart', 'figure'),
         Output('line-chart', 'figure'),
         Output('total-anomalies', 'children'),
         Output('above-threshold', 'children'),
         Output('common-anomaly', 'children'),
         Output('detection-accuracy', 'children'),
         Output('camera-1-progress', 'value'),
         Output('camera-1-progress', 'label'),
         Output('camera-1-status', 'children'),
         Output('camera-2-progress', 'value'),
         Output('camera-2-progress', 'label'),
         Output('camera-2-status', 'children'),
         Output('processing-progress', 'value'),
         Output('processing-progress', 'label'),
         Output('processing-status', 'children')],
        [Input('interval-component', 'n_intervals')]
    )
    def update_all_components(n):
        with server.metrics_lock:
            metrics = server.metrics
        
        # Process camera health
        cam1_health = int(metrics['camera_health']['value'].strip('%'))
        cam2_health = max(70, cam1_health - 5)  # Simulate second camera
        processing_health = min(100, cam1_health + 2)  # Simulate processing
        
        # Generate anomalies data based on metrics
        anomalies = [
            int(metrics['scanned']['value'].replace(',', '')) * float(metrics['anomaly_rate']['value'].strip('%')) / 100,
            int(metrics['scanned']['value'].replace(',', '')) * 0.02,  # Simulated week 2
            int(metrics['scanned']['value'].replace(',', '')) * float(metrics['anomaly_rate']['value'].strip('%')) / 100 * 1.5,
            int(metrics['scanned']['value'].replace(',', '')) * 0.03  # Simulated week 4
        ]
        anomalies = [int(a) for a in anomalies]
        
        # Main chart
        colors = ['#4CAF50' if val <= threshold else '#F44336' for val in anomalies]
        main_fig = {
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
                    'y0': threshold,
                    'y1': threshold,
                    'line': {'color': '#FF9800', 'width': 3, 'dash': 'dot'}
                }],
                'annotations': [
                    dict(
                        x=week,
                        y=val,
                        text=str(val),
                        xanchor='center',
                        yanchor='bottom',
                        showarrow=False,
                        font=dict(color='white', size=12))
                    for week, val in zip(weeks, anomalies)
                ] + [{
                    'x': len(weeks)-0.5,
                    'y': threshold,
                    'text': f'THRESHOLD ({threshold})',
                    'showarrow': False,
                    'font': {'size': 12, 'color': '#FF9800'},
                    'bgcolor': 'rgba(255,255,255,0.8)',
                    'bordercolor': '#FF9800'
                }],
                'margin': {'l': 50, 'r': 30, 't': 80, 'b': 60},
                'height': 400,
                'hovermode': 'closest'
            }
        }
        
        # Pie chart (simplified based on top anomalies)
        pie_fig = {
            'data': [go.Pie(
                labels=['Split', 'Crack', 'Deformation', 'Other'],
                values=[
                    int(metrics['top_anomaly']['count']),
                    int(metrics['recent_anomaly']['count']),
                    max(5, int(metrics['top_anomaly']['count']) // 3),
                    10  # Constant "other" value
                ],
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
        }
        
        # Line chart (simulated accuracy trends)
        line_fig = {
            'data': [go.Scatter(
                x=weeks,
                y=[max(1, int(a * 0.1)) for a in anomalies],  # False positives
                mode='lines+markers',
                name='False Positives',
                line={'color': '#FFA500', 'width': 3, 'shape': 'spline'},
                marker={'size': 10}
            ), go.Scatter(
                x=weeks,
                y=[max(0, int(a * 0.03)) for a in anomalies],  # False negatives
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
        }
        
        # Calculate summary stats
        total_anomalies = sum(anomalies)
        above_threshold = sum(1 for a in anomalies if a > threshold)
        
        return (
            main_fig,
            pie_fig,
            line_fig,
            str(total_anomalies),
            f"{above_threshold} weeks",
            metrics['top_anomaly']['value'],
            "92.5%",  # Simulated accuracy
            cam1_health, f"{cam1_health}%", "Online",
            cam2_health, f"{cam2_health}%", "Online",
            processing_health, f"{processing_health}%", "Normal"
        )