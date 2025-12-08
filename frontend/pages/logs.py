"""Logs page - View execution history and logs."""
import dash
from dash import html, dcc, callback, Input, Output, State, ALL, MATCH
import dash_bootstrap_components as dbc
from datetime import datetime
import json
from backend.core.database import SessionLocal
from backend.core import api
from frontend.components.status_badge import status_badge

dash.register_page(__name__, path="/logs", name="Logs")

layout = html.Div(
    [
        html.H1("Execution Logs", className="mb-4"),
        
        # Filters
        dbc.Row(
            [
                dbc.Col(
                    dbc.Select(
                        id="logs-job-filter",
                        options=[{"label": "All Jobs", "value": "all"}],
                        value="all",
                        className="mb-3",
                    ),
                    width=12,
                    md=3,
                ),
                dbc.Col(
                    dbc.Select(
                        id="logs-status-filter",
                        options=[
                            {"label": "All Status", "value": "all"},
                            {"label": "Success", "value": "success"},
                            {"label": "Failed", "value": "failed"},
                            {"label": "Running", "value": "running"},
                        ],
                        value="all",
                        className="mb-3",
                    ),
                    width=12,
                    md=3,
                ),
                dbc.Col(
                    dbc.Input(
                        id="logs-search",
                        type="text",
                        placeholder="Search logs...",
                        className="mb-3",
                    ),
                    width=12,
                    md=4,
                ),
                dbc.Col(
                    dbc.Button("Export CSV", id="logs-export-btn", color="secondary", outline=True, className="w-100"),
                    width=12,
                    md=2,
                ),
            ],
        ),
        
        # Download component for export
        dcc.Download(id="logs-download"),
        
        # Logs Table
        html.Div(
            id="logs-table-container",
        ),
        
        # Auto-refresh toggle
        html.Div(
            [
                dbc.Checkbox(
                    id="logs-auto-refresh",
                    label="Auto-refresh (5s)",
                    value=False,
                    className="mt-3",
                ),
            ],
        ),
        
        dcc.Interval(id="logs-interval", interval=5000, n_intervals=0, disabled=True),
    ],
    className="container-fluid",
)


# Callbacks

@callback(
    Output("logs-interval", "disabled"),
    Input("logs-auto-refresh", "value"),
)
def toggle_auto_refresh(auto_refresh):
    """Enable/disable auto-refresh."""
    return not auto_refresh


@callback(
    Output("logs-job-filter", "options"),
    Input("logs-interval", "n_intervals"),
)
def update_job_filter_options(n):
    """Populate job filter dropdown with available jobs."""
    db = SessionLocal()
    try:
        jobs = api.get_jobs(db)
        options = [{"label": "All Jobs", "value": "all"}]
        for job in jobs:
            options.append({"label": job.name, "value": job.id})
        return options
    finally:
        db.close()


