import re
from typing import Dict

from nlp_model import get_nlp, clean_text

def detect_carte_identite(text: str) -> bool:
    """
    Détecte si le texte correspond à une carte d'identité française.
    """
    text_upper = text.upper()
    keywords = [
        "RÉPUBLIQUE FRANÇAISE",
        "CARTE NATIONALE D'IDENTITÉ",
        "IDENTITÉ",
        "N° DOCUMENT",
        "AUTORITÉ"
    ]
    return any(kw in text_upper for kw in keywords)

def extract_sexe(lines) -> str:
    """
    Extrait le sexe à partir des lignes OCR.
    """
    sex_keywords = {
        "Masculin": ["M", "MASCULIN", "HOMME", "H"],
        "Féminin": ["F", "FÉMININ", "FEMME"]
    }
    for line in lines:
        line_upper = line.upper()
        for sex, keywords in sex_keywords.items():
            if any(kw in line_upper for kw in keywords):
                return sex
    return "Inconnu"

def extract_info_id(text: str) -> Dict[str, str]:
    """
    Extrait les informations clés d'une carte d'identité française à partir du texte OCR.
    Retourne un dictionnaire avec les champs standardisés.
    """
    try:
        # Nettoyage du texte
        text_clean = clean_text(text)
        lines = [line.strip() for line in text_clean.split('\n') if line.strip()]
        full_text = " ".join(lines)

        # Chargement du pipeline NLP
        nlp = get_nlp()
        doc = nlp(full_text)

        result = {
            "numero_carte": "Inconnu",
            "nom": "Inconnu",
            "prenom": "Inconnu",
            "date_naissance": "Inconnu",
            "lieu_naissance": "Inconnu",
            "sexe": "Inconnu",
            "adresse": "Inconnu",
            "date_expiration": "Inconnu"
        }

        # Extraction numéro de carte (2 lettres + 6 chiffres, espace optionnel)
        id_match = re.search(r'\b[A-Z]{2}\s?\d{6}\b', full_text)
        if id_match:
            result["numero_carte"] = id_match.group(0).replace(" ", "")

        # Extraction date de naissance (ex : né(e) le 12/05/1980)
        date_naissance_match = re.search(
            r'(?:(?:né[e]? le|naissance)[:\-]?\s*)(\d{2}[\./\-\s]?\d{2}[\./\-\s]?\d{4})',
            full_text, re.IGNORECASE
        )
        if date_naissance_match:
            # Format standardisé, remplace espaces et points par -
            date = re.sub(r'[\./\s]', '-', date_naissance_match.group(1))
            result["date_naissance"] = date

        # Extraction date expiration (ex: valide jusqu'au 12/05/2025)
        expiration_match = re.search(
            r'(date d\'expiration|valide jusqu\'au|expire le)[:\-]?\s*(\d{2}[\./\-\s]?\d{2}[\./\-\s]?\d{4})',
            full_text, re.IGNORECASE
        )
        if expiration_match:
            date = re.sub(r'[\./\s]', '-', expiration_match.group(2))
            result["date_expiration"] = date

        # Extraction lieu de naissance
        naissance_lieu_match = re.search(
            r'(lieu de naissance|né[e]? à)[:\-]?\s*([A-Za-zÀ-ÖØ-öø-ÿ\s\-]{2,50})',
            full_text, re.IGNORECASE
        )
        if naissance_lieu_match:
            lieu = naissance_lieu_match.group(2).strip()
            result["lieu_naissance"] = lieu

        # Extraction sexe via la fonction dédiée
        result["sexe"] = extract_sexe(lines)

        # Extraction adresse (ligne contenant un code postal et mot clé adresse)
        adresse_keywords = ["rue", "av.", "avenue", "boul.", "boulevard", "impasse", "allée", "route", "chemin", "place"]
        for line in lines:
            if re.search(r'\b\d{5}\b', line) and any(kw in line.lower() for kw in adresse_keywords):
                result["adresse"] = line.strip()
                break

        # Extraction Nom / Prénom via spaCy entités PERSONNES ("PER")
        for ent in doc.ents:
            if ent.label_ == "PER":
                parts = ent.text.strip().split()
                if len(parts) >= 2:
                    result["prenom"] = " ".join(parts[:-1])
                    result["nom"] = parts[-1].upper()
                    break

        # Fallback regex nom/prénom si spaCy n'a rien détecté
        if result["nom"] == "Inconnu" or result["prenom"] == "Inconnu":
            nom_match = re.search(r'NOM\s*[:\-]?\s*([A-ZÉÈÊËÀÂÇÏÎÔÙÛÜ\- ]+)', full_text, re.IGNORECASE)
            prenom_match = re.search(r'PRÉ?NOM\s*[:\-]?\s*([A-ZÉÈÊËÀÂÇÏÎÔÙÛÜ][a-zéèêëàâçïîôùûü\- ]+)', full_text, re.IGNORECASE)
            if nom_match:
                result["nom"] = nom_match.group(1).strip().upper()
            if prenom_match:
                result["prenom"] = prenom_match.group(1).strip().capitalize()

        return result

    except Exception as e:
        print(f"[extract_info_id] Erreur: {e}")
        return {
            "numero_carte": "Inconnu",
            "nom": "Inconnu",
            "prenom": "Inconnu",
            "date_naissance": "Inconnu",
            "lieu_naissance": "Inconnu",
            "sexe": "Inconnu",
            "adresse": "Inconnu",
            "date_expiration": "Inconnu"
        }
