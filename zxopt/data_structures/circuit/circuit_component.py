from typing import TYPE_CHECKING

from zxopt.data_structures.circuit.register.register import RegisterBit

if TYPE_CHECKING:
    from zxopt.data_structures.circuit.circuit import Circuit

class CircuitComponent:
    def __init__(self, affected_bits: set[RegisterBit] = frozenset()):
        self.circuit: "Circuit" = None
        self.step: int = -1
        self.affected_bits: set[RegisterBit] = affected_bits  # the (qu)bits this component is connected to