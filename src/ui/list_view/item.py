from datetime import datetime, timedelta
from typing import Any

import customtkinter


def get_time_since(start_date: datetime, prefix: str):
    now = datetime.now()
    days_since_created = now - start_date
    if days_since_created <= timedelta(days=7):
        dd = "days"
        if days_since_created.days == 1:
            dd = "day"
        return f"{prefix} {days_since_created.days} {dd} ago"
    return start_date.strftime(f"{prefix} at %Y/%m/%d %I:%M %p")


class FolderItem(customtkinter.CTkFrame):
    def __init__(
            self,
            master: Any,
            folder_name: str,
            created_date: datetime,
            updated_date: datetime,
            **kwargs
    ):
        super().__init__(master, **kwargs)
        self.name = folder_name
        self.created_date = created_date
        self.updated_date = updated_date
        self.grid_columnconfigure(index=0, weight=1)
        # self.grid_columnconfigure(index=1, weight=3) # TODO when have folder icon
        self.name_label = customtkinter.CTkLabel(self, text=self.name, fg_color="gray30", corner_radius=6)
        self.name_label.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="new")
        self.created_label = customtkinter.CTkLabel(
            self,
            text=get_time_since(self.created_date, "created"),
            fg_color="gray30",
            corner_radius=6,
        )
        self.created_label.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="new")
        self.updated_label = customtkinter.CTkLabel(
            self,
            text=get_time_since(self.updated_date, "updated"),
            fg_color="gray30",
            corner_radius=6,
        )
        self.updated_label.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="new")
