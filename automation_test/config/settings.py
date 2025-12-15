"""Test settings loader."""

from pathlib import Path

from automation_lib.core.config import Config


class TestSettings:
    """Manages test configuration settings."""

    def __init__(self, config_path: str = None):
        """Initialize test settings.

        Args:
            config_path: Path to settings.yaml file. If None, uses default location.
        """
        if config_path is None:
            # Default to config/settings.yaml relative to project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "settings.yaml"

        self.config = (
            Config(str(config_path)) if Path(config_path).exists() else Config()
        )

    def get(self, key: str, default=None):
        """Get configuration value by key.

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)

    @property
    def environment(self) -> str:
        """Get current environment."""
        return self.config.get("environment", "staging")

    @property
    def base_url(self) -> str:
        """Get base URL."""
        return self.config.get("base_url", "")

    @property
    def browser_type(self) -> str:
        """Get browser type."""
        return self.config.get("browser.type", "chromium")

    @property
    def headless(self) -> bool:
        """Get headless mode setting."""
        return self.config.get("browser.headless", False)

    @property
    def timeout(self) -> int:
        """Get default timeout."""
        return self.config.get("browser.timeout", 30000)

    def get_db_config(self) -> dict:
        """Get database configuration."""
        return self.config.get("db", {})

    def get_test_user(self, user_type: str = "admin") -> dict:
        """Get test user credentials.

        Args:
            user_type: Type of user (admin, regular, etc.)

        Returns:
            Dictionary with username and password
        """
        return self.config.get(f"test_users.{user_type}", {})
