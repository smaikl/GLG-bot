import logging
from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class BotConfig:
    token: str = "8023162420:AAHIyO6YnYPqud1893bd6TlsqnwLQoFq3uk"
    

@dataclass
class DbConfig:
    db_name: str = "bot_database.sqlite"
    db_path: str = "database"


@dataclass
class Config:
    bot: BotConfig = field(default_factory=BotConfig)
    db: DbConfig = field(default_factory=DbConfig)
    files_dir: str = "files"


config = Config()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
