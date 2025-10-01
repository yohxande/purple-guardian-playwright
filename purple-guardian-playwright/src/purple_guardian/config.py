"""
💜 Configuration management for Purple Guardian
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import os


@dataclass
class PurpleConfig:
    """
    💜 Purple Guardian configuration class
    
    Centralized configuration management for all Purple Guardian settings.
    """
    
    # Browser settings
    headless: bool = True
    browser_args: list = field(default_factory=lambda: [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions"
    ])
    user_agent: Optional[str] = None
    viewport: Dict[str, int] = field(default_factory=lambda: {"width": 1920, "height": 1080})
    
    # Timeout settings
    default_timeout: int = 30000  # 30 seconds
    page_load_timeout: int = 60000  # 60 seconds
    element_timeout: int = 10000  # 10 seconds
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True
    
    # Monitoring settings
    enable_strict_monitoring: bool = True
    enable_dom_monitoring: bool = True
    enable_network_monitoring: bool = True
    enable_console_monitoring: bool = True
    
    # Detection settings
    enable_violation_detection: bool = True
    detect_unexpected_elements: bool = True
    detect_prohibited_texts: bool = True
    detect_missing_elements: bool = True
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "💜 %(asctime)s [%(levelname)s] %(name)s: %(message)s"
    enable_rich_logging: bool = True
    
    # Screenshots and debugging
    screenshot_on_violation: bool = True
    screenshot_path: str = "./screenshots"
    save_page_source_on_violation: bool = False
    page_source_path: str = "./page_sources"
    
    # Performance settings
    concurrent_limit: int = 5
    memory_limit_mb: int = 512
    cpu_limit_percent: int = 80
    
    # Custom settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization validation and setup"""
        self._validate_config()
        self._setup_directories()

    def _validate_config(self):
        """Validate configuration values"""
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        
        if self.retry_delay < 0:
            raise ValueError("retry_delay must be >= 0")
        
        if self.default_timeout < 1000:
            raise ValueError("default_timeout must be >= 1000ms")
        
        if not isinstance(self.viewport, dict) or "width" not in self.viewport or "height" not in self.viewport:
            raise ValueError("viewport must be a dict with 'width' and 'height' keys")
        
        if self.viewport["width"] < 100 or self.viewport["height"] < 100:
            raise ValueError("viewport dimensions must be >= 100px")

    def _setup_directories(self):
        """Setup required directories"""
        if self.screenshot_on_violation:
            os.makedirs(self.screenshot_path, exist_ok=True)
        
        if self.save_page_source_on_violation:
            os.makedirs(self.page_source_path, exist_ok=True)

    @classmethod
    def from_env(cls) -> "PurpleConfig":
        """Create configuration from environment variables"""
        config = cls()
        
        # Browser settings
        if os.getenv("PURPLE_HEADLESS"):
            config.headless = os.getenv("PURPLE_HEADLESS").lower() == "true"
        
        if os.getenv("PURPLE_USER_AGENT"):
            config.user_agent = os.getenv("PURPLE_USER_AGENT")
        
        # Timeout settings
        if os.getenv("PURPLE_DEFAULT_TIMEOUT"):
            config.default_timeout = int(os.getenv("PURPLE_DEFAULT_TIMEOUT"))
        
        if os.getenv("PURPLE_PAGE_LOAD_TIMEOUT"):
            config.page_load_timeout = int(os.getenv("PURPLE_PAGE_LOAD_TIMEOUT"))
        
        # Retry settings
        if os.getenv("PURPLE_MAX_RETRIES"):
            config.max_retries = int(os.getenv("PURPLE_MAX_RETRIES"))
        
        if os.getenv("PURPLE_RETRY_DELAY"):
            config.retry_delay = float(os.getenv("PURPLE_RETRY_DELAY"))
        
        # Monitoring settings
        if os.getenv("PURPLE_STRICT_MONITORING"):
            config.enable_strict_monitoring = os.getenv("PURPLE_STRICT_MONITORING").lower() == "true"
        
        # Logging settings
        if os.getenv("PURPLE_LOG_LEVEL"):
            config.log_level = os.getenv("PURPLE_LOG_LEVEL")
        
        # Screenshot settings
        if os.getenv("PURPLE_SCREENSHOT_PATH"):
            config.screenshot_path = os.getenv("PURPLE_SCREENSHOT_PATH")
        
        return config

    @classmethod
    def from_file(cls, config_path: str) -> "PurpleConfig":
        """Create configuration from JSON/YAML file"""
        import json
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.endswith('.json'):
                    data = json.load(f)
                elif config_path.endswith(('.yml', '.yaml')):
                    try:
                        import yaml
                        data = yaml.safe_load(f)
                    except ImportError:
                        raise ImportError("PyYAML is required to load YAML config files")
                else:
                    raise ValueError("Config file must be JSON or YAML")
            
            return cls(**data)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_path}")
        except Exception as e:
            raise ValueError(f"Error loading config file: {e}")

    def save_to_file(self, config_path: str):
        """Save configuration to JSON/YAML file"""
        import json
        from dataclasses import asdict
        
        data = asdict(self)
        
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.endswith('.json'):
                    json.dump(data, f, indent=2)
                elif config_path.endswith(('.yml', '.yaml')):
                    try:
                        import yaml
                        yaml.dump(data, f, default_flow_style=False, indent=2)
                    except ImportError:
                        raise ImportError("PyYAML is required to save YAML config files")
                else:
                    raise ValueError("Config file must be JSON or YAML")
                    
        except Exception as e:
            raise ValueError(f"Error saving config file: {e}")

    def update(self, **kwargs):
        """Update configuration values"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self.custom_settings[key] = value
        
        # Re-validate after updates
        self._validate_config()
        self._setup_directories()

    def get_browser_launch_options(self) -> Dict[str, Any]:
        """Get browser launch options for Playwright"""
        options = {
            "headless": self.headless,
            "args": self.browser_args.copy()
        }
        
        if self.user_agent:
            options["user_agent"] = self.user_agent
        
        return options

    def get_browser_context_options(self) -> Dict[str, Any]:
        """Get browser context options for Playwright"""
        options = {
            "viewport": self.viewport.copy()
        }
        
        if self.user_agent:
            options["user_agent"] = self.user_agent
        
        return options

    def get_page_options(self) -> Dict[str, Any]:
        """Get page options for Playwright"""
        return {
            "default_timeout": self.default_timeout
        }

    def copy(self) -> "PurpleConfig":
        """Create a copy of the configuration"""
        from dataclasses import replace
        return replace(self)

    def merge(self, other: "PurpleConfig") -> "PurpleConfig":
        """Merge with another configuration"""
        from dataclasses import asdict, replace
        
        # Get current config as dict
        current_data = asdict(self)
        other_data = asdict(other)
        
        # Merge dictionaries
        merged_data = {**current_data, **other_data}
        
        # Merge custom settings separately
        merged_custom = {**current_data.get("custom_settings", {}), **other_data.get("custom_settings", {})}
        merged_data["custom_settings"] = merged_custom
        
        return PurpleConfig(**merged_data)

    def __str__(self) -> str:
        return f"💜 PurpleConfig(headless={self.headless}, max_retries={self.max_retries})"

    def __repr__(self) -> str:
        return (f"PurpleConfig(headless={self.headless}, max_retries={self.max_retries}, "
                f"default_timeout={self.default_timeout})")


# Predefined configurations
class PresetConfigs:
    """💜 Predefined configuration presets"""
    
    @staticmethod
    def development() -> PurpleConfig:
        """Development configuration with debugging enabled"""
        return PurpleConfig(
            headless=False,
            screenshot_on_violation=True,
            save_page_source_on_violation=True,
            log_level="DEBUG",
            enable_rich_logging=True,
            default_timeout=10000,
            max_retries=1
        )
    
    @staticmethod
    def production() -> PurpleConfig:
        """Production configuration optimized for performance"""
        return PurpleConfig(
            headless=True,
            screenshot_on_violation=False,
            save_page_source_on_violation=False,
            log_level="WARNING",
            enable_rich_logging=False,
            default_timeout=30000,
            max_retries=3
        )
    
    @staticmethod
    def testing() -> PurpleConfig:
        """Testing configuration for CI/CD environments"""
        return PurpleConfig(
            headless=True,
            screenshot_on_violation=True,
            save_page_source_on_violation=True,
            log_level="INFO",
            enable_rich_logging=False,
            default_timeout=20000,
            max_retries=2,
            browser_args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-extensions",
                "--disable-gpu",
                "--single-process"
            ]
        )
    
    @staticmethod
    def debugging() -> PurpleConfig:
        """Debugging configuration with maximum verbosity"""
        return PurpleConfig(
            headless=False,
            screenshot_on_violation=True,
            save_page_source_on_violation=True,
            log_level="DEBUG",
            enable_rich_logging=True,
            default_timeout=60000,
            max_retries=0,  # No retries for debugging
            enable_strict_monitoring=True,
            enable_dom_monitoring=True,
            enable_network_monitoring=True,
            enable_console_monitoring=True
        )