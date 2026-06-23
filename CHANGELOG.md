# Changelog

All notable changes to this project are documented here.

## [0.1.0] - 2026-06-06

First public release.

### Added

- **HMM regime detection** — classifies markets into bull, bear, and sideways using Gaussian Hidden Markov Models on returns and volatility
- **Backtesting engine** — compares buy-and-hold vs regime-switching with lagged signals and transaction costs
- **8 sector presets** — broad market, technology, financials, healthcare, energy, international, growth/value, crypto-adjacent
- **CLI** — `regime-engine` command with sector, period, and quantum flags
- **Web dashboard** — Streamlit UI with interactive Plotly charts, KPI cards, and download buttons
- **Jupyter walkthrough** — step-by-step notebook in `notebooks/walkthrough.ipynb`
- **Quantum module** — optional QAOA portfolio optimization via Qiskit (`--quantum`)
- **Install scripts** — `install.bat` / `install.sh` for one-click setup
- **Verification** — `scripts/verify.py` health check and `pytest` smoke tests
- **Documentation** — `README.md`, `EXPLAINED_SIMPLE.md`, `GITHUB_SETUP.md`

### Requirements

- Python 3.10+
- Internet connection (Yahoo Finance data)

### Disclaimer

Research and education tool only. Not financial advice.

[0.1.0]: https://github.com/OuroTools/Quantum-regime-engine/releases/tag/v0.1.0
