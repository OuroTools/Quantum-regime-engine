# Regime Detection Engine — Explained Like You're Five (and then a bit more)

This document explains **every file and every idea** in plain language. No finance or quantum PhD required.

---

## The big picture (30 seconds)

Imagine the stock market has **moods**:

- **Bull** = happy, prices mostly go up
- **Bear** = scared, prices mostly go down
- **Sideways** = bored, prices wiggle but don't really go anywhere

This tool:

1. Downloads past stock prices from the internet
2. Uses math (a Hidden Markov Model) to guess which mood the market is in
3. Pretends you invested differently in each mood
4. Checks if that would have done better than just buying and holding

That's it. Everything else is details.

---

## Folder map — what each file is for

```
quantum-regime-engine/
├── main.py                 ← Run from terminal (no browser)
├── dashboard.py            ← Run in browser (pretty buttons)
├── EXPLAINED_SIMPLE.md     ← You are here
├── README.md               ← Quick technical readme
├── requirements.txt        ← List of Python packages to install
├── notebooks/
│   └── walkthrough.ipynb   ← Step-by-step lesson in Jupyter
├── output/                 ← Charts and reports saved here (after CLI run)
└── src/regime_engine/      ← The actual brain
    ├── data.py
    ├── hmm_detector.py
    ├── strategies.py
    ├── backtest.py
    ├── quantum_opt.py
    ├── pipeline.py
    ├── sectors.py
    └── visualize.py
```

---

## How to run each part

| What | Command | Baby explanation |
|------|---------|------------------|
| Terminal version | `python main.py` | Text output + saves PNG charts |
| Web dashboard | `streamlit run dashboard.py` | Click buttons in your browser |
| Notebook lesson | `jupyter notebook notebooks/walkthrough.ipynb` | Learn step by step with cells you can re-run |
| Tech sector example | `python main.py --sector technology` | Same tool, different stocks |

---

## `requirements.txt` — the shopping list

Before Python can run this, it needs helper libraries:

| Package | What it does (baby terms) |
|---------|---------------------------|
| **yfinance** | Grabs stock prices from Yahoo Finance (like copying numbers from a website, automatically) |
| **pandas** | Spreadsheets for Python — rows = days, columns = stocks |
| **numpy** | Fast math on lists of numbers |
| **hmmlearn** | The HMM library — finds hidden "moods" in data |
| **scipy** | More math tools (used for classical portfolio optimization) |
| **matplotlib** | Draws line charts |
| **scikit-learn** | Machine learning utilities (we use it to scale numbers) |
| **qiskit** + friends | IBM's quantum computing toolkit (optional fancy optimizer) |
| **streamlit** | Turns Python scripts into web pages |
| **jupyter** | Interactive notebook environment |

Install all at once: `pip install -r requirements.txt`

---

## `src/regime_engine/data.py` — Getting the numbers

### `fetch_prices(tickers, period)`

**Baby terms:** Asks Yahoo "what was SPY worth each day for the last 10 years?" and puts answers in a table.

**Why:** You can't detect moods without history.

### `compute_features(prices)`

**Baby terms:** Turns raw prices into two clues the computer can read:

1. **Log return** — "How much did price change today?" (up or down %)
2. **Volatility** — "How wild were the last ~21 days?" (bumpy = high vol)

**Why:** The HMM needs simple number pairs per day, not just "$500 per share."

### `train_test_split_by_date(df, test_years)`

**Baby terms:** Cut the calendar in half-ish. Train on the old years, test on the recent years.

**Why:** If you test on the same data you trained on, you're cheating (like studying the exact exam questions). Recent years = "did it work on stuff it never saw?"

---

## `src/regime_engine/hmm_detector.py` — Finding the mood

### What is an HMM (Hidden Markov Model)?

**Baby terms:** Imagine a mood ring you **can't see**, but you **can see** what it does to the market (small jumps vs big scary jumps). The HMM guesses the hidden mood from those visible clues.

It assumes:

- The market is **always** in exactly one mood (state)
- Moods **stick** — bull today probably means bull tomorrow (but not always)
- Each mood produces **typical** returns and volatility

### `RegimeLabel` — the three moods

- `BULL` — good times
- `BEAR` — bad times  
- `SIDEWAYS` — meh times

### `RegimeDetector` class

| Method | Baby terms |
|--------|------------|
| `fit(features)` | "Study the past and learn what bull/bear/sideways look like" |
| `predict_regimes(features)` | "For each day, label it bull, bear, or sideways" |
| `regime_summary(...)` | "How many bull days? Average return in bear days?" |
| `transition_matrix()` | "If today is bull, what's the % chance tomorrow is still bull?" |

### How states become bull/bear/sideways

The HMM finds 3 anonymous states (State 0, 1, 2). We **rename** them after training:

- State with **highest** average return → **bull**
- State with **lowest** average return → **bear**
- The middle one → **sideways**

---

## `src/regime_engine/strategies.py` — What to buy in each mood

### `RegimeStrategy`

**Baby terms:** A rulebook.

| Mood | Default rule |
|------|--------------|
| Bull | Put 100% in stocks (SPY) |
| Bear | Put 100% in bonds (TLT) — safer when stocks hurt |
| Sideways | Split: 50% stocks, 30% bonds, 20% gold (GLD) |

### `build_allocation_series(regimes, tickers)`

**Baby terms:** For every day, write down what % you hold in each stock.

### `optimize_weights_mean_variance(returns)`

**Baby terms:** Classical math finds a "best" mix of stocks for a given mood — balance return vs risk. Not magic; just calculus.

### `QuantumRegimeStrategy`

Same idea, but tries **QAOA** (quantum optimizer) instead of classical math when `--quantum` is on.

---

## `src/regime_engine/backtest.py` — Pretend we traded

