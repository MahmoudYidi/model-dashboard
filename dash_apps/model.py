from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

def init_model_app(server):
    dash_app = Dash(
        __name__, server=server, url_base_pathname='/model/',
        external_stylesheets=[dbc.themes.BOOTSTRAP, "https://use.fontawesome.com/releases/v5.15.4/css/all.css"],
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
    )

    # Dummy streaming info (replace with real-time logic)
    camera_online = True
    camera_resolution = "1920x1080"
    stream_fps = 30
    stream_bitrate = "4 Mbps"
    stream_latency = "120 ms"
    frame_drops = 0
    codec_used = "H.264"
    stream_url = "rtsp://camera/stream"

    # Camera status
    status_text = "Online" if camera_online else "Offline"
    status_color = "success" if camera_online else "danger"

    def create_status_alert(status_text, status_color):
        return dbc.Alert(
            f"Camera is {status_text}",
            color=status_color,
            className="text-center fw-bold",
            style={"fontSize": "1.2rem", "borderRadius": "12px"}
        )

    def create_info_card(title, value, icon=None):
        return dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H6(title, className="card-title mb-1"),
                    html.I(className=f"fas {icon} float-end fa-2x opacity-25" if icon else "", style={"color": "#666"})
                ], className="d-flex justify-content-between"),
                html.H4(value, className="mb-0 mt-2")
            ]),
            className="mb-3 border-0 shadow-sm h-100",
            style={
                "borderRadius": "15px",
                "background": "linear-gradient(145deg, #ffffff, #f0f0f0)",
                "boxShadow": "0 6px 12px rgba(0,0,0,0.08)"
            }
        )

    dash_app.layout = html.Div(style={
        "background": "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
        "minHeight": "100vh",
        "padding": "20px"
    }, children=[

        # Header
        html.Div(className="text-center mb-4", children=[
            html.H1("Model Live Stream", style={
                "color": "#2c3e50",
                "textShadow": "1px 1px 2px rgba(0,0,0,0.1)",
                "fontWeight": "bold"
            }),
            html.Small("Monitor live camera status and stream performance", className="text-muted")
        ]),

        # Camera status indicator
        create_status_alert(status_text, status_color),

        # Info cards
        dbc.Row([
            dbc.Col(create_info_card("Resolution", camera_resolution, icon="fa-arrows-alt"), md=3, sm=6),
            dbc.Col(create_info_card("FPS", f"{stream_fps} fps", icon="fa-tachometer-alt"), md=3, sm=6),
            dbc.Col(create_info_card("Bitrate", stream_bitrate, icon="fa-signal"), md=3, sm=6),
            dbc.Col(create_info_card("Latency", stream_latency, icon="fa-clock"), md=3, sm=6),
        ], className="g-3 mb-4"),

        # Streaming video & stats
        dbc.Row([
            dbc.Col(html.Div([
                html.Video(
                    controls=True,
                    autoPlay=True,
                    muted=True,
                    style={
                        "width": "100%",
                        "height": "auto",
                        "borderRadius": "15px",
                        "boxShadow": "0 10px 30px rgba(0,0,0,0.15)"
                    },
                    src="/assets/sample_video.mp4",  # <-- Replace with actual stream
                    id="streaming-video"
                ),
                html.Div("🔴 Live Camera Stream", className="text-center mt-2", style={"fontWeight": "600", "color": "#333"})
            ]), md=8),

            dbc.Col(dbc.Card([
                dbc.CardHeader("📊 Streaming Info", className="fw-bold text-center"),
                dbc.CardBody([
                    dbc.ListGroup([
                        dbc.ListGroupItem([
                            html.Span("Frame Drops"),
                            html.Span(str(frame_drops), className="badge bg-success rounded-pill")
                        ], className="d-flex justify-content-between align-items-center"),

                        dbc.ListGroupItem([
                            html.Span("Codec"),
                            html.Span(codec_used, className="badge bg-secondary rounded-pill")
                        ], className="d-flex justify-content-between align-items-center"),

                        dbc.ListGroupItem([
                            html.Span("Streaming URL"),
                            html.Span(stream_url, className="text-truncate", style={"maxWidth": "160px", "fontSize": "0.85rem"})
                        ], className="d-flex justify-content-between align-items-center")
                    ], flush=True)
                ])
            ], style={
                "borderRadius": "15px",
                "boxShadow": "0 10px 30px rgba(0,0,0,0.1)",
                "height": "100%"
            }), md=4)
        ]),

        # Footer
        html.Div([
            html.Small("Last updated: Just now", className="text-muted")
        ], className="text-end mt-3")
    ])

    return dash_app
