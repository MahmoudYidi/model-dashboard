from flask import Flask, render_template, redirect, url_for, flash, send_file, request, jsonify,session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.prediction_model import run_model
from dash.dependencies import Input, Output, State
from utils.auth import User, configure_auth
import pandas as pd
import dash
from dash import dcc, html
import io
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Initialize extensions
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    # Configure authentication
    configure_auth(login_manager)
    
    # Sample user data (in production, use a database)
    # Generate password hash first: generate_password_hash('yourpassword')
    users = {
        'admin': {
            'password': 'pbkdf2:sha256:260000$N2B9Jz5Y7b8O9P0Q$1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z'
        }
    }

    @app.route('/')
    @login_required
    def home():
        return render_template('dashboard.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if username in users and password == 'password':  # INSECURE - for testing only
                user = User(username)
                login_user(user)
                return redirect(url_for('home'))
            flash('Invalid username or password', 'danger')
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))
    
    @app.route('/run-model')
    @login_required
    def run_model_route():
        try:
            results = run_model()
            flash('Model executed successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'Model execution failed: {str(e)}', 'danger')
            return redirect(url_for('home'))
    
    @app.route('/export-results')
    @login_required
    def export_results():
        try:
            results = run_model()
            df = pd.DataFrame(results['data'])
            
            output = io.BytesIO()
            df.to_csv(output, index=False)
            output.seek(0)
            
            return send_file(
                output,
                as_attachment=True,
                download_name='model_results.csv',
                mimetype='text/csv'
            )
        except Exception as e:
            flash(f'Export failed: {str(e)}', 'danger')
            return redirect(url_for('home'))
    
    @app.route('/set-fruit', methods=['POST'])
    @login_required
    def set_fruit():
        selected_fruit = request.json.get('fruit')
        # Store in Flask session
        session['selected_fruit'] = selected_fruit
        # You could also store in database for persistence
        return jsonify({
            'status': 'success', 
            'fruit': selected_fruit,
            'message': f"Now analyzing {selected_fruit}" if selected_fruit else "Selection cleared"
        })

    # Main Dash App for Analytics
    analytics_app = dash.Dash(__name__, server=app, url_base_pathname='/analytics/')

    # Threshold value (adjust as needed)
    THRESHOLD = 8

    # Data preparation
    weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    anomalies = [12, 3, 19, 5]

    # Create separate traces for above/below threshold
    below_threshold = {
        'x': [week for week, val in zip(weeks, anomalies) if val <= THRESHOLD],
        'y': [val for val in anomalies if val <= THRESHOLD],
        'type': 'bar',
        'name': 'Normal',
        'marker': {'color': '#4CAF50'}  # Green
    }

    above_threshold = {
        'x': [week for week, val in zip(weeks, anomalies) if val > THRESHOLD],
        'y': [val for val in anomalies if val > THRESHOLD],
        'type': 'bar',
        'name': 'Critical',
        'marker': {'color': '#F44336'}  # Red
    }

    analytics_app.layout = html.Div([
        html.Div(className='analytics-header', children=[
            html.H1('Anomaly Analytics', className='text-center mb-2'),
            html.Div(f"Threshold: {THRESHOLD} anomalies/week", 
                    className='threshold-badge mb-3')
        ]),
        
        dcc.Graph(
            id='anomaly-chart',
            figure={
                'data': [above_threshold, below_threshold],
                'layout': {
                    'title': 'Anomalies Detected Per Week',
                    'shapes': [{
                        'type': 'line',
                        'x0': -0.5,
                        'x1': len(weeks)-0.5,
                        'y0': THRESHOLD,
                        'y1': THRESHOLD,
                        'line': {
                            'color': '#FF9800',
                            'width': 2,
                            'dash': 'dot'
                        }
                    }],
                    'annotations': [{
                        'x': len(weeks)-0.5,
                        'y': THRESHOLD,
                        'xref': 'x',
                        'yref': 'y',
                        'text': f'Target ({THRESHOLD})',
                        'showarrow': False,
                        'ax': 0,
                        'ay': -20,
                        'bgcolor': 'white',
                        'bordercolor': '#FF9800'
                    }],
                    'plot_bgcolor': 'rgba(240,240,240,0.8)',
                    'paper_bgcolor': 'rgba(0,0,0,0)',
                    'margin': dict(t=40, b=40)
                }
            },
            config={'displayModeBar': False}
        ),
        
        html.Div(className='stats-card', children=[
            html.H3('Summary Statistics', className='stats-header'),
            html.Div([
                html.P([
                    html.Span("Total Anomalies: ", className='stat-label'),
                    html.Span("39", className='stat-value')
                ]),
                html.P([
                    html.Span("Above Threshold: ", className='stat-label'),
                    html.Span("2 weeks", className='stat-value critical')
                ]),
                html.P([
                    html.Span("Most Common Type: ", className='stat-label'),
                    html.Span("Split", className='stat-value')
                ]),
                html.P([
                    html.Span("Detection Accuracy: ", className='stat-label'),
                    html.Span("92.5%", className='stat-value')
                ])
            ])
        ])
    ])

    # Insights Dash App
    insights_app = dash.Dash(__name__, server=app, url_base_pathname='/insights/')
    insights_app.layout = html.Div([
        html.H1('Insights Dashboard', className='text-center mb-4'),
        dcc.Tabs([
            dcc.Tab(label='Anomaly Types', children=[
            html.Div(className='anomaly-container', children=[
                dcc.Graph(
                    figure={
                        'data': [{
                            'labels': ['Split', 'Mould', 'Zip', 'Other'],
                            'values': [45, 30, 20, 5],
                            'type': 'pie',
                            'hole': 0.4,  # Creates a donut chart
                            'textinfo': 'percent+label',
                            'textposition': 'inside',
                            'insidetextorientation': 'radial',
                            'marker': {
                                'colors': ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2'],  # Professional color palette
                                'line': {'color': '#fff', 'width': 2}
                            },
                            'hoverinfo': 'label+percent+value',
                            'textfont': {'size': 12}
                        }],
                        'layout': {
                            'title': {
                                'text': 'Anomaly Distribution',
                                'font': {'size': 18, 'color': '#2d3436'},
                                'x': 0.5,
                                'xanchor': 'center'
                            },
                            'legend': {
                                'orientation': 'h',
                                'y': -0.15,
                                'x': 0.5,
                                'xanchor': 'center',
                                'itemwidth': 30,
                                'itemgap': 5,
                                'font': {'size': 10},
                                'bgcolor': 'rgba(0,0,0,0)'
                            },
                            'margin': dict(t=50, b=50, l=20, r=20),
                            'paper_bgcolor': 'rgba(0,0,0,0)',
                            'plot_bgcolor': 'rgba(0,0,0,0)',
                            'annotations': [{
                                'text': 'Most Frequent:<br><b>Split (45%)</b>',
                                'x': 0.5,
                                'y': 0.5,
                                'font': {'size': 14, 'color': '#4e79a7'},
                                'showarrow': False,
                                'align': 'center'
                            }],
                            'uniformtext': {
                                'minsize': 10,
                                'mode': 'hide'
                            }
                        }
                    },
                    config={
                        'displayModeBar': False,
                        'responsive': True
                    },
                    style={'height': '400px'}
                ),
                
                # Image container (positioned absolutely)
                html.Div(className='anomaly-image-container', children=[
                    html.Img(
                        src='/static/images/sample.png',
                        style={
                            'maxHeight': '120px',
                            'borderRadius': '8px',
                            'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
                            'border': '2px solid #fff'
                        }
                    )
                ])
            ])
        ]),
            dcc.Tab(label='Yield Forecast', children=[
                dcc.Graph(
                    figure={
                        'data': [
                            {'x': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
                             'y': [100, 110, 105, 120, 125],
                             'type': 'line',
                             'name': 'Projected'}
                        ],
                        'layout': {
                            'title': '6-Month Yield Forecast'
                        }
                    }
                )
            ])
        ])
    ])

    # BotanistGPT Dash App
    botanist_app = dash.Dash(
    __name__,
    server=app,
    url_base_pathname='/botanist-gpt/',
    external_stylesheets=[
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
        'https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap'
    ]
    )

    botanist_app.layout = html.Div(
        className="chat-app-container",
        style={
            'background': 'linear-gradient(135deg, #f5f7fa 0%, #e4f0e2 100%)',
            'minHeight': '100vh',
            'padding': '20px'
        },
        children=[
            html.Div(
                className="chat-window",
                style={
                    'maxWidth': '800px',
                    'margin': '0 auto',
                    'borderRadius': '12px',
                    'overflow': 'hidden',
                    'boxShadow': '0 10px 30px rgba(0,0,0,0.1)',
                    'height': '80vh',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'background': '#ffffff'
                },
                children=[
                    # Header
                    html.Div(
                        className="chat-header",
                        style={
                            'background': 'linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%)',
                            'color': 'white',
                            'padding': '18px 20px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'gap': '12px'
                        },
                        children=[
                            html.Div(
                                className="avatar",
                                style={
                                    'width': '40px',
                                    'height': '40px',
                                    'background': 'rgba(255,255,255,0.2)',
                                    'borderRadius': '50%',
                                    'display': 'flex',
                                    'alignItems': 'center',
                                    'justifyContent': 'center'
                                },
                                children=[
                                    html.I(className='fas fa-leaf')
                                ]
                            ),
                            html.Div(
                                children=[
                                    html.H4(
                                        'FarmGPT',
                                        style={
                                            'margin': '0',
                                            'fontWeight': '600',
                                            'fontFamily': "'Poppins', sans-serif"
                                        }
                                    ),
                                    html.Div(
                                        [
                                            html.Span(
                                                className="status-dot",
                                                style={
                                                    'display': 'inline-block',
                                                    'width': '8px',
                                                    'height': '8px',
                                                    'background': '#76FF03',
                                                    'borderRadius': '50%',
                                                    'marginRight': '6px'
                                                }
                                            ),
                                            'Online - Plant Health Assistant'
                                        ],
                                        style={
                                            'fontSize': '0.8rem',
                                            'opacity': '0.9'
                                        }
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # Chat History
                    html.Div(
                        id='chat-history',
                        className="chat-history",
                        style={
                            'flex': '1',
                            'padding': '20px',
                            'overflowY': 'auto',
                            'background': '#f9f9f9',
                            'display': 'flex',
                            'flexDirection': 'column',
                            'gap': '15px'
                        },
                        children=[
                            # Initial bot message
                            html.Div(
                                className="message-bot",
                                style={
                                    'alignSelf': 'flex-start',
                                    'maxWidth': '70%',
                                    'display': 'flex',
                                    'gap': '10px'
                                },
                                children=[
                                    html.Div(
                                        className="bot-avatar",
                                        style={
                                            'flexShrink': '0',
                                            'width': '32px',
                                            'height': '32px',
                                            'background': '#4CAF50',
                                            'color': 'white',
                                            'borderRadius': '50%',
                                            'display': 'flex',
                                            'alignItems': 'center',
                                            'justifyContent': 'center'
                                        },
                                        children=[
                                            html.I(className='fas fa-robot')
                                        ]
                                    ),
                                    html.Div(
                                        className="message-content",
                                        style={
                                            'background': 'white',
                                            'padding': '12px 16px',
                                            'borderRadius': '18px',
                                            'borderBottomLeftRadius': '4px',
                                            'boxShadow': '0 2px 8px rgba(0,0,0,0.05)'
                                        },
                                        children=[
                                            html.P(
                                                "Hello! I'm your plant health assistant. How can I help today?",
                                                style={
                                                    'margin': '0',
                                                    'color': '#333',
                                                    'lineHeight': '1.4'
                                                }
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # Input Area
                    html.Div(
                        className="input-container",
                        style={
                            'padding': '15px',
                            'background': 'white',
                            'borderTop': '1px solid #eee',
                            'display': 'flex',
                            'gap': '10px'
                        },
                        children=[
                            dcc.Input(
                                id='user-input',
                                type='text',
                                placeholder='Ask about plant diseases, pests, or care tips...',
                                style={
                                    'flex': '1',
                                    'padding': '12px 15px',
                                    'border': '1px solid #ddd',
                                    'borderRadius': '24px',
                                    'outline': 'none',
                                    'fontFamily': "'Poppins', sans-serif",
                                    'fontSize': '0.95rem'
                                },
                                n_submit=0
                            ),
                            html.Button(
                                html.I(className='fas fa-paper-plane'),
                                id='send-button',
                                style={
                                    'width': '50px',
                                    'height': '50px',
                                    'border': 'none',
                                    'background': 'linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%)',
                                    'color': 'white',
                                    'borderRadius': '50%',
                                    'cursor': 'pointer',
                                    'transition': 'all 0.2s'
                                }
                            )
                        ]
                    )
                ]
            )
        ]
    )
    def generate_response(message):
        """Placeholder response generator for FarmGPT"""
        message = message.lower()
        
        # Response templates
        responses = {
            'hello': "Hello! I'm FarmGPT, your plant health assistant. How can I help with your crops today?",
            'hi': "Hi there! Ask me about plant diseases, pest control, or growth tips.",
            'pest': "For pest control, I recommend neem oil spray (mix 2 tbsp neem oil with 1 gallon water). Apply weekly until resolved.",
            'disease': "Common plant diseases include powdery mildew and blight. Could you describe the leaf discoloration pattern?",
            'water': "Most plants need 1-2 inches of water weekly. Check soil moisture by inserting your finger 1-2 inches deep.",
            'fertiliz': "Use a balanced 10-10-10 fertilizer every 4-6 weeks during growing season. Reduce in winter.",
            'fruit': "For better fruit yield, ensure proper pollination and consistent watering. Thin overcrowded fruits early in season.",
            'yellow': "Yellow leaves often indicate overwatering or nitrogen deficiency. Check soil drainage first.",
            'wilting': "Wilting could mean underwatering, root rot, or pest damage. Inspect roots and soil moisture.",
            'default': "I can analyze plant health issues. Please share: 1) Plant type 2) Symptoms 3) Duration of problem"
        }
        
        # Check for keywords
        for keyword, response in responses.items():
            if keyword in message:
                return response
        
        # Default response
        return responses['default']

    # Simple callback for the chat interface
    @botanist_app.callback(
        [Output('chat-history', 'children'),
        Output('user-input', 'value')],
        [Input('send-button', 'n_clicks'),
        Input('user-input', 'n_submit')],
        [State('chat-history', 'children'),
        State('user-input', 'value')]
    )
    def update_chat(n_clicks, n_submit, existing_messages, message):
        if not message or (not n_clicks and not n_submit):
            return dash.no_update
        
        user_msg = html.Div(className='message-user', children=[
            html.Div(className='avatar', children=[
                html.I(className='fas fa-user')
            ]),
            html.Div(className='message-content', children=[
                html.P(message, className='m-0')
            ])
        ])
        
        bot_response = generate_response(message)  # Your response function
        
        bot_msg = html.Div(className='message-bot', children=[
            html.Div(className='avatar', children=[
                html.I(className='fas fa-robot')
            ]),
            html.Div(className='message-content', children=[
                html.P(bot_response, className='m-0')
            ])
        ])
        
        existing_messages = existing_messages or []
        existing_messages.extend([user_msg, bot_msg])
        
        return existing_messages, ''

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)