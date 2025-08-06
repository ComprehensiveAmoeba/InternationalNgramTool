# n-Gram Analysis Tool for Amazon Bulk Sheets

This Streamlit app helps you analyze customer search terms from Sponsored Products campaigns using n-gram breakdown (monograms, bigrams, trigrams). It works with **Amazon Bulk Sheets** exported from the Ad Console.

> Supports **US** and **DE** (German) marketplaces with language-aware stopwords and column mappings.

---

## Features

- Upload your Sponsored Products Bulk Sheet (Ad Console export)
- Perform n-gram analysis on customer search terms
- Automatic removal of stopwords (based on report language)
- Monogram / Bigram / Trigram metrics:
  - Impressions
  - Clicks
  - Spend
  - Sales
  - Units
  - CTR, Conversion Rate, ACOS, CPA, CPC
- 🔧 Optional filters:
  - Only analyze specific SKUs
  - Exclude branded terms
- Download full Excel report with all breakdowns

---

## 📥 How to use

1. Run the app:

   ```bash
   streamlit run main.py
