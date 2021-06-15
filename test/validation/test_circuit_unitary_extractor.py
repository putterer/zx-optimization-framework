import unittest

import numpy as np

from zxopt.data_structures.circuit import Circuit, GateComponent, HadamardGateType, PauliXGateType
from zxopt.data_structures.circuit.register.quantum_register import QuantumRegister
from zxopt.validation import CircuitUnitaryExtractor


class CircuitUnitaryExtractorTest(unittest.TestCase):
    def test_single_qubits(self):
        circuit = Circuit()
        register = QuantumRegister(3)
        circuit.add_register(register)
        circuit.add_component(GateComponent(register[0], HadamardGateType()))
        circuit.add_component(GateComponent(register[2], PauliXGateType()))

        extractor = CircuitUnitaryExtractor(circuit)
        unitary = extractor.extract_matrix()

        self.assertTrue(all(unitary == np.array([ # TODO: debug test, debug unitary extractor, more unit tests for controlled gates
            [0,1,0,0,0,1,0,0],
            [1,0,0,0,1,0,0,0],
            [0,0,0,1,0,0,0,1],
            [0,0,1,0,0,0,1,0],
            [0,1,0,0,0,-1,0,0],
            [1,0,0,0,-1,0,0,0],
            [0,0,0,1,0,0,0,-1],
            [0,0,1,0,0,0,-1,0],
        ])))