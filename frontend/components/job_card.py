"""Job card component for displaying job info visually."""
from dash import html, dcc
import dash_bootstrap_components as dbc
from frontend.components.status_badge import status_indicator, status_badge
from datetime import datetime, timedelta


def format_time_ago(dt: datetime) -> str:
    """Format datetime as 'X minutes/hours/days ago'."""
    if dt is None:
        return "Never"
    
    now = datetime.utcnow()
    delta = now - dt
    
    if delta < timedelta(minutes=1):
        return "just now"
    elif delta < timedelta(hours=1):
        minutes = int(delta.total_seconds() / 60)
        return f"{minutes}m ago"
    elif delta < timedelta(days=1):
        hours = int(delta.total_seconds() / 3600)
        return f"{hours}h ago"
    else:
        days = delta.days
        return f"{days}d ago"


def format_time_until(dt: datetime) -> str:
    """Format datetime as 'in X minutes/hours/days'."""
    if dt is None:
        return "Not scheduled"
    
    now = datetime.utcnow()
    delta = dt - now
    
    if delta < timedelta(0):
        return "overdue"
    elif delta < timedelta(minutes=1):
        return "in <1m"
    elif delta < timedelta(hours=1):
        minutes = int(delta.total_seconds() / 60)
        return f"in {minutes}m"
    elif delta < timedelta(days=1):
        hours = int(delta.total_seconds() / 3600)
        return f"in {hours}h"
    else:
        days = delta.days
        return f"in {days}d"


def job_card(job: dict) -> dbc.Card:
    """
    Create a visual card for a job.
    
    Args:
        job: Dict with keys: id, name, description, status, last_status,
             next_run (datetime), last_run (datetime), schedule_value
    
    Returns:
        dbc.Card component
    """
    # Determine overall status for indicator
    if job.get("status") == "paused":
        indicator_status = "paused"
    elif job.get("last_status") == "failed":
        indicator_status = "failed"
    elif job.get("last_status") == "success":
        indicator_status = "success"
    else:
        indicator_status = "active"
    
    # Format times
    next_run_text = format_time_until(job.get("next_run")) if job.get("next_run") else "—"
    last_run_text = format_time_ago(job.get("last_run")) if job.get("last_run") else "Never"
    last_status = job.get("last_status") or "—"
    last_status_text = last_status.capitalize() if isinstance(last_status, str) else "—"
    
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                status_indicator(indicator_status, size="md"),
                                html.H5(job.get("name", "Unnamed Job"), className="d-inline mb-0"),
                            ],
                            className="d-flex align-items-center mb-2",
                        ),
                        html.P(
                            job.get("description") or job.get("schedule_value", "No description"),
                            className="text-muted small mb-3",
                        ),
                    ],
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Strong("Next: "),
                                html.Span(next_run_text, className="text-info"),
                            ],
                            className="mb-1",
                        ),
                        html.Div(
                            [
                                html.Strong("Last: "),
                                html.Span(f"{last_status_text} ({last_run_text})", 
                                         className=f"text-{'success' if last_status_text.lower() == 'success' else 'danger' if last_status_text.lower() == 'failed' else 'muted'}"),
                            ],
                            className="mb-3",
                        ),
                    ],
                    className="small",
                ),
                html.Div(
                    [
                        dbc.Button(
                            "⏸ Pause" if job.get("status") == "active" else "▶ Resume",
                            id={"type": "job-action", "action": "pause" if job.get("status") == "active" else "resume", "job_id": job.get("id")},
                            color="warning" if job.get("status") == "active" else "success",
                            size="sm",
                            className="me-2",
                            outline=True,
                        ),
                        dbc.Button(
                            "▶ Run Now",
                            id={"type": "job-action", "action": "run-now", "job_id": job.get("id")},
                            color="primary",
                            size="sm",
                            className="me-2",
                            outline=True,
                        ),
                        dbc.Button(
                            "📋 Logs",
                            id={"type": "job-action", "action": "view-logs", "job_id": job.get("id")},
                            color="secondary",
                            size="sm",
                            outline=True,
                        ),
                    ],
                    className="d-flex gap-2",
                ),
            ],
        ),
        className="job-card mb-3",
    )
