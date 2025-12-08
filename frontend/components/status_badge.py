"""Status badge component with colored indicators."""
from dash import html
import dash_bootstrap_components as dbc


def status_badge(status: str, text: str = None) -> html.Span:
    """
    Create a status badge with colored indicator.
    
    Args:
        status: 'success', 'failed', 'paused', 'running', 'active', 'disabled'
        text: Optional custom text (default: status.capitalize())
    
    Returns:
        html.Span with badge
    """
    if text is None:
        text = status.capitalize()
    
    # Color mapping
    color_map = {
        "success": "success",
        "failed": "danger",
        "paused": "warning",
        "running": "info",
        "active": "success",
        "disabled": "secondary",
        "timeout": "danger",
    }
    
    # Icon mapping
    icon_map = {
        "success": "✓",
        "failed": "✗",
        "paused": "⏸",
        "running": "▶",
        "active": "●",
        "disabled": "○",
        "timeout": "⏱",
    }
    
    color = color_map.get(status.lower(), "secondary")
    icon = icon_map.get(status.lower(), "•")
    
    return dbc.Badge(
        [icon, " ", text],
        color=color,
        className="status-badge",
        pill=True,
    )


def status_indicator(status: str, size: str = "md") -> html.Span:
    """
    Create a simple status indicator dot (●).
    
    Args:
        status: 'success', 'failed', 'paused', 'running'
        size: 'sm', 'md', 'lg'
    
    Returns:
        html.Span with colored dot
    """
    color_map = {
        "success": "#3FB950",
        "failed": "#F85149",
        "paused": "#D29922",
        "running": "#1F6FEB",
        "active": "#3FB950",
    }
    
    size_map = {
        "sm": "8px",
        "md": "12px",
        "lg": "16px",
    }
    
    color = color_map.get(status.lower(), "#8B949E")
    dot_size = size_map.get(size, "12px")
    
    return html.Span(
        "●",
        style={
            "color": color,
            "fontSize": dot_size,
            "marginRight": "8px",
            "lineHeight": "1",
        },
        title=status.capitalize(),
    )
