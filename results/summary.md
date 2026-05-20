# Geographic Representation in Hypertension Clinical Trials
## PubMed Analysis — 100 Most Recent Clinical Trials

**Search Query:** `hypertension[Title/Abstract] AND Clinical Trial[pt]`  
**Publication Range:** 2026–2026  
**Total Trials Analyzed:** 100

---

## Key Finding: Geographic Representation Gap

| Region | Trials | Percentage |
|---|---|---|
| Global North | 46 | 46.0% |
| Global South | 29 | 29.0% |
| Unknown/Other | 25 | 25.0% |

**Representation ratio:** For every 1 Global South trial, there are approximately 1.6 Global North trials.

---

## Top 15 Countries by Trial Count

| Country | Trials |
|---|---|
| USA | 23 |
| China | 12 |
| India | 4 |
| The Netherlands | 4 |
| Brazil | 3 |
| Republic of Korea | 3 |
| Egypt | 3 |
| Spain | 2 |
| United Kingdom | 2 |
| Pakistan | 2 |
| Switzerland | 2 |
| Sweden | 1 |
| Ann Arbor | 1 |
| New York | 1 |
| Iowa | 1 |


---

## Interpretation

Hypertension disproportionately affects populations in the Global South: it is the leading cause of cardiovascular mortality in sub-Saharan Africa, South Asia, and Latin America. However, this analysis shows that 46.0% of clinical trials are conducted in Global North institutions.

This creates a systematic bias in treatment evidence: clinical guidelines derived from these trials may not reflect how hypertension presents, progresses, or responds to treatment in lower-income populations. Factors such as dietary patterns, genetic variation, access to antihypertensive medications, and comorbidity profiles differ substantially across regions.

---

## Methodology

- Data source: PubMed via NCBI Entrez API (Biopython)
- Country extraction: parsed from author affiliation strings (last segment after final comma)
- Region classification: based on UN HDI groupings (Global North = high-income OECD + select high-HDI nations)
- Primary country assigned from first author's first affiliation
- Scripts: `fetch_trials.py` | Output: `results/trials.csv`
