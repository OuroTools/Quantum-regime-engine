"""Hidden Markov Model regime detection."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal

import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM
from sklearn.preprocessing import StandardScaler


class RegimeLabel(str, Enum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"


@dataclass
class RegimeDetector:
    """
    Fit a Gaussian HMM on return/volatility features and map latent states
    to bull / bear / sideways labels by mean return.
    """

    n_states: int = 3
    random_state: int = 42
    n_iter: int = 200

    model_: GaussianHMM | None = None
    scaler_: StandardScaler | None = None
    state_to_regime_: dict[int, RegimeLabel] | None = None

    def fit(self, features: pd.DataFrame) -> "RegimeDetector":
        X = features[["log_return", "volatility"]].values
        self.scaler_ = StandardScaler()
        X_scaled = self.scaler_.fit_transform(X)

        self.model_ = GaussianHMM(
            n_components=self.n_states,
            covariance_type="full",
            n_iter=self.n_iter,
            random_state=self.random_state,
            tol=1e-3,
        )
        self.model_.fit(X_scaled)
        self.state_to_regime_ = self._label_states(features, X_scaled)
        return self

    def _label_states(self, features: pd.DataFrame, X_scaled: np.ndarray) -> dict[int, RegimeLabel]:
        assert self.model_ is not None
        states = self.model_.predict(X_scaled)

        state_stats: list[tuple[int, float, float]] = []
        for s in range(self.n_states):
            mask = states == s
            mean_ret = float(features.loc[mask, "log_return"].mean())
            mean_vol = float(features.loc[mask, "volatility"].mean())
            state_stats.append((s, mean_ret, mean_vol))

        # Sort by mean return: highest -> bull, lowest -> bear, middle -> sideways
        sorted_by_return = sorted(state_stats, key=lambda x: x[1])
        mapping: dict[int, RegimeLabel] = {}
        if self.n_states == 3:
            mapping[sorted_by_return[0][0]] = RegimeLabel.BEAR
            mapping[sorted_by_return[1][0]] = RegimeLabel.SIDEWAYS
            mapping[sorted_by_return[2][0]] = RegimeLabel.BULL
        else:
            for i, (state_id, _, _) in enumerate(sorted_by_return):
                if i == 0:
                    mapping[state_id] = RegimeLabel.BEAR
                elif i == len(sorted_by_return) - 1:
                    mapping[state_id] = RegimeLabel.BULL
                else:
                    mapping[state_id] = RegimeLabel.SIDEWAYS

        return mapping

    def predict_regimes(self, features: pd.DataFrame) -> pd.Series:
        """Predict regime label for each row (uses Viterbi decoding)."""
        if self.model_ is None or self.scaler_ is None or self.state_to_regime_ is None:
            raise RuntimeError("Call fit() before predict_regimes().")

        X = features[["log_return", "volatility"]].values
        X_scaled = self.scaler_.transform(X)
        states = self.model_.predict(X_scaled)
        labels = [self.state_to_regime_[s] for s in states]
        return pd.Series(labels, index=features.index, name="regime")

    def predict_proba_regimes(self, features: pd.DataFrame) -> pd.DataFrame:
        """Posterior probability of each HMM state per day."""
        if self.model_ is None or self.scaler_ is None:
            raise RuntimeError("Call fit() before predict_proba_regimes().")

        X = features[["log_return", "volatility"]].values
        X_scaled = self.scaler_.transform(X)
        posteriors = self.model_.predict_proba(X_scaled)
        cols = [f"state_{i}" for i in range(self.n_states)]
        return pd.DataFrame(posteriors, index=features.index, columns=cols)

    def regime_summary(self, features: pd.DataFrame, regimes: pd.Series) -> pd.DataFrame:
        """Aggregate statistics per detected regime."""
        df = features.copy()
        df["regime"] = regimes.map(lambda r: r.value if hasattr(r, "value") else r)
        summary = (
            df.groupby("regime", observed=True)
            .agg(
                days=("log_return", "count"),
                mean_daily_return=("log_return", "mean"),
                ann_return=("log_return", lambda x: (1 + x.mean()) ** 252 - 1),
                mean_vol=("volatility", "mean"),
            )
            .sort_index()
        )
        return summary

    def transition_matrix(self) -> pd.DataFrame:
        """Labeled transition probabilities between regimes."""
        if self.model_ is None or self.state_to_regime_ is None:
            raise RuntimeError("Call fit() first.")

        raw = self.model_.transmat_
        labels = [self.state_to_regime_[i].value for i in range(self.n_states)]
        return pd.DataFrame(raw, index=labels, columns=labels)
