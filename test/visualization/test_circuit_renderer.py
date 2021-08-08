
from zxopt.openqasm import OpenQasmParser
from zxopt.visualization import CircuitRenderer, Window

### Circuit renderer test
# Loads a bell swap circuit from QASM and displays it
if __name__ == "__main__":
    circuit = OpenQasmParser().load_file("./circuits/bell_swap.qasm")
    renderer = CircuitRenderer(circuit)

    window = Window(renderer)
    window.main_loop()