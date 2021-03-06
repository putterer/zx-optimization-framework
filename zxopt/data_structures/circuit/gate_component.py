from math import sqrt, pi
from typing import Set

import numpy as np

from zxopt.data_structures.circuit.circuit_component import CircuitComponent
from zxopt.data_structures.circuit.register.quantum_register import QuantumBit
from zxopt.data_structures.circuit.register.register import RegisterBit
from zxopt.util.toolbox import round_complex


class GateComponent(CircuitComponent):
    target_qubit: QuantumBit
    control_bits: Set[RegisterBit]
    gate_type: "GateType"

    def __init__(self, target_qubit: QuantumBit, gate_type: "GateType", control_bits: Set[RegisterBit] = frozenset()):
        super().__init__(control_bits.union({target_qubit}))

        self.target_qubit = target_qubit
        self.control_bits = control_bits
        self.gate_type = gate_type


class GateType:
    representation: str

    def __init__(self, representation: str, matrix: np.ndarray):
        self.representation = representation
        self.matrix = matrix

class UnitaryGateType(GateType): # defines an arbitrary unitary gate used by the QE OpenQASM library to define all other gates
    def __init__(self, representation: str, theta: float = None, phi: float = None, lmbda: float = 0.0):
        self.representation = representation

        if theta is None and phi is None:
            theta = 0
            phi = 0
        if theta is None:
            theta = pi / 2.0

        super().__init__(representation, np.array([
            [round_complex(np.exp(-1j * (phi+lmbda) / 2.0) * np.cos(theta / 2.0)),   round_complex((-1.0) * np.exp(-1j * (phi-lmbda) / 2.0) * np.sin(theta / 2.0))], # todo: unit test
            [round_complex(np.exp(1j * (phi-lmbda) / 2.0) * np.sin(theta / 2.0)),    round_complex(np.exp(1j * (phi+lmbda) / 2.0) * np.cos(theta / 2.0))]
        ]))

# OpenQASM also defines the CX gate, this implementation supports all gates as controllable and therefore uses the normal X gate

class HadamardGateType(GateType): # todo unit test (e.g. self inverse, pauli algebra...)
    def __init__(self):
        super().__init__("H", np.array([
            [1, 1],
            [1, -1]
        ]) * (1.0 / sqrt(2)))

class PauliXGateType(GateType):
    def __init__(self):
        super().__init__("X", np.array([
            [0, 1],
            [1, 0]
        ]))

class PauliYGateType(GateType):
    def __init__(self):
        super().__init__("Y", np.array([
            [0, -1j],
            [-1j, 0]
        ]))

class PauliZGateType(GateType):
    def __init__(self):
        super().__init__("Z", np.array([
            [1, 0],
            [0, -1]
        ]))

class PhaseGateType(GateType):
    def __init__(self):
        super().__init__("S", np.array([
            [1, 0],
            [0, 1j]
        ]))

class TGateType(GateType):
    def __init__(self):
        super().__init__("T", np.array([
            [1, 0],
            [0, np.exp(1j * pi / 4.0)]
        ]))



# class IdentityGate(UnitaryGate): # definitions see qelib1.inc
#     def __init__(self):
#         super().__init__("I", 0.0, 0.0, 0.0)
#
# class PauliXGate(UnitaryGate):
#     def __init__(self):
#         super().__init__("X", pi, 0.0, pi)
#
# class PauliYGate(UnitaryGate):
#     def __init__(self):
#         super().__init__("X", pi, pi/2.0, pi/2.0)
#
# class PauliZGate(UnitaryGate):
#     def __init__(self):
#         super().__init__("X", lmbda = pi)
#
# class HadamardGate(UnitaryGate):
#     def __init__(self):
#         super().__init__("H", phi = 0.0, lmbda = pi)
#
# class PhaseGate(UnitaryGate):
#     def __init__(self):
#         super().__init__("S", lmbda = pi/2.0)
#
# class TGate(UnitaryGate):
#     def __init__(self):
#         super().__init__("X", lmbda = pi/4.0)