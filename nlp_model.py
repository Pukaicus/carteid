import spacy
from spacy.pipeline import EntityRuler
import re

def clean_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text) 
    return text.strip()

def create_entity_ruler(nlp):
    if "entity_ruler" in nlp.pipe_names:
        return nlp.get_pipe("entity_ruler")

    ruler = nlp.add_pipe("entity_ruler", before="ner")
    patterns = [
        {"label": "NUMERO_CARTE", "pattern": [{"TEXT": {"REGEX": "^[A-Z0-9]{8,}$"}}]},
        {"label": "SEXE", "pattern": [{"LOWER": "masculin"}]},
        {"label": "SEXE", "pattern": [{"LOWER": "féminin"}]},
        {"label": "SEXE", "pattern": [{"LOWER": "m"}]},
        {"label": "SEXE", "pattern": [{"LOWER": "f"}]},
        {"label": "NATIONALITE", "pattern": [{"LOWER": "française"}]},
        {"label": "DATE_NAISSANCE", "pattern": [{"LOWER": {"REGEX": "né|née"}}, {"LOWER": "le"}]},
        {"label": "ADRESSE", "pattern": [{"LOWER": "adresse"}]},
    ]
    ruler.add_patterns(patterns)
    return ruler

_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("fr_core_news_md") 
        create_entity_ruler(_nlp)
    return _nlp

nlp = get_nlp()
