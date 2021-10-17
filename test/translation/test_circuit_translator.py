from zxopt.openqasm import OpenQasmParser
from zxopt.translation import CircuitTranslator
from zxopt.visualization import DiagramRenderer, Window, CircuitRenderer

# The unit test is part of "test_circuit_diagram_translation_equality"

### Test
# Reads a simple test circuit, translates it to a diagram and renders the diagram
if __name__ == "__main__":
    circuit = OpenQasmParser().load_file("./circuits/test/bell_state_test_circuit.qasm")
    diagram = CircuitTranslator(circuit).translate()

    circuit_renderer = CircuitRenderer(circuit)
    diagram_renderer = DiagramRenderer(diagram, disable_alignment=False)

    window = Window(circuit_renderer)
    window.main_loop()

    window = Window(diagram_renderer)
    window.main_loop()