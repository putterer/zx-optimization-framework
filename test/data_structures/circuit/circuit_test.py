import unittest

from zxopt.data_structures.circuit import Circuit, MeasurementComponent, GateComponent, PauliXGateType
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

        self.assertEqual(0, measurement.step)

    def test_get_components_affecting_bits(self):
        circuit = Circuit()
        qreg = QuantumRegister(2)
        creg = ClassicalRegister(2)
        operation1 = GateComponent(qreg[0], PauliXGateType(), {creg[0]}) # measurements always affect everything, do not use measurements for this test :)
        operation2 = GateComponent(qreg[1], PauliXGateType(), {creg[1]})
        circuit.add_register(qreg)
        circuit.add_register(creg)
        circuit.add_component(operation1)
        circuit.add_component(operation2)

        self.assertIn(operation1, circuit.get_components_affecting_bits({qreg[0]}))
        self.assertIn(operation1, circuit.get_components_affecting_bits({creg[0]}))
        self.assertIn(operation2, circuit.get_components_affecting_bits({qreg[1]}))
        self.assertIn(operation2, circuit.get_components_affecting_bits({creg[1]}))

        self.assertNotIn(operation1, circuit.get_components_affecting_bits({qreg[1]}))
        self.assertNotIn(operation1, circuit.get_components_affecting_bits({creg[1]}))
        self.assertNotIn(operation2, circuit.get_components_affecting_bits({qreg[0]}))
        self.assertNotIn(operation2, circuit.get_components_affecting_bits({creg[0]}))

        self.assertIn(operation1, circuit.get_components_affecting_bits({qreg[0], qreg[1]}))
        self.assertIn(operation2, circuit.get_components_affecting_bits({qreg[0], qreg[1]}))

    def test_add_components_step(self):
        circuit = Circuit()
        qreg = QuantumRegister(3)
        creg = ClassicalRegister(3)
        circuit.add_register(qreg)
        circuit.add_register(creg)

        for i in range(100):
            comp = GateComponent(qreg[i % 2], PauliXGateType(), {creg[0]})
            circuit.add_component(comp)

            self.assertEqual(i, comp.step)

        comp = GateComponent(qreg[2], PauliXGateType(), {creg[1]})
        circuit.add_component(comp)

        self.assertEqual(0, comp.step)