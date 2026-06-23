## Quantum Regime Engine v0.1.0

**First release** — HMM market regime detection with backtesting and an optional quantum portfolio optimizer.

### Highlights

- Detect **bull / bear / sideways** market moods from live price data
- **Backtest** regime-switching vs buy-and-hold (honest out-of-sample evaluation)
- **3 ways to run:** CLI (`regime-engine`), web dashboard (`regime-dashboard`), Jupyter notebook
- **8 sector presets** (SPY broad market, XLK tech, XLF financials, and more)
- Optional **QAOA** optimizer for per-regime portfolio weights (Qiskit)

### Quick start

```bash
git clone https://github.com/OuroTools/Quantum-regime-engine.git
cd Quantum-regime-engine
pip install -e ".[all]"
regime-engine
regime-dashboard
```

Windows: run `install.bat` instead.

### What's included

| Component | Description |
|-----------|-------------|
| `regime-engine` | Terminal analysis + PNG charts in `output/` |
| `regime-dashboard` | Browser UI with interactive charts |
| `notebooks/walkthrough.ipynb` | Interactive tutorial |
| `EXPLAINED_SIMPLE.md` | Plain-English guide to every module |

### Requirements

- Python 3.10+
- Internet (Yahoo Finance)

### Disclaimer

This is a **research and portfolio project**, not financial advice. Past backtests do not guarantee future results.

---

**Full changelog:** [CHANGELOG.md](https://github.com/OuroTools/Quantum-regime-engine/blob/main/CHANGELOG.md)
