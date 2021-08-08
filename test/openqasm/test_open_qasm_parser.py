
from zxopt.openqasm import OpenQasmParser

### Test
if __name__ == "__main__":
    parser = OpenQasmParser()
    circuit = parser.load_file("circuits/test/recursion_test.qasm")