### Why backtest?

**Baby terms:** Before risking real money, replay history: "If I had followed these rules, what would have happened?"

### `Backtester`

Compares two players:

1. **Buy & hold** — buy SPY once, never sell (the lazy strategy)
2. **Regime switching** — change holdings when mood changes

### Important honesty trick: **lagged weights**

We use **yesterday's** mood to choose **today's** holdings. Why? In real life you don't know today's mood until the day is over. Using same-day mood = cheating.

### Transaction costs

When you switch from stocks to bonds, brokers charge fees. We subtract a tiny penalty (5 basis points = 0.05%) when weights change.

### Metrics (the scorecard)

| Metric | Baby terms |
|--------|------------|
| **Total return** | How much $1 grew over the whole test period |
| **Ann. return** | That return expressed "per year" |
| **Ann. vol** | How bumpy the ride was (higher = scarier) |
| **Sharpe** | Return ÷ bumpiness — reward per unit of stress |
| **Max drawdown** | Worst drop from a peak ("how bad was the worst slump?") |

---

## `src/regime_engine/quantum_opt.py` — The quantum corner (optional)

### What problem does it solve?

**Baby terms:** "I have 3 ETFs. What mix is best?" That's portfolio optimization — pick weights that add to 100%.

### Classical vs quantum

- **Classical (scipy):** Normal computer, calculus
- **Quantum (QAOA):** Formulate the problem as a **QUBO** (yes/no decisions with penalties) and let a **quantum-inspired algorithm** search for a good answer

### `quantum_portfolio_weights(returns)`

1. Build a QUBO from expected returns and risks
2. Run QAOA via Qiskit
3. If quantum fails or too many assets → fall back to classical

**Honest note:** On your laptop this simulates quantum on a normal CPU. Real quantum hardware is for experiments; the **software skills** (formulating finance as QUBO, using Qiskit) are what matter for a quantum software engineer resume.

---

## `src/regime_engine/sectors.py` — Preset stock groups

**Baby terms:** Shortcuts so you don't type tickers.

| Preset | What it analyzes |
|--------|------------------|
| Broad Market | SPY + bonds + gold |
| Technology | XLK, QQQ, TLT |
| Financials | XLF, KRE, TLT |
| Healthcare | XLV, SPY, TLT |
| Energy | XLE, USO, TLT |
| International | EFA, EEM, TLT |
| Growth vs Value | SPY, IVW, IVE |
| Crypto-Adjacent | SPY, IBIT (Bitcoin ETF), TLT |

Each preset has a **primary** ticker (used to detect mood) and a **portfolio** (what you might switch between).

---

## `src/regime_engine/pipeline.py` — The assembly line

**Baby terms:** One function `run_analysis()` that chains everything:

```
download → features → train HMM → predict → strategy → backtest → report
```

Used by CLI, dashboard, and notebook so they all do the **same** thing (no copy-paste bugs).

`AnalysisResult` = a box holding all outputs (charts data, metrics, current mood, etc.).

---

## `src/regime_engine/visualize.py` — Pictures

| Function | Baby terms |
|----------|------------|
| `make_regime_figure` | Price line + colored background (green bull, red bear, yellow sideways) |
| `make_equity_figure` | Two lines: how $1 grew under each strategy |
| `plot_regimes_on_price` | Same but saves to PNG file |
| `print_report` | Text summary for terminal |

---

## `main.py` — Terminal runner

**Baby terms:** The command-line remote control.

```
python main.py                      # default broad market
python main.py --sector technology  # tech sector
python main.py --quantum            # use QAOA for weights
```

Writes charts to `output/`.

---

## `dashboard.py` — Web runner

**Baby terms:** Same engine, but with sliders and buttons in your browser.

```
streamlit run dashboard.py
```

Opens a local website (usually `http://localhost:8501`).

---

## `notebooks/walkthrough.ipynb` — Interactive class

**Baby terms:** A homework notebook where each cell teaches one step. Run top to bottom to see the full story with your own eyes.

---

## Key concepts glossary

| Term | Baby explanation |
|------|------------------|
| **Ticker** | Stock nickname (SPY = S&P 500 fund) |
| **ETF** | A fund that holds many stocks; you buy one ticker |
| **Return** | % change in price |
| **Volatility** | How wildly prices swing |
| **Regime** | Market mood / environment |
| **HMM** | Math that guesses hidden moods from visible data |
| **Backtest** | Historical simulation |
| **Out-of-sample (OOS)** | Test on data the model never trained on |
| **Lookahead bias** | Cheating by using future info |
| **Sharpe ratio** | Good returns with less chaos = higher Sharpe |
| **QUBO** | Optimization written as "pick 0 or 1" with penalty rules |
| **QAOA** | Quantum Approximate Optimization Algorithm — hybrid quantum/classical solver |

---

## What to say in an interview

1. **Problem:** Markets change behavior; one strategy doesn't fit all moods.
2. **Method:** Gaussian HMM on returns + vol; 3 states labeled by mean return.
3. **Validation:** Walk-forward split; lagged signals; transaction costs.
4. **Quantum angle:** Portfolio weights per regime as QUBO + QAOA (Qiskit), with classical fallback.
5. **Honesty:** Regime switching doesn't always win on raw return; discuss overfitting and regime detection lag.

---

## Common questions

**Q: Is this financial advice?**  
A: No. It's a learning project. Past performance ≠ future results.

**Q: Why doesn't regime switching always win?**  
A: Moods are detected late, switching costs money, and moods are hard to predict out-of-sample.

**Q: Do I need a quantum computer?**  
A: No. Qiskit simulates on your laptop.

**Q: What's the first file to read in code?**  
A: `pipeline.py` — it's the map. Then `hmm_detector.py` for the cool math.
