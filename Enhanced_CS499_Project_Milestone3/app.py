"""Application entry point for the enhanced CS 340 dashboard."""

from dash import Dash

from animal_service import AnimalService
from callbacks import register_callbacks
from config import AppConfig
from database import AnimalShelter, DatabaseOperationError
from layout import build_layout


def create_app(config=None):
    """Create and configure the dashboard application."""
    app_config = config or AppConfig.from_env()

    database = AnimalShelter(app_config)
    animal_service = AnimalService(database)

    try:
        initial_data, initial_columns = animal_service.get_table_data(
            "WATER", "RANKED"
        )
    except DatabaseOperationError:
        initial_data, initial_columns = [], []

    app = Dash(__name__)
    app.title = app_config.app_title
    app.layout = build_layout(
        app_title=app_config.app_title,
        logo_path=app_config.logo_path,
        initial_data=initial_data,
        initial_columns=initial_columns,
    )
    register_callbacks(app, animal_service)

    return app


def main():
    """Load configuration and start the Dash server."""
    config = AppConfig.from_env()
    app = create_app(config)
    app.run(
        host=config.app_host,
        port=config.app_port,
    )


if __name__ == "__main__":
    main()
