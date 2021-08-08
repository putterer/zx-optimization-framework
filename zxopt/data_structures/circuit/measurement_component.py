from typing import TYPE_CHECKING

from zxopt.data_structures.circuit.circuit_component import CircuitComponent
from zxopt.data_structures.circuit.register.classical_register import ClassicalBit
from zxopt.data_structures.circuit.register.quantum_register import QuantumBit

if TYPE_CHECKING:
    from zxopt.data_structures.circuit.circuit import Circuit

class MeasurementComponent(CircuitComponent):
    measured_qubit: QuantumBit
    target_bit: ClassicalBit

    def __init__(self, measured_qubit: QuantumBit, target_bit: ClassicalBit):
        super().__init__({measured_qubit, target_bit})

        self.measured_qubit = measured_qubit
        self.target_bit = target_bit

    def set_circuit(self, circuit: "Circuit"):
        super().set_circuit(circuit)

        self.affected_bits = set(circuit.get_register_bits()) # measurement components acts like a barrier and affects / waits for everything