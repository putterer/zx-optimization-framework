from typing import Union

from zxopt.data_structures.circuit import Circuit
from zxopt.data_structures.diagram import Diagram
from zxopt.openqasm import OpenQasmParser
from zxopt.optimization import Optimizer, RankedOptimizationStrategy, CompoundSimplifier, SingleRuleSimplifier
from zxopt.optimization.optimization_strategy import RandomizedCompoundSimplifier
from zxopt.rewriting.zx_calculus.zx_calculus_rules import ZXRuleBialgebraLaw, ZXRuleSpider2, ZXRuleSpider1, \
    ZXRuleHopfLaw, ZXRulePiCommutation, ZXRuleColor, ZXRuleCopying
from zxopt.translation import CircuitTranslator
from zxopt.visualization import DiagramRenderer, Window, CircuitRenderer


# class OptimizationTest(unittest.TestCase):
#
#     def __init__(self):
#         super().__init__()

def render(object: Union[Circuit, Diagram]):
    if type(object) == Circuit:
        renderer = CircuitRenderer(object)
    elif type(object) == Diagram:
        renderer = DiagramRenderer(object)
    else:
        raise NotImplementedError("Cannot render object of type %s yet" % (type(object)))

    window = Window(renderer)
    window.main_loop()


# best, most reducing, hardest to get first, most destroying last
DEFAULT_ZX_RANKED_OPTIMIZATION_STRATEGY = RankedOptimizationStrategy( # TODO: this trusts the rule resetting process, instead reinstantiate every time?
    CompoundSimplifier([
        RandomizedCompoundSimplifier([
            SingleRuleSimplifier(ZXRuleBialgebraLaw())
        ]),
        RandomizedCompoundSimplifier([
            SingleRuleSimplifier(ZXRuleSpider1()),
            SingleRuleSimplifier(ZXRuleSpider2()),
            SingleRuleSimplifier(ZXRulePiCommutation()) # self inverse
        ]),
        RandomizedCompoundSimplifier([
            SingleRuleSimplifier(ZXRuleCopying()),
            SingleRuleSimplifier(ZXRuleCopying().inverse()),
            SingleRuleSimplifier(ZXRuleHopfLaw()),
            SingleRuleSimplifier(ZXRuleHopfLaw().inverse()),
            # SingleRuleSimplifier(ZXRuleBialgebraLaw().inverse()),
        ]),
        SingleRuleSimplifier(ZXRuleBialgebraLaw().inverse()),
        SingleRuleSimplifier(ZXRuleColor())
    ])
)

"""
Tests if a swap circuit consisting of three CNOT gates can be optimized away to the identity 
"""
def test_optimization_sawp_circuit():
    circuit = OpenQasmParser().load_file("./circuits/swap.qasm")
    # circuit = OpenQasmParser().load_file("./circuits/teleportation.qasm")
    render(circuit)

    diagram = CircuitTranslator(circuit).translate()
    # render(diagram)

    optimizer = Optimizer(diagram, DEFAULT_ZX_RANKED_OPTIMIZATION_STRATEGY, visualize=True)
    optimizer.optimize()

if __name__ == '__main__':
    test_optimization_sawp_circuit()