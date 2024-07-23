from typing import Any

import customtkinter
from customtkinter import CTkButton

from src.common.constants import STARTING_PAGE
from src.ui.context import Context


class PagingNavBar(customtkinter.CTkFrame):
    def __init__(self, master: Any, context: Context, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(index=0, weight=1)
        self.grid_columnconfigure(index=1, weight=1)
        self._context = context
        self._prev_page_btn = CTkButton(self, text="Prev", command=self.prev_page)
        self._next_page_btn = CTkButton(self, text="Next", command=self.next_page)
        self._prev_page_btn.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="nsew")
        self._next_page_btn.grid(row=0, column=1, padx=10, pady=(10, 10), sticky="nsew")

    def next_page(self):
        current_page = self._context.get_key("current_page", STARTING_PAGE)
        self._context.update_key("current_page", current_page + 1)

    def prev_page(self):
        current_page = self._context.get_key("current_page", STARTING_PAGE)
        if current_page > 1:
            self._context.update_key("current_page", current_page - 1)
