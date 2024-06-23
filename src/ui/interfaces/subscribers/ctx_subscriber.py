from abc import ABC, abstractmethod


class ContextSubscriber(ABC):
    @abstractmethod
    def on_ctx_change(self):
        raise NotImplementedError
