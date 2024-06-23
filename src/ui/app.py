import logging

import customtkinter

from src.common.objects import VaultType
from src.ui.context import Context
from src.ui.interfaces.subscribers.ctx_subscriber import ContextSubscriber
from src.ui.main_frame.gg_drive import GoogleDriveFrame


class AppUI(customtkinter.CTk, ContextSubscriber):

    def __init__(self, context: Context):
        super().__init__()
        self._context = context
        self.title("HR Assistant")
        self.geometry("600x400")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(0, weight=1)
        self._gg_drive_main_fr = GoogleDriveFrame(self, context=self._context)
        self._gg_drive_main_fr.grid_forget()

    def on_ctx_change(self):
        logging.getLogger(__name__).info("Change App UI")
        if self._context.main_view() == VaultType.GOOGLE_DRIVE.name:
            self._gg_drive_main_fr.show()
