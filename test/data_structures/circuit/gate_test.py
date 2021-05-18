import unittest


class GateTest(unittest.TestCase):
    pass

    # This can be done by checking the inner product (and therefore measurement probability)

    # def test_identity(self):
    #     self.assertTrue((IdentityGate().matrix == np.array([
    #         [1+0j, 0+0j],
    #         [0+0j, 1+0j],
    #     ])).all())
    #
    # def test_pauli_x(self):
    #     print(PauliXGate().matrix)
    #     print((PauliXGate().matrix == np.array([
    #         [0+0j, 1+0j],
    #         [1+0j, 0+0j],
    #     ])))
    #     self.assertTrue((PauliXGate().matrix == np.array([
    #         [0+0j, 1+0j],
    #         [1+0j, 0+0j],
    #     ])).all())
    #
    # def test_pauli_y(self):
    #     self.assertTrue((PauliYGate().matrix == np.array([
    #         [0+0j, 0+-1j],
    #         [0+1j, 0+0j],
    #     ])).all())
    #
    # def test_pauli_z(self):
    #     self.assertTrue((PauliZGate().matrix == np.array([
    #         [1+0j, 0+0j],
    #         [0+0j, -1+0j],
    #     ])).all())