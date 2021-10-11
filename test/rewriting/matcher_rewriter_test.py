import unittest
from math import pi
from typing import Tuple

from graph_tool import Vertex

from zxopt.data_structures.diagram import Diagram
from zxopt.rewriting import RewriteRule
from zxopt.rewriting.matcher import Matcher
from zxopt.rewriting.zx_calculus import ZXRuleSpider1, ZXRuleSpider2
from zxopt.rewriting.zx_calculus.zx_calculus_rules import ZXRuleBialgebraLaw, ZXRulePiCommutation, ZXRuleColor, \
    ZXRuleCopying, ZXRuleHopfLaw
from zxopt.visualization import DiagramRenderer, Window

SHOW_REWRITES = True
GENERATE_ISOMORPHISMS_ON_THE_FLY = True

class MatcherRewriterTest(unittest.TestCase):

    def assert_wire(self, s1: Vertex, s2: Vertex):
        self.assertEqual(1, len(list(filter(lambda x: x == s2, s1.all_neighbors()))))
        return [w for w in s1.all_edges() if w.source() == s2 or w.target() == s2][0]

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

        # Test for spider with 3 neighbors
        diagram = generate_three_spider_diagram((1.0*pi, "red"), (0.0*pi, "red"), (0.1*pi, "red"))
        b_in, b_out, s1, s2, s3 = get_three_spider_diagram_vertices(diagram)
        s4 = diagram.add_spider(0.5 * pi, "red", 1)
        diagram.add_wire(s2, s4)
        # show(diagram)
        self.assertFalse(rule_matches(diagram, ZXRuleSpider2()))

    def test_spider_rule_2_rewrite(self):
        diagram = generate_three_spider_diagram((1.0 * pi, "green"), (0.0 * pi, "red"), (0.7 * pi, "red"), hadamard=(True, True, False, False))
        rewrite(diagram, ZXRuleSpider2())
        b_in, b_out, s1, s2, s3 = get_three_spider_diagram_vertices(diagram)

        self.assertTrue(s2 is None)
        self.assertEqual(2, len(diagram.get_spiders()))
        self.assertEqual(1.0 * pi, diagram.get_spider_phase(s1))
        self.assertEqual(0.7 * pi, diagram.get_spider_phase(s3))
        self.assertEqual("green", diagram.get_spider_color(s1))
        self.assertEqual("red", diagram.get_spider_color(s3))

        w13 = self.assert_wire(s1, s3)
        w01 = self.assert_wire(b_in, s1)
        w34 = self.assert_wire(s3, b_out)
        self.assertTrue(diagram.is_wire_hadamard(w13))
        self.assertTrue(diagram.is_wire_hadamard(w01))
        self.assertFalse(diagram.is_wire_hadamard(w34))
        # show(diagram)

    def test_bialgebra_law_matches(self):
        diagram = generate_bialegbra_law_diagram((0.0, "green"), (0.0, "green"), (0.0, "red"), (0.0, "red"))
        self.assertTrue(rule_matches(diagram, ZXRuleBialgebraLaw()))

        diagram = generate_bialegbra_law_diagram((0.0, "green"), (0.0, "green"), (0.0, "red"), (0.0, "green"))
        self.assertFalse(rule_matches(diagram, ZXRuleBialgebraLaw()))

        diagram = generate_bialegbra_law_diagram((0.0, "green"), (0.0, "green"), (0.0, "green"), (0.0, "green"))
        self.assertFalse(rule_matches(diagram, ZXRuleBialgebraLaw()))

        diagram = generate_bialegbra_law_diagram((0.0, "green"), (0.1 * pi, "green"), (0.0, "red"), (0.0, "red"))
        self.assertFalse(rule_matches(diagram, ZXRuleBialgebraLaw()))

        diagram = generate_bialegbra_law_diagram((0.0, "green"), (0.0, "green"), (0.0, "red"), (0.0, "green"), hadamard=(False, True, False, False))
        self.assertFalse(rule_matches(diagram, ZXRuleBialgebraLaw()))

        diagram = generate_bialegbra_law_diagram((0.0, "green"), (0.0, "green"), (0.0, "red"), (0.0, "green"), internal_wiring=(True, True, False, True))
        self.assertFalse(rule_matches(diagram, ZXRuleBialgebraLaw()))

        pass

    def test_bialgebra_law_rewrite_inverse_rewrite(self):
        diagram = generate_bialegbra_law_diagram((0.0, "green"), (0.0, "green"), (0.0, "red"), (0.0, "red"))
        diagram.set_wire_hadamard(next(diagram.get_vertex_from_identifier("b_in1").all_edges()), True)

        show(diagram)
        rewrite(diagram, ZXRuleBialgebraLaw())
        show(diagram)

        self.assertFalse(rule_matches(diagram, ZXRuleBialgebraLaw()))

        self.assertTrue(rule_matches(diagram, ZXRuleBialgebraLaw().inverse()))
        rewrite(diagram, ZXRuleBialgebraLaw().inverse())
        show(diagram)


    def test_pi_comm_matches(self):
        diagram = generate_three_spider_diagram((1.0 * pi, "red"), (0.25 * pi, "green"), (0.5 * pi, "red"), hadamard=(True, False, False, False))
        self.assertTrue(rule_matches(diagram, ZXRulePiCommutation()))

        diagram = generate_three_spider_diagram((1.0 * pi, "red"), (0.25 * pi, "red"), (0.5 * pi, "red"), hadamard=(True, False, False, False)) # color fail
        self.assertFalse(rule_matches(diagram, ZXRulePiCommutation()))

        diagram = generate_three_spider_diagram((0.75 * pi, "red"), (0.25 * pi, "green"), (0.5 * pi, "red"), hadamard=(True, False, False, False)) # phase fail
        self.assertFalse(rule_matches(diagram, ZXRulePiCommutation()))

        diagram = generate_three_spider_diagram((1.0 * pi, "red"), (0.25 * pi, "green"), (0.5 * pi, "red"), hadamard=(False, True, False, False)) # hadamard fail
        self.assertFalse(rule_matches(diagram, ZXRulePiCommutation()))

    def test_pi_comm_rewrite(self):
        diagram = generate_three_spider_diagram((1.0 * pi, "red"), (0.25 * pi, "green"), (0.5 * pi, "red"), hadamard=(True, False, False, False))

        show(diagram)
        rewrite(diagram, ZXRulePiCommutation())
        b_in, b_out, s1, s2, s3 = get_three_spider_diagram_vertices(diagram)
        # w01 = self.assert_wire(b_in, s1)
        # self.assertTrue(diagram.is_wire_hadamard(w01))

        show(diagram) # Not verifying the 2 new spiders, check manually!

    def test_color_rule_matches(self):
        diagram = generate_three_spider_diagram((1.0 * pi, "red"), (0.5 * pi, "green"), (0.25 * pi, "red"), hadamard=(True, False, False, False))
        self.assertTrue(rule_matches(diagram, ZXRuleColor()))

    def test_color_rule_rewrite(self):
        diagram = generate_three_spider_diagram((1.0 * pi, "red"), (0.5 * pi, "green"), (0.25 * pi, "red"), hadamard=(True, False, True, False))

        show(diagram)
        rewrite(diagram, ZXRuleColor())
        show(diagram)


    def test_bialgebra_rule_inverse(self):
        rule = ZXRuleBialgebraLaw()
        inverse = rule.inverse()

        self.assertEqual(2, len(inverse.connecting_wires_spider_mapping))
        self.assertEqual(2, len(inverse.connecting_wires_spider_mapping[0]))
        self.assertEqual(2, len(inverse.connecting_wires_spider_mapping[1]))
        self.assertEqual(rule.source, inverse.target)
        self.assertEqual(rule.target, inverse.source)

        # rewrite is part of the normal rewrite test

    def test_copying_rule_matches(self):
        diagram = generate_copying_diagram((0.0 * pi, "green"), (0.0 * pi, "red"), hadamard=(False, False, False))
        self.assertTrue(rule_matches(diagram, ZXRuleCopying()))

        diagram = generate_copying_diagram((0.0 * pi, "green"), (0.0 * pi, "red"), hadamard=(False, True, False))
        self.assertTrue(rule_matches(diagram, ZXRuleCopying()))

        diagram = generate_copying_diagram((0.0 * pi, "green"), (0.0 * pi, "red"), hadamard=(True, False, False))
        self.assertFalse(rule_matches(diagram, ZXRuleCopying()))

        diagram = generate_copying_diagram((0.5 * pi, "green"), (0.0 * pi, "red"), hadamard=(False, False, False))
        self.assertFalse(rule_matches(diagram, ZXRuleCopying()))

    def test_copying_rule_rewrite_inverse_rewrite(self):
        diagram = generate_copying_diagram((0.0 * pi, "green"), (0.0 * pi, "red"), hadamard=(False, True, False))
        show(diagram)
        rewrite(diagram, ZXRuleCopying())
        show(diagram)

        self.assertTrue(rule_matches(diagram, ZXRuleCopying().inverse()))
        rewrite(diagram, ZXRuleCopying().inverse())
        show(diagram)

    def test_hopf_law_rule_match(self):
        diagram = generate_hopf_law_diagram((0.0 * pi, "green"), (0.0 * pi, "red"), hadamard=(False, False, False, False))
        self.assertTrue(rule_matches(diagram, ZXRuleHopfLaw()))

        diagram = generate_hopf_law_diagram((0.0 * pi, "green"), (0.0 * pi, "red"), hadamard=(False, True, False, False))
        self.assertFalse(rule_matches(diagram, ZXRuleHopfLaw()))

        diagram = generate_hopf_law_diagram((0.0 * pi, "green"), (0.0 * pi, "green"), hadamard=(False, True, False, False))
        self.assertFalse(rule_matches(diagram, ZXRuleHopfLaw()))

        diagram = generate_hopf_law_diagram((1.0 * pi, "green"), (0.0 * pi, "red"), hadamard=(False, True, False, False))
        self.assertFalse(rule_matches(diagram, ZXRuleHopfLaw()))

    def test_hopf_law_rule_rewrite_inverse_rewrite(self):
        diagram = generate_hopf_law_diagram((0.0 * pi, "green"), (0.0 * pi, "red"), hadamard=(True, False, False, False))
        show(diagram)
        rewrite(diagram, ZXRuleHopfLaw())
        show(diagram)

        self.assertTrue(rule_matches(diagram, ZXRuleHopfLaw().inverse()))
        rewrite(diagram, ZXRuleHopfLaw().inverse())
        show(diagram)


