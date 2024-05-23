import os
import shutil


class DiskSentinel:
    def __init__(
            self,
            config,
    ):
        self._temp_dirs = [
            config.get('temp_dir', None),
        ]

    def clean_up(self):
        for temp_dir in self._temp_dirs:
            if not temp_dir:
                continue
            for child in os.listdir(self._gg_temp_dir):
                if os.path.isfile(child):
                    os.remove(child)
                else:
                    shutil.rmtree(child)
