import nltk

nltk.download('punkt')
nltk.download('punkt_tab')

def segment_by_paragraphs(paragraphs,
                          min_words,
                          max_words):
    """
    Гибридная сегментация:
    - маленькие абзацы не дробим
    - большие дробим по предложениям
    """

    chunks = []
    current_chunk = []
    current_len = 0

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        words_in_par = len(nltk.word_tokenize(paragraph))

        # --- 1. СЛИШКОМ БОЛЬШОЙ АБЗАЦ ---
        if words_in_par > max_words:
            sentences = nltk.sent_tokenize(paragraph)

            for sent in sentences:
                sent_len = len(nltk.word_tokenize(sent))

                current_chunk.append(sent)
                current_len += sent_len

                if current_len >= min_words:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_len = 0

        # --- 2. ОБЫЧНЫЙ АБЗАЦ ---
        else:
            current_chunk.append(paragraph)
            current_len += words_in_par

            if current_len >= max_words:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_len = 0

    # --- хвост ---
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def words_in_par_count(paragraphs):
    count_words = []
    for paragraph in paragraphs:
        count_words.append(len(nltk.word_tokenize(paragraph)))
    return round(sum(count_words)/len(count_words))


def window_with_overlap(segments, overlap_sentences):
    """
    Добавляет к каждому сегменту n последних предложений из предыдущего
    """

    result = []

    prev_sentences = []

    for segment in segments:
        # разбиваем текущий сегмент
        current_sentences = nltk.sent_tokenize(segment)

        # берём overlap из предыдущего
        overlap = prev_sentences[-overlap_sentences:] if prev_sentences else []

        # объединяем
        new_segment = " ".join(overlap + current_sentences)

        result.append(new_segment)

        # обновляем предыдущие
        prev_sentences = current_sentences

    return result