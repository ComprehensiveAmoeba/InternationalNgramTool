# n-gram analysis tool — User Guide

This document explains how to use the tool, the methodology behind its calculations, and how to interpret the results.

---

## 1) What you need
- An **Excel (.xlsx)** that contains **both**:
  - **Sponsored Products Campaigns** sheet  
    - US sheet key: `Sponsored Products Campaigns`  
    - DE sheet key: `Sponsored Products-Kampagnen`
  - **Search Term report** as a sheet in the **same file**  
    - US sheet name: `SP Search Term Report`  
    - DE sheet name: `SP Bericht „Suchbegriff“`
- Make sure the **report language matches the country** you will select in the app (US or DE).

### Required columns by country

**US**
- Search term sheet: `Customer Search Term`, `Impressions`, `Clicks`, `Spend`, `Sales`, `Units`, `Campaign Name (Informational only)`
- Campaigns sheet: `Campaign Name (Informational only)`, `SKU`

**DE**
- Search term sheet: `Suchbegriff eines Kunden`, `Impressions`, `Klicks`, `Ausgaben`, `Verkäufe`, `Einheiten`, `Kampagnenname (Nur zu Informationszwecken)`
- Campaigns sheet: `Kampagnenname (Nur zu Informationszwecken)`, `SKU`

> 💡 If your Search Term Report exports as a separate file, **copy its sheet into the bulk workbook** so you upload just one .xlsx.

---

## 2) Launch the app
1. Open the Streamlit app.
2. You’ll see the logo, title, and a short description with the required report screenshot.

---

## 3) Configure inputs
1. **Select Country for Report Language**: choose **US** or **DE** (this switches column/stopword mappings).
2. **Upload file**: click **“Upload Bulk Sheet with Sponsored Products Campaigns”** and select your combined `.xlsx`.
3. **SKU analysis mode**:
   - **Full Bulk Sheet** → analyze all campaigns present.
   - **Specific SKUs** → paste SKUs (**one per line**) to limit analysis to campaigns mapped to those SKUs.
4. **Brand exclusions (optional)**: paste brand terms, **one per line**. Any search term containing any of these substrings (case-insensitive) will be removed **before** n-gramming.

---

## 4) Run the analysis
- Click **“Perform n-gram analysis”**.
- On first run, the app may download small **NLTK resources** (stopwords/wordnet). Keep internet on.
- If you chose **Specific SKUs** and none map to campaigns, you’ll get an **Excel error report** with:
  - **Unmapped SKUs**
  - **SKU to Campaign Mapping**
- If your filters remove everything, you’ll see **“The filtered dataset is empty.”**

---

## 5) Methodology of Aggregation

The tool works in four structured steps once your Bulk + Search Term data is loaded:

### 1. Tokenization & Cleaning
- Each row in the **Search Term Report** is processed.
- Search term text is:
  - Lowercased  
  - Split into words (`\\b\\w+\\b`)  
  - Non-alphabetic tokens removed  
  - Stopwords removed (English or German, plus custom fillers)  
  - Remaining tokens **lemmatized** with `WordNetLemmatizer`

Example: `"best running shoes for men"` → `["best", "running", "shoe", "men"]`

### 2. N-gram Generation
- For each cleaned token list:
  - **Monograms** = single words  
  - **Bigrams** = sliding pairs  
  - **Trigrams** = sliding triples
- Added as a new column.

### 3. Exploding and Grouping
- Data is **exploded** so each search term row produces multiple rows, one per n-gram.  
  - E.g. `"best running shoe"` with 10 clicks contributes 10 clicks to `"best"`, `"running"`, `"shoe"`, `"best running"`, `"running shoe"`, and `"best running shoe"`.
- Grouped by unique n-gram, summing:  
  - Impressions  
  - Clicks  
  - Spend  
  - Sales  
  - Units

### 4. Derived Metrics
After grouping, the following KPIs are calculated:

- **CTR (Click-Through Rate)** = Clicks / Impressions  
- **Conversion Rate (CVR)** = Units / Clicks  
- **ACOS (Advertising Cost of Sales)** = Spend / Sales  
- **CPA (Cost per Acquisition)** = Spend / Units  
- **CPC (Cost per Click)** = Spend / Clicks  

### 5. Sorting
- Within each sheet (`Monograms`, `Bigrams`, `Trigrams`), rows are sorted by **Spend descending**.
- A consolidated `Report` sheet merges them all with a `N-Gram Type` column.

---

## 6) Download your results
When finished you’ll see:
- ✅ **“Analysis completed. Download the report below:”**
- A **Download Excel File** link containing four sheets:
  - `Monograms`
  - `Bigrams`
  - `Trigrams`
  - `Report`

---

## 7) How to read & use the output
- **Top-spend n-grams**: highest potential optimization impact.
- **High clicks + low/no sales** → candidates for **negatives**.
- **High CR, good ACOS** → **harvest** into keywords/product targets.
- **Bigrams/Trigrams** reveal context for refining match types and ad copy.
- **Brand exclusions**: keep focus on generic queries.

---

## 8) Tips & troubleshooting
- **Sheet names/columns must match exactly** (see section 1).
- **Language mismatch** (e.g., DE file + US selection) will break mappings.
- **Stopwords**: English/German + custom fillers are removed. You can edit the code if you need to keep specific words.
- **NaN/∞ metrics**: happen when denominators are 0. Filter these downstream.
- **SKU mapping**: campaigns are linked to SKUs via the Campaigns sheet. If a campaign has multiple SKUs, the last row read will win—clean your mapping if needed.

---

## 9) Best practices for workflow
1. Pull the latest **Bulk + Search Term** reports.
2. Merge the sheets into one `.xlsx`.
3. Run **brand-excluded** analysis to focus on generic demand.
4. Action list:
   - Add **negatives** for wasteful n-grams.
   - **Harvest** winning n-grams into new KWs/targets.
   - Adjust **bids/budgets** based on ACOS/CR.
5. Re-run weekly to track improvements.

---

## 10) Data privacy
- The app processes data **locally** in your browser session.  
- Only the files you upload are used.  
- No external APIs are called for your campaign data.

---
"""

with open("/mnt/data/ngram_tool_guide.txt", "w") as f:
    f.write(content)

"/mnt/data/ngram_tool_guide.txt"
