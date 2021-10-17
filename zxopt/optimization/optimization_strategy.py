import abc
import random
from typing import List, Optional

from zxopt.data_structures.diagram import Diagram
from zxopt.rewriting import RewriteRule
from zxopt.rewriting.matcher import Matcher


class OptimizationStrategy:

    def __init__(self):
        pass

    @abc.abstractmethod
    def find_next_rule(self, diagram: Diagram) -> Optional[RewriteRule]:
        raise NotImplementedError()

"""
Executes rules by rank, when one rules matches, returns back to the top of the list and starts again
"""
class RankedOptimizationStrategy(OptimizationStrategy):
    simplifier: "Simplifier"

    def __init__(self, simplifier: "Simplifier"):
        super().__init__()
        self.simplifier = simplifier

    def find_next_rule(self, diagram: Diagram) -> Optional[RewriteRule]:
        order_rules_considered = self.simplifier.rules()

        matcher = Matcher(diagram)
        for rule in order_rules_considered:
            match = matcher.match_rule(rule, apply=False, generate_on_the_fly=True)

            if match is not None:
                return rule

        return None

class Simplifier:
    """
    Returns an ordered list of rules to be applied
    """
    @abc.abstractmethod
    def rules(self) -> List[RewriteRule]:
        raise NotImplementedError()

class SingleRuleSimplifier(Simplifier):
    rule: RewriteRule

    def __init__(self, rule: RewriteRule):
        self.rule = rule

    def rules(self) -> List[RewriteRule]:
        return [self.rule]

class CompoundSimplifier(Simplifier):
    simplifiers: List[Simplifier]
    randomized: bool

    def __init__(self, simplifiers: List[Simplifier], randomized: bool = False):
        self.simplifiers = simplifiers
        self.randomized = randomized

    def rules(self) -> List[RewriteRule]:
        rules = []
        for s in self.simplifiers:
            for r in s.rules():
                rules.append(r)

        if self.randomized:
            random.shuffle(rules)

        return rules

class RandomizedCompoundSimplifier(CompoundSimplifier):
    def __init__(self, simplifiers: List[Simplifier]):
        super(RandomizedCompoundSimplifier, self).__init__(simplifiers=simplifiers, randomized=True)