from abc import ABC, abstractmethod
from src.utils.word32 import Word32


class IntegerEncoder(ABC):
    @abstractmethod
    def encode(self, value: int) -> Word32:
        raise NotImplementedError