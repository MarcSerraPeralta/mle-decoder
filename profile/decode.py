import stim
from mle_decoder import MLEDecoder


circuit = stim.Circuit.generated(
    code_task="surface_code:rotated_memory_z",
    rounds=4,
    distance=3,
    after_clifford_depolarization=5e-3,
)
dem = circuit.detector_error_model()

sampler = dem.compile_sampler()
defects, _, _ = sampler.sample(shots=100)
decoder = MLEDecoder(dem)

_ = decoder.decode_batch(defects)
