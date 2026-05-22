from lxml import etree
from collections import defaultdict
import re
import streamlit as st

def parse_txt(file):
    text = file.read().decode("utf-8")

    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

    return paragraphs


def extract_paragraphs(file):
    tree = etree.parse(file)
    root = tree.getroot()

    body = root.find(".//{*}body")
    
    if body is None:
        raise ValueError("Не найден <body> в TEI файле")

    paragraphs = []

    # ищем все параграфы внутри body
    for p in body.findall(".//{*}p"):
        text = " ".join(p.itertext())
        text = " ".join(text.split())

        if text:  # пропускаем пустые
            paragraphs.append(text)

    return paragraphs


def extract_said_replicas(body):
    characters = defaultdict(list)

    for said in body.findall(".//{*}said"):

        # только вслух
        if said.get("aloud") != "true":
            continue

        who = said.get("who")
        if not who:
            continue

        speakers = re.split(r"[ ,]+", who.strip())

        # текст
        text = " ".join(said.itertext())
        text = " ".join(text.split())

        if not text:
            continue

        for speaker in speakers:
            if speaker:
                characters[speaker].append(text)

    return dict(characters)


def extract_sp_replicas(body):
    """
    Парсинг TEI <sp>.
    """
    characters = defaultdict(list)

    for sp in body.findall(".//{*}sp"):

        who = sp.get("who")

        if not who:
            continue

        speakers = re.split(
            r"[ ,]+",
            who.strip()
        )

        texts = []

        for child in sp:

            tag = etree.QName(child).localname

            # пропускаем speaker
            if tag == "speaker":
                continue

            child_text = " ".join(
                child.itertext()
            )

            child_text = " ".join(
                child_text.split()
            )

            if child_text:
                texts.append(child_text)

        full_text = " ".join(texts)

        if not full_text:
            continue

        for speaker in speakers:

            if speaker:
                characters[speaker].append(
                    full_text
                )

    return dict(characters)

def extract_custom_replicas(
    body,
    custom_tag,
    speaker_attr="who"
):
    """
    Парсинг пользовательского тега.
    """
    characters = defaultdict(list)

    xpath = f".//{{*}}{custom_tag}"

    for element in body.findall(xpath):

        who = element.get(speaker_attr)

        if not who:
            continue

        speakers = re.split(
            r"[ ,]+",
            who.strip()
        )

        text = " ".join(
            element.itertext()
        )

        text = " ".join(
            text.split()
        )

        if not text:
            continue

        for speaker in speakers:

            if speaker:
                characters[speaker].append(
                    text
                )

    return dict(characters)


def extract_character_replicas(
    file,
    speech_mode,
    custom_tag=None,
    speaker_attr="who"
):
    """
    Главная функция-диспетчер.
    """

    tree = etree.parse(file)
    root = tree.getroot()

    body = root.find(".//{*}body")

    if body is None:
        raise ValueError("Не найден <body>")

    if speech_mode == "TEI <said>":
        return extract_said_replicas(body)

    elif speech_mode == "TEI <sp>":
        return extract_sp_replicas(body)

    elif speech_mode == "Пользовательский тег":

        if not custom_tag:
            raise ValueError(
                "Не указан пользовательский тег"
            )

        return extract_custom_replicas(
            body=body,
            custom_tag=custom_tag,
            speaker_attr=speaker_attr
        )

    else:
        raise ValueError(
            "Неизвестный формат разметки"
        )


def extract_character_names(file):
    tree = etree.parse(file)
    root = tree.getroot()

    char_map = {}

    for person in root.findall(".//{*}listPerson/{*}person"):
        # xml:id
        char_id = person.get("{http://www.w3.org/XML/1998/namespace}id")

        # первый persName (ТОЛЬКО прямой, не вложенный)
        pers_name = person.find("{*}persName")

        if char_id and pers_name is not None:
            name = "".join(pers_name.itertext()).strip()
            char_map[char_id] = name

    return char_map


def replace_ids_with_names(replicas, char_map):
    updated = {}

    for speaker_id, texts in replicas.items():
        clean_id = speaker_id.replace("#", "")
        name = char_map.get(clean_id, speaker_id)

        updated[f'{name}, {speaker_id}'] = texts

    return updated


def parse_word_list(uploaded_file, lexicon):
    """
    Чтение TXT-файла:
    одно слово или выражение на строку.
    """

    content = uploaded_file.read().decode("utf-8")
    
    for line in content.splitlines():

        line = line.strip()

        if not line:
            continue

        try:
            lemma, polarity = line.split(",")

            lemma = lemma.strip().lower()
            polarity = polarity.strip().lower()

            if lemma not in lexicon.keys():
                if polarity == "positive":
                    lexicon[lemma] = 1

                elif polarity == "negative":
                    lexicon[lemma] = -1

        except ValueError:
            st.warning(
                f"Не удалось обработать строку: {line}"
            )

    return lexicon
    


def parse_custom_lexicon(uploaded_file):
    """
    Формат:
    слово, positive
    слово, negative
    """

    lexicon = {}

    content = uploaded_file.read().decode("utf-8")

    for line in content.splitlines():

        line = line.strip()

        if not line:
            continue

        try:
            lemma, polarity = line.split(",")

            lemma = lemma.strip()
            polarity = polarity.strip().lower()

            if polarity == "positive":
                lexicon[lemma] = 1

            elif polarity == "negative":
                lexicon[lemma] = -1

        except ValueError:
            st.warning(
                f"Не удалось обработать строку: {line}"
            )

    return lexicon