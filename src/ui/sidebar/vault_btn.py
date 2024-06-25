import logging
from typing import Any

from customtkinter import CTkButton

from src.common.objects import VaultType
from src.ui.context import Context


class VaultButton(CTkButton):
    def __init__(
            self,
            master: Any,
            context: Context,
            vault_type: VaultType,
            **kwargs,
    ):
        super().__init__(master, **kwargs)
        self._vault_type = vault_type
        self._context = context
        self._command = self.on_click

    def on_click(self):
        logging.getLogger(__name__).info(
            "Clicked Button %s",
            self._vault_type.name,
        )
        self._context.update_key("vault_type", self._vault_type.name)
