import re

import jieba
from fugashi import Tagger
from nltk.tokenize import sent_tokenize


class SentenceSplitter:
    def __init__(self):
        self.nltk_supported_languages = [
            "cs",
            "da",
            "de",
            "el",
            "en",
            "es",
            "et",
            "fi",
            "fr",
            "it",
            "nl",
            "no",
            "pl",
            "pt",
            "sl",
            "sv",
            "tr",
        ]
        self.nltk_lang_map = {
            "cs": "czech",
            "da": "danish",
            "de": "german",
            "el": "greek",
            "en": "english",
            "es": "spanish",
            "et": "estonian",
            "fi": "finnish",
            "fr": "french",
            "it": "italian",
            "nl": "dutch",
            "no": "norwegian",
            "pl": "polish",
            "pt": "portuguese",
            "sl": "slovene",
            "sv": "swedish",
            "tr": "turkish",
        }
        self.terminators = [".", "!", "?"]
        self.ja_zh_terminators = ["。", "！", "？"]

    def _split_sentences_generic(self, text):
        terminators = "".join(self.terminators)
        pattern = rf"(?<=[{terminators}])\s+"
        return re.split(pattern, text.strip())

    def _split_sentences_japanese(self, text):
        tagger = Tagger()

        sentences = []
        nodes = tagger(text)
        sentence = ""

        for node in nodes:
            if node.surface in self.ja_zh_terminators:
                sentence += node.surface
                if sentence:
                    sentences.append(sentence.strip())
                    sentence = ""
            else:
                sentence += node.surface
        return sentences

    def _split_sentences_chinese(self, text):
        sentences = []
        seg_list = jieba.cut(text, cut_all=False)
        sentence = ""

        for word in seg_list:
            sentence += word
            if word in self.ja_zh_terminators:
                sentences.append(sentence)
                sentence = ""
        return sentences

    def _split_sentences_using_nltk(self, text, language):
        return sent_tokenize(text, language=language)

    def split_sentences(self, text, lang_code):
        text = text.strip()
        if lang_code in self.nltk_supported_languages:
            lang_name = self.nltk_lang_map.get(lang_code)
            return self._split_sentences_using_nltk(text, lang_name)
        elif lang_code == "ja":
            return self._split_sentences_japanese(text)
        elif lang_code in ["zh-hans", "zh-hant"]:
            return self._split_sentences_chinese(text)
        return self._split_sentences_generic(text)
