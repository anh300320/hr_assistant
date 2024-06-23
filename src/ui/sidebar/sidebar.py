from typing import Iterable

import customtkinter
from customtkinter import CTkButton

from src.common.objects import VaultType
from src.ui.sidebar.vault_btn import VaultButton


class Sidebar(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            context,
    ):
        super().__init__(master)
        self.title = customtkinter.CTkLabel(self, text="Home", fg_color="gray30", corner_radius=6)
        self.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="nsw")
        self.title.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="ew")
        self.gg_drive_button = VaultButton(self, text="Drive", context=context, vault_type=VaultType.GOOGLE_DRIVE)
        self.gg_drive_button.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="new")
        self.local_button = VaultButton(self, text="Local", context=context, vault_type=VaultType.LOCAL_DISK)
        self.local_button.grid(row=2, column=0, padx=10, pady=(10, 10), sticky="new")
