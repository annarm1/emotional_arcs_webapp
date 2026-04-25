from lxml import etree
from collections import defaultdict
import re
import nltk
import zipfile
import io


def extract_txt_from_zip(uploaded_file):
    z = zipfile.ZipFile(uploaded_file)

    texts = {}

    for name in z.namelist():
        if name.endswith(".txt"):
            with z.open(name) as f:
                content = f.read().decode("utf-8")
                texts[name] = content

    return texts


def parse_txt(file):
    text = file.read().decode("utf-8")

    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    sentences = nltk.sent_tokenize(text)

    return paragraphs, sentences


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


def extract_character_replicas(file):
    tree = etree.parse(file)
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

        # разбиваем нескольких говорящих
        speakers = re.split(r"[ ,]+", who.strip())

        # текст
        text = " ".join(said.itertext())
        text = " ".join(text.split())

        if not text:
            continue

        # добавляем каждому персонажу
        for speaker in speakers:
            if speaker:  # защита от пустых строк
                characters[speaker].append(text)

    return dict(characters)