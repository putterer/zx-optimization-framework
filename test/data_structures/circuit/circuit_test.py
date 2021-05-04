import unittest

from zxopt.data_structures.circuit import Circuit, MeasurementComponent
from zxopt.data_structures.circuit.register.classical_register import ClassicalRegister
from zxopt.data_structures.circuit.register.quantum_register import QuantumRegister


class CircuitTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(CircuitTest, self).__init__(*args, **kwargs)

    def test_add_remove_quantum_register(self):
        circuit = Circuit()
        qreg = QuantumRegister(1)

        circuit.add_register(qreg)
        self.assertIn(qreg, circuit.quantum_registers)
        self.assertEqual(circuit, qreg.circuit)
        circuit.remove_register(qreg)
        self.assertNotIn(qreg, circuit.quantum_registers)

    def test_add_remove_classical_register(self):
        circuit = Circuit()
        creg = ClassicalRegister(1)

        circuit.add_register(creg)
        self.assertIn(creg, circuit.classical_registers)
        self.assertEqual(circuit, creg.circuit)
        circuit.remove_register(creg)
        self.assertNotIn(creg, circuit.classical_registers)


    def test_add_component(self):
        circuit = Circuit()
        qreg = QuantumRegister(1)
        creg = ClassicalRegister(1)
        measurement = MeasurementComponent(qreg[0], creg[0])

        self.assertIn(qreg[0], measurement.affected_bits)
        self.assertIn(creg[0], measurement.affected_bits)

        circuit.add_register(qreg)
        circuit.add_register(creg)
        circuit.add_component(measurement)

        self.assertIn(measurement, circuit.components)
        self.assertEqual(circuit, measurement.circuit)

        # TODO: temporal

    def test_get_components_affecting_bits(self):
        circuit = Circuit()
        qreg = QuantumRegister(2)
        creg = ClassicalRegister(2)
        measurement1 = MeasurementComponent(qreg[0], creg[0])
        measurement2 = MeasurementComponent(qreg[1], creg[1])
        circuit.add_register(qreg)
        circuit.add_register(creg)
        circuit.add_component(measurement1)
        circuit.add_component(measurement2)

        self.assertIn(measurement1, circuit.get_components_affecting_bits({qreg[0]}))
        self.assertIn(measurement1, circuit.get_components_affecting_bits({creg[0]}))
        self.assertIn(measurement2, circuit.get_components_affecting_bits({qreg[1]}))
        self.assertIn(measurement2, circuit.get_components_affecting_bits({creg[1]}))

        self.assertNotIn(measurement1, circuit.get_components_affecting_bits({qreg[1]}))
        self.assertNotIn(measurement1, circuit.get_components_affecting_bits({creg[1]}))
        self.assertNotIn(measurement2, circuit.get_components_affecting_bits({qreg[0]}))
        self.assertNotIn(measurement2, circuit.get_components_affecting_bits({creg[0]}))

        self.assertIn(measurement1, circuit.get_components_affecting_bits({qreg[0],qreg[1]}))
        self.assertIn(measurement2, circuit.get_components_affecting_bits({qreg[0],qreg[1]}))