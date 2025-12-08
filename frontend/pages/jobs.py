"""Jobs page - List and manage all jobs."""
import dash
from dash import html, dcc, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
from backend.core.database import SessionLocal
from backend.core import api
from frontend.components.status_badge import status_badge
from datetime import datetime

dash.register_page(__name__, path="/jobs", name="Jobs")

layout = html.Div(
    [
        html.Div(
            [
                html.H1("Jobs", className="d-inline me-3"),
                dbc.Button("+ New Job", color="primary", href="/new-job", className="float-end"),
            ],
            className="mb-4",
        ),
        
        # Search and Filters
        dbc.Row(
            [
                dbc.Col(
                    dbc.Input(
                        id="jobs-search",
                        type="text",
                        placeholder="Search jobs...",
                        className="mb-3",
                    ),
                    width=12,
                    md=8,
                ),
                dbc.Col(
                    dbc.Select(
                        id="jobs-filter",
                        options=[
                            {"label": "All Jobs", "value": "all"},
                            {"label": "Active", "value": "active"},
                            {"label": "Paused", "value": "paused"},
                            {"label": "Failed", "value": "failed"},
                        ],
                        value="all",
                        className="mb-3",
                    ),
                    width=12,
                    md=4,
                ),
            ],
        ),
        
        # Jobs Table
        html.Div(
            id="jobs-table-container",
        ),
        
        # Auto-refresh interval
        dcc.Interval(id="jobs-interval", interval=5000, n_intervals=0),
    ],
    className="container-fluid",
)


# Callbacks
@callback(
    Output("jobs-table-container", "children"),
    [
        Input("jobs-interval", "n_intervals"),
        Input("jobs-search", "value"),
        Input("jobs-filter", "value"),
    ],
)
def update_jobs_table(n, search, filter_value):
    """Update jobs table with filtering."""
    db = SessionLocal()
    try:
        # Get jobs based on filter
        if filter_value == "all":
            jobs = api.get_jobs(db)
        else:
            jobs = api.get_jobs(db, status=filter_value)
        
        if not jobs:
            return html.Div(
                [
                    html.P("No jobs found. Create your first job!", className="text-muted text-center py-5"),
                    html.Div(
                        dbc.Button("+ New Job", color="primary", href="/new-job", size="lg"),
                        className="text-center",
                    ),
                ],
            )
        
        # Apply search filter
        if search and search.strip():
            search_lower = search.lower()
            jobs = [j for j in jobs if search_lower in j.name.lower() or (j.description and search_lower in j.description.lower())]
        
        if not jobs:
            return html.Div(
                html.P(f"No jobs match your search: '{search}'", className="text-muted text-center py-5"),
            )
        
        # Build table rows
        table_rows = []
        for job in jobs:
            # Format next run
            next_run_text = "—"
            if job.next_run:
                delta = job.next_run - datetime.utcnow()
                if delta.total_seconds() < 0:
                    next_run_text = "Overdue"
                elif delta.total_seconds() < 3600:
                    next_run_text = f"in {int(delta.total_seconds() / 60)}m"
                elif delta.total_seconds() < 86400:
                    next_run_text = f"in {int(delta.total_seconds() / 3600)}h"
                else:
                    next_run_text = f"in {delta.days}d"
            
            # Format last run
            last_run_text = "Never"
            if job.last_run:
                delta = datetime.utcnow() - job.last_run
                if delta.total_seconds() < 60:
                    last_run_text = "just now"
                elif delta.total_seconds() < 3600:
                    last_run_text = f"{int(delta.total_seconds() / 60)}m ago"
                elif delta.total_seconds() < 86400:
                    last_run_text = f"{int(delta.total_seconds() / 3600)}h ago"
                else:
                    last_run_text = f"{delta.days}d ago"
            
            table_rows.append(
                html.Tr(
                    [
                        html.Td(
                            html.Div(
                                [
                                    status_badge(job.status),
                                ],
                                className="d-flex align-items-center",
                            ),
                        ),
                        html.Td(
                            html.Div(
                                [
                                    html.Strong(job.name),
                                    html.Br(),
                                    html.Small(job.description or "—", className="text-muted"),
                                ],
                            ),
                        ),
                        html.Td(job.schedule_type.upper()),
                        html.Td(next_run_text),
                        html.Td(last_run_text),
                        html.Td(
                            html.Div(
                                [
                                    dbc.Button(
                                        "⏸" if job.status == "active" else "▶",
                                        id={"type": "job-toggle", "id": job.id},
                                        color="warning" if job.status == "active" else "success",
                                        size="sm",
                                        className="me-1",
                                        outline=True,
                                        title="Pause" if job.status == "active" else "Resume",
                                    ),
                                    dbc.Button(
                                        "▶",
                                        id={"type": "job-run-now", "id": job.id},
                                        color="primary",
                                        size="sm",
                                        className="me-1",
                                        outline=True,
                                        title="Run Now",
                                    ),
                                    dbc.Button(
                                        "📋",
                                        id={"type": "job-view-logs", "id": job.id},
                                        color="secondary",
                                        size="sm",
                                        className="me-1",
                                        outline=True,
                                        title="View Logs",
                                    ),
                                    dbc.Button(
                                        "🗑",
                                        id={"type": "job-delete", "id": job.id},
                                        color="danger",
                                        size="sm",
                                        outline=True,
                                        title="Delete",
                                    ),
                                ],
                                className="d-flex gap-1",
                            ),
                        ),
                    ],
                )
            )
        
        table = dbc.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Status", style={"width": "100px"}),
                            html.Th("Job"),
                            html.Th("Type", style={"width": "100px"}),
                            html.Th("Next Run", style={"width": "120px"}),
                            html.Th("Last Run", style={"width": "120px"}),
                            html.Th("Actions", style={"width": "200px"}),
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
                html.P(f"Showing {len(jobs)} job(s)", className="text-muted mb-2"),
                table,
            ],
        )
    
    finally:
        db.close()
