import streamlit as st
import pandas as pd
import re
import datetime
from nltk import bigrams, trigrams
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import nltk
import base64
from io import BytesIO
import ssl

# Bypass SSL for nltk downloads
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Download required nltk resources
for resource in ["wordnet", "stopwords"]:
    try:
        nltk.data.find(f"corpora/{resource}")
    except LookupError:
        nltk.download(resource)

# Persistent session state
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "report_download_link" not in st.session_state:
    st.session_state.report_download_link = None

# Logo and header
logo_url = "https://assets.zyrosite.com/m5KLvqrBjzHJbZkk/soypat_logo_white_bg-A0x11BXpQ0Tr9o5B.png"
website_url = "https://www.soypat.es"
st.markdown(f'''
    <div style="text-align: center;">
        <a href="{website_url}" target="_blank">
            <img src="{logo_url}" style="max-width: 100%; height: auto;">
        </a>
    </div>
''', unsafe_allow_html=True)

st.title("n-gram analysis tool")

st.markdown("""
**Description:**  
To use this tool, go to the Bulk Operations section in the Ad Console and request a file like the one shown in this [screenshot](https://assets.zyrosite.com/m5KLvqrBjzHJbZkk/ngram_bulk_needs-YrDqqxMLQrtekppJ.png).  
Make sure the language of the report matches the selected country.
""")

# Country selection
country = st.selectbox("Select Country for Report Language", ["US", "DE"])

# Column mappings
column_map = {
    "US": {
        "search_term_sheet": "SP Search Term Report",
        "campaign_sheet_key": "Sponsored Products Campaigns",
        "search_term_col": "Customer Search Term",
        "campaign_name_col": "Campaign Name (Informational only)",
        "sku_col": "SKU",
        "impr": "Impressions",
        "clicks": "Clicks",
        "spend": "Spend",
        "sales": "Sales",
        "units": "Units"
    },
    "DE": {
        "search_term_sheet": 'SP Bericht „Suchbegriff“',
        "campaign_sheet_key": "Sponsored Products-Kampagnen",
        "search_term_col": "Suchbegriff eines Kunden",
        "campaign_name_col": "Kampagnenname (Nur zu Informationszwecken)",
        "sku_col": "SKU",
        "impr": "Impressions",
        "clicks": "Klicks",
        "spend": "Ausgaben",
        "sales": "Verkäufe",
        "units": "Einheiten"
    }
}
cols = column_map[country]

# Stopwords per country
if country == "DE":
    stop_words = set(stopwords.words("german"))
    custom_german_stops = {
        "für", "mit", "von", "an", "bei", "der", "die", "das", "den", "dem",
        "ein", "eine", "einer", "eines", "und", "im", "in", "auf", "aus",
        "zu", "zum", "zur", "über", "unter", "oder", "auch", "man", "mehr",
        "weniger", "nicht", "kein", "keine", "nach", "ab", "bis", "um"
    }
    stop_words.update(custom_german_stops)
else:
    stop_words = set(stopwords.words("english"))
    stop_words.update({"in", "for", "the", "of", "if", "when", "and", "de", "para"})

# Tokenizer
def clean_tokenize(text, stop_words=set()):
    lemmatizer = WordNetLemmatizer()
    tokens = re.findall(r'\b\w+\b', str(text).lower())
    return [lemmatizer.lemmatize(token) for token in tokens if token.isalpha() and token not in stop_words]

# Aggregator
def aggregate_ngrams(data, ngram_func, stop_words):
    data["ngrams"] = data[cols["search_term_col"]].apply(lambda x: list(ngram_func(clean_tokenize(x, stop_words))))
    ngrams_expanded = data.explode("ngrams")
    if not ngrams_expanded.empty:
        agg = ngrams_expanded.groupby("ngrams")[
            [cols["impr"], cols["clicks"], cols["spend"], cols["sales"], cols["units"]]
        ].sum().reset_index()
        agg["CTR"] = agg[cols["clicks"]] / agg[cols["impr"]]
        agg["Conversion Rate"] = agg[cols["units"]] / agg[cols["clicks"]]
        agg["ACOS"] = agg[cols["spend"]] / agg[cols["sales"]]
        agg["CPA"] = agg[cols["spend"]] / agg[cols["units"]]
        agg["CPC"] = agg[cols["spend"]] / agg[cols["clicks"]]
        return agg.sort_values(by=cols["spend"], ascending=False)
    return pd.DataFrame()

