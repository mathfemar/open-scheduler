"""New Job page - Create and configure new jobs."""
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import os
import json
from datetime import datetime

dash.register_page(__name__, path="/new-job", name="New Job")

layout = html.Div(
    [
        html.H1("Create New Job", className="mb-4"),
        
        # Hidden stores
        dcc.Store(id="selected-file-path"),
        dcc.Store(id="uploaded-file-info"),
        
        # Step 1: Select File
        dbc.Card(
            [
                dbc.CardHeader(html.H5("Step 1: Select Python File")),
                dbc.CardBody(
                    [
                        dbc.Tabs(
                            [
                                dbc.Tab(
                                    label="Project Files",
                                    tab_id="tab-project",
                                    children=[
                                        html.Div(
                                            [
                                                dbc.Button(
                                                    "Refresh File Tree",
                                                    id="refresh-tree-btn",
                                                    color="secondary",
                                                    size="sm",
                                                    outline=True,
                                                    className="mb-3",
                                                ),
                                                html.Div(
                                                    id="file-tree-container",
                                                    className="mt-3",
                                                ),
                                            ],
                                            className="mt-3",
                                        ),
                                    ],
                                ),
                                dbc.Tab(
                                    label="Upload New",
                                    tab_id="tab-upload",
                                    children=[
                                        html.Div(
                                            [
                                                dcc.Upload(
                                                    id="upload-file",
                                                    children=html.Div(
                                                        [
                                                            html.I(className="bi bi-cloud-upload", style={"fontSize": "3rem"}),
                                                            html.P("Drag and drop or click to select .py file", className="mt-3"),
                                                            html.P("Max file size: 5MB", className="text-muted small"),
                                                        ],
                                                    ),
                                                    className="upload-zone",
                                                    multiple=False,
                                                ),
                                                html.Div(id="upload-status", className="mt-3"),
                                            ],
                                            className="mt-3",
                                        ),
                                    ],
                                ),
                            ],
                            id="file-tabs",
                            active_tab="tab-project",
                        ),
                    ],
                ),
            ],
            className="mb-4",
        ),
        
        # File Preview
        dbc.Card(
            [
                dbc.CardHeader(
                    html.Div(
                        [
                            html.H5("Preview", className="mb-0 d-inline"),
                            html.Small(" ", id="preview-file-path", className="text-muted ms-2"),
                        ],
                        className="d-flex align-items-center",
                    ),
                ),
                dbc.CardBody(
                    [
                        html.Pre(
                            "# Select a file to preview",
                            id="file-preview",
                            className="code-preview",
                            style={"maxHeight": "300px", "overflowY": "auto"},
                        ),
                    ],
                ),
            ],
            className="mb-4",
        ),
        
        # Step 2: Configure Schedule
        dbc.Card(
            [
                dbc.CardHeader(html.H5("Step 2: Configure Schedule")),
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label("Job Name"),
                                        dbc.Input(id="job-name", type="text", placeholder="My Job"),
                                    ],
                                    width=12,
                                    md=6,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Description"),
                                        dbc.Input(id="job-description", type="text", placeholder="Optional description"),
                                    ],
                                    width=12,
                                    md=6,
                                ),
                            ],
                            className="mb-3",
                        ),
                        
                        dbc.Label("Schedule Type"),
                        dbc.RadioItems(
                            id="schedule-type",
                            options=[
                                {"label": " Cron (e.g., daily at 2 AM)", "value": "cron"},
                                {"label": " Interval (e.g., every 10 minutes)", "value": "interval"},
                                {"label": " One-time (run once at specific time)", "value": "once"},
                            ],
                            value="interval",
                            className="mb-3",
                        ),
                        
                        html.Div(id="schedule-config-container", children=[
                            html.P("Schedule configuration will appear here", className="text-muted"),
                        ]),
                        
                        # Advanced Options (collapsed)
                        dbc.Accordion(
                            [
                                dbc.AccordionItem(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Timeout (seconds)"),
                                                        dbc.Input(id="job-timeout", type="number", value=300, min=1),
                                                        html.Small("Maximum execution time (default: 300s)", className="text-muted"),
                                                    ],
                                                    width=12,
                                                    md=4,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Max Retries"),
                                                        dbc.Input(id="job-retry-max", type="number", value=3, min=0, max=10),
                                                        html.Small("Number of retry attempts on failure", className="text-muted"),
                                                    ],
                                                    width=12,
                                                    md=4,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Retry Delay (seconds)"),
                                                        dbc.Input(id="job-retry-delay", type="number", value=60, min=0),
                                                        html.Small("Wait time between retries", className="text-muted"),
                                                    ],
                                                    width=12,
                                                    md=4,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Arguments (comma-separated)"),
                                                        dbc.Input(id="job-args", type="text", placeholder="arg1, arg2, arg3"),
                                                        html.Small("Command line arguments for the script", className="text-muted"),
                                                    ],
                                                    width=12,
                                                    md=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Environment Variables (JSON)"),
                                                        dbc.Textarea(
                                                            id="job-env",
                                                            placeholder='{"KEY": "value"}',
                                                            rows=2,
                                                        ),
                                                        html.Small('JSON object with env vars', className="text-muted"),
                                                    ],
                                                    width=12,
                                                    md=6,
                                                ),
                                            ],
                                        ),
                                    ],
                                    title="Advanced Options",
                                ),
                            ],
                            start_collapsed=True,
                            className="mb-3 accordion-dark",
                        ),
                        
                        html.Hr(),
                        
                        # Status alerts
                        html.Div(id="job-form-alert"),
                        
                        # Actions
                        html.Div(
                            [
                                dbc.Button("Test Run", id="test-run-btn", color="secondary", outline=True, className="me-2"),
                                dbc.Button("Cancel", color="secondary", outline=True, href="/jobs", className="me-2"),
                                dbc.Button("Save as Draft", id="save-draft-btn", color="warning", outline=True, className="me-2"),
                                dbc.Button("Activate Job", id="activate-job-btn", color="success"),
                            ],
                            className="text-end",
                        ),
                    ],
                ),
            ],
        ),
    ],
    className="container-fluid",
)


