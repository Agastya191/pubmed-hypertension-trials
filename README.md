# Geographic Representation in Hypertension Clinical Trials

Analysis of the 100 most recent PubMed clinical trials related to hypertension, examining where research is conducted and quantifying the Global North vs Global South representation gap.

---

## Research Question

Hypertension is the leading preventable cause of cardiovascular mortality globally, with the highest burden concentrated in low- and middle-income countries. This project asks: does the geographic distribution of clinical trial research reflect that burden — or does it reflect something else?

---

## Method

1. Query PubMed via the NCBI Entrez API (Biopython) for the 100 most recent clinical trials tagged with hypertension
2. Parse author affiliation strings to extract the country of each trial's lead institution
3. Classify each country as Global North or Global South using UN HDI groupings
4. Output a structured DataFrame and a written summary of the representation gap

---

## Setup

```bash
pip install biopython pandas
python fetch_trials.py
```

Output is written to `results/trials.csv` and `results/summary.md`.

---

## Output

| File | Description |
|---|---|
| `results/trials.csv` | One row per trial with PMID, title, year, journal, authors, affiliations, country, and region |
| `results/summary.md` | Markdown summary with representation gap analysis |

---

## Project Structure

```
pubmed-hypertension-trials/
├── fetch_trials.py     # Main script: fetch, parse, classify, summarize
├── results/
│   ├── trials.csv      # Generated output
│   └── summary.md      # Generated markdown summary
└── README.md
```

---

## Key Finding

See `results/summary.md` after running the script. The analysis quantifies the ratio of Global North to Global South trials and identifies the top contributing countries — revealing a systematic mismatch between where hypertension research is conducted and where its burden is highest.

---

## Author

Agastya Munnangi  
[GitHub](https://github.com/Agastya191) · [Portfolio](https://agastya191.github.io)
