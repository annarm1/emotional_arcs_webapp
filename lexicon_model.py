class LexiconModel:
    def __init__(self, lexicon_path: str):
        self.lexicon = self.load_lexicon('rusentilex_2017.txt')
        
    def load_lexicon(self, path: str) -> dict[str, str]:
        """
        Создание словаря на основе РуСентиЛекс:
        Возвращает словарь, в котором ключи - леммы из словаря, 
        а значения - тональность (позитивная (positive), негативная(negative), нейтральная (neutral))
        """
        lexicon = {}
        with open(path, "r", encoding="utf-8") as rusentilex:
            for line in rusentilex:
                if not line.startswith('!'):
                    lemma = line.split(', ')[2]
                    sentiment = line.split(', ')[3]
                    lexicon[lemma] = sentiment
        return lexicon

    def lex_analyze(lemmas, lexicon):
        neg_lex = []
        pos_lex = []
        neu_lex = []
        for k, v in lexicon.items():
            if v == 'negative':
                neg_lex.append(k)
            elif v == 'positive':
                pos_lex.append(k)
            elif v == 'neutral':
                neu_lex.append(k)
        pos_score = 0
        neg_score = 0
        neu_score = 0
        for lemma in lemmas:
            if lemma in pos_lex:
                pos_score += 1
            elif lemma in neg_lex:
                neg_score += 1
            elif lemma in neu_lex:
                neu_score += 1
        return pos_score, neg_score, neu_score