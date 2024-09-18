from datetime import datetime, timedelta
from typing import Any

import customtkinter
import pytz

from src.common.objects import FileType
from PIL import Image

def get_time_since(start_date: datetime, prefix: str):
    now = datetime.now(tz=pytz.UTC)
    days_since_created = now - start_date
    if days_since_created <= timedelta(days=7):
        dd = "days"
        if days_since_created.days == 1:
            dd = "day"
        return f"{prefix} {days_since_created.days} {dd} ago"
    return start_date.strftime(f"{prefix} at %Y/%m/%d %I:%M %p")


class AssetItem(customtkinter.CTkFrame):
    def __init__(
            self,
            master: Any,
            asset_type: FileType,
            folder_name: str,
            created_date: datetime,
            updated_date: datetime,
            **kwargs
    ):
        super().__init__(master, **kwargs)
        self.name = folder_name
        self.asset_type = asset_type
        self.created_date = created_date
        self.updated_date = updated_date
        self.grid_columnconfigure(index=0, weight=1)
        self.grid_columnconfigure(index=1, weight=3)
        # self.grid_columnconfigure(index=1, weight=3) # TODO when have folder icon
        if self.asset_type == FileType.FOLDER:
            image_fp = "resources/assets/icon_folder.png"
        else:
            image_fp = "resources/assets/icon_file.png"
        icon = customtkinter.CTkImage(
            light_image=Image.open(image_fp),
            dark_image=Image.open(image_fp),
            size=(60, 90)
        )
        self.icon = customtkinter.CTkLabel(
            self,
            text="",
            image=icon,
            corner_radius=6,
        )
        self.icon.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="new")
        self._asset_info = AssetInfo(
            self,
            create_at=self.created_date,
            modify_at=self.updated_date,
            name=self.name
        )
        self._asset_info.grid(row=0, column=1, padx=10, pady=(10, 10), sticky="nsew")


class AssetInfo(customtkinter.CTkFrame):
    def __init__(
            self,
            master: Any,
            create_at: datetime,
            modify_at: datetime,
            name: str,
            **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.grid_rowconfigure(index=2, weight=1)
        self.grid_columnconfigure(index=0, weight=1)
        self.name_label = customtkinter.CTkLabel(
            self,
            text=name,
            fg_color="gray30",
            corner_radius=6,
        )
        self.name_label.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="new")
        self.created_label = customtkinter.CTkLabel(
            self,
            text=get_time_since(create_at, "created"),
            fg_color="gray30",
            corner_radius=6,
        )
        self.created_label.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="new")
        self.updated_label = customtkinter.CTkLabel(
            self,
            text=get_time_since(modify_at, "updated"),
            fg_color="gray30",
            corner_radius=6,
        )
        self.updated_label.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="new")
