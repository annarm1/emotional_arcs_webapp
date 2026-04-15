from lxml import etree


def extract_paragraphs(file):
    tree = etree.parse(file)
    root = tree.getroot()

    # берём только основной текст романа
    body = root.find(".//{*}body")
    
    if body is None:
        raise ValueError("Не найден <body> в TEI файле")

    paragraphs = []

    # ищем все параграфы внутри body
    for p in body.findall(".//{*}p"):
        text = " ".join(p.itertext())   # убираем вложенные теги
        text = " ".join(text.split())   # чистка пробелов

        if text:  # пропускаем пустые
            paragraphs.append(text)

    return paragraphs