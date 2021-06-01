import math
from typing import cast

from graph_tool import Vertex

from zxopt.data_structures.circuit import Circuit, CircuitComponent, GateComponent, PauliXGateType, HadamardGateType, \
    PauliZGateType
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

    def __init__(self, circuit: Circuit):
        super().__init__()
        self.circuit = circuit
        self.diagram = Diagram()
        self.input_boundaries_by_qubit = {}
        self.output_boundaries_by_qubit = {}

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
                s = self.diagram.add_spider(phase=math.pi, color="red")
                self.advance_frontier(s, component.target_qubit)
            # TODO: Y gate
            if isinstance(gate_type, PauliZGateType):
                s = self.diagram.add_spider(phase=math.pi, color="green")
                self.advance_frontier(s, component.target_qubit)
            # if isinstance(gate_type, PhaseGateType): #TODO
            #     s = self.diagram.add_spider(phase=math.pi, color="red")
            #     self.advance_frontier(s, component.target_qubit)
            # if isinstance(gate_type, TGateType): #TODO
            #     s = self.diagram.add_spider(phase=math.pi, color="red")
            #     self.advance_frontier(s, component.target_qubit)

            #TODO: arbitrary unitary

        else: # controlled X
            assert isinstance(gate_type, PauliXGateType), "Can only parse controlled not (CX) gates"
            assert len(component.control_bits) == 1, "Can only parse controlled gates with one control"

            green_spider = self.diagram.add_spider(phase=0.0, color="green")
            red_spider = self.diagram.add_spider(phase=0.0, color="red")

            self.diagram.add_wire(green_spider, red_spider)

            self.advance_frontier(green_spider, cast(QuantumBit, next(iter(component.control_bits))))
            self.advance_frontier(red_spider, component.target_qubit)

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