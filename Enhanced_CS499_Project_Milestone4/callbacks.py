"""Dash callbacks that respond to user interactions."""

import dash_leaflet as dl
from dash import dcc, html, no_update
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

from database import DatabaseOperationError
from validators import ValidationError


def register_callbacks(app, animal_service):
    """Register all dashboard callbacks on the supplied Dash app."""

    @app.callback(
        Output("datatable-id", "data"),
        Output("datatable-id", "columns"),
        Output("datatable-id", "selected_rows"),
        Output("status-message", "children"),
        Input("filter-type", "value"),
        Input("search-mode", "value"),
    )
    def update_dashboard(filter_type: str, search_mode: str):
        try:
            data, columns = animal_service.get_table_data(filter_type, search_mode)
            selected_rows = [0] if data else []
            if search_mode == "RANKED" and filter_type != "RESET":
                message = (
                    f"Displaying {len(data)} rescue candidate(s), ranked by match score."
                )
            else:
                message = f"Displaying {len(data)} exact matching animal record(s)."
            return data, columns, selected_rows, message
        except ValidationError as exc:
            return no_update, no_update, no_update, str(exc)
        except DatabaseOperationError:
            return (
                no_update,
                no_update,
                no_update,
                "Animal records could not be loaded.",
            )

    @app.callback(
        Output("graph-id", "children"),
        Input("datatable-id", "derived_virtual_data"),
    )
    def update_graph(view_data):
        if not view_data:
            return html.P("No animal data is available for the chart.")

        frame = pd.DataFrame.from_records(view_data)
        if "breed" not in frame.columns:
            return html.P("Breed data is unavailable.")

        return dcc.Graph(
            figure=px.pie(frame, names="breed", title="Preferred Animals")
        )

    @app.callback(
        Output("datatable-id", "style_data_conditional"),
        Input("datatable-id", "selected_columns"),
    )
    def update_styles(selected_columns):
        if not selected_columns:
            return []

        styles = []
        for column_id in selected_columns:
            style = {
                "if": {"column_id": column_id},
                "background_color": "#D2F3FF",
            }
            styles.append(style)
        return styles

    @app.callback(
        Output("map-id", "children"),
        Input("datatable-id", "derived_virtual_data"),
        Input("datatable-id", "derived_virtual_selected_rows"),
    )
    def update_map(view_data, selected_rows):
        if not view_data:
            return html.P("No animal location is available.")

        row_index = selected_rows[0] if selected_rows else 0
        if row_index < 0 or row_index >= len(view_data):
            row_index = 0

        record = view_data[row_index]
        latitude = _to_float(record.get("location_lat"))
        longitude = _to_float(record.get("location_long"))

        if latitude is None or longitude is None:
            return html.P("The selected animal does not have a valid location.")

        animal_name = record.get("name") or "Unnamed animal"
        breed = record.get("breed") or "Unknown breed"

        return dl.Map(
            style={"width": "100%", "height": "500px"},
            center=[latitude, longitude],
            zoom=10,
            children=[
                dl.TileLayer(id="base-layer-id"),
                dl.Marker(
                    position=[latitude, longitude],
                    children=[
                        dl.Tooltip(str(breed)),
                        dl.Popup([html.H3("Animal Name"), html.P(str(animal_name))]),
                    ],
                ),
            ],
        )


def _to_float(value):
    """Convert a location value to float without raising a UI error."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
