from typing import TYPE_CHECKING

from zxopt.data_structures.circuit.register.register import RegisterBit

if TYPE_CHECKING:
    from zxopt.data_structures.circuit.circuit import Circuit

class CircuitComponent:
    circuit: "Circuit"
    step: int
    affected_bits: set[RegisterBit]

    def __init__(self, affected_bits: set[RegisterBit] = frozenset()):
        self.circuit = None
        self.step = -1
        self.affected_bits = affected_bits  # the (qu)bits this component is connected to

    def set_circuit(self, circuit: "Circuit"):
        self.circuit = circuit