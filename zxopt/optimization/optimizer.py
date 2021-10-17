from zxopt.data_structures.diagram import Diagram
from zxopt.optimization import OptimizationStrategy
from zxopt.rewriting.matcher import Matcher
from zxopt.util import Loggable
from zxopt.validation import DiagramLinearExtractor, validate_operation_equality
from zxopt.visualization import Window, DiagramRenderer


class Optimizer(Loggable):
    diagram: Diagram
    strategy: OptimizationStrategy
    visualize: bool


    def __init__(self, diagram: Diagram, strategy: OptimizationStrategy, visualize: bool = False):
        super().__init__()
        self.diagram = diagram
        self.strategy = strategy
        self.visualize = visualize


    def optimize(self):
        validator = DiagramLinearExtractor(self.diagram)

        iterations = 0
        while True:
            iterations += 1
            if self.visualize:
                Window(DiagramRenderer(self.diagram)).main_loop()

            next_rule = self.strategy.find_next_rule(self.diagram)

            if next_rule is None:
                self.log.info(f"Diagram optimization took {iterations} iterations")
                return

            self.log.info(f"Iterations: {iterations}, applying {next_rule.name} to diagram")

            transform_before = validator.extract_matrix()

            matcher = Matcher(self.diagram)
            matcher.match_rule(next_rule, apply=True, generate_on_the_fly=True)

            transform_after = validator.extract_matrix()
            rewrite_validity = validate_operation_equality(transform_before, transform_after)

            if rewrite_validity:
                self.log.info("Rewrite performed and validated")
            else:
                self.log.error("INVALID REWRITE DETECTED")