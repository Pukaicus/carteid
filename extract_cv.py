import re
from typing import Dict, List, Union
import dateparser
from nlp_model import nlp


def clean_text(text: str) -> str:
    """
    Nettoyage simple du texte OCR brut :
    - suppression espaces/tabs multiples
    - suppression caractères parasites
    - remplacement ponctuations incohérentes
    """
    text = text.replace('\r', '\n')
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'[^\w\s@.+\-/]', '', text) 
    text = re.sub(r'\n+', '\n', text)
    return text.strip()


def parse_date(date_str: str) -> str:
    """Parse une date française en format ISO, sinon 'Inconnu'"""
    dt = dateparser.parse(date_str, languages=['fr'])
    if dt:
        return dt.strftime('%Y-%m-%d')
    return "Inconnu"


def extract_info_cv(text: str) -> Dict[str, Union[str, List[Union[str, Dict[str, str]]]]]:
    # Nettoyage du texte brut OCR
    cleaned_text = clean_text(text)
    raw_lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
    lower_text = cleaned_text.lower()

    result = {
        "nom": "Inconnu",
        "prenom": "Inconnu",
        "email": "Inconnu",
        "telephone": "Inconnu",
        "adresse": "Inconnu",
        "date_naissance": "Inconnu",
        "competences": [],
        "langues": [],
        "experiences": [],
        "formations": []
    }

    # Email (plusieurs formats possibles)
    email_match = re.search(r'\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b', cleaned_text)
    if email_match:
        result["email"] = email_match.group(0)

    # Téléphone : formats +33, 0x, avec espaces, tirets, points, normalisé
    phone_match = re.search(r'((?:\+33|0)[1-9](?:[ \-\.]?\d{2}){4})', cleaned_text)
    if phone_match:
        tel = phone_match.group(0)
        tel = re.sub(r'[^\d+]', '', tel)
        result["telephone"] = tel

    # Adresse : détecte ligne avec code postal + mots clés rue/avenue/boulevard/impasse/allée
    for line in raw_lines:
        if re.search(r'\b\d{5}\b', line) and any(kw in line.lower() for kw in ['rue', 'avenue', 'av.', 'bd', 'boulevard', 'impasse', 'allée']):
            result["adresse"] = line
            break

    # Date de naissance : extraction améliorée
    dates_found = re.findall(r'\b\d{1,2}[\/\-\.\s]\d{1,2}[\/\-\.\s]\d{2,4}\b', cleaned_text)
    date_naissance = "Inconnu"
    for d in dates_found:
        parsed_date = dateparser.parse(d, languages=['fr'])
        if parsed_date and 1900 <= parsed_date.year <= 2010:
            date_naissance = parsed_date.strftime('%Y-%m-%d')
            break
    result["date_naissance"] = date_naissance

    # Nom/prénom : spaCy sur premières lignes (extraction entités PERSON)
    doc = nlp(" ".join(raw_lines[:5]))
    for ent in doc.ents:
        if ent.label_ == "PER" or ent.label_ == "PERSON":
            names = ent.text.strip().split()
            if len(names) >= 2:
                result["prenom"] = " ".join(names[:-1])
                result["nom"] = names[-1].upper()
                break

    # Fallback regex nom/prénom sur la première ligne (souvent format "Prénom NOM")
    if result["prenom"] == "Inconnu" and raw_lines:
        name_match = re.match(r'^([A-ZÉÈÊÎ][a-zéèêëàâçïîôùûü]+)[\s\-]+([A-Z\s\-]+)$', raw_lines[0])
        if name_match:
            result["prenom"] = name_match.group(1)
            result["nom"] = name_match.group(2).strip().upper()

    # Compétences : élargissement + fuzzy simple (ignore accents et casse)
    comp_keywords = ["python", "java", "sql", "c++", "c#", "javascript", "html", "css", "php", "mysql",
                     "docker", "kubernetes", "linux", "react", "nodejs", "git", "aws", "azure", "tensorflow"]
    comp_found = set()
    for kw in comp_keywords:
        pattern = rf'\b{re.escape(kw)}\b'
        if re.search(pattern, lower_text):
            comp_found.add(kw.upper())
    result["competences"] = sorted(list(comp_found))

    # Langues : détection souple avec niveaux variés, prise en compte 'courant', 'bilingue', 'notions'
    def parse_langues_block(text_block: str) -> List[Dict[str, str]]:
        langues_list = []
        langues_possibles = ["anglais", "espagnol", "allemand", "italien", "chinois", "arabe", "russe"]
        niveau_possibles = ["A1", "A2", "B1", "B2", "C1", "C2", "courant", "bilingue", "notions", "débutant", "intermédiaire"]
        parts = re.split(r'[,\n]', text_block)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            for langue in langues_possibles:
                if langue in part.lower():
                    niveau_match = re.search(r'\b(' + "|".join(niveau_possibles) + r')\b', part, re.IGNORECASE)
                    niveau = niveau_match.group(0).capitalize() if niveau_match else "Inconnu"
                    langues_list.append({"langue": langue.capitalize(), "niveau": niveau})
                    break
        return langues_list

    langues_block = ""
    in_langues_section = False
    for line in raw_lines:
        if "langues" in line.lower():
            in_langues_section = True
            continue
        if in_langues_section:
            if not line.strip() or re.match(r'^[A-Z\s]+$', line.strip()):  # fin de section
                break
            langues_block += line + "\n"

    if langues_block:
        result["langues"] = parse_langues_block(langues_block)

    # Formations : extraction lignes après section FORMATIONS jusqu'à section vide ou majuscules
    formations = []
    in_formations_section = False
    for line in raw_lines:
        if "formations" in line.lower():
            in_formations_section = True
            continue
        if in_formations_section:
            if not line.strip() or re.match(r'^[A-Z\s]+$', line.strip()):
                break
            formations.append(line.strip())
    result["formations"] = [{"formation": f} for f in formations if f]

    # Expériences : même principe que formations, avec extraction date(s) possibles (non structurée ici)
    experiences = []
    in_experiences_section = False
    for line in raw_lines:
        if "experiences" in line.lower():
            in_experiences_section = True
            continue
        if in_experiences_section:
            if not line.strip() or re.match(r'^[A-Z\s]+$', line.strip()):
                break
            experiences.append(line.strip())
    result["experiences"] = [{"experience": e} for e in experiences if e]

    return result
