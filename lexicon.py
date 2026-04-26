import streamlit as st
import re
import pymorphy3  # type: ignore
import nltk
nltk.download('punkt')

morph = pymorphy3.MorphAnalyzer()

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^а-яё\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def lemmatize(cleaned_text):
    words = cleaned_text.split()
    
    lemmas = [morph.parse(word)[0].normal_form for word in words if word]
    
    return " ".join(lemmas)


@st.cache_data
def load_rusentilex(filepath):
    """
    Загружает RuSentiLex
    """
    lexicon = {}

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if not line.startswith('!'):
                line = line.strip()
                if not line:
                    continue
                parts = [p.strip() for p in line.split(",")]
                if len(parts) < 4:
                    continue
                lemma = parts[2]
                polarity = parts[3]

                if polarity == "positive":
                    lexicon[lemma] = 1
                elif polarity == "negative":
                    lexicon[lemma] = -1

        return lexicon
    

def count_sentiment_lex(segments, lexicon):
    sentiments_out = []
    for segment in segments:
        max_ngram = 7
        segment = clean_text(segment)
        words = lemmatize(segment).split()

        score = 0
        i = 0
        n = len(words)

        while i < n:
            matched = False

            # пробуем самые длинные выражения
            for size in range(max_ngram, 0, -1):
                if i + size > n:
                    continue

                phrase = " ".join(words[i:i+size])

                if phrase in lexicon:
                    score += lexicon[phrase]
                    i += size
                    matched = True
                    break

            if not matched:
                i += 1

        if n > 0:
            score = score / n * 100
        sentiments_out.append(score)
    return sentiments_out