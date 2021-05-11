from zxopt.data_structures.circuit.circuit_component import CircuitComponent
from zxopt.data_structures.circuit.register.classical_register import ClassicalBit
from zxopt.data_structures.circuit.register.quantum_register import QuantumBit


class MeasurementComponent(CircuitComponent):
    def __init__(self, measured_qubit: QuantumBit, target_bit: ClassicalBit):
        super().__init__({measured_qubit, target_bit})

        self.measured_qubit: QuantumBit = measured_qubit
        self.target_bit: ClassicalBit = target_bit

