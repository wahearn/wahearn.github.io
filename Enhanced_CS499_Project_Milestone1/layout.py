"""Dashboard layout and user-interface components."""

import base64
from pathlib import Path

from dash import dash_table, dcc, html


FILTER_OPTIONS = [
    {"label": "Water Rescue", "value": "WATER"},
    {"label": "Mountain Rescue", "value": "MOUNTAIN"},
    {"label": "Disaster Rescue", "value": "DISASTER"},
    {"label": "Reset", "value": "RESET"},
]


def _build_logo(logo_path: str):
    """Return the configured logo or a text fallback if the file is absent."""
    path = Path(logo_path)
    if not path.is_file():
        return html.Div(
            "Grazioso Salvare",
            style={"textAlign": "center", "fontWeight": "bold", "fontSize": "24px"},
        )

    encoded_image = base64.b64encode(path.read_bytes()).decode("utf-8")
    return html.Img(
        id="logo",
        src=f"data:image/png;base64,{encoded_image}",
        style={
            "height": "100px",
            "display": "block",
            "marginLeft": "auto",
            "marginRight": "auto",
        },
    )


def build_layout(
    app_title: str,
    logo_path: str,
    initial_data,
    initial_columns,
):
    """Build the complete Dash application layout."""
    return html.Div(
        [
            _build_logo(logo_path),
            html.H1(app_title, style={"textAlign": "center"}),
            html.Hr(),
            html.Div(
                [
                    html.Label("Select Rescue Type:"),
                    dcc.RadioItems(
                        id="filter-type",
                        options=FILTER_OPTIONS,
                        value="WATER",
                        labelStyle={"display": "inline-block", "marginRight": "18px"},
                    ),
                ]
            ),
            html.Div(
                id="status-message",
                role="status",
                style={"marginTop": "10px", "minHeight": "24px"},
            ),
            html.Hr(),
            dash_table.DataTable(
                id="datatable-id",
                columns=initial_columns,
                data=initial_data,
                row_selectable="single",
                selected_rows=[0] if initial_data else [],
                page_size=10,
                style_table={"overflowX": "auto"},
            ),
            html.Br(),
            html.Hr(),
            html.Div(
                className="row",
                style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
                children=[
                    html.Div(
                        id="graph-id",
                        className="col s12 m6",
                        style={"flex": "1", "minWidth": "320px"},
                    ),
                    html.Div(
                        id="map-id",
                        className="col s12 m6",
                        style={"flex": "1", "minWidth": "320px"},
                    ),
                ],
            ),
        ],
        style={"padding": "20px"},
    )
