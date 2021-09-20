from typing import Callable

from zxopt.rewriting import RewriteRule, RewriteVariable
from zxopt.rewriting.rewrite_phase_expression import BinaryOperationExpression, ConstantExpression
from zxopt.rewriting.rewrite_rule import SPIDER_COLOR_WHITE, CONNECTING_WIRES_ANY, SPIDER_COLOR_BLACK

OP_ADDITION: Callable = lambda a, b: a + b

class ZXRuleSpider1(RewriteRule):
    def __init__(self):
        super().__init__()

        alpha_source = RewriteVariable()
        beta_source = RewriteVariable()
        s1_source = self.source.add_spider(SPIDER_COLOR_WHITE, alpha_source, CONNECTING_WIRES_ANY, 0)
        s2_source = self.source.add_spider(SPIDER_COLOR_WHITE, beta_source, CONNECTING_WIRES_ANY, 0)
        w1_source = self.source.add_wire(s1_source, s2_source, is_hadamard=False)

        alpha_target = RewriteVariable()
        beta_target = RewriteVariable()
        s_target = self.target.add_spider(SPIDER_COLOR_WHITE, BinaryOperationExpression(alpha_target, beta_target, OP_ADDITION), CONNECTING_WIRES_ANY, 0)

        self.variable_mapping[alpha_source] = alpha_target
        self.variable_mapping[beta_source] = beta_target
        self.connecting_wires_spider_mapping[s1_source] = s_target
        self.connecting_wires_spider_mapping[s2_source] = s_target

    def inverse(self):
        raise NotImplementedError() # TODO


class ZXRuleSpider2(RewriteRule):
    def __init__(self):
        super().__init__()

        s_source = self.source.add_spider(SPIDER_COLOR_WHITE, ConstantExpression(0.0), 2, 0) # hadamard count not matched, none flipped!

        self.connecting_wires_spider_mapping[s_source] = None

    def inverse(self):
        raise NotImplementedError() # TODO


class ZXRuleBialgebraLaw(RewriteRule):
    def __init__(self):
        super().__init__()

        s11_source = self.source.add_spider(SPIDER_COLOR_WHITE, ConstantExpression(0.0), 1, 0)
        s12_source = self.source.add_spider(SPIDER_COLOR_WHITE, ConstantExpression(0.0), 1, 0)
        s21_source = self.source.add_spider(SPIDER_COLOR_BLACK, ConstantExpression(0.0), 1, 0)
        s22_source = self.source.add_spider(SPIDER_COLOR_BLACK, ConstantExpression(0.0), 1, 0)
        w1_source = self.source.add_wire(s11_source, s21_source, is_hadamard=False)
        w2_source = self.source.add_wire(s11_source, s22_source, is_hadamard=False)
        w3_source = self.source.add_wire(s12_source, s21_source, is_hadamard=False)
        w4_source = self.source.add_wire(s12_source, s22_source, is_hadamard=False)

        s1_target = self.target.add_spider(SPIDER_COLOR_WHITE, ConstantExpression(0.0), 1, 0)
        s2_target = self.target.add_spider(SPIDER_COLOR_BLACK, ConstantExpression(0.0), 1, 0)
        w1_target = self.target.add_wire(s1_target, s2_target, is_hadamard=False)

        self.connecting_wires_spider_mapping[s11_source] = s1_target
        self.connecting_wires_spider_mapping[s12_source] = s1_target
        self.connecting_wires_spider_mapping[s21_source] = s2_target
        self.connecting_wires_spider_mapping[s22_source] = s2_target

    def inverse(self):
        raise NotImplementedError() # TODO


class ZXRule(RewriteRule):
    def __init__(self):
        super().__init__()

        # TODO