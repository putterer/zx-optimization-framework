import math
from typing import cast

from graph_tool import Vertex

from zxopt.data_structures.circuit import Circuit, CircuitComponent, GateComponent, PauliXGateType, HadamardGateType, \
    PauliZGateType, PauliYGateType, PhaseGateType, TGateType
from zxopt.data_structures.circuit.register.quantum_register import QuantumBit
from zxopt.data_structures.diagram import Diagram
from zxopt.data_structures.diagram.diagram import INPUT, OUTPUT
from zxopt.openqasm import OpenQasmParser
from zxopt.util import Loggable
from zxopt.visualization import Window, DiagramRenderer


class CircuitTranslator(Loggable):
    circuit: Circuit
    diagram: Diagram
    input_boundaries_by_qubit: dict[QuantumBit, Vertex]
    output_boundaries_by_qubit: dict[QuantumBit, Vertex]
    current_frontier_by_qubit: dict[QuantumBit, Vertex] # graph nodes for the current frontier per qubit (what node each operation per qubit would connect to)
    hadamard_status_by_qubit: dict[QuantumBit, bool]
    qubit_indicies: dict[QuantumBit, int]

    def __init__(self, circuit: Circuit):
        super().__init__()
        self.circuit = circuit
        self.diagram = Diagram()
        self.input_boundaries_by_qubit = {}
        self.output_boundaries_by_qubit = {}

        quantum_bits = circuit.get_quantum_bits()
        self.qubit_indicies = { quantum_bits[i]: i for i in range(len(quantum_bits))}

    # translation based on universal CNOT, Z(alpha), H
    # X(alpha) = HZ(alpha)H can be represented as a spider as well
    def translate(self) -> Diagram:
        qubits = cast(list[QuantumBit], self.circuit.get_quantum_bits())

        # Parse registers
        self.input_boundaries_by_qubit = {qubit: self.diagram.add_boundary(INPUT) for qubit in qubits}
        self.current_frontier_by_qubit = self.input_boundaries_by_qubit.copy()
        self.hadamard_status_by_qubit = {qubit: False for qubit in qubits}

        # Parse components step by step
        for step in range(self.circuit.step_count()):
            for component in self.circuit.get_components_by_step(step):
                self.translate_component(component)

        # Advance to output boundaries, apply pending hadamards
        self.output_boundaries_by_qubit = {qubit: self.diagram.add_boundary(OUTPUT) for qubit in qubits}
        for q in qubits:
            self.advance_frontier(self.output_boundaries_by_qubit[q], q)

        return self.diagram


    def translate_component(self, component: CircuitComponent):
        if not isinstance(component, GateComponent):
            return

        gate_type = component.gate_type


        if len(component.control_bits) == 0: # not controlled
            if isinstance(gate_type, HadamardGateType):
                self.hadamard_status_by_qubit[component.target_qubit] = not self.hadamard_status_by_qubit[component.target_qubit]
                return

            if isinstance(gate_type, PauliXGateType):
                s = self.diagram.add_spider(phase=math.pi, color="red", origin_qubit_index=self.qubit_indicies[component.target_qubit])
                self.advance_frontier(s, component.target_qubit)

            if isinstance(gate_type, PauliYGateType):
                s1 = self.diagram.add_spider(phase=math.pi, color="green", origin_qubit_index=self.qubit_indicies[component.target_qubit]) # Y = iZX
                s2 = self.diagram.add_spider(phase=math.pi, color="red", origin_qubit_index=self.qubit_indicies[component.target_qubit])
                self.advance_frontier(s1, component.target_qubit)
                self.advance_frontier(s2, component.target_qubit)

            if isinstance(gate_type, PauliZGateType):
                s = self.diagram.add_spider(phase=math.pi, color="green", origin_qubit_index=self.qubit_indicies[component.target_qubit])
                self.advance_frontier(s, component.target_qubit)
            if isinstance(gate_type, PhaseGateType):
                s = self.diagram.add_spider(phase=math.pi / 2.0, color="green", origin_qubit_index=self.qubit_indicies[component.target_qubit])
                self.advance_frontier(s, component.target_qubit)
            if isinstance(gate_type, TGateType):
                s = self.diagram.add_spider(phase=math.pi / 4.0, color="green", origin_qubit_index=self.qubit_indicies[component.target_qubit])
                self.advance_frontier(s, component.target_qubit)

            #TODO: arbitrary unitary

        else: # controlled gate
            assert isinstance(gate_type, PauliXGateType) or isinstance(gate_type, PauliZGateType), f"Can only parse CX and CZ gates, not {type(gate_type)}"
            assert len(component.control_bits) == 1, "Can only parse controlled gates with one control"

            is_cx = isinstance(gate_type, PauliXGateType)

            control_qubit = cast(QuantumBit, next(iter(component.control_bits)))
            target_qubit = component.target_qubit

            s1 = self.diagram.add_spider(phase=0.0, color="green", origin_qubit_index=self.qubit_indicies[control_qubit])
            s2 = self.diagram.add_spider(phase=0.0, color=("red" if is_cx else "green"), origin_qubit_index=self.qubit_indicies[target_qubit])

            self.diagram.add_wire(s1, s2, is_hadamard=(not is_cx))

            self.advance_frontier(s1, control_qubit)
            self.advance_frontier(s2, target_qubit)

    def advance_frontier(self, new_frontier: Vertex, qubit: QuantumBit):
        old_frontier = self.current_frontier_by_qubit[qubit]

        self.diagram.add_wire(old_frontier, new_frontier, is_hadamard=self.hadamard_status_by_qubit[qubit])

        self.current_frontier_by_qubit[qubit] = new_frontier
        self.hadamard_status_by_qubit[qubit] = False


### Test
if __name__ == "__main__":
    circuit = OpenQasmParser().load_file("./circuits/test/simple_translation_test.qasm")
    diagram = CircuitTranslator(circuit).translate()

    renderer = DiagramRenderer(diagram)
    # renderer = CircuitRenderer(circuit)

    window = Window(renderer)
    window.main_loop()