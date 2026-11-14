"""
J.A.R.V.I.S. — Audio Cache
Caches synthesized audio for frequently spoken phrases (e.g. greetings, status alerts)
to avoid unnecessary CPU cycles and eliminate latency on repeated lines.
"""

import os
import hashlib
import shutil
from typing import Optional


class AudioCache:
    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir is None:
            base = os.path.dirname(os.path.abspath(__file__))
            self.cache_dir = os.path.join(base, "cache")
        else:
            self.cache_dir = cache_dir

        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_key(self, text: str, profile_name: str) -> str:
        """Unique SHA256 key per text + profile combination."""
        raw = f"{profile_name}::{text.strip().lower()}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def get_path(self, text: str, profile_name: str) -> str:
        key = self._get_key(text, profile_name)
        return os.path.join(self.cache_dir, f"{key}.wav")

    def has(self, text: str, profile_name: str) -> bool:
        path = self.get_path(text, profile_name)
        return os.path.isfile(path) and os.path.getsize(path) > 1000

    def put(self, text: str, profile_name: str, src_wav_path: str) -> str:
        target = self.get_path(text, profile_name)
        if os.path.abspath(src_wav_path) != os.path.abspath(target):
            shutil.copyfile(src_wav_path, target)
        return target

    def clear(self) -> int:
        """Deletes all cached audio files. Returns count of deleted items."""
        count = 0
        if os.path.isdir(self.cache_dir):
            for fname in os.listdir(self.cache_dir):
                if fname.endswith(".wav"):
                    p = os.path.join(self.cache_dir, fname)
                    try:
                        os.remove(p)
                        count += 1
                    except OSError:
                        pass
        return count

