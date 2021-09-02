import unittest
from math import pi

from zxopt.data_structures.diagram import Diagram
from zxopt.rewriting.matcher import Matcher
from zxopt.rewriting.zx_calculus import ZXRuleSpider1


class MatcherRewriterTest(unittest.TestCase):
    def test_spider_rule_1(self):
        diagram = generate_three_spider_diagram()
        matcher = Matcher(diagram)

        matches = matcher.match_rule(ZXRuleSpider1(), apply=True)
        self.assertTrue(matches)




def generate_three_spider_diagram() -> Diagram:
    diagram = Diagram()
    b_in = diagram.add_boundary("in", 0)
    b_out = diagram.add_boundary("out", 0)
    s1 = diagram.add_spider(1.0 * pi, "green", 0)
    s2 = diagram.add_spider(0.5 * pi, "red", 0)
    s3 = diagram.add_spider(0.25 * pi, "red", 0)
    diagram.add_wire(b_in, s1)
    diagram.add_wire(s1, s2)
    diagram.add_wire(s2, s3)
    diagram.add_wire(s3, b_out)
    return diagram