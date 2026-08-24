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

SEARCH_MODE_OPTIONS = [
    {"label": "Ranked recommendations", "value": "RANKED"},
    {"label": "Exact matches", "value": "EXACT"},
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
                ],
                style={"marginBottom": "12px"},
            ),
            html.Div(
                [
                    html.Label("Search Method:"),
                    dcc.RadioItems(
                        id="search-mode",
                        options=SEARCH_MODE_OPTIONS,
                        value="RANKED",
                        labelStyle={"display": "inline-block", "marginRight": "18px"},
                    ),
                    html.Small(
                        "Ranked recommendations score breed (+5), age under 8 "
                        "weeks (+0.5), 8 weeks to 6 months (+2.5), 6 months to 2 "
                        "years (+2.4), or 3 through 6 years (+0.10), sex "
                        "(+2.25). Other ages receive no age points. Dogs age 7 or "
                        "older receive a -2.2 penalty, with a minimum total score "
                        "of 0.",
                        style={"display": "block", "marginTop": "5px"},
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
                page_size=15,
                sort_action="native",
                filter_action="native",
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
