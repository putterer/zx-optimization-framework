from typing import Callable

from zxopt.rewriting import RewriteRule, RewriteVariable
from zxopt.rewriting.rewrite_phase_expression import BinaryOperationExpression, ConstantExpression
from zxopt.rewriting.rewrite_rule import SPIDER_COLOR_WHITE, CONNECTING_WIRES_ANY

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


class ZXRule(RewriteRule):
    def __init__(self):
        super().__init__()

        # TODO