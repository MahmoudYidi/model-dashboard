from dash import Dash, html, dcc, Input, Output, State, ctx, no_update
import dash_bootstrap_components as dbc
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
from datetime import datetime

# Load .env vars
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")

# Chat history storage file
CHAT_HISTORY_FILE = "botanist_chat_history.json"

# Load chat history from file
def load_chat_history():
    try:
        if os.path.exists(CHAT_HISTORY_FILE):
            with open(CHAT_HISTORY_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return []

# Save chat history to file
def save_chat_history(history):
    try:
        with open(CHAT_HISTORY_FILE, 'w') as f:
            json.dump(history, f)
    except Exception:
        pass

# Modern 3D plant-themed message bubble
def create_message(text, is_user, timestamp=None):
    timestamp = timestamp or datetime.now().strftime("%H:%M")
    content = dcc.Markdown(text, className="m-0", link_target="_blank") if not is_user else html.Span(text)
    
    return html.Div(
        className="d-flex mb-3",
        style={
            "justifyContent": "flex-end" if is_user else "flex-start",
            "paddingLeft": "12px" if not is_user else "0",
            "paddingRight": "12px" if is_user else "0"
        },
        children=[
            html.Div(
                style={
                    "background": "linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%)" if is_user else "linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)",
                    "color": "white" if is_user else "#2d3748",
                    "padding": "14px 18px",
                    "borderRadius": "18px",
                    "borderTopLeftRadius": "4px" if is_user else "18px",
                    "borderTopRightRadius": "18px" if is_user else "4px",
                    "maxWidth": "75%",
                    "boxShadow": "0 4px 20px rgba(30, 100, 40, 0.3)" if is_user else "0 4px 20px rgba(0, 0, 0, 0.1)",
                    "fontSize": "15px",
                    "lineHeight": "1.6",
                    "fontFamily": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
                    "position": "relative",
                    "border": "1px solid rgba(74, 107, 59, 0.1)" if not is_user else "none",
                    "transform": "perspective(500px) translateZ(10px)",
                    "transition": "all 0.3s ease",
                    "backdropFilter": "blur(2px)" if not is_user else "none",
                },
                children=[
                    html.Div(
                        style={
                            "position": "absolute",
                            "width": "100%",
                            "height": "100%",
                            "background": "url('https://www.transparenttextures.com/patterns/soft-circle-scales.png')" if not is_user else "none",
                            "opacity": "0.05",
                            "top": "0",
                            "left": "0",
                            "borderRadius": "inherit",
                            "pointerEvents": "none"
                        }
                    ),
                    content,
                    html.Div(
                        timestamp,
                        style={
                            "position": "absolute",
                            "bottom": "-18px",
                            ("right" if is_user else "left"): "12px",
                            "fontSize": "11px",
                            "color": "#718096" if not is_user else "rgba(255,255,255,0.7)"
                        }
                    )
                ]
            )
        ]
    )

def init_botanist_app(server):
    dash_app = Dash(
        __name__,
        server=server,
        url_base_pathname="/botanist-gpt/",
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            "https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css",
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
        ],
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ]
    )

    # Load initial chat history
    initial_history = load_chat_history()
    initial_messages = []
    
    if not initial_history:
        initial_messages.append(create_message(
            "🌱 **Welcome to GreenAI-GPT!**\n\nI'm your AI botanist assistant specializing in:\n\n"
            "• Plant disease diagnosis & treatment\n"
            "• Pest identification & organic control\n"
            "• Soil health optimization\n"
            "• Horticultural best practices\n\n"
            "How can I help with your plants today?",
            is_user=False,
            timestamp=datetime.now().strftime("%H:%M")
        ))
    else:
        for msg in initial_history:
            initial_messages.append(create_message(
                msg["text"],
                msg["is_user"],
                msg.get("timestamp", datetime.now().strftime("%H:%M"))
            ))

    dash_app.layout = dbc.Container([
        # 3D Green Background
        html.Div(className="bg-3d-effect", style={
            "position": "fixed",
            "top": "0",
            "left": "0",
            "width": "100%",
            "height": "100%",
            "background": "linear-gradient(160deg, #e8f5e9 0%, #c8e6c9 50%, #a5d6a7 100%)",
            "zIndex": "-1",
            "overflow": "hidden"
        }, children=[
            html.Div(style={
                "position": "absolute",
                "width": "200%",
                "height": "200%",
                "background": "url('https://www.transparenttextures.com/patterns/leaves-pattern.png')",
                "opacity": "0.03",
                "animation": "bgScroll 120s linear infinite",
                "transform": "rotate(15deg)"
            })
        ]),
        
        # Main Content Container
        dbc.Row([
            dbc.Col([
                # Header
                html.Div([
                    html.Div([
                        html.Img(
                            src="/static/images/logo3.png",
                            style={
                                "height": "40px",
                                "marginRight": "12px",
                                "filter": "drop-shadow(0 2px 4px rgba(0,0,0,0.1))"
                            }
                        ),
                        html.H2("GPT", className="m-0", style={
                            "fontSize": "1.8rem",
                            "fontWeight": "700",
                            "color": "#2e7d32",
                            "textShadow": "0 2px 4px rgba(0,0,0,0.05)",
                            "letterSpacing": "-0.5px"
                        }),
                    ], className="d-flex align-items-center justify-content-center mt-4 mb-2"),
                    html.P("Your AI crop assistant", className="text-center mb-4", style={
                        "fontSize": "1rem",
                        "fontWeight": "500",
                        "color": "#4a6b3b",
                    }),
                ], style={
                    "height": "10vh",
                    "paddingBottom": "20px",
                    "background": "rgba(255,255,255,0.7)",
                    "backdropFilter": "blur(8px)",
                    "borderRadius": "16px",
                    "margin": "0 -10px",
                    "padding": "10px 10px",
                    "boxShadow": "0 4px 6px rgba(0,0,0,0.05)",
                    "border": "1px solid rgba(74, 107, 59, 0.1)"
                }),
                
                # Chat Window
                dbc.Card([
                    dbc.CardBody([
                        html.Div(id="chat-history", style={
                            "height": "80vh",
                            "overflowY": "auto",
                            "padding": "1.5rem",
                            "backgroundColor": "rgba(255,255,255,0.85)",
                            "borderRadius": "12px",
                            "border": "1px solid rgba(74, 107, 59, 0.1)",
                            "boxShadow": "inset 0 1px 3px rgba(0,0,0,0.05)",
                            "scrollBehavior": "smooth"
                        }, children=initial_messages)
                    ], style={"padding": "0"})
                ], style={
                    "borderRadius": "16px",
                    "boxShadow": "0 10px 25px -5px rgba(0,0,0,0.1)",
                    "border": "none",
                    "background": "rgba(255,255,255,0.7)",
                    "backdropFilter": "blur(6px)",
                    "marginTop": "20px"
                }),
                
                # Input Area
                dbc.InputGroup([
                    dcc.Textarea(
                        id="user-input",
                        placeholder="Message FarmGPT... (Shift+Enter for new line)",
                        className="form-control",
                        style={
                            "fontSize": "15px",
                            "padding": "12px 16px",
                            "borderRadius": "12px",
                            "border": "1px solid rgba(74, 107, 59, 0.2)",
                            "resize": "none",
                            "minHeight": "60px",
                            "maxHeight": "120px",
                            "boxShadow": "inset 0 1px 3px rgba(0,0,0,0.05)",
                            "transition": "all 0.3s ease",
                            "background": "rgba(255,255,255,0.9)",
                            "marginTop": "20px"
                        },
                        rows=1
                    ),
                    dbc.Button(
                        html.I(className="fas fa-leaf"),
                        id="send-button",
                        color="primary",
                        n_clicks=0,
                        className="px-3",
                        style={
                            "borderRadius": "12px",
                            "marginLeft": "8px",
                            "marginTop": "20px",
                            "background": "linear-gradient(135deg, #4a8c55 0%, #2e7d32 100%)",
                            "border": "none",
                            "height": "50px",
                            "boxShadow": "0 4px 6px rgba(46, 125, 50, 0.2)",
                            "transition": "all 0.2s ease",
                            "transform": "translateY(0)",
                            ":hover": {
                                "transform": "translateY(-2px)",
                                "boxShadow": "0 6px 8px rgba(46, 125, 50, 0.3)"
                            },
                            ":active": {
                                "transform": "translateY(0)"
                            }
                        }
                    )
                ], className="mb-4", style={"maxWidth": "800px", "margin": "0 auto"}),
                
                # Subtle decorative elements
                html.Div(style={
                    "textAlign": "center",
                    "marginTop": "20px",
                    "color": "rgba(74, 107, 59, 0.3)",
                    "fontSize": "12px"
                }, children=[
                    html.I(className="fas fa-seedling", style={"margin": "0 5px"}),
                    html.I(className="fas fa-leaf", style={"margin": "0 5px"}),
                    html.I(className="fas fa-spa", style={"margin": "0 5px"})
                ])
                
            ], md=10, lg=8, className="mx-auto")
        ], className="mt-2"),
        
        dcc.Store(id="chat-store", data=initial_history),
        dcc.Interval(id="scroll-interval", interval=500, n_intervals=0, max_intervals=1),
        dcc.Interval(id="save-interval", interval=10000, n_intervals=0),
        
        # CSS Animations
        dcc.Markdown("""
            <style>
                @keyframes bgScroll {
                    0% { transform: translateX(0) translateY(0) rotate(15deg); }
                    100% { transform: translateX(-50%) translateY(-50%) rotate(15deg); }
                }
                .bg-3d-effect {
                    perspective: 1000px;
                }
            </style>
        """, dangerously_allow_html=True)
    ], fluid=True, style={
        "maxWidth": "1200px",
        "padding": "0 20px",
        "minHeight": "100vh"
    })

    # Callbacks remain the same as previous version
    @dash_app.callback(
        Output("chat-history", "children"),
        Output("chat-store", "data"),
        Output("user-input", "value"),
        Output("scroll-interval", "n_intervals"),
        Input("send-button", "n_clicks"),
        State("user-input", "value"),
        State("chat-store", "data"),
        prevent_initial_call=True
    )
    def handle_message(n_clicks, user_msg, chat_history):
        if not user_msg or user_msg.strip() == "":
            return no_update, no_update, "", 0

        chat_history = chat_history or []
        timestamp = datetime.now().strftime("%H:%M")

        # Append user input
        chat_history.append({
            "text": user_msg, 
            "is_user": True,
            "timestamp": timestamp
        })

        try:
            # Build context from previous messages
            context = "\n".join(
                f"{'User' if msg['is_user'] else 'Assistant'}: {msg['text']}" 
                for msg in chat_history[-6:]  # Keep last 3 exchanges for context
            )
            
            prompt = f"""
You are FarmGPT, a professional botanist AI assistant with expertise in:
- Plant pathology and diseases
- Entomology and pest management
- Soil science and nutrition
- Horticulture and agriculture
- Organic and sustainable practices

Guidelines:
1. Maintain context from previous messages when relevant
2. Use markdown formatting for clear responses:
   - **Bold** for key terms
   - _Italics_ for scientific names
   - Bullet points for lists
   - Headings for sections
3. Be concise but thorough
4. Provide actionable advice
5. Cite sources when possible

Current conversation context:
{context}

Respond to this latest query:
{user_msg}
"""
            response = model.generate_content(prompt)
            response_text = getattr(response, "text", "⚠️ Could not get a valid response.")
        except Exception as e:
            response_text = f"⚠️ Error: {str(e)}"

        # Append AI response
        chat_history.append({
            "text": response_text, 
            "is_user": False,
            "timestamp": datetime.now().strftime("%H:%M")
        })

        # Save to history
        save_chat_history(chat_history)

        # Render messages
        history_ui = [create_message(msg["text"], msg["is_user"], msg.get("timestamp")) for msg in chat_history]

        return history_ui, chat_history, "", 0

    @dash_app.callback(
        Output("chat-history", "style"),
        Input("scroll-interval", "n_intervals"),
        prevent_initial_call=True
    )
    def scroll_to_bottom(n):
        return {
            "height": "60vh",
            "overflowY": "auto",
            "padding": "1.5rem",
            "backgroundColor": "rgba(255,255,255,0.85)",
            "borderRadius": "12px",
            "border": "1px solid rgba(74, 107, 59, 0.1)",
            "scrollBehavior": "smooth",
            "animation": "fadeIn 0.3s ease-in-out",
            "boxShadow": "inset 0 1px 3px rgba(0,0,0,0.05)"
        }

    @dash_app.callback(
        Output("save-interval", "n_intervals"),
        Input("save-interval", "n_intervals"),
        State("chat-store", "data"),
        prevent_initial_call=True
    )
    def auto_save_chat(n, chat_data):
        if chat_data:
            save_chat_history(chat_data)
        return n

    return dash_app.server