import re
import spacy
from typing import Dict

nlp = spacy.load("fr_core_news_md")

def detect_carte_identite(text: str) -> bool:
    text_upper = text.upper()
    keywords = [
        "RÉPUBLIQUE FRANÇAISE",
        "CARTE NATIONALE D'IDENTITÉ",
        "IDENTITÉ",
        "N° DOCUMENT",
        "AUTORITÉ"
    ]
    return any(kw in text_upper for kw in keywords)

def extract_info_id(text: str) -> Dict[str, str]:
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    full_text = " ".join(lines)
    doc = nlp(full_text)

    result = {
        "numero_carte": "Inconnu",
        "nom": "Inconnu",
        "prenom": "Inconnu",
        "date_naissance": "Inconnu",
        "lieu_naissance": "Inconnu",        # 🆕
        "sexe": "Inconnu",
        "adresse": "Inconnu",
        "date_expiration": "Inconnu"        # 🆕
    }

    # Numéro de carte (format : 2 lettres + 6 chiffres)
    id_match = re.search(r'\b[A-Z]{2}\d{6}\b', full_text)
    if id_match:
        result["numero_carte"] = id_match.group(0)

    # Date de naissance
    date_naissance_match = re.search(
        r'(?:(?:né[e]? le|naissance)[:\-]?\s*)(\d{2}[\/\-. ]\d{2}[\/\-. ]\d{4})',
        full_text, re.IGNORECASE
    )
    if date_naissance_match:
        result["date_naissance"] = date_naissance_match.group(1)

    # Date d'expiration
    expiration_match = re.search(
        r'(date d\'expiration|valide jusqu\'au|expire le)[:\-]?\s*(\d{2}[\/\-. ]\d{2}[\/\-. ]\d{4})',
        full_text, re.IGNORECASE
    )
    if expiration_match:
        result["date_expiration"] = expiration_match.group(2)

    # Lieu de naissance
    naissance_lieu_match = re.search(
        r'(lieu de naissance|né[e]? à)[:\-]?\s*([\w\s\-]+)', full_text, re.IGNORECASE
    )
    if naissance_lieu_match:
        lieu = naissance_lieu_match.group(2).strip()
        if len(lieu.split()) <= 6:
            result["lieu_naissance"] = lieu

    # Sexe
    sex_keywords = {
        "masculin": ["M", "MASCULIN", "HOMME", "H"],
        "féminin": ["F", "FÉMININ", "FEMME"]
    }
    for line in lines:
        line_upper = line.upper()
        for sex, keywords in sex_keywords.items():
            if any(kw in line_upper for kw in keywords):
                result["sexe"] = sex.capitalize()
                break

    # Adresse (ligne avec code postal + mot-clé)
    for line in lines:
        if re.search(r'\b\d{5}\b', line) and any(
            kw in line.lower() for kw in ["rue", "av.", "avenue", "boul.", "boulevard", "impasse", "allée"]
        ):
            result["adresse"] = line
            break

    # Nom / Prénom : priorité à spaCy
    for ent in doc.ents:
        if ent.label_ == "PER":
            parts = ent.text.split()
            if len(parts) >= 2:
                result["prenom"] = " ".join(parts[:-1])
                result["nom"] = parts[-1].upper()
                break
    else:
        # Fallback regex
        nom_match = re.search(r'NOM\s*[:\-]\s*([A-ZÉÈÊËÀÂÇÏÎÔÙÛÜ\- ]+)', full_text, re.IGNORECASE)
        prenom_match = re.search(r'PRÉ?NOM\s*[:\-]\s*([A-ZÉÈÊËÀÂÇÏÎÔÙÛÜ][a-zéèêëàâçïîôùûü\- ]+)', full_text, re.IGNORECASE)
        if nom_match:
            result["nom"] = nom_match.group(1).strip().upper()
        if prenom_match:
            result["prenom"] = prenom_match.group(1).strip().capitalize()

    return result
