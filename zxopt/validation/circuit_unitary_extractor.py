import functools

import numpy as np

from zxopt.data_structures.circuit import Circuit, GateComponent
from zxopt.util import Loggable

PROJECTOR_ZERO = np.array([1,0]).reshape(2,1) @ np.array([1,0]).reshape(1,2)  # |0><0| = [[1,0],[0,0]]
PROJECTOR_ONE = np.array([0,1]).reshape(2,1) @ np.array([0,1]).reshape(1,2)  # |1><1| = [[0,0],[0,1]]


class CircuitUnitaryExtractor(Loggable):
    circuit: Circuit
    qubit_count: int

    def __init__(self, circuit: Circuit):
        super(CircuitUnitaryExtractor, self).__init__()
        self.circuit = circuit
        self.qubit_count = len(circuit.get_quantum_bits())
        self.qubits = circuit.get_quantum_bits()
        self.qubit_indicies = { self.qubits[i]: i for i in range(len(self.qubits))}

    def extract_matrix(self):
        circuit = self.circuit

        transformation = np.identity(2 ** self.qubit_count)

        for step in range(circuit.step_count()):
            gates: list[GateComponent] = [c for c in circuit.get_components_by_step(step) if isinstance(c, GateComponent)]
            controlled_gates = [g for g in gates if len(g.control_bits) > 0]
            non_controlled_gates = [g for g in gates if len(g.control_bits) == 0]

            non_controlled_transformations_by_qubit = [np.identity(2)] * self.qubit_count

            for gate in non_controlled_gates:
                non_controlled_transformations_by_qubit[self.qubit_indicies[gate.target_qubit]] = gate.gate_type.matrix

            non_controlled_gates_transformation = self.kron(non_controlled_transformations_by_qubit) # this could be pulled into the controlled gate transformation, but would have to be used there for each gate

            transformation = non_controlled_gates_transformation @ transformation


            for gate in controlled_gates:
                assert len(gate.control_bits) == 1, "Cannot deal with gates using more than one control (yet)"

                # what happens if control is 0
                transformations_by_qubit = [np.identity(2)] * self.qubit_count
                transformations_by_qubit[self.qubit_indicies[gate.control_bits[0]]] = PROJECTOR_ZERO
                mat_not_triggered = self.kron(transformations_by_qubit)

                # what happens if control is 1
                transformations_by_qubit = [np.identity(2)] * self.qubit_count
                transformations_by_qubit[self.qubit_indicies[gate.control_bits[0]]] = PROJECTOR_ONE
                transformations_by_qubit[self.qubit_indicies[gate.target_qubit]] = gate.gate_type.matrix
                mat_triggered = self.kron(transformations_by_qubit)

                controlled_gate_mat = mat_not_triggered + mat_triggered

                transformation = controlled_gate_mat @ transformation


        # TODO unit test

        return transformation

    def kron(self, unitaries):
        return functools.reduce(lambda val,element: np.kron(val, element), unitaries)