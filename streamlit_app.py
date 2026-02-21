import streamlit as st
import re
import pymorphy3
from preprocessing import preprocess, clean_text

# Инициализация морфологического анализатора
morph = pymorphy3.MorphAnalyzer()

st.title("Прототип веб-ресурса для предобработки текста")
st.write("Загрузите текстовый файл в формате .txt для получения очищенного текста и списка лемм.")

uploaded_file = st.file_uploader("Выберите файл", type=["txt"])

if uploaded_file is not None:
    # Чтение файла
    raw_text = uploaded_file.read().decode("utf-8")
    
    st.subheader("Исходный текст (200 символов)")
    st.text_area("Текст", raw_text[:200], height=200)
    
    cleaned_text = clean_text(raw_text)
    lemmas = preprocess(raw_text)
    
    st.subheader("Очищенный текст")
    st.text_area("После предобработки (200 символов)", cleaned_text[:200], height=200)
    
    st.subheader("Леммы")
    st.text_area("Список лемм (первые 10)", " ".join(lemmas[:10]), height=200)