from typing import Any, List, Set

import customtkinter

from src.common.objects import Metadata
from src.ui.list_view.item import AssetItem


class ListContainer(customtkinter.CTkScrollableFrame):
    def __init__(self, master: Any, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_rowconfigure(index=5, weight=1)
        self.grid_columnconfigure(index=0, weight=1)
        self._items: list[AssetItem] = []

    def add_items(self, metadatas: List[Metadata], checked_ids: Set[str]):
        if len(metadatas) > 5:
            raise Exception("Number of item exceeded")
        for i, metadata in enumerate(metadatas):
            item = AssetItem(
                self,
                metadata=metadata,
                is_checked=(metadata.vault_id in checked_ids)
            )
            item.grid(row=i, column=0, padx=10, pady=(10, 10), sticky="new")
            self._items.append(item)

    def clear_items(self):
        for item in self._items:
            item.destroy()
        self._items = []