def generate_three_spider_diagram(p1: Tuple[float, str], p2: Tuple[float, str], p3: Tuple[float, str], star_topology: bool = False, hadamard: Tuple[bool, bool, bool, bool] = (False, False, False, False)) -> Diagram:
    diagram = Diagram()
    b_in = diagram.add_boundary("in", 0, "b_in")
    b_out = diagram.add_boundary("out", 0, "b_out")
    s1 = diagram.add_spider(p1[0], p1[1], 0, "s1")
    s2 = diagram.add_spider(p2[0], p2[1], 0, "s2")
    s3 = diagram.add_spider(p3[0], p3[1], 0, "s3")
    w1 = diagram.add_wire(b_in, s1, hadamard[0])
    w2 = diagram.add_wire(s1, s2, hadamard[1])
    w3 = diagram.add_wire(s2, s3, hadamard[2])
    if not star_topology:
        w4 = diagram.add_wire(s3, b_out, hadamard[3])
    else:
        w4 = diagram.add_wire(s2, b_out, hadamard[3])
    return diagram

def get_three_spider_diagram_vertices(diagram: Diagram) -> Tuple[Vertex, Vertex, Vertex, Vertex, Vertex]:
    return diagram.get_vertex_from_identifier("b_in"), diagram.get_vertex_from_identifier("b_out"), diagram.get_vertex_from_identifier("s1"), diagram.get_vertex_from_identifier("s2"), diagram.get_vertex_from_identifier("s3")

