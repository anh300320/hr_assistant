from typing import List

from src.common.objects import Metadata
from src.ui.interfaces.subscribers.ctx_subscriber import ContextSubscriber


class Context:
    def __init__(
            self,
    ):
        self.data = {}
        self._subscribers: List[ContextSubscriber] = []

    def add_subscriber(self, subscriber: ContextSubscriber):
        self._subscribers.append(subscriber)

    def update_key(self, key, value):
        self.data[key] = value
        self._notify()

    def _notify(self):
        for sub in self._subscribers:
            sub.on_ctx_change()
