import nltk
import streamlit as st

nltk.download('punkt')
nltk.download('punkt_tab')

def words_in_par_count(paragraphs): 
    """ 
    Подсчет слов в параграфе 
    """ 
    count_words = [] 
    for paragraph in paragraphs: 
        count_words.append(len(nltk.word_tokenize(paragraph)))
    
    return round(sum(count_words)/len(count_words))


def segments_by_paragraphs(paragraphs, min_words, max_words):
    """
    Гибридная сегментация:
    - маленькие абзацы не изменяются
    - большие сегментируются по предложениям
    """

    chunks = []
    current_chunk = []
    current_len = 0

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        words_in_par = len(nltk.word_tokenize(paragraph))

        # --- СЛИШКОМ БОЛЬШОЙ АБЗАЦ ---
        if words_in_par > max_words:
            sentences = nltk.sent_tokenize(paragraph)

            for sent in sentences:
                sent_len = len(nltk.word_tokenize(sent))

                if current_len + sent_len > max_words:
                    if current_chunk:
                        chunks.append(" ".join(current_chunk))
                        current_chunk = []
                        current_len = 0

                current_chunk.append(sent)
                current_len += sent_len

                if current_len >= min_words:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_len = 0

        # --- ОБЫЧНЫЙ АБЗАЦ ---
        else:
            if current_len + words_in_par > max_words:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_len = 0

            current_chunk.append(paragraph)
            current_len += words_in_par

    # хвост
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def apply_overlap(segments, overlap_sentences):
    result = []

    prev_sentences = []

    for segment in segments:
        current_sentences = nltk.sent_tokenize(segment)

        overlap = (
            prev_sentences[-overlap_sentences:]
            if prev_sentences
            else []
        )

        result.append(
            " ".join(overlap + current_sentences)
        )

        prev_sentences = current_sentences

    return result


def segmentation_settings_ui(
    paragraphs,
    mode,
    min_default=80,
    max_default=200,
    min_range=(20, 300),
    max_range=(50, 500)
):
    if mode == 'Арка персонажа':
        st.write(f"Количество реплик: {len(paragraphs)}")
        st.write(f"Среднее количество слов в реплике: {words_in_par_count(paragraphs)}")

    elif mode == 'Общая сюжетная арка' or mode == 'txt':
        st.write(f'Количество параграфов: {len(paragraphs)}')
        st.write(f'Среднее количество слов в одном параграфе: {words_in_par_count(paragraphs)}')

    st.subheader("⚙️ Параметры сегментации")

    st.info(
        "Сегменты формируются на основе абзацев и предложений в них. "
        "Выберите необходимые параметры сегментации. " \
        "Меньшее количество сегментов даст более плавную картину. "
        "Чем больше сегментов, тем точнее анализ каждого, но также время загрузки может увеличиться. " \
    )

    min_words = st.slider(
        "Минимум слов",
        *min_range,
        min_default,
        step=10
    )

    max_words = st.slider(
        "Максимум слов",
        *max_range,
        max_default,
        step=10
    )
    
    if min_words > max_words:
        st.warning("Минимальное значение должно быть меньше максимального")
        st.stop()

    st.subheader("🔁 Параметры контекстного окна")
    
    st.info(
        "Контекстное окно добавляет n-количество предложений из предыдущего сегмента. " \
        "Благодаря этому динамика становится более плавной"
    )

    use_overlap = st.checkbox(
        "Добавить контекстное окно",
        value=True
    )

    overlap_sentences = 0

    if use_overlap:
        overlap_sentences = st.slider(
            "Размер окна",
            1,
            5,
            2
        )

    return (
        min_words,
        max_words,
        use_overlap,
        overlap_sentences
    )


def segment_text(
    paragraphs,
    min_words,
    max_words,
    use_overlap,
    overlap_sentences=2
):
    """
    Полный pipeline сегментации текста.
    """

    segments = segments_by_paragraphs(
        paragraphs,
        min_words,
        max_words
    )

    if use_overlap:
        segments = apply_overlap(
            segments,
            overlap_sentences
        )

    return segments


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

    txt_data = "\n".join(lines)

    st.download_button(
        "📥 Скачать сегменты (.txt)",
        txt_data,
        "segments.txt",
        "text/plain"
    )

    st.write(f'Результат: {len(segments)} сегментов')