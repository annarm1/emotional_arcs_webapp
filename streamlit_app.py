import streamlit as st

from tei_parser import extract_paragraphs
from segmentation import segment_by_paragraphs, words_in_par_count, window_with_overlap
from sentiment_model import estimate_sentiment
from utils import smooth_signal, plot_curve_interactive

def prepare_segments_for_download(segments, sentiments):
    lines = []

    for i, (segment, sentiment) in enumerate(zip(segments, sentiments), start=1):
        lines.append(f"=== Сегмент {i} ===")
        lines.append(f"Тональность: {round(sentiment, 3)}")
        lines.append(segment)
        lines.append("")

    return "\n".join(lines)


with st.spinner("Загрузка модели..."):
    from sentiment_model import load_model
    load_model()

st.title("📊 Анализ эмоциональной динамики текста")

# --- 1. Загрузка файла ---
uploaded_file = st.file_uploader(
        "Загрузите документ с TEI-разметкой",
        type=["xml"]
    )

if uploaded_file:

    st.success("Файл успешно загружен!")

    # --- Парсинг ---
    paragraphs = extract_paragraphs(uploaded_file)
   
    st.write(f"Количество параграфов: {len(paragraphs)}")
    st.write(f"Среднее количество слов в одном параграфе: {words_in_par_count(paragraphs)}")



    st.subheader("⚙️ Параметры сегментации")

    st.info(
    "Сегменты формируются на основе абзацев. "
    "Контекстное окно добавляет предложения из предыдущего сегмента, "
    "что делает эмоциональную кривую более плавной."
    )
    

    min_words = st.slider(
        "Минимальное количество слов в сегменте",
        min_value=50,
        max_value=200,
        value=150,
        step=10
    )

    max_words = st.slider(
        "Максимальное количество слов в сегменте",
        min_value=100,
        max_value=400,
        value=300,
        step=10
    )
        
    if min_words >= max_words:
        st.warning("Минимальное значение должно быть меньше максимального")
        st.stop()
        
    # --- Сегменты ---
    segments = segment_by_paragraphs(
        paragraphs,
        min_words,
        max_words
    )

    st.write(f"📊 Количество сегментов: {len(segments)}")
    

    st.subheader("🔁 Параметры контекстного окна")

    use_overlap = st.checkbox(
        "Добавить контекст предыдущего сегмента",
        value=True
    )

    overlap_n = st.slider(
        "Количество предложений из предыдущего сегмента",
        min_value=0,
        max_value=5,
        value=2
    )

    if use_overlap and overlap_n > 0:
        segments = window_with_overlap(segments, overlap_n)

    # --- 3. Общая эмоциональная динамика ---
    st.subheader("📈 Эмоциональная динамика")

    if st.button("Построить эмоциональную арку"):

        with st.spinner("Анализируем текст..."):

            sentiments = estimate_sentiment(segments)
            smoothed = smooth_signal(sentiments)

        st.success("Готово!")

        fig = plot_curve_interactive(
            smoothed,
            "Общая эмоциональная динамика"
        )

        st.plotly_chart(fig, use_container_width=True)

        txt_data = prepare_segments_for_download(segments, sentiments)
        
        st.download_button(
            label="📥 Скачать сегменты (.txt)",
            data=txt_data,
            file_name="segments.txt",
            mime="text/plain"
        )

        # --- дополнительная инфа ---
        st.write("📊 Статистика:")

        st.write(f"- Количество сегментов: {len(segments)}")
        st.write(f"- Средняя тональность: {sum(sentiments)/len(sentiments):.3f}")