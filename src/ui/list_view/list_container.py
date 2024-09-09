from typing import Any, List

import customtkinter

from src.common.objects import Metadata
from src.ui.list_view.item import AssetItem


class ListContainer(customtkinter.CTkScrollableFrame):
    def __init__(self, master: Any, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_rowconfigure(index=5, weight=1)
        self._items: list[AssetItem] = []

    def add_items(self, metadatas: List[Metadata]):
        if len(metadatas) > 5:
            raise Exception("Number of item exceeded")
        for i, metadata in enumerate(metadatas):
            item = AssetItem(
                self,
                asset_type=metadata.file_type,
                folder_name=metadata.name,
                created_date=metadata.create_date,
                updated_date=metadata.update_date
            )
            item.grid(row=i, column=0, padx=10, pady=(10, 10), sticky="new")
            self._items.append(item)

    def clear_items(self):
        for item in self._items:
            item.destroy()
        self._items = []
