ALL_POSES = ['ADJ', 'ADP', 'ADV', 'AUX', 'CONJ', 'CCONJ', 'DET', 'INTJ', 'NOUN', 'NUM', 'PART', 'PRON', 'PROPN', 'PUNCT', 'SCONJ', 'SYM', 'VERB', 'X', 'SPACE']
PROCESSABLE_POSES = ALL_POSES


SPACY_MODEL_NAME = 'pl_core_news_sm'
#SPACY_MODEL_NAME = 'pl_core_news_md'


def get_spacyed_content(text: str, nlp) -> list:
    spacy_doc = nlp(text)
    return spacy_doc


def filter_spacyed_content(spacy_text: list) -> list:
    processed_content = list()
    for token in spacy_text:
        if token.pos_ in PROCESSABLE_POSES:
            processed_content.append(token.lemma_)
    return processed_content
