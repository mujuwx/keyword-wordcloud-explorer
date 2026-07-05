import re
from collections import Counter
from pathlib import Path

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS


TOP_X_TERMS = 100
KEYWORD_COLUMN = "Keyword Phrase"
VOLUME_COLUMN = "Search Volume"


st.title("Keyword Word Cloud Explorer")

st.info("""
Upload an Amazon keyword research spreadsheet from Helium10 (e.g. Magnet or Cerebro) and generate a word cloud showing the most common words that appear within those keyword phrases.

You can also perfom some basic, explorative analysis. Select any word from the dropdown to see:
- The keyword phrases containing that word
- The monthly search volume for those phrases
- Related search opportunities
""")

uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

stopwords = STOPWORDS.copy()
stopwords.update({
    "amazon",
    "uk"
})

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df = df.dropna(subset=[KEYWORD_COLUMN, VOLUME_COLUMN])

    word_frequencies = Counter()

    for _, row in df.iterrows():
        keyword_phrase = str(row[KEYWORD_COLUMN]).lower()
        words = re.findall(r"\b[a-z0-9]+\b", keyword_phrase)

        for word in words:
            if word not in stopwords:
                word_frequencies[word] += 1

    top_word_frequencies = dict(word_frequencies.most_common(TOP_X_TERMS))

    wordcloud = WordCloud(
        width=1600,
        height=800,
        background_color="white"
    ).generate_from_frequencies(top_word_frequencies)

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

    selected_word = st.selectbox(
        "Choose a word to inspect",
        list(top_word_frequencies.keys())
    )

    matching_rows = df[
        df[KEYWORD_COLUMN]
        .astype(str)
        .str.lower()
        .str.contains(rf"\b{re.escape(selected_word)}\b", regex=True)
    ][[KEYWORD_COLUMN, VOLUME_COLUMN]]

    matching_rows = matching_rows.sort_values(
        by=VOLUME_COLUMN,
        ascending=False
    )

    st.subheader(f"Keyword phrases containing '{selected_word}'")
    st.dataframe(matching_rows, use_container_width=True)