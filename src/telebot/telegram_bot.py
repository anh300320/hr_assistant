import html
import io
import logging

from telegram import Update
from telegram.ext import CallbackContext, Application, CommandHandler, MessageHandler, filters

from src.common.objects import VaultType
from src.config.base import Config
from src.core.core import HrAssistantCore
from src.database.connection import get_db
from src.database.crud import get_tracked_folders
from src.payslip.payslip_worker import PayslipWorker


_logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(
            self,
            config: Config,
            core: HrAssistantCore,
    ):
        self._telegram_bot_token = config.telegram_bot_token
        self._core = core
        self._payslips_worker = PayslipWorker()
        self._is_muted = False

    def run(self):
        application = Application.builder().token(self._telegram_bot_token).build()
        application.add_handler(CommandHandler("search", self.search))
        application.add_handler(CommandHandler("list", self.get_tracked_folders))
        application.add_handler(CommandHandler("index", self.index))
        application.add_handler(CommandHandler("target_range", self.config_target_range))
        application.add_handler(CommandHandler("target_list", self.config_target_list))
        application.add_handler(CommandHandler("email_column", self.config_email_column))
        application.add_handler(CommandHandler("mute", self.mute))
        # application.add_handler(MessageHandler(filters.Document.ALL, self.handle_file()))
        application.add_handler(MessageHandler(filters.ALL, self.handle_file))
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    async def help(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text("Please ")

    async def get_tracked_folders(self, update: Update, context: CallbackContext):
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

    # Function to handle file uploads
    async def handle_file(self, update: Update, context: CallbackContext):
        # Check if the message has a document or photo
        if update.message.document:
            file = update.message.document
            file_id = file.file_id
            file_name = file.file_name

            # Download the file
            bot = update.message.get_bot()
            new_file = await bot.get_file(file_id)

            buffer = io.BytesIO()

            await new_file.download_to_memory(buffer)  # Save file in the current directory

            for name, email in self._payslips_worker.run(buffer.getvalue()):
                if not self._is_muted:
                    await update.message.reply_text(f"Đã gửi payslip cho {name}, email {email} rùiiiii hihi!")

            await update.message.reply_text(f"Xong rùiiiii!")

    async def all_msg(self, update: Update, context: CallbackContext):
        await update.message.reply_text("Em Zuppy chinhhh.")

    async def config_target_range(self, update: Update, context: CallbackContext):
        range = context.args
        if len(range) != 2:
            await update.message.reply_text("Bạn nhập 2 số thui nháaa.")
            return
        self._payslips_worker.target_start = int(range[0])
        self._payslips_worker.target_end = int(range[1])
        self._payslips_worker.target_list = []
        await update.message.reply_text("Cập nhật cấu hình xong rùi áaa.")

    async def config_target_list(self, update: Update, context: CallbackContext):
        targets = context.args
        self._payslips_worker.target_start = 0
        self._payslips_worker.target_end = 1000000
        self._payslips_worker.target_list = [int(v) for v in targets]
        await update.message.reply_text("Cập nhật cấu hình xong rùi áaa.")

    async def config_email_column(self, update: Update, context: CallbackContext):
        targets = context.args
        self._payslips_worker.email_column = targets[0]
        await update.message.reply_text("Cập nhật cấu hình xong rùi áaa.")

    async def mute(self, update: Update, context: CallbackContext):
        if not self._is_muted:
            self._is_muted = True
            await update.message.reply_text("Dạ Zuppy im lặng ạ hic.")
        else:
            self._is_muted = False
            await update.message.reply_text("Hihi Zuppy gáy liên tục liềnnnn.")