# ====================
# CALLBACKS
# ====================

# Callback 1: Load file tree from tracked directories
@callback(
    Output("file-tree-container", "children"),
    [Input("refresh-tree-btn", "n_clicks")],
    prevent_initial_call=False,
)
def update_file_tree(n_clicks):
    """Load and display visual file tree from all tracked directories."""
    from backend.core.database import SessionLocal
    from backend.core import api
    from backend.core.fileops import list_files
    
    session = SessionLocal()
    try:
        # Get tracked directories
        tracked_dirs = api.get_tracked_dirs(session)
        
        print(f"[DEBUG] Found {len(tracked_dirs)} tracked directories")
        
        if not tracked_dirs:
            return dbc.Alert(
                "No tracked directories found. Add directories in Settings.",
                color="warning",
            )
        
        # Collect all files from tracked directories
        all_files = []
        for td in tracked_dirs:
            print(f"[DEBUG] Checking directory: {td.path}, exists: {os.path.exists(td.path)}")
            if os.path.exists(td.path):
                try:
                    files = list_files(td.path)
                    print(f"[DEBUG] Found {len(files)} .py files in {td.path}")
                    for f in files:
                        f["tracked_dir_id"] = td.id
                        f["tracked_dir_path"] = td.path
                    all_files.extend(files)
                except Exception as e:
                    print(f"[ERROR] Failed to list files in {td.path}: {e}")
        
        print(f"[DEBUG] Total files collected: {len(all_files)}")
        
        if not all_files:
            return dbc.Alert(
                "No Python files found in tracked directories.",
                color="info",
            )
        
        # Build hierarchical tree structure
        def build_tree_structure(files, root_path):
            """Organize files into folder hierarchy."""
            tree = {"files": [], "folders": {}}
            
            for f in files:
                rel_path = f["relpath"]
                parts = rel_path.split(os.sep)
                
                # Navigate/create folder structure
                current = tree
                for i, part in enumerate(parts[:-1]):
                    if part not in current["folders"]:
                        current["folders"][part] = {"files": [], "folders": {}}
                    current = current["folders"][part]
                
                # Add file to final folder
                if "files" not in current:
                    current["files"] = []
                current["files"].append(f)
            
            return tree
        
        # Build tree UI components
        def render_tree(tree_dict, path_prefix="", depth=0):
            """Recursively render tree structure with collapsible folders."""
            elements = []
            
            # Render folders
            for folder_name, folder_data in sorted(tree_dict["folders"].items()):
                folder_id = f"folder-{path_prefix}-{folder_name}".replace(os.sep, "-").replace(" ", "_")
                
                # Folder header (clickable to expand/collapse)
                folder_header = html.Div(
                    [
                        html.Span("▶ ", className="tree-folder-icon", id={"type": "folder-icon", "id": folder_id}),
                        html.I(className="bi bi-folder me-2", style={"color": "var(--warning-orange)"}),
                        html.Span(folder_name, style={"fontWeight": "500"}),
                    ],
                    className="tree-folder",
                    id={"type": "folder-toggle", "id": folder_id},
                    n_clicks=0,
                )
                
                # Folder children (initially hidden)
                folder_children = html.Div(
                    render_tree(folder_data, f"{path_prefix}/{folder_name}", depth + 1),
                    className="tree-children",
                    id={"type": "folder-content", "id": folder_id},
                    style={"display": "none"},
                )
                
                elements.append(html.Div([folder_header, folder_children]))
            
            # Render files in current folder
            for f in sorted(tree_dict["files"], key=lambda x: x["relpath"]):
                file_element = html.Div(
                    [
                        html.I(className="bi bi-file-code tree-file-icon"),
                        html.Span(os.path.basename(f["relpath"]), style={"fontWeight": "400"}),
                        html.Small(f" ({f['size_kb']:.1f} KB)", className="text-muted ms-2"),
                    ],
                    className="tree-file",
                    id={"type": "file-item", "path": f["abspath"]},
                    n_clicks=0,
                )
                elements.append(file_element)
            
            return elements
        
        # Build complete tree for all tracked directories
        tree_components = []
        for td in tracked_dirs:
            td_files = [f for f in all_files if f["tracked_dir_path"] == td.path]
            if td_files:
                tree_structure = build_tree_structure(td_files, td.path)
                
                # Root folder for this tracked directory
                root_name = os.path.basename(td.path) or td.path
                tree_components.append(
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.I(className="bi bi-folder-fill me-2", style={"color": "var(--accent-blue)"}),
                                    html.Strong(root_name),
                                    html.Small(f" ({len(td_files)} files)", className="text-muted ms-2"),
                                ],
                                className="mb-2",
                                style={"fontSize": "1rem", "padding": "8px 0"},
                            ),
                            html.Div(render_tree(tree_structure, root_name), className="ms-3"),
                        ],
                        className="mb-4",
                    )
                )
        
        result = html.Div(tree_components, style={"maxHeight": "500px", "overflowY": "auto"})
        print(f"[DEBUG] Returning tree with {len(tree_components)} root folders")
        return result
    
    except Exception as e:
        print(f"[ERROR] File tree callback failed: {e}")
        import traceback
        traceback.print_exc()
        return dbc.Alert(
            f"Error loading file tree: {str(e)}",
            color="danger",
        )
    
    finally:
        session.close()


