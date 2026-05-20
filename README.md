# pubmed-hypertension-trials

Fetches the 100 most recent PubMed clinical trials on hypertension and analyzes geographic representation across Global North and Global South institutions.

## Setup

```bash
pip install -r requirements.txt
python fetch_trials.py
```

## Output

`results/trials.csv` — trial metadata with parsed countries  
`results/summary.md` — representation gap analysis

## Finding

46% Global North · 29% Global South · 25% unresolved  
USA accounts for 23 of 100 trials.

