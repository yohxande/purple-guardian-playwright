"""
💜 Purple Guardian - Zero-tolerance automation framework
"""

__version__ = "0.1.0"
__author__ = "Yohxande"

from .core import PurpleGuardian
from .workflows import Workflow
from .monitors import StrictMonitor
from .strategies import RestartStrategy
from .config import PurpleConfig

__all__ = [
    "PurpleGuardian",
    "Workflow",
    "StrictMonitor",
    "RestartStrategy",
    "PurpleConfig"
]

# 💜 ASCII Art for fun
PURPLE_BANNER = """
╔═══════════════════════════════════════╗
║     💜 PURPLE GUARDIAN ACTIVE 💜      ║
║     Zero Tolerance · Pure Execution   ║
╚═══════════════════════════════════════╝
"""

def print_banner():
    from rich.console import Console
    from rich.text import Text

    console = Console()
    text = Text(PURPLE_BANNER)
    text.stylize("bold magenta")
    console.print(text)