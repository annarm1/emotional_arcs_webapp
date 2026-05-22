import streamlit as st
import re
import pymorphy3  # type: ignore
import nltk
nltk.download('punkt')

from parser import parse_word_list, parse_custom_lexicon

morph = pymorphy3.MorphAnalyzer()


def clean_text(text):
    """
    Очистка текста
    """
    text = text.lower()
    text = re.sub(r"[^а-яё\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def lemmatize(cleaned_text):
    """
    Лемматизация
    """
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
    """
    Подсчет тональности: лексиконный метод
    """
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



def lexicon_settings_ui():

    lexicon_mode = st.radio(
        "Источник словаря",
        [
            "Использовать RuSentiLex",
            "Добавить слова в RuSentiLex",
            "Загрузить собственный словарь"
        ]
    )

    lexicon = load_rusentilex("rusentilex_2017.txt")

    # ---------------- BASE ----------------

    if lexicon_mode == "Использовать RuSentiLex":
        return lexicon

    # ---------------- EXTEND ----------------

    elif lexicon_mode == "Добавить слова в RuSentiLex":

        st.info(
            "Загрузите TXT-файлы с дополнительной "
            "лексикой. Каждая строка должна "
            "содержать одно слово или выражение."
        )

        with st.expander(
            "Пример формата словаря"
        ):

            st.code(
            "лемма\nужасный\nстрашный\nВолан-де-Морт"
                        )

        uploaded_lexicon_pos = st.file_uploader(
            "Положительная лексика",
            type=["txt"]
        )

        uploaded_lexicon_neg = st.file_uploader(
            "Отрицательная лексика",
            type=["txt"]
        )

        if uploaded_lexicon_pos:

            positive_words = parse_word_list(
                uploaded_lexicon_pos
            )

            for word in positive_words:

                if word not in lexicon:
                    lexicon[word] = 1

        if uploaded_lexicon_neg:

            negative_words = parse_word_list(
                uploaded_lexicon_neg
            )

            for word in negative_words:

                if word not in lexicon:
                    lexicon[word] = -1

        return lexicon

    # ---------------- CUSTOM ----------------

    elif lexicon_mode == "Загрузить собственный словарь":

        with st.expander(
            "Формат пользовательского словаря"
        ):

            st.code(
                """лемма\nтональность\nпрекрасный, positive\nужасный, negative\nрадость, positive"""
                                )

        uploaded_lexicon_user = st.file_uploader(
            "TXT-файл словаря",
            type=["txt"]
        )

        if uploaded_lexicon_user:
            try:
                return parse_custom_lexicon(
                    uploaded_lexicon_user
                )
            except Exception:
                st.error(
                    "Не удалось обработать словарь."
                )
        return None
