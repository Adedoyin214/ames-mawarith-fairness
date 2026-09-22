# AMES Mawārith Fairness — Inequality Metrics in Islamic Inheritance

**Project 3 of AMES (Algorithmic Mawārith Execution System)** — quantifies fairness and wealth concentration in Islamic (Fara'id) inheritance distribution using four standard inequality indices, benchmarked against a civil equal-share alternative. Built on the outputs of [Project 1](../ames-faraid-engine) (20 PCIED cases) and [Project 2](../ames-mawarith-simulation) (5,000 simulated cases).

## What it does

- Computes **Gini coefficient**, **Theil T index**, **Atkinson index (ε=0.5)**, and **coefficient of variation** for each of the 20 PCIED estates and all 5,000 simulation records
- Benchmarks every case against a **civil equal-share** distribution (Gini = 0 by construction) to isolate how much of the "inequality" in Islamic shares is structural differentiation rather than randomness
- Breaks results down by correction type ('Awl / Radd / Tanzeel / Standard), family profile, and number of heirs
- Plots Lorenz curves for representative cases to visualize the Islamic vs. civil distributions directly

## Contents

| File | Description |
|---|---|
| `Project3_fairness_analysis.py` | Computes Gini, Theil T, Atkinson, CV, Palma ratio, and the civil benchmark for both datasets |
| `mawaarith_engine_v2.py` | The underlying Fiqh al-Mawārith engine (shared across all AMES projects) |
| `notebooks/Project3_Fairness.ipynb` | Analysis notebook — case-by-case metrics, simulation summary, key findings |
| `Project3_Dashboard.html` | Interactive results dashboard |
| `images/Project3_fig1_pcied_fairness.png` | Gini per PCIED case (Islamic vs. civil), Gini vs. CV colored by Theil T, mean Gini by correction type |
| `images/Project3_fig2_sim_gini.png` | Gini distribution across 5,000 simulations, by family profile, and vs. number of heirs |
| `images/Project3_fig3_multi_metrics.png` | Theil T, Atkinson, and CV distributions across simulations |
| `images/Project3_fig4_lorenz.png` | Lorenz curves — Islamic vs. civil equal-share, for four representative cases |
| `data/PCIED_2023_cases.md` | Source dataset (shared with Projects 1 & 2) |
| `reports/Project3_Fairness_Report.docx` | Full written report |

## Key findings

| Metric | Islamic (Simulation, N=5,000) | Islamic (PCIED, N=20) | Civil Benchmark |
|---|:---:|:---:|:---:|
| Gini | 0.1949 | 0.2281 | 0.0000 |
| Theil T | 0.1191 | 0.1310 | 0.0000 |
| Atkinson (ε=0.5) | 0.0585 | 0.0680 | 0.0000 |
| Coefficient of Variation | 0.4478 | — | 0.0000 |

- **Islamic inheritance is moderately unequal by design** — a mean Gini around 0.20–0.23 reflects structured differentiation (wives get 1/4 or 1/8, daughters half of sons, mothers 1/6 or 1/3), not randomness.
- **Civil equal-share hits Gini = 0 by construction**, but that "fairness" ignores the differentiated relationships and obligations Islamic law is accounting for.
- **Complex, multi-heir family structures produce the highest inequality** (mean Gini ≈ 0.243 in simulation), since they combine the widest range of fixed-share and residue heirs.
- **Gini rises with heir count** — as more heirs are added, the spread between the largest residue (ʿAṣaba) share and the smallest fixed share (e.g. 1/6 mother) widens.
- **Case 7 (Hadi Ridwan) is the only perfectly equal PCIED case (Gini = 0.000)** — three heirs (wife, mother, two maternal brothers) happened to receive equal per-person amounts after Radd.

![Fairness metrics across 20 PCIED cases](images/Project3_fig1_pcied_fairness.png)
![Lorenz curves — Islamic vs civil](images/Project3_fig4_lorenz.png)

## Running it

```bash
python Project3_fairness_analysis.py
```

Requires `simulation_results.json` from Project 2 in the working directory, plus `mawaarith_engine_v2` (included). Outputs `pcied_fairness.json` and `sim_fairness.json`, consumed by the notebook and dashboard.

## Author

Abdulbasit A. Adedeji (Data Ustadh)