def generate_bialegbra_law_diagram(p11: Tuple[float, str], p12: Tuple[float, str], p21: Tuple[float, str], p22: Tuple[float, str], internal_wiring: Tuple[bool, bool, bool, bool] = (True, True, True, True), hadamard: Tuple[bool, bool, bool, bool] = (False, False, False, False)):
    diagram = Diagram()
    b_in1 = diagram.add_boundary("in", 0, "b_in1")
    b_in2 = diagram.add_boundary("in", 1, "b_in2")
    b_out1 = diagram.add_boundary("out", 0, "b_out1")
    b_out2 = diagram.add_boundary("out", 1, "b_out2")

    s11 = diagram.add_spider(p11[0], p11[1], 0, "s11")
    s12 = diagram.add_spider(p12[0], p12[1], 1, "s12")
    s21 = diagram.add_spider(p21[0], p21[1], 0, "s21")
    s22 = diagram.add_spider(p22[0], p22[1], 1, "s22")

    diagram.add_wire(b_in1, s11)
    diagram.add_wire(b_in2, s12)
    diagram.add_wire(s21, b_out1)
    diagram.add_wire(s22, b_out2)

    if internal_wiring[0]:
        diagram.add_wire(s11, s21, hadamard[0])
    if internal_wiring[1]:
        diagram.add_wire(s11, s22, hadamard[1])
    if internal_wiring[2]:
        diagram.add_wire(s12, s21, hadamard[2])
    if internal_wiring[3]:
        diagram.add_wire(s12, s22, hadamard[3])

    return diagram