@callback(
    Output("logs-table-container", "children"),
    [
        Input("logs-interval", "n_intervals"),
        Input("logs-job-filter", "value"),
        Input("logs-status-filter", "value"),
        Input("logs-search", "value"),
    ],
)
def update_logs_table(n, job_filter, status_filter, search):
    """Update execution logs table."""
    db = SessionLocal()
    try:
        # Get executions with filters
        job_id = None if job_filter == "all" else job_filter
        status = None if status_filter == "all" else status_filter
        
        executions = api.get_executions(db, job_id=job_id, status=status, limit=100)
        
        if not executions:
            return html.Div(
                html.P("No execution logs found.", className="text-muted text-center py-5"),
            )
        
        # Apply search filter
        if search and search.strip():
            search_lower = search.lower()
            executions = [
                e for e in executions 
                if (e.output and search_lower in e.output.lower()) or 
                   (e.job and search_lower in e.job.name.lower())
            ]
        
        if not executions:
            return html.Div(
                html.P(f"No logs match your search: '{search}'", className="text-muted text-center py-5"),
            )
        
        # Build table rows
        table_rows = []
        for exe in executions:
            # Format duration
            duration_text = f"{exe.duration:.2f}s" if exe.duration else "—"
            
            # Format timestamp
            timestamp = exe.started_at.strftime("%Y-%m-%d %H:%M:%S") if exe.started_at else "—"
            
            # Job name
            job_name = exe.job.name if exe.job else "Unknown"
            
            # Output preview (first 100 chars)
            output_preview = ""
            if exe.output:
                output_preview = exe.output[:100] + "..." if len(exe.output) > 100 else exe.output
            
            # Expandable row
            row_id = f"log-row-{exe.id}"
            
            table_rows.append(
                html.Tr(
                    [
                        html.Td(timestamp, style={"fontSize": "0.9rem"}),
                        html.Td(job_name),
                        html.Td(status_badge(exe.status)),
                        html.Td(duration_text),
                        html.Td(
                            html.Div(
                                [
                                    html.Span(output_preview, className="text-muted small"),
                                    html.Br() if output_preview else None,
                                    dbc.Button(
                                        "▼ Show Output",
                                        id={"type": "log-toggle", "id": exe.id},
                                        color="link",
                                        size="sm",
                                        className="p-0 mt-1",
                                    ) if exe.output else None,
                                ],
                            ),
                        ),
                    ],
                    id={"type": "log-row", "id": exe.id},
                )
            )
            
            # Expandable output row (hidden by default)
            if exe.output:
                table_rows.append(
                    html.Tr(
                        [
                            html.Td(
                                html.Div(
                                    [
                                        html.H6("Full Output:", className="mb-2"),
                                        html.Pre(
                                            exe.output,
                                            className="code-preview",
                                            style={"maxHeight": "300px", "overflowY": "auto"},
                                        ),
                                    ],
                                    className="p-3",
                                ),
                                colSpan=5,
                            ),
                        ],
                        id={"type": "log-output", "id": exe.id},
                        style={"display": "none"},
                    )
                )
        
        table = dbc.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Timestamp", style={"width": "180px"}),
                            html.Th("Job", style={"width": "200px"}),
                            html.Th("Status", style={"width": "100px"}),
                            html.Th("Duration", style={"width": "100px"}),
                            html.Th("Output"),
                        ],
                    ),
                ),
                html.Tbody(table_rows),
            ],
            bordered=True,
            hover=True,
            responsive=True,
            className="mt-3",
        )
        
        return html.Div(
            [
                html.P(f"Showing {len(executions)} execution(s)", className="text-muted mb-2"),
                table,
            ],
        )
    
    finally:
        db.close()


@callback(
    [
        Output({"type": "log-output", "id": MATCH}, "style"),
        Output({"type": "log-toggle", "id": MATCH}, "children"),
    ],
    Input({"type": "log-toggle", "id": MATCH}, "n_clicks"),
    State({"type": "log-output", "id": MATCH}, "style"),
    prevent_initial_call=True,
)
def toggle_log_output(n_clicks, current_style):
    """Toggle log output visibility."""
    if not n_clicks:
        return dash.no_update, dash.no_update
    
    is_hidden = current_style.get("display") == "none"
    new_style = {"display": "table-row"} if is_hidden else {"display": "none"}
    new_text = "▲ Hide Output" if is_hidden else "▼ Show Output"
    
    return new_style, new_text


@callback(
    Output("logs-download", "data"),
    Input("logs-export-btn", "n_clicks"),
    [
        State("logs-job-filter", "value"),
        State("logs-status-filter", "value"),
    ],
    prevent_initial_call=True,
)
def export_logs(n_clicks, job_filter, status_filter):
    """Export logs to CSV."""
    if not n_clicks:
        return dash.no_update
    
    db = SessionLocal()
    try:
        # Get executions with filters
        job_id = None if job_filter == "all" else job_filter
        status = None if status_filter == "all" else status_filter
        
        executions = api.get_executions(db, job_id=job_id, status=status, limit=1000)
        
        if not executions:
            return dash.no_update
        
        # Build CSV content
        csv_lines = ["Timestamp,Job,Status,Duration (s),Exit Code,Output"]
        for exe in executions:
            timestamp = exe.started_at.strftime("%Y-%m-%d %H:%M:%S") if exe.started_at else ""
            job_name = exe.job.name if exe.job else "Unknown"
            duration = f"{exe.duration:.2f}" if exe.duration else ""
            exit_code = str(exe.exit_code) if exe.exit_code is not None else ""
            output = (exe.output or "").replace('"', '""')  # Escape quotes
            
            csv_lines.append(f'"{timestamp}","{job_name}","{exe.status}","{duration}","{exit_code}","{output}"')
        
        csv_content = "\n".join(csv_lines)
        
        return dict(
            content=csv_content,
            filename=f"execution_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        )
    
    finally:
        db.close()

