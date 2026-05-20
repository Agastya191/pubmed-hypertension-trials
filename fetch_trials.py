import os
import time
import re
import pandas as pd
from Bio import Entrez

# configuration

Entrez.email = "agmunnangi@agastya191.github.io" 
SEARCH_TERM  = "hypertension[Title/Abstract] AND Clinical Trial[pt]"
MAX_RESULTS  = 100
OUTPUT_DIR   = "results"

# countries 

GLOBAL_NORTH = {
    "usa", "united states", "u.s.", "u.s.a", "us",
    "uk", "united kingdom", "england", "scotland", "wales",
    "canada", "australia", "new zealand",
    "germany", "france", "italy", "spain", "netherlands",
    "sweden", "norway", "denmark", "finland", "switzerland",
    "austria", "belgium", "portugal", "ireland", "greece",
    "japan", "south korea", "singapore", "israel",
    "czech republic", "poland", "hungary", "slovakia",
    "luxembourg", "iceland", "liechtenstein", "monaco",
    "taiwan", "hong kong",
}

GLOBAL_SOUTH = {
    "china", "india", "brazil", "mexico", "indonesia",
    "pakistan", "nigeria", "bangladesh", "ethiopia", "philippines",
    "egypt", "vietnam", "turkey", "iran", "thailand",
    "south africa", "kenya", "ghana", "tanzania", "uganda",
    "colombia", "argentina", "peru", "venezuela", "chile",
    "malaysia", "myanmar", "cambodia", "laos", "nepal",
    "sri lanka", "iraq", "syria", "jordan", "lebanon",
    "morocco", "algeria", "tunisia", "libya", "sudan",
    "senegal", "cameroon", "mozambique", "zambia", "zimbabwe",
    "cuba", "ecuador", "bolivia", "paraguay", "uruguay",
    "saudi arabia", "uae", "qatar", "kuwait", "bahrain",
    "russia", "ukraine", "kazakhstan", "uzbekistan",
}


def classify_region(country: str) -> str:
    """Classify a country string as Global North, Global South, or Unknown."""
    if not country:
        return "Unknown"
    c = country.lower().strip()
    for north in GLOBAL_NORTH:
        if north in c:
            return "Global North"
    for south in GLOBAL_SOUTH:
        if south in c:
            return "Global South"
    return "Unknown"


def extract_country_from_affiliation(affiliation: str) -> str:
    """
    Extract the most likely country from an affiliation string.
    Affiliations typically end with the country name after the last comma.
    Handles common abbreviations and edge cases.
    """
    if not affiliation:
        return ""

    affiliation = re.sub(r"\S+@\S+", "", affiliation)

    parts = [p.strip().rstrip(".") for p in re.split(r"[;,]", affiliation)]
    parts = [p for p in parts if len(p) > 2]

    if not parts:
        return ""

    candidate = parts[-1].strip()
    candidate = re.sub(r"\s+\d{4,}$", "", candidate).strip()
    us_match = re.search(
        r"\b(USA|U\.S\.A\.|United States|U\.S\.)\b", affiliation, re.IGNORECASE
    )
    if us_match:
        return "USA"

    uk_match = re.search(
        r"\b(United Kingdom|UK|England|Scotland|Wales|U\.K\.)\b",
        affiliation, re.IGNORECASE
    )
    if uk_match:
        return "United Kingdom"

    return candidate


def fetch_pubmed_ids(term: str, max_results: int) -> list:
    """
    Search PubMed and return a list of article IDs.
    """
    print(f"Searching PubMed for: {term}")
    handle = Entrez.esearch(
        db="pubmed",
        term=term,
        retmax=max_results,
        sort="pub date",
    )
    record = Entrez.read(handle)
    handle.close()

    ids = record["IdList"]
    print(f"Found {record['Count']} total results. Fetching {len(ids)} records.")
    return ids


def fetch_article_details(pmids: list) -> list:
    """
    Fetch full article details for a list of PubMed IDs.
    Returns a list of parsed record dicts.
    Rate limited to 3 requests/second (NCBI policy).
    """
    records = []
    batch_size = 20

    for i in range(0, len(pmids), batch_size):
        batch = pmids[i : i + batch_size]
        print(f"  Fetching records {i+1}–{i+len(batch)}...")

        handle = Entrez.efetch(
            db="pubmed",
            id=",".join(batch),
            rettype="xml",
            retmode="xml",
        )
        batch_records = Entrez.read(handle)
        handle.close()

        for article in batch_records["PubmedArticle"]:
            records.append(parse_article(article))

        time.sleep(0.34)

    return records