def get_bialgebra_law_diagram_vertices(diagram: Diagram) -> Tuple[Vertex, Vertex, Vertex, Vertex]:
    return diagram.get_vertex_from_identifier("s11"), diagram.get_vertex_from_identifier("s12"), diagram.get_vertex_from_identifier("s21"), diagram.get_vertex_from_identifier("s22")

def generate_copying_diagram(p1: Tuple[float, str], p2: Tuple[float, str], hadamard: Tuple[bool, bool, bool] = (False, False, False)) -> Diagram:
    diagram = Diagram()
    b1 = diagram.add_boundary("in", 0, "b1")
    b2 = diagram.add_boundary("in", 1, "b2")

    s1 = diagram.add_spider(p1[0], p1[1], 0, "s1")
    s2 = diagram.add_spider(p2[0], p2[1], 0, "s2")

    w1 = diagram.add_wire(s1, s2, hadamard[0])
    w2 = diagram.add_wire(s2, b1, hadamard[1])
    w3 = diagram.add_wire(s2, b2, hadamard[2])

    return diagram

def generate_hopf_law_diagram(p1: Tuple[float, str], p2: Tuple[float, str], hadamard: Tuple[bool, bool, bool, bool] = (False, False, False, False)) -> Diagram:
    diagram = Diagram()
    b_in = diagram.add_boundary("in", 0, "b_in")
    b_out = diagram.add_boundary("out", 0, "b_out")
    s1 = diagram.add_spider(p1[0], p1[1], 0, "s1")
    s2 = diagram.add_spider(p2[0], p2[1], 0, "s2")
    w1 = diagram.add_wire(b_in, s1, hadamard[0])
    w2 = diagram.add_wire(s1, s2, hadamard[1])
    w3 = diagram.add_wire(s1, s2, hadamard[2])
    w4 = diagram.add_wire(s2, b_out, hadamard[3])

    return diagram

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