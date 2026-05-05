import nltk
import streamlit as st

nltk.download('punkt')
nltk.download('punkt_tab')

def words_in_par_count(paragraphs):
    count_words = []
    for paragraph in paragraphs:
        count_words.append(len(nltk.word_tokenize(paragraph)))
    return round(sum(count_words)/len(count_words))

def segment_by_paragraphs(paragraphs, min_words, max_words):
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


def window_with_overlap(segments, overlap_sentences):
    """
    Добавляет к каждому сегменту n последних предложений из предыдущего
    """

    result = []

    prev_sentences = []

    for segment in segments:
        current_sentences = nltk.sent_tokenize(segment)
        overlap = prev_sentences[-overlap_sentences:] if prev_sentences else []
        new_segment = " ".join(overlap + current_sentences)

        result.append(new_segment)

        prev_sentences = current_sentences

    return result


def segmentation_ui(min_def, max_def, min_range, max_range):
    """
    Функция для расчета min и max слов
    """
    st.subheader("⚙️ Параметры сегментации")

    st.info(
        "Сегменты формируются на основе абзацев и предложений в них. "
        "Выберите необходимые параметры сегментации. " \
        "Меньшее количество сегментов даст более плавную картину. "
        "Чем больше сегментов, тем точнее анализ каждого, но это может сказаться на итоговом результате. " \
        "Рекомендуем выбирать не более 1000 сегментов для анализа."
    )

    min_w = st.slider("Минимум слов", *min_range, min_def, step=10)
    max_w = st.slider("Максимум слов", *max_range, max_def, step=10)

    if min_w >= max_w:
        st.warning("Минимальное значение должно быть меньше максимального")
        st.stop()

    return min_w, max_w


def overlap(max_val=5, default=2):
    """
    Функция для применения окна
    """
    st.info(
        "Контекстное окно добавляет n-количество предложений из предыдущего сегмента. " \
        "Благодаря этому динамика становится более плавной"
    )

    st.subheader("🔁 Параметры контекстного окна")

    use_overlap = st.checkbox("Добавить контекстное окно", value=True)

    overlap_n = 0
    if use_overlap:
        overlap_n = st.slider("Размер окна (предложения)", 1, max_val, default)

    return use_overlap, overlap_n