# Callback 1.5: Toggle folder expand/collapse
@callback(
    [
        Output({"type": "folder-content", "id": dash.MATCH}, "style"),
        Output({"type": "folder-icon", "id": dash.MATCH}, "children"),
    ],
    [Input({"type": "folder-toggle", "id": dash.MATCH}, "n_clicks")],
    [State({"type": "folder-content", "id": dash.MATCH}, "style")],
    prevent_initial_call=True,
)
def toggle_folder(n_clicks, current_style):
    """Toggle folder visibility."""
    if not n_clicks:
        return dash.no_update, dash.no_update
    
    # Toggle display
    is_hidden = current_style.get("display") == "none"
    new_style = {"display": "block"} if is_hidden else {"display": "none"}
    new_icon = "▼ " if is_hidden else "▶ "
    
    return new_style, new_icon


# Callback 2: Handle file selection from tree
@callback(
    [
        Output("selected-file-path", "data"),
        Output("file-preview", "children"),
        Output("preview-file-path", "children"),
    ],
    [Input({"type": "file-item", "path": dash.ALL}, "n_clicks")],
    [State({"type": "file-item", "path": dash.ALL}, "id")],
    prevent_initial_call=True,
)
def select_file(n_clicks_list, id_list):
    """Handle file selection and preview."""
    from backend.core.fileops import read_file
    
    # Find which file was clicked
    for i, n_clicks in enumerate(n_clicks_list):
        if n_clicks and n_clicks > 0:
            file_path = id_list[i]["path"]
            
            try:
                # Read file content
                content = read_file(file_path, root=None)
                
                return (
                    file_path,
                    content,
                    file_path,
                )
            except Exception as e:
                return (
                    None,
                    f"# Error reading file: {str(e)}",
                    "Error",
                )
    
    return (dash.no_update, dash.no_update, dash.no_update)


