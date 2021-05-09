"""
This module allows representing quantum circuits based on their individual components
"""

__all__ = [
    "Circuit",
    "CircuitComponent",
    "GateComponent",
    "BarrierComponent",
    "MeasurementComponent",
    "Register",
    "RegisterBit",
    "ClassicalRegister",
    "ClassicalBit",
    "QuantumRegister",
    "QuantumBit",
    "Gate",
    "UnitaryGate",
    "IdentityGate",
    "PauliXGate",
    "PauliYGate",
    "PauliZGate",
    "HadamardGate",
    "PhaseGate",
    "TGate",
]

from zxopt.data_structures.circuit.barrier_component import BarrierComponent
from zxopt.data_structures.circuit.circuit import Circuit
from zxopt.data_structures.circuit.circuit_component import CircuitComponent
from zxopt.data_structures.circuit.gate_component import GateComponent, Gate, UnitaryGate, PauliXGate, \
    PauliYGate, PauliZGate, HadamardGate, PhaseGate, TGate
from zxopt.data_structures.circuit.measurement_component import MeasurementComponent
from zxopt.data_structures.circuit.register.classical_register import ClassicalRegister, ClassicalBit
from zxopt.data_structures.circuit.register.quantum_register import QuantumRegister, QuantumBit
from zxopt.data_structures.circuit.register.register import Register, RegisterBit