# Inputs
data_file = st.file_uploader("Upload Bulk Sheet with Sponsored Products Campaigns", type="xlsx", key="file_upload")
sku_mode = st.radio("Select SKU analysis mode:", ["Full Bulk Sheet", "Specific SKUs"], key="sku_mode")
sku_input = st.text_area("Enter SKUs (one per line)", key="sku_input") if sku_mode == "Specific SKUs" else ""
brand_exclusions = st.text_area("Optionally enter brand terms to exclude (one per line)", key="brand_exclusions")

# Run button
if st.button("Perform n-gram analysis", key="analyze_button") and data_file:
    bulk = pd.ExcelFile(data_file)
    campaign_sheets = [s for s in bulk.sheet_names if cols["campaign_sheet_key"] in s]
    campaign_to_sku = {}
    for sheet in campaign_sheets:
        df = bulk.parse(sheet)
        df = df[df[cols["sku_col"]].notnull()]
        for _, row in df.iterrows():
            campaign = row[cols["campaign_name_col"]]
            sku = row[cols["sku_col"]]
            campaign_to_sku[campaign] = sku

    search_term_data = bulk.parse(cols["search_term_sheet"])

    if sku_mode == "Specific SKUs":
        selected_skus = set(sku.strip().upper() for sku in sku_input.splitlines())
        included_campaigns = [c for c, s in campaign_to_sku.items() if s.upper() in selected_skus]
        if not included_campaigns:
            st.error("No campaigns found for the specified SKUs.")
            unmapped = selected_skus - set(s.upper() for s in campaign_to_sku.values())
            err_df = pd.DataFrame({"Unmapped SKUs": list(unmapped)})
            map_df = pd.DataFrame.from_dict(campaign_to_sku, orient="index", columns=["SKU"]).reset_index()
            map_df.rename(columns={"index": cols["campaign_name_col"]}, inplace=True)
            out = BytesIO()
            with pd.ExcelWriter(out, engine="openpyxl") as w:
                err_df.to_excel(w, sheet_name="Unmapped SKUs", index=False)
                map_df.to_excel(w, sheet_name="SKU to Campaign Mapping", index=False)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%S_%H-%M-%S")
            b64 = base64.b64encode(out.getvalue()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="error_report_{timestamp}.xlsx">Download Error Report</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.stop()
        else:
            search_term_data = search_term_data[search_term_data[cols["campaign_name_col"]].isin(included_campaigns)]

    if brand_exclusions:
        excluded_terms = set(brand_exclusions.lower().splitlines())
        search_term_data = search_term_data[~search_term_data[cols["search_term_col"]].str.lower().apply(
            lambda x: any(term in x for term in excluded_terms)
        )]

    if search_term_data.empty:
        st.error("The filtered dataset is empty.")
        st.stop()

    mono = aggregate_ngrams(search_term_data, lambda x: x, stop_words)
    bi = aggregate_ngrams(search_term_data, bigrams, stop_words)
    tri = aggregate_ngrams(search_term_data, trigrams, stop_words)

    report_df = pd.concat([mono, bi, tri], keys=["Monograms", "Bigrams", "Trigrams"])
    report_df.reset_index(level=0, inplace=True)
    report_df.rename(columns={"level_0": "N-Gram Type"}, inplace=True)

    out = BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        mono.to_excel(writer, sheet_name="Monograms", index=False)
        bi.to_excel(writer, sheet_name="Bigrams", index=False)
        tri.to_excel(writer, sheet_name="Trigrams", index=False)
        report_df.to_excel(writer, sheet_name="Report", index=False)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%S_%H-%M-%S")
    filename = f"ngram_analysis_output_{timestamp}.xlsx"
    b64 = base64.b64encode(out.getvalue()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">Download Excel File</a>'

    st.session_state.analysis_done = True
    st.session_state.report_download_link = href

# Show download link if available
if st.session_state.analysis_done and st.session_state.report_download_link:
    st.success("Analysis completed. Download the report below:")
    st.markdown(st.session_state.report_download_link, unsafe_allow_html=True)
