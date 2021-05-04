from zxopt.data_structures.circuit.circuit_component import CircuitComponent
from zxopt.data_structures.circuit.register.classical_register import ClassicalRegister
from zxopt.data_structures.circuit.register.quantum_register import QuantumRegister
from zxopt.data_structures.circuit.register.register import RegisterBit, Register


class Circuit:
    def __init__(self):
        self.components: set[CircuitComponent] = set()
        self.quantum_registers: set[QuantumRegister] = set()
        self.classical_registers: set[ClassicalRegister] = set()

    def add_component(self, component: CircuitComponent):
        component.circuit = self



        self.components.add(component)

    def remove_component(self, component: CircuitComponent):
        component.circuit = None
        self.components.remove(component)

    """
    Returns all components that affect any of the specified bits
    """
    def get_components_affecting_bits(self, bits: set[RegisterBit]):
        return set(filter(lambda c: any([bit in c.affected_bits for bit in bits]), self.components))

    def add_register(self, register: Register):
        if isinstance(register, QuantumRegister):
            self.quantum_registers.add(register)
        elif isinstance(register, ClassicalRegister):
            self.classical_registers.add(register)
        else:
            raise NotImplementedError("Unsupported register type")
        register.circuit = self

    def remove_register(self, register: Register):
        if isinstance(register, QuantumRegister):
            self.quantum_registers.remove(register)
        elif isinstance(register, ClassicalRegister):
            self.classical_registers.remove(register)
        else:
            raise NotImplementedError("Unsupported register type")
        register.circuit = self