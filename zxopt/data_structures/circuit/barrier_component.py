from typing import Set

from zxopt.data_structures.circuit.circuit_component import CircuitComponent
from zxopt.data_structures.circuit.register.register import RegisterBit


class BarrierComponent(CircuitComponent):
    def __init__(self, bits: Set[RegisterBit]):
        super().__init__(bits)