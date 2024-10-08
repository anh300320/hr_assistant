import logging
from typing import Any, Dict, Tuple, Iterable

import customtkinter
from src.common.objects import Metadata, VaultType
from src.database.crud import get_tracked_folders
from src.ui.context import Context
from src.ui.interfaces.subscribers.ctx_subscriber import ContextSubscriber
from src.ui.list_view.list_container import ListContainer
from src.ui.paging_nav_bar.paging_nav_bar import PagingNavBar
from src.vault.google_drive import GoogleDrive


FOLDER_LIST_CACHE_SIZE = 10


class GoogleDriveFrame(customtkinter.CTkFrame, ContextSubscriber):

    def __init__(
            self,
            master: Any,
            config,
            **kwargs,
    ):
        super().__init__(master, **kwargs)
        self._context = Context()
        self._context.add_subscriber(self)
        self._search_bar = customtkinter.CTkEntry(
            self,
            placeholder_text="enter your folder name",
        )
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=8)
        self.grid_rowconfigure(2, weight=1)
        self._search_bar.bind("<Return>", self.enter_search_folder)
        self._search_bar.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="new")
        self._vault = GoogleDrive(config)
        self._list_folders = ListContainer(self)
        self._list_folders.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="nsew")
        self._pages_data: Dict[Tuple[str, str], Any] = {}
        self._page_nav_bar = PagingNavBar(self, self._context)
        self._page_nav_bar.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="sew")
        self._current_search_key = None
        self._next_page_token = None

    def show(self):
        self.grid(row=0, column=1, padx=0, pady=(10, 10), sticky="nsew")

    def enter_search_folder(self, search_bar):
        self._current_search_key = self._search_bar.get()
        self._next_page_token = None
        self._context.update_key("current_page", 1)

    def _update_page_display(self, folders: list[Metadata]):
        if len(self._pages_data) > FOLDER_LIST_CACHE_SIZE:
            self._pages_data.clear()
        self._pages_data[self._current_page_key()] = folders
        self._list_folders.clear_items()
        tracked_folder = self._load_tracked_folders(folders)
        tracked_ids = {f.vault_id for f in tracked_folder}
        self._list_folders.add_items(folders, tracked_ids)

    def add_folder_to_track_list(self, selected_option):
        logging.getLogger(__name__).info(
            "Selected %s", selected_option
        )

    def _load_tracked_folders(self, folders: list[Metadata]) -> Iterable[Metadata]:
        ids = {f.vault_id for f in folders}
        tracked_folders = get_tracked_folders(ids, VaultType.GOOGLE_DRIVE)
        return tracked_folders

    def _current_page_key(self):
        return self._current_search_key, self._context.get_key("current_page")

    def on_ctx_change(self):
        if self._current_page_key() in self._pages_data:
            self._update_page_display(self._pages_data[self._current_page_key()])
        else:
            folders, self._next_page_token = self._vault.search_folder_by_name(
                folder_name=self._current_search_key,
                full_match=False,
                page_token=self._next_page_token
            )
            logging.getLogger(__name__).info(
                "Got candidates %s", folders
            )
            self._update_page_display(folders)
