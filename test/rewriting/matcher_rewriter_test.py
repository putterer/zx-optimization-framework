import unittest
from math import pi

from graph_tool import Vertex

from zxopt.data_structures.diagram import Diagram
from zxopt.rewriting import RewriteRule
from zxopt.rewriting.matcher import Matcher
from zxopt.rewriting.zx_calculus import ZXRuleSpider1, ZXRuleSpider2
from zxopt.visualization import DiagramRenderer, Window

SHOW_REWRITES = False
GENERATE_ISOMORPHISMS_ON_THE_FLY = False

class MatcherRewriterTest(unittest.TestCase):

    def test_spider_rule_1_match(self):
        diagram = generate_three_spider_diagram((1.0 * pi, "green"), (0.5 * pi, "red"), (0.25 * pi, "red"))
        self.assertTrue(rule_matches(diagram, ZXRuleSpider1()))

        diagram = generate_three_spider_diagram((1.0 * pi, "red"), (0.5 * pi, "red"), (0.25 * pi, "green"))
        self.assertTrue(rule_matches(diagram, ZXRuleSpider1()))

        diagram = generate_three_spider_diagram((1.0 * pi, "green"), (0.5 * pi, "red"), (0.25 * pi, "green"))
        self.assertFalse(rule_matches(diagram, ZXRuleSpider1()))

    def test_spider_rule_1_rewrite(self):
        diagram = generate_three_spider_diagram((1.0 * pi, "green"), (0.5 * pi, "red"), (0.25 * pi, "red"))

        show(diagram)

        rewrite(diagram, ZXRuleSpider1())
        b_in, b_out, s1, s2, s3 = get_three_spider_diagram_vertices(diagram)
        s_new = [s for s in diagram.get_spiders() if s != s1]

        self.assertAlmostEqual(1.0 * pi, diagram.get_spider_phase(s1))
        self.assertEqual("green", diagram.get_spider_color(s1))

        self.assertEqual(1, len(s_new))
        self.assertAlmostEqual(0.75 * pi, diagram.get_spider_phase(s_new[0]))
        self.assertEqual("red", diagram.get_spider_color(s_new[0]))

        show(diagram)

    def test_spider_rule_2_match(self):
        diagram = generate_three_spider_diagram((1.0*pi, "green"), (0.0*pi, "red"), (1.0*pi, "green"))
        self.assertTrue(rule_matches(diagram, ZXRuleSpider2()))

        diagram = generate_three_spider_diagram((1.0*pi, "green"), (1.0*pi, "red"), (0.0*pi, "red"))
        self.assertTrue(rule_matches(diagram, ZXRuleSpider2()))

        diagram = generate_three_spider_diagram((1.0*pi, "green"), (1.0*pi, "red"), (0.1*pi, "red"))
        self.assertFalse(rule_matches(diagram, ZXRuleSpider2()))

        diagram = generate_three_spider_diagram((1.0*pi, "green"), (1.0*pi, "red"), (0.1*pi, "red"))
        # TODO: 3 neighbors

    def test_spider_rule_2_rewrite(self):
        # TODO: hadamards
        pass


def generate_three_spider_diagram(p1: tuple[float, str], p2: tuple[float, str], p3: tuple[float, str], star_topology: bool = False) -> Diagram:
    diagram = Diagram()
    b_in = diagram.add_boundary("in", 0, "b_in")
    b_out = diagram.add_boundary("out", 0, "b_out")
    s1 = diagram.add_spider(p1[0], p1[1], 0, "s1")
    s2 = diagram.add_spider(p2[0], p2[1], 0, "s2")
    s3 = diagram.add_spider(p3[0], p3[1], 0, "s3")
    diagram.add_wire(b_in, s1)
    diagram.add_wire(s1, s2)
    diagram.add_wire(s2, s3)
    if not star_topology:
        diagram.add_wire(s3, b_out)
    else:
        diagram.add_wire(s2, b_out)
    return diagram

def get_three_spider_diagram_vertices(diagram: Diagram) -> tuple[Vertex, Vertex, Vertex, Vertex, Vertex]:
    return diagram.get_vertex_from_identifier("b_in"), diagram.get_vertex_from_identifier("b_out"), diagram.get_vertex_from_identifier("s1"), diagram.get_vertex_from_identifier("s2"), diagram.get_vertex_from_identifier("s3")


def rule_matches(diagram: Diagram, rule: RewriteRule, generate_on_the_fly: bool = GENERATE_ISOMORPHISMS_ON_THE_FLY) -> bool:
    matcher = Matcher(diagram)
    match = matcher.match_rule(rule, apply=False, generate_on_the_fly=generate_on_the_fly)
    return match is not None

def rewrite(diagram: Diagram, rule: RewriteRule, generate_on_the_fly: bool = GENERATE_ISOMORPHISMS_ON_THE_FLY):
    matcher = Matcher(diagram)
    match = matcher.match_rule(rule, apply=True, generate_on_the_fly=generate_on_the_fly)

def show(diagram: Diagram):
    if SHOW_REWRITES:
        renderer = DiagramRenderer(diagram)
        window = Window(renderer)
        window.main_loop()