def parse_article(article):
    """
    Parse a single PubMed article record into a flat dict.
    Extracts: PMID, title, year, journal, authors, affiliations, countries.
    """
    medline = article["MedlineCitation"]
    art     = medline["Article"]

    # PMID
    pmid = str(medline["PMID"])

    # Title
    title = str(art.get("ArticleTitle", ""))

    # Year
    try:
        year = str(art["Journal"]["JournalIssue"]["PubDate"].get("Year", ""))
    except Exception:
        year = ""

    # jorunal
    try:
        journal = str(art["Journal"]["Title"])
    except Exception:
        journal = ""

    # Authors and affiliations
    authors      = []
    affiliations = []

    author_list = art.get("AuthorList", [])
    for author in author_list:
        last  = str(author.get("LastName", ""))
        first = str(author.get("ForeName", ""))
        if last:
            authors.append(f"{last} {first}".strip())

        aff_list = author.get("AffiliationInfo", [])
        for aff in aff_list:
            aff_str = str(aff.get("Affiliation", ""))
            if aff_str and aff_str not in affiliations:
                affiliations.append(aff_str)

    countries = []
    for aff in affiliations:
        country = extract_country_from_affiliation(aff)
        if country and country not in countries:
            countries.append(country)

    primary_country = countries[0] if countries else "Unknown"
    primary_region  = classify_region(primary_country)

    return {
        "pmid":            pmid,
        "title":           title,
        "year":            year,
        "journal":         journal,
        "n_authors":       len(authors),
        "authors":         "; ".join(authors[:5]), 
        "affiliations":    " | ".join(affiliations[:3]),
        "primary_country": primary_country,
        "primary_region":  primary_region,
        "all_countries":   "; ".join(countries),
    }


def build_summary(df: pd.DataFrame) -> str:
    """
    Build a markdown summary of the representation gap.
    """
    total = len(df)
    region_counts = df["primary_region"].value_counts()
    country_counts = df["primary_country"].value_counts().head(15)

    north_n   = region_counts.get("Global North", 0)
    south_n   = region_counts.get("Global South", 0)
    unknown_n = region_counts.get("Unknown", 0)

    north_pct   = round(north_n / total * 100, 1)
    south_pct   = round(south_n / total * 100, 1)
    unknown_pct = round(unknown_n / total * 100, 1)

    year_range = f"{df['year'].min()}–{df['year'].max()}" if "year" in df else "N/A"

    # Top countries table
    country_table = "| Country | Trials |\n|---|---|\n"
    for country, count in country_counts.items():
        country_table += f"| {country} | {count} |\n"

    summary = f"""# Geographic Representation in Hypertension Clinical Trials
## PubMed Analysis — 100 Most Recent Clinical Trials

**Search Query:** `hypertension[Title/Abstract] AND Clinical Trial[pt]`  
**Publication Range:** {year_range}  
**Total Trials Analyzed:** {total}

---

## Key Finding: Geographic Representation Gap

| Region | Trials | Percentage |
|---|---|---|
| Global North | {north_n} | {north_pct}% |
| Global South | {south_n} | {south_pct}% |
| Unknown/Other | {unknown_n} | {unknown_pct}% |

**Representation ratio:** For every 1 Global South trial, there are approximately {round(north_n/south_n, 1) if south_n > 0 else "N/A"} Global North trials.

---

## Top 15 Countries by Trial Count

{country_table}

---

## Interpretation

Hypertension disproportionately affects populations in the Global South — it is the leading cause of cardiovascular mortality in sub-Saharan Africa, South Asia, and Latin America. However, this analysis shows that **{north_pct}% of clinical trials** are conducted in Global North institutions.

This creates a systematic bias in treatment evidence: clinical guidelines derived from these trials may not reflect how hypertension presents, progresses, or responds to treatment in lower-income populations. Factors such as dietary patterns, genetic variation, access to antihypertensive medications, and comorbidity profiles differ substantially across regions.

The result is a literature that is technically rigorous but geographically narrow — producing recommendations that are applied globally but validated locally.

---

## Methodology

- Data source: PubMed via NCBI Entrez API (Biopython)
- Country extraction: parsed from author affiliation strings (last segment after final comma)
- Region classification: based on UN HDI groupings (Global North = high-income OECD + select high-HDI nations)
- Primary country assigned from first author's first affiliation
- Scripts: `fetch_trials.py` | Output: `results/trials.csv`
"""
    return summary


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # fetch IDs
    pmids = fetch_pubmed_ids(SEARCH_TERM, MAX_RESULTS)

    # get full records
    print("\nFetching article details...")
    records = fetch_article_details(pmids)

    # create DataFrame
    df = pd.DataFrame(records)
    df.to_csv(os.path.join(OUTPUT_DIR, "trials.csv"), index=False)
    print(f"\nSaved {len(df)} records to {OUTPUT_DIR}/trials.csv")

    # get stats
    print("\nRegion breakdown:")
    print(df["primary_region"].value_counts())
    print("\nTop 10 countries:")
    print(df["primary_country"].value_counts().head(10))

    # create markdown summary
    summary = build_summary(df)
    summary_path = os.path.join(OUTPUT_DIR, "summary.md")
    with open(summary_path, "w") as f:
        f.write(summary)
    print(f"\nSaved summary to {summary_path}")
    print("\nDone.")


if __name__ == "__main__":
    main()
