import numpy as np
import stim
import gurobipy as gp
from gurobipy import GRB


class MLEDecoder:
    """Most-likely error decoder."""

    def __init__(self, dem: stim.DetectorErrorModel, verbose=False):
        """Initializes the ``MLEDecoder``.

        Parameters
        ----------
        dem
            Detector error model.
        verbose
            If ``True``, the gurobi model prints its progress.
        """
        if not isinstance(dem, stim.DetectorErrorModel):
            raise TypeError(
                f"'dem' must be a stim.DetectorErrorModel, but {type(dem)} was given."
            )

        self.verbose = verbose
        self.dem = dem.flattened()
        self.detector_support, self.probs, self.logical_matrix = _prepare_decoder(dem)

        self.num_errors, self.num_detectors, self.num_observables = (
            self.dem.num_errors,
            self.dem.num_detectors,
            self.dem.num_observables,
        )

        return

    def decode_to_faults_array(self, defects: np.ndarray) -> np.ndarray:
        if not isinstance(defects, np.ndarray):
            raise TypeError(
                f"'defects' is not a np.ndarray, but {type(defects)} was given."
            )
        if len(defects.shape) != 1:
            raise TypeError(
                f"'defects' must be a vector, but shape {defects.shape} was given."
            )
        if defects.dtype != bool:
            raise TypeError(
                f"'defects' must be an array of type bool, but type {defects.dtype} was given."
            )

        # if no detector is triggered, the output is always "no error"
        if defects.sum() == 0:
            return np.zeros(self.num_errors, dtype=bool)

        # define model
        model = gp.Model("milp")
        if not self.verbose:
            model.Params.OutputFlag = 0
            model.Params.LogToConsole = 0

        # define variables
        errors = model.addMVar(shape=self.num_errors, vtype=GRB.BINARY, name="errors")
        dummy = model.addMVar(
            shape=self.num_detectors, vtype=GRB.INTEGER, name="dummy", lb=0
        )

        # add constraints
        for det_ind, support in self.detector_support.items():
            model.addConstr(
                errors[support] @ np.ones_like(support) - 2 * dummy[det_ind]
                == defects[det_ind],
                "syndromes",
            )

        # define cost function to maximize
        obj_fn = (np.log(self.probs / (1 - self.probs))).T @ errors
        model.setObjective(obj_fn, GRB.MAXIMIZE)

        # update model to build the contraints and cost function
        model.update()
        if self.verbose:
            model.display()  # prints model

        # solve MILP problem
        model.optimize()

        # convert errors to logical correction (attribute 'x' has the numpy values)
        error_vars = []
        for k in range(self.num_errors):
            error_vars.append(model.getVarByName(f"errors[{k}]"))
        predicted_errors = np.array(model.getAttr("X", error_vars), dtype=bool)

        return predicted_errors

    def decode(self, defects: np.ndarray) -> np.ndarray:
        predicted_errors = self.decode_to_faults_array(defects)
        correction = (self.logical_matrix @ predicted_errors) % 2
        correction = correction.astype(bool)
        return correction

    def decode_batch(self, defects: np.ndarray) -> np.ndarray:
        if not isinstance(defects, np.ndarray):
            raise TypeError(
                f"'defects' is not a np.ndarray, but {type(defects)} was given."
            )
        if len(defects.shape) != 2:
            raise TypeError(
                f"'defects' must be a vector, but shape {defects.shape} was given."
            )

        num_shots = defects.shape[0]
        correction = np.zeros((num_shots, self.dem.num_observables), dtype=bool)
        for k in range(num_shots):
            correction[k] = self.decode(defects[k])

        return correction


def _prepare_decoder(
    dem: stim.DetectorErrorModel,
) -> tuple[dict[int, np.ndarray], np.ndarray, np.ndarray]:
    """
    Parameters
    ----------
    dem
        Detector error model (DEM) without decomposed hyperedges into edges.

    Returns
    -------
    detector_support
        Dictionary specifying the errors indices that trigger a detector.
        The keys correspond to the detector indices and the values correspond
        to a ``np.ndarray` specifying the error indices.
    err_probs : np.ndarray(E)
        Probabilities for each error mechanism.
    log_err_matrix : np.ndarray(L, E)
        Logicals-error matrix which relates the error mechanisms and the logical
        observables that they flip. ``L`` is the number of logical observables.
    """
    if not isinstance(dem, stim.DetectorErrorModel):
        raise TypeError(
            f"'dem' must be a stim.DetectorErrorModel, but {type(dem)} was given."
        )

    D, E, L = dem.num_detectors, dem.num_errors, dem.num_observables
    detector_support = {d: [] for d in range(D)}
    log_err_matrix = np.zeros((L, E), dtype=bool)
    err_probs = np.zeros((E,), dtype=float)
    err_ind = 0

    for instr in dem.flattened():
        if instr.type == "error":
            # get information
            p = instr.args_copy()[0]
            dets, logs = [], []
            for t in instr.targets_copy():
                if t.is_relative_detector_id():
                    dets.append(t.val)
                elif t.is_logical_observable_id():
                    logs.append(t.val)
                elif t.is_separator():
                    # avoid having D0 ^ D0 D1 which would only trigger D1 but
                    # can confuse this function. This is not for a matching decoder
                    # so one should never decompose the errors.
                    raise ValueError(
                        "Separators are not allowed in the detector error model."
                    )
                else:
                    raise ValueError(f"{t} is not implemented.")

            # add info to corresponding matrix and dictionary
            for det in dets:
                detector_support[det].append(err_ind)
            log_err_matrix[np.array(logs, dtype=int), err_ind] = True
            err_probs[err_ind] = p
            err_ind += 1
        elif instr.type == "detector":
            pass
        elif instr.type == "logical_observable":
            pass
        else:
            raise ValueError(f"{instr} is not implemented.")

    detector_support = {k: np.array(v, dtype=int) for k, v in detector_support.items()}

    return detector_support, err_probs, log_err_matrix
