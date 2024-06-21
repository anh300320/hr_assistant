import logging

import customtkinter

from src.common.objects import VaultType
from src.ui.context import Context
from src.ui.interfaces.subscribers.ctx_subscriber import ContextSubscriber
from src.ui.sidebar.vault_btn import VaultButton


class AppUI(customtkinter.CTk, ContextSubscriber):

    def __init__(self, context: Context):
        super().__init__()
        self._context = context
        self.title("HR Assistant")
        self.geometry("400x150")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1), weight=1)
        self.button = VaultButton(self, text="Drive", context=context, vault_type=VaultType.GOOGLE_DRIVE)
        self.button.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        self.button = VaultButton(self, text="Local", context=context, vault_type=VaultType.LOCAL_DISK)
        self.button.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="w")

    def on_ctx_change(self):
        logging.getLogger(__name__).info("Change App UI")
