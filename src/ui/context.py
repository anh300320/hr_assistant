from typing import List

from src.common.objects import Metadata
from src.ui.interfaces.subscribers.ctx_subscriber import ContextSubscriber


class Context:
    def __init__(
            self,
    ):
        self._data = {}
        self._subscribers: List[ContextSubscriber] = []

    def add_subscriber(self, subscriber: ContextSubscriber):
        self._subscribers.append(subscriber)

    def update_key(self, key, value):
        self._data[key] = value
        self._notify()

    def get_key(self, key, default_value = None):
        return self._data.get(key, default_value)

    def _notify(self):
        for sub in self._subscribers:
            sub.on_ctx_change()