# Callback 3: Handle file upload
@callback(
    [
        Output("uploaded-file-info", "data"),
        Output("upload-status", "children"),
        Output("file-preview", "children", allow_duplicate=True),
        Output("preview-file-path", "children", allow_duplicate=True),
        Output("selected-file-path", "data", allow_duplicate=True),
    ],
    [Input("upload-file", "contents")],
    [State("upload-file", "filename")],
    prevent_initial_call=True,
)
def handle_file_upload(contents, filename):
    """Handle file upload and save to first tracked directory."""
    import base64
    import hashlib
    from backend.core.database import SessionLocal
    from backend.core import api
    from backend.core.models import UploadedFile
    
    if not contents or not filename:
        return None, None, dash.no_update, dash.no_update, dash.no_update
    
    # Validate file extension
    if not filename.endswith(".py"):
        return (
            None,
            dbc.Alert("Only .py files are allowed.", color="danger"),
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )
    
    session = SessionLocal()
    try:
        # Decode file content
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        
        # Check file size (5MB limit)
        size_bytes = len(decoded)
        if size_bytes > 5 * 1024 * 1024:
            return (
                None,
                dbc.Alert("File size exceeds 5MB limit.", color="danger"),
                dash.no_update,
                dash.no_update,
                dash.no_update,
            )
        
        # Get first tracked directory
        tracked_dirs = api.get_tracked_dirs(session)
        if not tracked_dirs:
            return (
                None,
                dbc.Alert("No tracked directories found. Add one in Settings first.", color="danger"),
                dash.no_update,
                dash.no_update,
                dash.no_update,
            )
        
        upload_dir = tracked_dirs[0].path
        
        # Save file
        stored_path = os.path.join(upload_dir, "uploaded", filename)
        os.makedirs(os.path.dirname(stored_path), exist_ok=True)
        
        with open(stored_path, "wb") as f:
            f.write(decoded)
        
        # Calculate hash
        file_hash = hashlib.sha256(decoded).hexdigest()
        
        # Save metadata to DB
        uploaded_file = UploadedFile(
            filename=filename,
            stored_path=stored_path,
            file_hash=file_hash,
            size_bytes=size_bytes,
            uploaded_at=datetime.utcnow(),
        )
        session.add(uploaded_file)
        session.commit()
        
        # Read content for preview
        content_text = decoded.decode("utf-8", errors="replace")
        
        return (
            {"path": stored_path, "filename": filename},
            dbc.Alert(f"File uploaded successfully: {filename}", color="success"),
            content_text,
            stored_path,
            stored_path,
        )
    
    except Exception as e:
        return (
            None,
            dbc.Alert(f"Upload failed: {str(e)}", color="danger"),
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )
    
    finally:
        session.close()


# Callback 4: Update schedule config UI based on schedule type
@callback(
    Output("schedule-config-container", "children"),
    [Input("schedule-type", "value")],
)
def update_schedule_config(schedule_type):
    """Show appropriate schedule configuration inputs."""
    if schedule_type == "cron":
        return html.Div(
            [
                dbc.Label("Cron Expression"),
                dbc.Input(
                    id={"type": "schedule-input", "name": "cron-value"},
                    type="text",
                    placeholder="0 2 * * * (every day at 2 AM)",
                ),
                html.Small(
                    [
                        "Format: ",
                        html.Code("minute hour day month day_of_week"),
                        " • ",
                        html.A("Cron help", href="https://crontab.guru", target="_blank"),
                    ],
                    className="text-muted",
                ),
            ],
        )
    
    elif schedule_type == "interval":
        return html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Interval Value"),
                                dbc.Input(
                                    id={"type": "schedule-input", "name": "interval-value"},
                                    type="number",
                                    value=10,
                                    min=1,
                                ),
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Unit"),
                                dbc.Select(
                                    id={"type": "schedule-input", "name": "interval-unit"},
                                    options=[
                                        {"label": "Seconds", "value": "seconds"},
                                        {"label": "Minutes", "value": "minutes"},
                                        {"label": "Hours", "value": "hours"},
                                    ],
                                    value="minutes",
                                ),
                            ],
                            width=6,
                        ),
                    ],
                ),
                html.Small("Run job repeatedly at this interval", className="text-muted"),
            ],
        )
    
    elif schedule_type == "once":
        return html.Div(
            [
                dbc.Label("Run At"),
                dbc.Input(
                    id={"type": "schedule-input", "name": "once-value"},
                    type="datetime-local",
                ),
                html.Small("Job will run once at the specified time", className="text-muted"),
            ],
        )
    
    return html.P("Invalid schedule type", className="text-danger")


