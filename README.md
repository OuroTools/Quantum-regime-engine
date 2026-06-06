# Quantum Regime Engine

Detect **bull / bear / sideways** market regimes with a Hidden Markov Model, backtest regime-switching strategies vs buy-and-hold, and optionally optimize portfolios with **QAOA** (Qiskit).

> Research and education tool only — not financial advice.

**Plain-English guide:** [EXPLAINED_SIMPLE.md](EXPLAINED_SIMPLE.md)  
**GitHub publish guide:** [GITHUB_SETUP.md](GITHUB_SETUP.md)

---

## Quick start (Windows)

```bash
cd quantum-regime-engine
install.bat
```

Then:

```bash
regime-engine          # terminal analysis + saves charts to output/
regime-dashboard       # web dashboard in browser
```

---

## Quick start (Mac / Linux)

```bash
cd quantum-regime-engine
chmod +x install.sh
./install.sh
```

---

## Manual install

```bash
pip install -e ".[all]"
python scripts/verify.py
```

---

## Three ways to use

| Mode | Command |
|------|---------|
| **CLI** | `regime-engine` or `python main.py` |
| **Web dashboard** | `regime-dashboard` or `streamlit run dashboard.py` |
| **Notebook** | `jupyter notebook notebooks/walkthrough.ipynb` |

### CLI examples

```bash
regime-engine
regime-engine --sector technology
regime-engine --sector financials --period 15y --test-years 3
regime-engine --quantum
regime-engine --ticker QQQ --portfolio QQQ TLT GLD
```

### Sector presets

`broad_market` · `technology` · `financials` · `healthcare` · `energy` · `international` · `growth_value` · `crypto_adjacent`

---

## What you get

| Output | Location |
|--------|----------|
| Regime chart (PNG) | `output/regimes_oos.png` |
| Equity curves (PNG) | `output/equity_curves.png` |
| Text report | `output/report.txt` |
| Interactive charts | Web dashboard tabs |

---

## Project structure

```
quantum-regime-engine/
├── install.bat / install.sh     # one-click setup
├── main.py / dashboard.py       # dev shortcuts
├── scripts/verify.py            # health check
├── src/regime_engine/           # core library
│   ├── data.py                  # Yahoo Finance download
│   ├── hmm_detector.py          # HMM regime detection
│   ├── strategies.py            # allocation rules
│   ├── backtest.py              # strategy simulation
│   ├── quantum_opt.py           # QAOA optimizer
│   ├── pipeline.py              # end-to-end runner
│   ├── dashboard_app.py         # Streamlit UI
│   └── cli.py                   # console commands
├── notebooks/walkthrough.ipynb
├── tests/test_smoke.py
└── GITHUB_SETUP.md
```

---

## Tests

```bash
pytest
```

Requires internet (downloads live prices).

---

## Requirements

- Python 3.10+
- Internet connection (Yahoo Finance)

---

## License

MIT — see [LICENSE](LICENSE).
