# encryption/fragmenter.py
from typing import List
import os
import math


class Fragmenter:
    def __init__(self, fragment_size: int = Config.FRAGMENT_SIZE):
        self.fragment_size = fragment_size

    def fragment_file(self, file_data: bytes) -> List[bytes]:
        """Split file into fragments of specified size."""
        num_fragments = math.ceil(len(file_data) / self.fragment_size)
        fragments = []

        for i in range(num_fragments):
            start = i * self.fragment_size
            end = start + self.fragment_size
            fragment = file_data[start:end]
            fragments.append(fragment)

        return fragments

    def reconstruct_file(self, fragments: List[bytes]) -> bytes:
        """Reconstruct original file from fragments."""
        return b''.join(fragments)
