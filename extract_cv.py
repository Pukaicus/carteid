import re
from typing import Dict, List, Union

from nlp_model import nlp

def extract_info_cv(text: str) -> Dict[str, Union[str, List[Union[str, Dict[str, str]]]]]:
    # On conserve les retours à la ligne, mais on nettoie les espaces inutiles dans chaque ligne
    raw_lines = [line.strip() for line in text.split('\n') if line.strip()]
    clean_text = "\n".join(raw_lines)
    lower_text = clean_text.lower()

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

    # Email : regex classique, simple et efficace
    email_match = re.search(r'\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b', clean_text)
    if email_match:
        result["email"] = email_match.group(0)

    # Téléphone : on garde uniquement chiffres + + (ex: +33612345678)
    phone_match = re.search(r'((?:\+33|0)[1-9](?:[ \-\.]?\d{2}){4})', clean_text)
    if phone_match:
        result["telephone"] = re.sub(r'[^\d+]', '', phone_match.group(0))

    # Adresse : ligne avec code postal + mot clé rue/avenue etc.
    for line in raw_lines:
        if re.search(r'\b\d{5}\b', line) and any(
            kw in line.lower() for kw in ['rue', 'avenue', 'av.', 'bd', 'boulevard', 'impasse', 'allée']
        ):
            result["adresse"] = line
            break

    # Date de naissance : on détecte plusieurs formats, pas uniquement AAAAMMJJ
    date_match = re.search(r'(\d{2}[\/\-\.\s]\d{2}[\/\-\.\s]\d{4})', clean_text)
    if date_match:
        date_str = date_match.group(1).replace('.', '/').replace('-', '/').replace(' ', '/')
        result["date_naissance"] = date_str

    # Nom / prénom : spaCy sur les 5 premières lignes (souvent au début du CV)
    doc = nlp(" ".join(raw_lines[:5]))
    for ent in doc.ents:
        if ent.label_ == "PER":
            names = ent.text.strip().split()
            if len(names) >= 2:
                result["prenom"] = " ".join(names[:-1])
                result["nom"] = names[-1].upper()
                break

    # Fallback regex : tentative d'extraire nom et prénom sur première ligne, amélioration possible selon format CV
    if result["prenom"] == "Inconnu" and raw_lines:
        name_match = re.match(r'^([A-ZÉÈÊÎ][a-zéèêëàâçïîôùûü]+)[\s\-]+([A-Z\s\-]+)$', raw_lines[0])
        if name_match:
            result["prenom"] = name_match.group(1)
            result["nom"] = name_match.group(2).strip().upper()

    # Compétences : on élargit la liste connue pour couvrir plus de technos courantes
    comp_keywords = ["python", "java", "sql", "c++", "c#", "javascript", "html", "css", "php", "mysql", "docker", "kubernetes", "linux", "react", "nodejs", "git"]
    comp_found = {kw.upper() for kw in comp_keywords if re.search(rf'\b{re.escape(kw)}\b', lower_text)}
    result["competences"] = sorted(list(comp_found))

    # Langues : parse proprement le bloc LANGUES, tolérance aux formats variés
    def parse_langues_block(text_block: str) -> List[Dict[str, str]]:
        langues_list = []
        langues_possibles = ["anglais", "espagnol", "allemand", "italien", "chinois", "arabe", "russe"]
        niveau_possibles = ["A1", "A2", "B1", "B2", "C1", "C2"]
        parts = re.split(r'[,\n]', text_block)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            for langue in langues_possibles:
                if langue in part.lower():
                    niveau_match = re.search(r'\b(' + "|".join(niveau_possibles) + r')\b', part, re.IGNORECASE)
                    niveau = niveau_match.group(0).upper() if niveau_match else "Inconnu"
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
            if not line.strip() or re.match(r'^[A-Z\s]+$', line.strip()):  # Arrêt à fin de section
                break
            langues_block += line + "\n"

    if langues_block:
        result["langues"] = parse_langues_block(langues_block)

    # Formations : extraction après section FORMATIONS jusqu'à autre section vide ou majuscule
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

    # Expériences : idem que formations
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
