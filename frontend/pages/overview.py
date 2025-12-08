"""Overview/Dashboard page - Shows active jobs and KPIs."""
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from datetime import datetime, timedelta
from backend.core.database import SessionLocal
from backend.core import api
from frontend.components.job_card import job_card

dash.register_page(__name__, path="/", name="Overview")

layout = html.Div(
    [
        html.H1("Overview", className="mb-4"),
        
        # KPI Cards Row
        dbc.Row(
            id="kpi-cards-row",
            className="mb-4",
        ),
        
        # Active Jobs Section
        html.H3("Active Jobs", className="mb-3"),
        html.Div(
            id="active-jobs-container",
        ),
        
        # Recent Activity Chart
        html.H3("Recent Activity", className="mt-5 mb-3"),
        dcc.Graph(
            id="activity-chart",
            config={"displayModeBar": False},
            style={"height": "300px"},
        ),
        
        # Auto-refresh interval (5 seconds)
        dcc.Interval(id="overview-interval", interval=5000, n_intervals=0),
    ],
    className="container-fluid",
)


@callback(
    Output("kpi-cards-row", "children"),
    Input("overview-interval", "n_intervals"),
)
def update_kpi_cards(n):
    """Update KPI cards with real data."""
    db = SessionLocal()
    try:
        stats = api.get_stats(db)
        
        return [
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Div(str(stats["total_jobs"]), className="kpi-value"),
                            html.Div("Total Jobs", className="kpi-label"),
                        ],
                        className="kpi-card",
                    ),
                ),
                width=12,
                md=3,
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Div(str(stats["active_jobs"]), className="kpi-value text-success"),
                            html.Div("Active", className="kpi-label"),
                        ],
                        className="kpi-card",
                    ),
                ),
                width=12,
                md=3,
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Div(f"{stats['success_rate']}%", className="kpi-value text-info"),
                            html.Div("Success Rate", className="kpi-label"),
                        ],
                        className="kpi-card",
                    ),
                ),
                width=12,
                md=3,
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Div(str(stats["failed_today"]), className="kpi-value text-danger"),
                            html.Div("Failed Today", className="kpi-label"),
                        ],
                        className="kpi-card",
                    ),
                ),
                width=12,
                md=3,
            ),
        ]
    finally:
        db.close()


@callback(
    Output("active-jobs-container", "children"),
    Input("overview-interval", "n_intervals"),
)
def update_active_jobs(n):
    """Update active jobs list."""
    db = SessionLocal()
    try:
        jobs = api.get_jobs(db, status="active")
        
        if not jobs:
            return html.Div(
                [
                    html.P("No active jobs yet. Create your first job!", className="text-muted text-center py-5"),
                    html.Div(
                        dbc.Button("+ New Job", color="primary", href="/new-job", size="lg"),
                        className="text-center",
                    ),
                ],
            )
        
        # Create job cards
        job_cards = []
        for job in jobs[:10]:  # Show top 10
            job_dict = {
                "id": job.id,
                "name": job.name,
                "description": job.description or "",
                "status": job.status,
                "last_status": job.last_status,
                "next_run": job.next_run,
                "last_run": job.last_run,
                "schedule_value": job.schedule_value,
            }
            job_cards.append(dbc.Col(job_card(job_dict), width=12, md=6, lg=4))
        
        return dbc.Row(job_cards)
    finally:
        db.close()


@callback(
    Output("activity-chart", "figure"),
    Input("overview-interval", "n_intervals"),
)
def update_activity_chart(n):
    """Update recent activity chart."""
    db = SessionLocal()
    try:
        # Get executions from last 24 hours
        executions = api.get_executions(db, limit=100)
        
        if not executions:
            # Empty chart
            fig = go.Figure()
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                annotations=[
                    dict(
                        text="No execution data yet",
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        y=0.5,
                        showarrow=False,
                        font=dict(size=16, color="#8B949E"),
                    )
                ],
            )
            return fig
        
        # Group by hour and status
        now = datetime.utcnow()
        hours = [(now - timedelta(hours=i)) for i in range(24)]
        hours.reverse()
        
        success_counts = []
        failed_counts = []
        
        for hour in hours:
            hour_start = hour.replace(minute=0, second=0, microsecond=0)
            hour_end = hour_start + timedelta(hours=1)
            
            success = sum(1 for e in executions if hour_start <= e.started_at < hour_end and e.status == "success")
            failed = sum(1 for e in executions if hour_start <= e.started_at < hour_end and e.status in ("failed", "timeout"))
            
            success_counts.append(success)
            failed_counts.append(failed)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=[h.strftime("%H:00") for h in hours],
            y=success_counts,
            name="Success",
            marker_color="#3FB950",
        ))
        
        fig.add_trace(go.Bar(
            x=[h.strftime("%H:00") for h in hours],
            y=failed_counts,
            name="Failed",
            marker_color="#F85149",
        ))
        
        fig.update_layout(
            barmode="stack",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, title="Hour"),
            yaxis=dict(showgrid=True, gridcolor="#30363D", title="Executions"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=40, b=40),
        )
        
        return fig
    finally:
        db.close()
