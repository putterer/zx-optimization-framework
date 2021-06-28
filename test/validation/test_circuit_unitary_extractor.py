import math
import unittest

import numpy as np

from zxopt.data_structures.circuit import Circuit, GateComponent, HadamardGateType, PauliXGateType
from zxopt.data_structures.circuit.register.quantum_register import QuantumRegister
from zxopt.util.toolbox import matrix_equality
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

        target = np.array([
            [0,1,0,0,0,1,0,0],
            [1,0,0,0,1,0,0,0],
            [0,0,0,1,0,0,0,1],
            [0,0,1,0,0,0,1,0],
            [0,1,0,0,0,-1,0,0],
            [1,0,0,0,-1,0,0,0],
            [0,0,0,1,0,0,0,-1],
            [0,0,1,0,0,0,-1,0],
        ]) * (1/math.sqrt(2))

        self.assertTrue(matrix_equality(unitary, target))


    def test_h_cx(self):
        circuit = Circuit()
        register = QuantumRegister(3)
        circuit.add_register(register)
        circuit.add_component(GateComponent(register[1], HadamardGateType()))
        circuit.add_component(GateComponent(register[0], PauliXGateType(), set([register[2]])))

        extractor = CircuitUnitaryExtractor(circuit)
        unitary = extractor.extract_matrix()

        print(unitary)

        target = np.array([
            [1,0,1,0,0,0,0,0],
            [0,0,0,0,0,1,0,1],
            [1,0,-1,0,0,0,0,0],
            [0,0,0,0,0,1,0,-1],
            [0,0,0,0,1,0,1,0],
            [0,1,0,1,0,0,0,0],
            [0,0,0,0,1,0,-1,0],
            [0,1,0,-1,0,0,0,0],
        ]) * (1/math.sqrt(2))

        self.assertTrue(matrix_equality(unitary, target))