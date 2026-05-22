import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from lexicon import load_rusentilex, count_sentiment_lex


MODEL_NAME = 'cointegrated/rubert-tiny-sentiment-balanced'


@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

    if torch.cuda.is_available():
        model = model.cuda()

    model.eval()

    return tokenizer, model


def estimate_sentiment(messages):
    tokenizer, model = load_model()

    sentiment_out = []

    for text in messages:
        with torch.no_grad():
            inputs = tokenizer(
                text,
                return_tensors='pt',
                truncation=True,
                padding=True
            ).to(model.device)

            proba = torch.sigmoid(model(**inputs).logits).cpu().numpy()[0]
            sentiment_out.append(proba.dot([-1, 0, 1]))

    return sentiment_out

def run_analysis(segments, mode):
    """
    Функция анализа и визуализации
    """
    if mode == 'Нейросетевой (RuBERT)':
        sentiments = estimate_sentiment(segments)
    elif mode == 'Лексиконный (RuSentiLex)':
        lexicon = load_rusentilex("rusentilex_2017.txt")
        sentiments = count_sentiment_lex(segments, lexicon)
    return sentiments