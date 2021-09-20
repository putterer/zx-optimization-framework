

"""
An expression in the phase of a spider of a rewrite structure
"""
import abc
from typing import Callable, Set


class RewritePhaseExpression:
    def __init__(self):
        pass

    """
    Evaluate this expression
    will fail if some variables haven't resolved yet or the expression contains arbitrary statements
    """
    @abc.abstractmethod
    def evaluate(self) -> float:
        raise NotImplementedError()

    """
    Check if the given value matches this expression
    """
    @abc.abstractmethod
    def matches(self, value: float, epsilon: float = 0.00001) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def is_resolved(self) -> bool:
        raise NotImplementedError()

    """
    Reset the expression before reuse, clearing out any set variables
    """
    def reset(self):
        pass

    """
    Return all variables in this expression
    """
    @abc.abstractmethod
    def variables(self) -> Set["RewriteVariable"]:
        raise NotImplementedError()


"""
Represents a variable in a rewrite structure for capturing a value and applying it to the target rewrite structure
"""
class RewriteVariable(RewritePhaseExpression):
    resolved: bool # has this variable been resolved in the found subgraph / copied over from the source structure yet?
    value: float

    def __init__(self):
        super().__init__()

        self.resolved = False
        self.value = 0.0

    def evaluate(self) -> float:
        if not self.resolved:
            raise ValueError("This variable has not yet resolved")
        else:
            return self.value

    def matches(self, value: float, epsilon: float = 0.00001) -> bool:
        if self.resolved:
            return abs(value - self.value) < epsilon
        else:
            self.resolve(value)
            return True

    def is_resolved(self) -> bool:
        return self.resolved

    def resolve(self, value: float):
        self.resolved = True
        self.value = value

    def reset(self):
        self.resolved = False
        self.value = 0.0

    def variables(self) -> Set["RewriteVariable"]:
        return {self}


class ConstantExpression(RewritePhaseExpression):
    constant_value: float

    def __init__(self, value: float):
        super().__init__()
        self.constant_value = value

    def evaluate(self) -> float:
        return self.constant_value

    def matches(self, value: float, epsilon: float = 0.00001) -> bool:
        return abs(self.constant_value - value) < epsilon

    def is_resolved(self) -> bool:
        return True

    def variables(self) -> Set[RewriteVariable]:
        return set()

class BinaryOperationExpression(RewritePhaseExpression):
    left_expr: RewritePhaseExpression
    right_expr: RewritePhaseExpression
    operation: Callable

    def __init__(self, left_expr: RewritePhaseExpression, right_expr: RewritePhaseExpression, operation: Callable):
        super().__init__()
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.operation = operation

    def evaluate(self) -> float:
        return self.operation(self.left_expr.evaluate(), self.right_expr.evaluate())

    def matches(self, value: float, epsilon: float = 0.00001) -> bool:
        return abs(self.evaluate() - value) < epsilon # TODO: this would be non deterministic and in its current form will prevent a such a rule from being applied in the inverse, non deterministic direction

    def is_resolved(self) -> bool:
        return self.left_expr.is_resolved() and self.right_expr.is_resolved()

    def reset(self):
        self.left_expr.reset()
        self.right_expr.reset()

    def variables(self) -> Set[RewriteVariable]:
        return self.left_expr.variables().union(self.right_expr.variables())