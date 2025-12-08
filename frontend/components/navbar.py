"""Navigation bar component."""
from dash import html, dcc
import dash_bootstrap_components as dbc


def create_navbar():
    """Create the top navigation bar."""
    return dbc.Navbar(
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.A(
                                dbc.Row(
                                    [
                                        dbc.Col(html.I(className="bi bi-clock-history me-2", style={"fontSize": "1.5rem"})),
                                        dbc.Col(dbc.NavbarBrand("Open Scheduler", className="ms-2")),
                                    ],
                                    align="center",
                                    className="g-0",
                                ),
                                href="/",
                                style={"textDecoration": "none"},
                            ),
                        ),
                    ],
                    align="center",
                    className="flex-grow-1",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Nav(
                                [
                                    dbc.NavLink("Overview", href="/", active="exact", className="px-3"),
                                    dbc.NavLink("Jobs", href="/jobs", active="exact", className="px-3"),
                                    dbc.NavLink("New Job", href="/new-job", active="exact", className="px-3"),
                                    dbc.NavLink("Logs", href="/logs", active="exact", className="px-3"),
                                    dbc.NavLink("Settings", href="/settings", active="exact", className="px-3"),
                                ],
                                navbar=True,
                                className="ms-auto",
                            ),
                        ),
                    ],
                    align="center",
                ),
            ],
            fluid=True,
        ),
        color="dark",
        dark=True,
        className="mb-4",
        sticky="top",
    )
