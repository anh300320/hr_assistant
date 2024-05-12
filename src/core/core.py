from src.vault.base import Vault


class HrAssistantCore:
    def __init__(
            self,
            vault: Vault,
    ):
        self._vault = vault

    def index(self):
        pass