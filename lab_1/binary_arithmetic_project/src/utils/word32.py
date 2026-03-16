from __future__ import annotations
from typing import List
from src.config import WORD_SIZE_BITS

class Word32:
    def __init__(self, bits: List[int]) -> None:
        self._validate(bits)
        self._bits = bits[:] 
        
    @property
    def bits(self) -> List[int]:
        return self._bits[:]
    
    def to_string(self) -> str:
        return "".join("1" if bit else "0" for bit in self._bits)
    
    @staticmethod
    def _validate(bits: List[int]) ->None:
        if len(bits) !=WORD_SIZE_BITS:
          raise ValueError("Word32 must contain exactly 32 bits")  
        if any(bit not in (0, 1) for bit in bits):
           raise ValueError("Word32 bits must be only 0 or 1")    
    
    def __eq__(self, other: object) ->bool:
        if not isinstance(other, Word32):
            return False
        return self._bits == other._bits            
