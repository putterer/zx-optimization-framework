import math

import cairo

from zxopt.data_structures.circuit import Circuit, GateComponent, MeasurementComponent
from zxopt.data_structures.circuit.register.quantum_register import QuantumBit
from zxopt.data_structures.circuit.register.register import RegisterBit
from zxopt.openqasm import OpenQasmParser
from zxopt.visualization.render_util import draw_line, draw_text, ALIGN_RIGHT, BASELINE_CENTER, color, \
    fill_square, BLACK, ALIGN_CENTER, fill_circle, normalise_tuple_vec
from zxopt.visualization.renderer import Renderer
from zxopt.visualization.window import Window

BIT_SPACING = 60
STEP_SPACING = 60
COMPONENT_SIZE = 40
CONTROL_RADIUS = COMPONENT_SIZE / 10.0

MEASUREMENT_SYMBOL_RADIUS = 12.0
FONT_SIZE = 14

TOP_OFFSET = 30 + COMPONENT_SIZE / 2.0
LEFT_OFFSET = 30

GATE_COLOR = "#278f42"
MEASUREMENT_COLOR = "#acacac"

class CircuitRenderer(Renderer):
    circuit: Circuit
    register_bit_positions: dict[RegisterBit, int]
    circuit_width: int

    def __init__(self, circuit: Circuit):
        super().__init__()
        self.circuit = circuit
        self.register_bit_positions = {}
        self.circuit_width = int((max([c.step for c in self.circuit.components]) + 1.33) * STEP_SPACING)

    def render(self, ctx: cairo.Context):
        ctx.select_font_face("Verdana", cairo.FONT_SLANT_NORMAL ,cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(FONT_SIZE)

        max_register_font_width = max([ctx.text_extents(register[0].get_name()).width for register in self.circuit.get_registers()])

        ctx.translate(LEFT_OFFSET + max_register_font_width, TOP_OFFSET)

        self.render_registers(ctx)

        ctx.translate(STEP_SPACING / 2.0 + 10.0, 0)
        self.render_components(ctx)

    def render_components(self, ctx: cairo.Context):
        for component in self.circuit.components:
            if isinstance(component, GateComponent):
                self.render_gate(ctx,
                                 component.step,
                                 self.register_bit_positions[component.target_qubit],
                                 [self.register_bit_positions[control_bit] for control_bit in component.control_bits],
                                 component.gate_type.representation)
            elif isinstance(component, MeasurementComponent):
                self.render_measurement(ctx,
                                        component.step,
                                        self.register_bit_positions[component.measured_qubit],
                                        self.register_bit_positions[component.target_bit])
            else:
                raise RuntimeError("Cannot render unknow circuit component type", type(component))

    def render_gate(self, ctx: cairo.Context, step: int, qubit_position: int, control_positions: list[int], representation: str):
        gate_pos = (step * STEP_SPACING, qubit_position * BIT_SPACING)

        color(ctx, BLACK)
        # render controls
        for control in control_positions:
            control_pos = (step * STEP_SPACING + 0.5, control * BIT_SPACING + 0.5)
            fill_circle(ctx, control_pos, CONTROL_RADIUS)
            draw_line(ctx, control_pos, (gate_pos[0] + 0.5, gate_pos[1]))

        # gate rect
        color(ctx, GATE_COLOR)
        fill_square(ctx, gate_pos, COMPONENT_SIZE)
        # gate text
        color(ctx, BLACK)
        draw_text(ctx, gate_pos, representation, ALIGN_CENTER, BASELINE_CENTER)

    def render_measurement(self, ctx: cairo.Context, step: int, qubit_position: int, target_position: int):
        measure_pos = (step * STEP_SPACING, qubit_position * BIT_SPACING)
        target_pos = (step * STEP_SPACING, target_position * BIT_SPACING)

        # arrow
        color(ctx, BLACK)
        draw_line(ctx, measure_pos, target_pos, offset=(0.5, 0.0))
        triangle_top_bot_offset = +9.0 if qubit_position > target_position else -9.0
        ctx.move_to(target_pos[0], target_pos[1])
        ctx.line_to(target_pos[0] + 5.0, target_pos[1] + triangle_top_bot_offset)
        ctx.line_to(target_pos[0] - 5.0, target_pos[1] + triangle_top_bot_offset)
        ctx.fill()

        # block
        color(ctx, MEASUREMENT_COLOR)
        fill_square(ctx, measure_pos, COMPONENT_SIZE)

        # icon, from my own code at https://github.com/Geosearchef/qirella/blob/master/src/main/kotlin/qcn/rendering/QCRenderer.kt
        circle_center = (measure_pos[0], measure_pos[1] + MEASUREMENT_SYMBOL_RADIUS / 2.0)
        indicator_length = normalise_tuple_vec((math.cos(1.0/3.0 * math.pi), -math.sin(1.0/3.0 * math.pi)), new_length=MEASUREMENT_SYMBOL_RADIUS*1.5)
        indicator_end = (circle_center[0] + indicator_length[0], circle_center[1] + indicator_length[1])

        color(ctx, BLACK)
        ctx.set_line_width(1.5)
        ctx.arc(circle_center[0], circle_center[1], MEASUREMENT_SYMBOL_RADIUS, math.pi, 0.0)
        ctx.move_to(circle_center[0], circle_center[1])
        ctx.line_to(indicator_end[0], indicator_end[1])
        ctx.stroke()


    def render_registers(self, ctx: cairo.Context):
        bits = self.circuit.get_register_bits()

        for i in range(len(bits)):
            bit = bits[i]
            self.register_bit_positions[bits[i]] = i
            y = i * BIT_SPACING

            color(ctx, BLACK)

            # register name
            name = bit.get_name()
            if name:
                draw_text(ctx, (-10, y - 3), name, align=ALIGN_RIGHT, baseline=BASELINE_CENTER)

            # register line
            if isinstance(bit, QuantumBit):
                ctx.set_line_width(1.0)
                draw_line(ctx, (0, y + 0.5), (self.circuit_width, y + 0.5))
            else:
                ctx.set_line_width(1.0)
                draw_line(ctx, (0, y - 1.5), (self.circuit_width, y - 1.5))
                draw_line(ctx, (0, y + 1.5), (self.circuit_width, y + 1.5))


### Test
if __name__ == "__main__":
    circuit = OpenQasmParser().load_file("./circuits/bell_swap.qasm")
    renderer = CircuitRenderer(circuit)

    window = Window(renderer)
    window.main_loop()
