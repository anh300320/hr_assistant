import html
import logging

from telegram import Update
from telegram.ext import CallbackContext, Application, CommandHandler, MessageHandler, filters

from src.common.objects import VaultType
from src.config.base import Config
from src.core.core import HrAssistantCore
from src.database.connection import get_db
from src.database.crud import get_tracked_folders

_logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(
            self,
            config: Config,
            core: HrAssistantCore,
    ):
        self._telegram_bot_token = config.telegram_bot_token
        self._core = core

    def run(self):
        application = Application.builder().token(self._telegram_bot_token).build()
        application.add_handler(CommandHandler("search", self.search))
        application.add_handler(CommandHandler("list", self.get_tracked_folders))
        application.add_handler(CommandHandler("index", self.index))
        application.add_handler(MessageHandler(filters.ALL, self.all_msg))
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    async def help(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text("Please ")

    async def get_tracked_folders(self, update: Update, context: CallbackContext):
        # query = ' '.join(context.args)
        # vault_type = VaultType(query.upper())
        with get_db() as db_sess:
            tracked_folders = get_tracked_folders(
                db_sess,
                vault_type=VaultType.GOOGLE_DRIVE,
            )
            lines = ""
            for folder in tracked_folders:
                lines += f"- {folder.name} {folder.update_date.strftime('%Y%m%d')}\n"
            text = (
                f"Thư mục quản lý:\n"
                f"{lines}"
            )
        await update.message.reply_text(text)

    async def index(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text("Bắt đầu xử lý dữ liệu.")
        self._core.index()
        await update.message.reply_text("Xử lý dữ liệu hoàn tất.")

    async def search(self, update: Update, context: CallbackContext) -> None:
        query = ' '.join(context.args)
        _logger.info("Query %s", query)
        with get_db() as db_sess:
            matched_entries = self._core.search(db_sess, query)
        lines = ""
        for entry in matched_entries:
            lines += f" [{entry.file_name}]({entry.path})  \n"
        text = f"""
            Kết quả tìm kiếm cho {html.escape(query)}:  
            {lines}
        """
        _logger.info("TEXT: %s", text)
        await update.message.reply_markdown_v2(text)

    async def all_msg(self, update: Update, context: CallbackContext):
        await update.message.reply_text("Em Zuppy chinhhh.")
