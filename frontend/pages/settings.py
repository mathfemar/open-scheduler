"""Settings page - Manage tracked directories and configuration."""
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import os
from backend.core.database import SessionLocal
from backend.core import api

dash.register_page(__name__, path="/settings", name="Settings")

layout = html.Div(
    [
        html.H1("Settings", className="mb-4"),
        
        # Tracked Directories Section
        dbc.Card(
            [
                dbc.CardHeader(html.H5("Tracked Directories")),
                dbc.CardBody(
                    [
                        html.P(
                            "Manage directories that will be scanned for Python files in the file tree.",
                            className="text-muted mb-3",
                        ),
                        
                        html.Div(
                            [
                                html.P("Tracked directories will appear here", className="text-muted"),
                            ],
                            id="tracked-dirs-list",
                            className="mb-3",
                        ),
                        
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Input(
                                        id="new-dir-path",
                                        type="text",
                                        placeholder="Enter directory path (e.g., C:\\Projects\\scripts)",
                                    ),
                                    width=12,
                                    md=10,
                                ),
                                dbc.Col(
                                    dbc.Button(
                                        "+ Add Directory",
                                        id="add-dir-btn",
                                        color="primary",
                                        className="w-100",
                                    ),
                                    width=12,
                                    md=2,
                                ),
                            ],
                        ),
                        html.Div(id="add-dir-feedback", className="mt-3"),
                    ],
                ),
            ],
            className="mb-4",
        ),
        
        # General Settings
        dbc.Card(
            [
                dbc.CardHeader(html.H5("General Settings")),
                dbc.CardBody(
                    [
                        html.P("App Information", className="mb-2"),
                        html.Small("Version: 1.0.0", className="text-muted d-block"),
                        html.Small("Auto-refresh interval: 5 seconds", className="text-muted d-block"),
                        html.Small("Max upload size: 5MB", className="text-muted d-block"),
                    ],
                ),
            ],
        ),
    ],
    className="container-fluid",
)


# Callbacks

@callback(
    Output("tracked-dirs-list", "children"),
    [
        Input("add-dir-btn", "n_clicks"),
        Input({"type": "remove-dir-btn", "id": dash.ALL}, "n_clicks"),
    ],
    prevent_initial_call=False,
)
def update_tracked_dirs_list(add_clicks, remove_clicks):
    """Display list of tracked directories."""
    db = SessionLocal()
    try:
        tracked_dirs = api.get_tracked_dirs(db)
        
        if not tracked_dirs:
            return html.P("No tracked directories yet. Add one below.", className="text-muted")
        
        dir_items = []
        for td in tracked_dirs:
            dir_items.append(
                dbc.ListGroupItem(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.I(className="bi bi-folder-fill me-2", style={"color": "var(--accent-blue)"}),
                                        html.Strong(td.path),
                                        html.Br(),
                                        html.Small(f"Added: {td.created_at.strftime('%Y-%m-%d %H:%M')}", className="text-muted"),
                                    ],
                                    className="flex-grow-1",
                                ),
                                dbc.Button(
                                    "🗑 Remove",
                                    id={"type": "remove-dir-btn", "id": td.id},
                                    color="danger",
                                    size="sm",
                                    outline=True,
                                ),
                            ],
                            className="d-flex align-items-center justify-content-between",
                        ),
                    ],
                )
            )
        
        return dbc.ListGroup(dir_items)
    
    finally:
        db.close()


@callback(
    [
        Output("add-dir-feedback", "children"),
        Output("new-dir-path", "value"),
    ],
    Input("add-dir-btn", "n_clicks"),
    State("new-dir-path", "value"),
    prevent_initial_call=True,
)
def add_directory(n_clicks, path):
    """Add new tracked directory."""
    if not n_clicks or not path:
        return dash.no_update, dash.no_update
    
    path = path.strip()
    
    # Validation
    if not path:
        return dbc.Alert("Please enter a directory path.", color="danger", dismissable=True), dash.no_update
    
    if not os.path.exists(path):
        return dbc.Alert(f"Directory does not exist: {path}", color="danger", dismissable=True), dash.no_update
    
    if not os.path.isdir(path):
        return dbc.Alert(f"Path is not a directory: {path}", color="danger", dismissable=True), dash.no_update
    
    # Check if readable
    try:
        os.listdir(path)
    except PermissionError:
        return dbc.Alert(f"No permission to read directory: {path}", color="danger", dismissable=True), dash.no_update
    
    db = SessionLocal()
    try:
        # Check if already exists
        existing = api.get_tracked_dirs(db)
        if any(td.path == path for td in existing):
            return dbc.Alert(f"Directory already tracked: {path}", color="warning", dismissable=True), dash.no_update
        
        # Add directory (api.add_tracked_dir expects a string path, not Pydantic object)
        api.add_tracked_dir(db, path)
        
        return dbc.Alert(f"Directory added successfully: {path}", color="success", dismissable=True), ""
    
    except Exception as e:
        return dbc.Alert(f"Error adding directory: {str(e)}", color="danger", dismissable=True), dash.no_update
    
    finally:
        db.close()


@callback(
    Output("add-dir-feedback", "children", allow_duplicate=True),
    Input({"type": "remove-dir-btn", "id": dash.ALL}, "n_clicks"),
    State({"type": "remove-dir-btn", "id": dash.ALL}, "id"),
    prevent_initial_call=True,
)
def remove_directory(n_clicks_list, id_list):
    """Remove tracked directory."""
    # Find which button was clicked
    for i, n_clicks in enumerate(n_clicks_list):
        if n_clicks and n_clicks > 0:
            dir_id = id_list[i]["id"]
            
            db = SessionLocal()
            try:
                success = api.remove_tracked_dir(db, dir_id)
                
                if success:
                    return dbc.Alert("Directory removed successfully.", color="success", dismissable=True)
                else:
                    return dbc.Alert("Failed to remove directory.", color="danger", dismissable=True)
            
            except Exception as e:
                return dbc.Alert(f"Error removing directory: {str(e)}", color="danger", dismissable=True)
            
            finally:
                db.close()
    
    return dash.no_update
