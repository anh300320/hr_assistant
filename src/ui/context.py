from typing import List

from src.ui.interfaces.subscribers.ctx_subscriber import ContextSubscriber


class Context:
    def __init__(
            self,
    ):
        self._main_view = "Home"
        self._subscribers = []

    def add_subscriber(self, subscriber: ContextSubscriber):
        self._subscribers.append(subscriber)

    def change_main_view(self, view):
        self._main_view = view
        self._notify()

    def _notify(self):
        for sub in self._subscribers:
            sub.on_ctx_change()
