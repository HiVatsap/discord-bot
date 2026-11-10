import logging

from rich.console import Console
from rich.logging import RichHandler

console = Console()

rich_handler = RichHandler(
    console=console,
    rich_tracebacks=True,
    show_time=True,
    show_level=True,
    show_path=False,
    markup=False,
    omit_repeated_times=False,
)

rich_handler.setFormatter(logging.Formatter("%(message)s"))

logging.basicConfig(
    level=logging.INFO,
    datefmt="[%H:%M:%S]",
    handlers=[rich_handler],
)

logging.getLogger("discord").setLevel(logging.WARNING)
logging.getLogger("discord.http").setLevel(logging.WARNING)

logger = logging.getLogger("DiscordBot")