import streamlit as st

from utils import smooth_signal, plot_curve_interactive
from lexicon import load_rusentilex, count_sentiment_lex
from sentiment_model import estimate_sentiment
from segmentation import words_in_par_count, segment_by_paragraphs, window_with_overlap, overlap, segmentation_ui


def prepare_segments_for_download(segments, sentiments):
    """
    Функция для полготовки файла с сегментами для загрузки
    """
    lines = []

    for i, (segment, sentiment) in enumerate(zip(segments, sentiments), start=1):
        lines.append(f"=== Сегмент {i} ===")
        lines.append(f"Тональность: {round(sentiment, 3)}")
        lines.append(segment)
        lines.append("")

    return "\n".join(lines)


def overlap(max_val=5, default=2):
    """
    Функция для применения окна
    """
    st.subheader("🔁 Параметры контекстного окна")

    use_overlap = st.checkbox("Добавить контекстное окно", value=True)

    overlap_n = 0
    if use_overlap:
        overlap_n = st.slider("Размер окна (предложения)", 1, max_val, default)

    return use_overlap, overlap_n


def run_analysis(segments, mode, title):
    """
    Функция анализа и визуализации
    """
    with st.spinner("Анализируем текст..."):
        if mode == 'Нейросетевой (RuBERT)':
            sentiments = estimate_sentiment(segments)
        elif mode == 'Лексиконный (RuSentiLex)':
            lexicon = load_rusentilex("rusentilex_2017.txt")
            sentiments = count_sentiment_lex(segments, lexicon)
        smoothed = smooth_signal(sentiments)

    txt_data = prepare_segments_for_download(segments, sentiments)

    st.download_button(
        "📥 Скачать сегменты (.txt)",
        txt_data,
        "segments.txt",
        "text/plain"
    )

    fig = plot_curve_interactive(smoothed, sentiments, title)
    st.plotly_chart(fig, use_container_width=True)

    # статистика
    st.write("📊 Статистика:")
    st.write(f"- Сегментов: {len(segments)}")
    st.write(f"- Средняя тональность: {sum(sentiments)/len(sentiments):.3f}")


def make_segments(paragraphs):
    """
    Функция для сегментации (полная)
    """

    st.write(f"Количество параграфов: {len(paragraphs)}")
    st.write(f"Среднее количество слов в одном параграфе: {words_in_par_count(paragraphs)}")

    min_words, max_words = segmentation_ui(
        150, 300,
        (10, 200),
        (20, 400)
    )
                    
    segments = segment_by_paragraphs(
        paragraphs,
        min_words,
        max_words
    )

    st.write(f"📊 Количество сегментов: {len(segments)}")
                
    use_overlap, overlap_n = overlap()

    if use_overlap and overlap_n > 0:
        segments = window_with_overlap(segments, overlap_n)
        
    return segments