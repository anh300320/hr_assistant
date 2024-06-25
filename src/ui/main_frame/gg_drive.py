import logging
from typing import Any

import customtkinter
from CTkListbox import CTkListbox
from customtkinter import CTkScrollableFrame

from src.ui.context import Context
from src.ui.interfaces.subscribers.ctx_subscriber import ContextSubscriber
from src.vault.google_drive import GoogleDrive


class GoogleDriveFrame(customtkinter.CTkFrame, ContextSubscriber):

    def __init__(
            self,
            master: Any,
            config,
            **kwargs,
    ):
        super().__init__(master, **kwargs)
        self._context = Context()
        self._search_bar = customtkinter.CTkEntry(
            self,
            placeholder_text="enter your folder name",
        )
        self.grid_columnconfigure(0, weight=1)
        self._search_bar.bind("<Return>", self.enter_search_folder)
        self._search_bar.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="new")
        self._vault = GoogleDrive(config)
        self.list_box = None
        # self._context.add_subscriber()

    def show(self):
        self.grid(row=0, column=1, padx=0, pady=(10, 10), sticky="nsew")

    def enter_search_folder(self, search_bar):
        search_value = self._search_bar.get()
        candidates = self._vault.search_folder_by_name(
            folder_name=search_value,
            full_match=False,
        )
        self.list_box = CTkListbox(self, command=self.add_folder_to_track_list)
        for i, folder in enumerate(candidates):
            self.list_box.option_add(i, folder.name)
        self.list_box.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="nsew")
        # self.list_box.s
        return candidates

    def add_folder_to_track_list(self, selected_option):
        logging.getLogger(__name__).info(
            "Selected %s", selected_option
        )

    def on_ctx_change(self):
        pass
