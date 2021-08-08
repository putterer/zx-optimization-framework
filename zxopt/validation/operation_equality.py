import numpy as np


def validate_operation_equality(m1: np.ndarray, m2: np.ndarray, epsilon: float = 0.00001) -> bool:
    if m1.shape != m2.shape:
        return False

    shape = m1.shape

    # run random inputs through it and check
    for i in range(100):
        input = np.random.rand(shape[0]) + np.random.rand(shape[0]) * 1j   # not normalized, nor are the matricies
        out1 = m1 @ input # TODO: normalize (the circuit one should already be normalized)
        out2 = m2 @ input

        # normalize using np.linalg.norm

        probs1 = np.conj(out1) * out1
        probs2 = np.conj(out2) * out2

        # can I just normalize the ouput as their square has to sum up to 1?
        probs1 /= np.sum(probs1)
        probs2 /= np.sum(probs2)

        # TODO: doesn't normalize out global phase

        for i in range(probs1.shape[0]):
            if np.abs(probs1[i] - probs2[i]) > epsilon:
                return False

        # TODO
        # generate random measurement operator
        # measure once
        # ensure equality

    return True