# Callback 5: Test Run
@callback(
    Output("job-form-alert", "children", allow_duplicate=True),
    [Input("test-run-btn", "n_clicks")],
    [
        State("selected-file-path", "data"),
        State("job-args", "value"),
        State("job-env", "value"),
        State("job-timeout", "value"),
    ],
    prevent_initial_call=True,
)
def test_run(n_clicks, file_path, args_str, env_str, timeout):
    """Execute selected file immediately and show results."""
    if not n_clicks:
        return dash.no_update
    
    if not file_path:
        return dbc.Alert("Please select a file first.", color="danger")
    
    from backend.core.executor import run_file
    
    try:
        # Parse args
        args = []
        if args_str and args_str.strip():
            args = [a.strip() for a in args_str.split(",")]
        
        # Parse env
        env = None
        if env_str and env_str.strip():
            env = json.loads(env_str)
        
        # Run file
        result = run_file(
            path=file_path,
            args=args,
            env=env,
            timeout=timeout or 300,
        )
        
        # Format result
        status_color = "success" if result["status"] == "success" else "danger"
        
        return dbc.Alert(
            [
                html.H5(f"Test Run: {result['status'].upper()}", className="alert-heading"),
                html.Hr(),
                html.P(f"Exit Code: {result['exit_code']}"),
                html.P(f"Duration: {result['duration']:.2f}s"),
                html.Hr(),
                html.H6("Output:"),
                html.Pre(
                    result["output"] or "(no output)",
                    style={"maxHeight": "200px", "overflowY": "auto", "fontSize": "0.85rem"},
                ),
            ],
            color=status_color,
            dismissable=True,
        )
    
    except json.JSONDecodeError:
        return dbc.Alert("Invalid JSON in Environment Variables.", color="danger", dismissable=True)
    except Exception as e:
        return dbc.Alert(f"Test run failed: {str(e)}", color="danger", dismissable=True)


# Callback 6: Save as Draft
@callback(
    Output("job-form-alert", "children", allow_duplicate=True),
    [Input("save-draft-btn", "n_clicks")],
    [
        State("selected-file-path", "data"),
        State("job-name", "value"),
        State("job-description", "value"),
        State("schedule-type", "value"),
        State({"type": "schedule-input", "name": "cron-value"}, "value"),
        State({"type": "schedule-input", "name": "interval-value"}, "value"),
        State({"type": "schedule-input", "name": "interval-unit"}, "value"),
        State({"type": "schedule-input", "name": "once-value"}, "value"),
        State("job-timeout", "value"),
        State("job-retry-max", "value"),
        State("job-retry-delay", "value"),
        State("job-args", "value"),
        State("job-env", "value"),
    ],
    prevent_initial_call=True,
)
def save_draft(
    n_clicks,
    file_path,
    name,
    description,
    schedule_type,
    cron_value,
    interval_value,
    interval_unit,
    once_value,
    timeout,
    retry_max,
    retry_delay,
    args_str,
    env_str,
):
    """Save job as draft (paused status)."""
    if not n_clicks:
        return dash.no_update
    
    return _create_job(
        file_path=file_path,
        name=name,
        description=description,
        schedule_type=schedule_type,
        cron_value=cron_value,
        interval_value=interval_value,
        interval_unit=interval_unit,
        once_value=once_value,
        timeout=timeout,
        retry_max=retry_max,
        retry_delay=retry_delay,
        args_str=args_str,
        env_str=env_str,
        status="paused",
    )


# Callback 7: Activate Job
@callback(
    Output("job-form-alert", "children", allow_duplicate=True),
    [Input("activate-job-btn", "n_clicks")],
    [
        State("selected-file-path", "data"),
        State("job-name", "value"),
        State("job-description", "value"),
        State("schedule-type", "value"),
        State({"type": "schedule-input", "name": "cron-value"}, "value"),
        State({"type": "schedule-input", "name": "interval-value"}, "value"),
        State({"type": "schedule-input", "name": "interval-unit"}, "value"),
        State({"type": "schedule-input", "name": "once-value"}, "value"),
        State("job-timeout", "value"),
        State("job-retry-max", "value"),
        State("job-retry-delay", "value"),
        State("job-args", "value"),
        State("job-env", "value"),
    ],
    prevent_initial_call=True,
)
def activate_job(
    n_clicks,
    file_path,
    name,
    description,
    schedule_type,
    cron_value,
    interval_value,
    interval_unit,
    once_value,
    timeout,
    retry_max,
    retry_delay,
    args_str,
    env_str,
):
    """Create and activate job."""
    if not n_clicks:
        return dash.no_update
    
    return _create_job(
        file_path=file_path,
        name=name,
        description=description,
        schedule_type=schedule_type,
        cron_value=cron_value,
        interval_value=interval_value,
        interval_unit=interval_unit,
        once_value=once_value,
        timeout=timeout,
        retry_max=retry_max,
        retry_delay=retry_delay,
        args_str=args_str,
        env_str=env_str,
        status="active",
    )


