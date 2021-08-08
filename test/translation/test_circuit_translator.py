from zxopt.openqasm import OpenQasmParser
from zxopt.translation import CircuitTranslator
from zxopt.visualization import DiagramRenderer, Window

# The unit test is part of "test_circuit_diagram_translation_equality"

### Test
# Reads a simple test circuit, translates it to a diagram and renders the diagram
if __name__ == "__main__":
    circuit = OpenQasmParser().load_file("./circuits/test/simple_translation_test.qasm")
    diagram = CircuitTranslator(circuit).translate()

    renderer = DiagramRenderer(diagram, disable_alignment=False)
    # renderer = CircuitRenderer(circuit)

    window = Window(renderer)
    window.main_loop()