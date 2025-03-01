import numpy as np
import stim

from mle_decoder import MLEDecoder


def test_MLEDecoder_decode():
    dem = stim.DetectorErrorModel(
        """
        error(0.1) D0 D2
        error(0.1) D0 D1 D2
        error(0.1) D1 D2 L0
        """
    )

    mle_decoder = MLEDecoder(dem)

    defects = np.array([1, 0, 1], dtype=bool)
    prediction = mle_decoder.decode(defects)

    assert prediction == np.array([0], dtype=bool)

    defects = np.array([0, 1, 1], dtype=bool)
    prediction = mle_decoder.decode(defects)

    assert prediction == np.array([1], dtype=bool)

    defects = np.array([1, 1, 1], dtype=bool)
    prediction = mle_decoder.decode(defects)

    assert prediction == np.array([0], dtype=bool)

    return
