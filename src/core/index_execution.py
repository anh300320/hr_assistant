from src.tokenizer.normalizer import NormalizeChain
from src.tokenizer.base import Tokenizer
from src.vault.base import Vault


class IndexExecution:
    def __init__(
            self,
            vault: Vault,
            normalize_chain: NormalizeChain,
            tokenizer: Tokenizer,
    ):
        self._vault = vault
        self._tokenizer = tokenizer
        self._normalize_chain = normalize_chain

    def run(self):
        all_metadata = self._vault.load_all_tracked_files()
        for metadata in all_metadata:
            file_content = self._vault.load_content(metadata)
