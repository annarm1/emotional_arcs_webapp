import re
import pymorphy3  # type: ignore
import nltk
nltk.download('punkt')

morph = pymorphy3.MorphAnalyzer()

def clean_text(text: str) -> str:
    """
    Очистка текста
    - приведение к нижнему регистру
    - сохранение только кириллических символов
    
    Возвращает очищенный от специальных символов текст
    """
    text = text.lower()
    text = re.sub(r"[^а-яё\s]", " ", text)
    re.sub(r"[^\w\s]", "", text)
    return text.strip()


def lemmatize(text: str) -> list[str]:
    words = text.lower().split()
    lemmas = [morph.parse(word)[0].normal_form for word in words]
    return lemmas

def sent_tokenize(text:str) -> list[str]:
    sentences = nltk.sent_tokenize(text)
    return sentences