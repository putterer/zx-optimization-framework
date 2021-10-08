import numpy as np

from zxopt.data_structures.diagram import Diagram
from zxopt.rewriting import RewriteRule
from zxopt.rewriting.matcher import Matcher
from zxopt.rewriting.rewrite_phase_expression import ConstantExpression
from zxopt.rewriting.rewrite_rule import SPIDER_COLOR_WHITE, CONNECTING_WIRES_ANY
from zxopt.rewriting.zx_calculus.zx_calculus_rules import ZXRuleHopfLaw


class ParallelLoopEdgeRemover:
    diagram: Diagram

    def __init__(self, diagram: Diagram):
        self.diagram = diagram

    """
    Remove all parallel edges present in the diagram that can be removed using the calculus
    """
    def remove_parallel_edges(self):
        matcher = Matcher(self.diagram)

        while True:
            normal_matched = matcher.match_rule(ParallelNormalEdgeRule(), apply=True)
            single_matched = matcher.match_rule(ParallelSingleHadEdgeRule(), apply=True)
            double_matched = matcher.match_rule(ParallelDoubleHadEdgeRule(), apply=True)
            hopf_law_matched = matcher.match_rule(ZXRuleHopfLaw(), apply=True)

            if normal_matched is None and single_matched is None and double_matched is None and hopf_law_matched is None:
                break

    """
    Remove all self loop edges present in the diagram that can be removed using the calculus
    """
    def remove_self_loops(self):
        matcher = Matcher(self.diagram)

        while True:
            normal_matched = matcher.match_rule(SelfLoopNormalRule(), apply=True)
            hadamard_matched = matcher.match_rule(SelfLoopHadamardRule(), apply=True)

            if normal_matched is None and hadamard_matched is None:
                break


class ParallelNormalEdgeRule(RewriteRule):

    def __init__(self):
        super().__init__()

        s1_source = self.source.add_spider(SPIDER_COLOR_WHITE, ConstantExpression(0), CONNECTING_WIRES_ANY, 0)
        s2_source = self.source.add_spider(SPIDER_COLOR_WHITE, ConstantExpression(0), CONNECTING_WIRES_ANY, 0)
        w1_source = self.source.add_wire(s1_source, s2_source, False)
        w2_source = self.source.add_wire(s1_source, s2_source, False)

        s1_target = self.source.add_spider(SPIDER_COLOR_WHITE, ConstantExpression(0), CONNECTING_WIRES_ANY, 0)
        s2_target = self.source.add_spider(SPIDER_COLOR_WHITE, ConstantExpression(0), CONNECTING_WIRES_ANY, 0)
        w1_target = self.target.add_wire(s1_source, s2_source, False)

        self.connecting_wires_spider_mapping[s1_source] = s1_target
        self.connecting_wires_spider_mapping[s2_source] = s2_target

    def inverse(self):
        raise NotImplementedError()

class ParallelSingleHadEdgeRule(RewriteRule):

    def __init__(self):
        super().__init__()

        s1_source = self.source.add_spider(SPIDER_COLOR_WHITE, ConstantExpression(0), CONNECTING_WIRES_ANY, 0)
        s2_source = self.source.add_spider(SPIDER_COLOR_WHITE, ConstantExpression(0), CONNECTING_WIRES_ANY, 0)
        w1_source = self.source.add_wire(s1_source, s2_source, True)
        w2_source = self.source.add_wire(s1_source, s2_source, False)

        s1_target = self.source.add_spider(SPIDER_COLOR_WHITE, ConstantExpression(np.pi), CONNECTING_WIRES_ANY, 0)
        s2_target = self.source.add_spider(SPIDER_COLOR_WHITE, ConstantExpression(0), CONNECTING_WIRES_ANY, 0)
        w1_target = self.target.add_wire(s1_source, s2_source, False)

        self.connecting_wires_spider_mapping[s1_source] = s1_target
        self.connecting_wires_spider_mapping[s2_source] = s2_target

    def inverse(self):
        raise NotImplementedError()


class ParallelDoubleHadEdgeRule(RewriteRule):

    def __init__(self):
        super().__init__()

        s1_source = self.source.add_spider(SPIDER_COLOR_WHITE, ConstantExpression(0), CONNECTING_WIRES_ANY, 0)
        s2_source = self.source.add_spider(SPIDER_COLOR_WHITE, ConstantExpression(0), CONNECTING_WIRES_ANY, 0)
        w1_source = self.source.add_wire(s1_source, s2_source, True)
        w2_source = self.source.add_wire(s1_source, s2_source, True)

        s1_target = self.source.add_spider(SPIDER_COLOR_WHITE, ConstantExpression(0), CONNECTING_WIRES_ANY, 0)
        s2_target = self.source.add_spider(SPIDER_COLOR_WHITE, ConstantExpression(0), CONNECTING_WIRES_ANY, 0)

        self.connecting_wires_spider_mapping[s1_source] = s1_target
        self.connecting_wires_spider_mapping[s2_source] = s2_target

    def inverse(self):
        raise NotImplementedError()

class SelfLoopNormalRule(RewriteRule):

    def __init__(self):
        super().__init__()

        s1_source = self.source.add_spider(SPIDER_COLOR_WHITE, ConstantExpression(0), CONNECTING_WIRES_ANY, 0)
        w1_source = self.source.add_wire(s1_source, s1_source, False)

        s1_target = self.source.add_spider(SPIDER_COLOR_WHITE, ConstantExpression(0), CONNECTING_WIRES_ANY, 0)

        self.connecting_wires_spider_mapping[s1_source] = s1_target

    def inverse(self):
        raise NotImplementedError()

class SelfLoopHadamardRule(RewriteRule):

    def __init__(self):
        super().__init__()

        s1_source = self.source.add_spider(SPIDER_COLOR_WHITE, ConstantExpression(0), CONNECTING_WIRES_ANY, 0)
        w1_source = self.source.add_wire(s1_source, s1_source, False)

        s1_target = self.source.add_spider(SPIDER_COLOR_WHITE, ConstantExpression(np.pi), CONNECTING_WIRES_ANY, 0)

        self.connecting_wires_spider_mapping[s1_source] = s1_target

    def inverse(self):
        raise NotImplementedError()