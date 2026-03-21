from src.common.logging import init_logging
from src.config.base import ConfigLoader
from src.core.core import HrAssistantCore
from src.search.boolean_search import parse_raw_boolean_search
from src.telebot.telegram_bot import TelegramBot

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]



def main():
    init_logging()
    config_loader = ConfigLoader()
    config = config_loader.load()
    hr_core = HrAssistantCore(config)
    telegram_bot = TelegramBot(config, hr_core)
    telegram_bot.run()


if __name__ == "__main__":
    main()
