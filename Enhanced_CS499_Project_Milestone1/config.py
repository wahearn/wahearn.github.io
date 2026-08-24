"""Application configuration loaded from environment variables."""

from dataclasses import dataclass
import os
from typing import Optional


@dataclass(frozen=True)
class AppConfig:
    """Settings used by the dashboard and MongoDB connection."""

    mongo_username: str
    mongo_password: str
    mongo_host: str = "localhost"
    mongo_port: int = 27017
    mongo_database: str = "aac"
    mongo_collection: str = "animals"
    mongo_auth_source: Optional[str] = None
    server_selection_timeout_ms: int = 5000

    app_title: str = "Ahearn CS-340 Dashboard"
    logo_path: str = "GraziosoSalvareLogo.png"
    app_host: str = "127.0.0.1"
    app_port: int = 8050

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration without storing the password in source code."""
        password = os.getenv("MONGO_PASSWORD", "").strip()
        if not password:
            raise ValueError(
                "MONGO_PASSWORD is required. Set it before starting the dashboard."
            )

        auth_source = os.getenv("MONGO_AUTH_SOURCE", "").strip() or None

        return cls(
            mongo_username=os.getenv("MONGO_USERNAME", "aacuser").strip(),
            mongo_password=password,
            mongo_host=os.getenv("MONGO_HOST", "localhost").strip(),
            mongo_port=int(os.getenv("MONGO_PORT", "27017")),
            mongo_database=os.getenv("MONGO_DATABASE", "aac").strip(),
            mongo_collection=os.getenv("MONGO_COLLECTION", "animals").strip(),
            mongo_auth_source=auth_source,
            server_selection_timeout_ms=int(
                os.getenv("MONGO_TIMEOUT_MS", "5000")
            ),
            app_title=os.getenv("APP_TITLE", "Ahearn CS-340 Dashboard").strip(),
            logo_path=os.getenv("APP_LOGO_PATH", "GraziosoSalvareLogo.png").strip(),
            app_host=os.getenv("APP_HOST", "127.0.0.1").strip(),
            app_port=int(os.getenv("APP_PORT", "8050")),
        )
