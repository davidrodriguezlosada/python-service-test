import sys
from pathlib import Path
import tomllib

from pydantic_settings import BaseSettings

# Add project root to Python path for pyproject.toml access
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def get_project_info():
    """Read project info from pyproject.toml"""
    pyproject_path = project_root / "pyproject.toml"

    if pyproject_path.exists():
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            project_data = data.get("project", {})
            return {
                "name": project_data.get("name", "python-service-test"),
                "version": project_data.get("version", "1.0.0")
            }
    return {"name": "python-service-test", "version": "1.0.0"}


class Settings(BaseSettings):
    # API Settings
    app_name: str = ""
    app_version: str = ""
    debug: bool = False

    # Kafka Settings
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic: str = "test-topic"
    kafka_consumer_group: str = "test-group"

    # Datadog Settings
    dd_service: str = "python-service-test"
    dd_env: str = "development"
    dd_version: str = ""
    dd_api_key: str = ""
    dd_enabled: bool = False  # Disable traces by default

    # Logging Settings
    log_level: str = "INFO"
    log_format: str = "xml"  # xml, json, ecs, or text

    # Tags for ECS logging
    tags_env: str = "dev"
    tags_application: str = ""
    tags_solution: str = "polaris"
    tags_service: str = ""
    tags_domain: str = "ecommerce"
    tags_version: str = ""
    tags_trace: bool = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set name and version from pyproject.toml if not provided
        project_info = get_project_info()
        if not self.app_name:
            self.app_name = project_info["name"]
        if not self.app_version:
            self.app_version = project_info["version"]
        if not self.tags_version:
            self.tags_version = project_info["version"]
        if not self.tags_application:
            self.tags_application = project_info["name"]
        if not self.tags_service:
            self.tags_service = project_info["name"]

    class Config:
        env_file = ".env"


settings = Settings()
