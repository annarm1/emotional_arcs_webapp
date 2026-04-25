import streamlit as st
import nltk

from tei_parser import extract_paragraphs, extract_character_replicas, extract_txt_from_zip, parse_txt
from segmentation import segment_by_paragraphs, words_in_par_count, window_with_overlap
from sentiment_model import estimate_sentiment
from utils import smooth_signal, plot_curve_interactive


# Функция для полготовки файла с сегментами для загрузки
def prepare_segments_for_download(segments, sentiments):
    lines = []

    for i, (segment, sentiment) in enumerate(zip(segments, sentiments), start=1):
        lines.append(f"=== Сегмент {i} ===")
        lines.append(f"Тональность: {round(sentiment, 3)}")
        lines.append(segment)
        lines.append("")

    return "\n".join(lines)


# Функция для сегментации
def segmentation_ui(min_def, max_def, min_range, max_range):
    st.subheader("⚙️ Параметры сегментации")

    st.info(
        "Сегменты формируются на основе абзацев."
        "Контекстное окно добавляет предложения из предыдущего сегмента."
    )

    min_w = st.slider("Минимум слов", *min_range, min_def, step=10)
    max_w = st.slider("Максимум слов", *max_range, max_def, step=10)

    if min_w >= max_w:
        st.warning("Минимальное значение должно быть меньше максимального")
        st.stop()

    return min_w, max_w


# Функция для применения окна
def overlap_ui(max_val=5, default=2):
    st.subheader("🔁 Параметры контекстного окна")

    use_overlap = st.checkbox("Добавить контекстное окно", value=True)

    overlap_n = 0
    if use_overlap:
        overlap_n = st.slider("Размер окна (предложения)", 1, max_val, default)

    return use_overlap, overlap_n


# Функция анализа и визуализации
def run_analysis(segments, title):
    with st.spinner("Анализируем текст..."):
        sentiments = estimate_sentiment(segments)
        smoothed = smooth_signal(sentiments)

    # скачать сегменты
    txt_data = prepare_segments_for_download(segments, sentiments)

    st.download_button(
        "📥 Скачать сегменты (.txt)",
        txt_data,
        "segments.txt",
        "text/plain"
    )

    # график
    fig = plot_curve_interactive(smoothed, sentiments, title)
    st.plotly_chart(fig, use_container_width=True)

    # статистика
    st.write("📊 Статистика:")
    st.write(f"- Сегментов: {len(segments)}")
    st.write(f"- Средняя тональность: {sum(sentiments)/len(sentiments):.3f}")


with st.spinner("Загрузка модели..."):
    from sentiment_model import load_model
    load_model()

st.title("📊 Анализ эмоциональной динамики текста")

data_mode = st.radio(
    "Выберите тип входных данных",
    ["TXT (один файл)", "TEI (XML) — с возможностью анализа речи персонажей"]
)

if data_mode == "TEI (XML) — с возможностью анализа речи персонажей":

    mode = st.radio(
        "Выберите тип анализа",
        ["Общая сюжетная арка", "Арка персонажа"]
    )

    # СЮЖЕТНАЯ АРКА
    if mode == "Общая сюжетная арка":

        uploaded_file = st.file_uploader(
                "Загрузите документ с TEI-разметкой",
                type=["xml"]
            )

        if uploaded_file:
            st.success("Файл успешно загружен!")

            paragraphs = extract_paragraphs(uploaded_file)
        
            st.write(f"Количество параграфов: {len(paragraphs)}")
            st.write(f"Среднее количество слов в одном параграфе: {words_in_par_count(paragraphs)}")

            min_words, max_words = segmentation_ui(
                150, 300,
                (10, 200),
                (20, 400)
            )

                
            if min_words >= max_words:
                st.warning("Минимальное значение должно быть меньше максимального")
                st.stop()
                
            segments = segment_by_paragraphs(
                paragraphs,
                min_words,
                max_words
            )

            st.write(f"📊 Количество сегментов: {len(segments)}")
            
            use_overlap, overlap_n = overlap_ui()

            if use_overlap and overlap_n > 0:
                segments = window_with_overlap(segments, overlap_n)

            # --- 3. Общая эмоциональная динамика ---
            st.subheader("📈 Эмоциональная динамика")

            if st.button("Построить эмоциональную арку"):
                run_analysis(segments, "Общая эмоциональная динамика")

        # АРКИ ПЕРСОНАЖЕЙ
    elif mode == "Арка персонажа":
        uploaded_file = st.file_uploader(
                "Загрузите документ с TEI-разметкой",
                type=["xml"]
            )
        
        if uploaded_file:
            replicas = extract_character_replicas(uploaded_file)
            character_map = {
                k.strip("#"): v
                for k, v in replicas.items()
                if len(v) >= 5
            }
            if not character_map:
                st.warning("Недостаточно данных по персонажам")
                st.stop()
            
            # сортировка по количеству реплик
            characters = sorted(
                character_map.keys(),
                key=lambda x: len(character_map[x]),
                reverse=True
            )

            selected = st.selectbox(
                "Выберите персонажа",
                [f"{c} ({len(character_map[c])})" for c in characters]
            )

            selected_character = selected.split(" (")[0]
            char_replicas = character_map[selected_character]

            st.write(
            f"Количество реплик: {len(char_replicas)}"
            )

            paragraphs = char_replicas

            min_words, max_words = segmentation_ui(
                50, 100,
                (20, 150),
                (50, 300)
            )
                
            if min_words >= max_words:
                st.warning("Минимальное значение должно быть меньше максимального")
                st.stop()

            segments = segment_by_paragraphs(
                paragraphs,
                min_words=min_words,
                max_words=max_words
            )

            st.write(f"📊 Количество сегментов: {len(segments)}")        
            use_overlap, overlap_n = overlap_ui()

            if use_overlap and overlap_n > 0:
                segments = window_with_overlap(segments, overlap_n)

            # --- 3. Общая эмоциональная динамика ---
            st.subheader("📈 Эмоциональная динамика")

            if st.button("Построить эмоциональную арку"):
                run_analysis(segments, f"Эмоциональная арка. {selected_character}")


elif data_mode == "TXT (один файл)":
    uploaded_file = st.file_uploader("Загрузите TXT файл", type=["txt"])
    if uploaded_file:
        st.success("Файл успешно загружен!")
        paragraphs, sentences = parse_txt(uploaded_file)
        st.write(f"Количество параграфов: {len(paragraphs)}")
        st.write(f"Среднее количество слов в одном параграфе: {words_in_par_count(paragraphs)}")

        min_words, max_words = segmentation_ui(
            150, 300,
            (10, 200),
            (20, 400)
        )
                
        if min_words >= max_words:
            st.warning("Минимальное значение должно быть меньше максимального")
            st.stop()
                
        segments = segment_by_paragraphs(
            paragraphs,
            min_words,
            max_words
        )

        st.write(f"📊 Количество сегментов: {len(segments)}")
            
        use_overlap, overlap_n = overlap_ui()

        if use_overlap and overlap_n > 0:
            segments = window_with_overlap(segments, overlap_n)

        # --- 3. Общая эмоциональная динамика ---
        st.subheader("📈 Эмоциональная динамика")

        if st.button("Построить эмоциональную арку"):
            run_analysis(segments, "Общая эмоциональная динамика")