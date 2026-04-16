from lxml import etree
from collections import defaultdict
import re

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


def extract_character_replicas(xml_path):
    tree = etree.parse(xml_path)
    root = tree.getroot()

    body = root.find(".//{*}body")
    if body is None:
        raise ValueError("Не найден <body>")

    characters = defaultdict(list)

    for said in body.findall(".//{*}said"):

        # только вслух
        if said.get("aloud") != "true":
            continue

        who = said.get("who")
        if not who:
            continue

        # 🔴 разбиваем нескольких говорящих
        speakers = re.split(r"[ ,]+", who.strip())

        # текст
        text = " ".join(said.itertext())
        text = " ".join(text.split())

        if not text:
            continue

        # 🔴 добавляем каждому персонажу
        for speaker in speakers:
            if speaker:  # защита от пустых строк
                characters[speaker].append(text)

    return dict(characters)