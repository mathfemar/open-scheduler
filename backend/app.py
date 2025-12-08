"""Main Dash application with multi-page support."""
import os
from dotenv import load_dotenv
load_dotenv()

# Environment variables
PROJECT_ROOT = os.getenv("PROJECT_ROOT") or os.getcwd()
HOST = os.getenv("APP_HOST", "0.0.0.0")
PORT = int(os.getenv("APP_PORT", "8050"))
DEBUG = os.getenv("DEBUG", "True").lower() in ("1", "true", "yes")

import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

# Initialize database
from backend.core.database import init_db
init_db()

# Initialize scheduler
from backend.core.scheduler import get_scheduler
scheduler = get_scheduler()
scheduler.start()

# Initialize Dash app with multi-page support and Bootstrap theme
app = Dash(
    __name__,
    use_pages=True,
    pages_folder=os.path.join(os.path.dirname(__file__), "..", "frontend", "pages"),
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css",
    ],
    assets_folder=os.path.join(os.path.dirname(__file__), "..", "frontend", "assets"),
)

# Shutdown scheduler on app exit
import atexit
atexit.register(lambda: scheduler.shutdown())

# Import navbar component
from frontend.components.navbar import create_navbar

# App layout with navbar and page container
app.layout = html.Div(
    [
        create_navbar(),
        dash.page_container,
    ],
)

if __name__ == '__main__':
    print(f"🚀 Starting Open Scheduler")
    print(f"   Project root: {PROJECT_ROOT}")
    print(f"   URL: http://localhost:{PORT}")
    print(f"   Debug mode: {DEBUG}")
    
    # Start the app
    try:
        app.run(host=HOST, port=PORT, debug=DEBUG)
    except TypeError:
        # Fallback for older Dash versions
        app.run_server(host=HOST, port=PORT, debug=DEBUG)
