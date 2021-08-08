import math
import unittest

import numpy as np

from zxopt.data_structures.circuit import Circuit
from zxopt.openqasm import OpenQasmParser
from zxopt.translation import CircuitTranslator
from zxopt.validation import CircuitUnitaryExtractor, DiagramLinearExtractor, validate_operation_equality


class CircuitDiagramTranslationEqualityTest(unittest.TestCase):
    def test_bell_state_circuit_translation(self):
        self.check_circuit_translation_equality(OpenQasmParser().load_file("../circuits/test/bell_state_test_circuit.qasm"))

    def test_simple_circuit_translation(self):
        self.check_circuit_translation_equality(OpenQasmParser().load_file("../circuits/test/simple_translation_test.qasm"))

    def check_circuit_translation_equality(self, circuit: Circuit):
        if not circuit:
            return

        # circuit_renderer = CircuitRenderer(circuit)
        # window = Window(circuit_renderer)
        # window.main_loop()

        diagram = CircuitTranslator(circuit).translate()
        # diagram_renderer = DiagramRenderer(diagram, disable_alignment=False)
        # window = Window(diagram_renderer)
        # window.main_loop()


        circuit_validator = CircuitUnitaryExtractor(circuit)
        circuit_extracted_matrix = circuit_validator.extract_matrix()

        diagram_validator = DiagramLinearExtractor(diagram)
        diagram_extracted_matrix = np.round(diagram_validator.extract_matrix(), decimals=5)

        print(circuit_extracted_matrix)
        print(diagram_extracted_matrix * np.exp(1j * math.pi / 4.0))
        equality = validate_operation_equality(circuit_extracted_matrix, diagram_extracted_matrix)
        print("Equality: ", equality)
        self.assertTrue(equality)

if __name__ == '__main__':
    CircuitUnitaryExtractorTest().test_bell_state_circuit_translation()