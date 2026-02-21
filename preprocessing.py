import re
import pymorphy3 # type: ignore

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


def lemmatize(words: list[str]) -> list[str]:
    """
    Лемматизация pymorphy
    
    Возвращает словарь лемм
    """
    return [morph.parse(word)[0].normal_form for word in words]


def preprocess(text: str) -> list[str]:
    """"
    Предворительная обработка текста
    - очистка
    - токенизация по пробелам
    - лемматизация
    
    Возвращает словарь из лемм
    """
    cleaned = clean_text(text)
    tokens = cleaned.split()
    return lemmatize(tokens)