# Helper function for job creation
def _create_job(
    file_path,
    name,
    description,
    schedule_type,
    cron_value,
    interval_value,
    interval_unit,
    once_value,
    timeout,
    retry_max,
    retry_delay,
    args_str,
    env_str,
    status,
):
    """Create job in database and optionally register with scheduler."""
    from backend.core.database import SessionLocal
    from backend.core import api
    from backend.core.schemas import JobCreate
    from backend.core.scheduler import get_scheduler
    from croniter import croniter
    
    # Validation
    if not file_path:
        return dbc.Alert("Please select a file.", color="danger", dismissable=True)
    
    if not name or not name.strip():
        return dbc.Alert("Job name is required.", color="danger", dismissable=True)
    
    if not os.path.exists(file_path):
        return dbc.Alert("Selected file does not exist.", color="danger", dismissable=True)
    
    # Build schedule_value based on schedule_type
    schedule_value = None
    
    if schedule_type == "cron":
        if not cron_value or not cron_value.strip():
            return dbc.Alert("Cron expression is required.", color="danger", dismissable=True)
        
        schedule_value = cron_value.strip()
        
        # Validate cron
        try:
            croniter(schedule_value)
        except Exception as e:
            return dbc.Alert(f"Invalid cron expression: {str(e)}", color="danger", dismissable=True)
    
    elif schedule_type == "interval":
        if not interval_value or interval_value <= 0:
            return dbc.Alert("Interval value must be greater than 0.", color="danger", dismissable=True)
        
        # Convert to seconds based on unit
        unit = interval_unit or "seconds"
        multipliers = {"seconds": 1, "minutes": 60, "hours": 3600}
        seconds = int(interval_value) * multipliers.get(unit, 1)
        
        schedule_value = str(seconds)
    
    elif schedule_type == "once":
        if not once_value:
            return dbc.Alert("Run date/time is required for one-time jobs.", color="danger", dismissable=True)
        
        # Parse datetime-local format: "YYYY-MM-DDTHH:MM"
        try:
            dt = datetime.fromisoformat(once_value)
            if dt < datetime.now():
                return dbc.Alert("One-time job must be scheduled in the future.", color="danger", dismissable=True)
            
            schedule_value = dt.isoformat()
        except ValueError as e:
            return dbc.Alert(f"Invalid date/time: {str(e)}", color="danger", dismissable=True)
    
    # Parse args and env
    args = []
    if args_str and args_str.strip():
        args = [a.strip() for a in args_str.split(",")]
    
    env = None
    if env_str and env_str.strip():
        try:
            env = json.loads(env_str)
        except json.JSONDecodeError:
            return dbc.Alert("Invalid JSON in Environment Variables.", color="danger", dismissable=True)
    
    # Create job
    session = SessionLocal()
    try:
        job_data = JobCreate(
            name=name.strip(),
            description=description.strip() if description else None,
            file_path=file_path,
            schedule_type=schedule_type,
            schedule_value=schedule_value,
            status=status,
            timeout=timeout or 300,
            retry_max=retry_max if retry_max is not None else 3,
            retry_delay=retry_delay if retry_delay is not None else 60,
            args=args,
            env=env,
        )
        
        job = api.create_job(session, job_data)
        
        # Register with scheduler if active
        if status == "active":
            scheduler = get_scheduler()
            scheduler.register_job(
                job_id=job.id,
                schedule_type=job.schedule_type,
                schedule_value=job.schedule_value,
            )
        
        status_text = "activated" if status == "active" else "saved as draft"
        
        return dbc.Alert(
            [
                html.H5(f"Job {status_text} successfully!", className="alert-heading"),
                html.P(f"Job ID: {job.id}"),
                html.P(f"Name: {job.name}"),
                html.Hr(),
                dbc.Button("View Jobs", href="/jobs", color="primary", size="sm"),
            ],
            color="success",
            dismissable=True,
        )
    
    except Exception as e:
        return dbc.Alert(f"Failed to create job: {str(e)}", color="danger", dismissable=True)
    
    finally:
        session.close()
