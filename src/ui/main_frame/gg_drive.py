from typing import Any

import customtkinter

from src.ui.context import Context
from src.ui.interfaces.subscribers.ctx_subscriber import ContextSubscriber


class GoogleDriveFrame(customtkinter.CTkFrame, ContextSubscriber):

    def __init__(
            self,
            master: Any,
            context: Context,
            **kwargs,
    ):
        super().__init__(master, **kwargs)
        self._context = context
        self._search_bar = customtkinter.CTkEntry(
            self,
            placeholder_text="enter your folder name",
        )
        self._search_bar.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="new")

    def show(self):
        self.grid(row=0, column=1, padx=0, pady=(10, 10), sticky="nsew")

    def on_ctx_change(self):
        pass
