import re
import spacy
from typing import Dict, List, Union

nlp = spacy.load("fr_core_news_md")

def extract_info_cv(text: str) -> Dict[str, Union[str, List[Union[str, Dict[str, str]]]]]:
    
    text = re.sub(r'\s+', ' ', text).strip()
    raw_lines = text.split('\n')
    lines = [line.strip() for line in raw_lines if line.strip()]
    lower_text = text.lower()

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

    # ----------- Email ----------
    email_match = re.search(r'\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b', text)
    if email_match:
        result["email"] = email_match.group(0)

    # ----------- Téléphone ----------
    phone_match = re.search(r'((?:\+33|0)[1-9](?:[ \-\.]?\d{2}){4})', text)
    if phone_match:
        result["telephone"] = re.sub(r'[^\d+]', '', phone_match.group(0))

    # ----------- Adresse ----------
    for line in lines:
        if re.search(r'\b\d{5}\b', line) and any(word in line.lower() for word in ['rue', 'avenue', 'av.', 'bd', 'boulevard', 'impasse', 'allée']):
            result["adresse"] = line
            break

    # ----------- Date de naissance ----------
    date_match = re.search(r'\b(19|20)\d{2}[\/\-\.\s]?(0[1-9]|1[0-2])[\/\-\.\s]?(0[1-9]|[12][0-9]|3[01])\b', text)
    if date_match:
        date_str = date_match.group(0).replace('.', '/').replace('-', '/').replace(' ', '/')
        result["date_naissance"] = date_str

    # ----------- Nom / Prénom (via spaCy dans les premières lignes) ----------
    doc = nlp(" ".join(lines[:5]))
    for ent in doc.ents:
        if ent.label_ == "PER":
            names = ent.text.strip().split()
            if len(names) >= 2:
                result["prenom"] = " ".join(names[:-1])
                result["nom"] = names[-1].upper()
                break

    # Fallback si spaCy échoue
    if result["prenom"] == "Inconnu" and len(lines) > 0:
        name_match = re.search(r'^([A-ZÉÈÊÎ][a-zéèêëàâçïîôùûü]+)[\s\-]+([A-Z\s\-]+)', lines[0])
        if name_match:
            result["prenom"] = name_match.group(1)
            result["nom"] = name_match.group(2).strip().upper()

    # ----------- Compétences (liste connue + mots techniques) ----------
    comp_keywords = ["python", "java", "sql", "c++", "c#", "javascript", "html", "css", "php", "mysql", "docker", "kubernetes", "linux"]
    comp_found = set()
    for kw in comp_keywords:
        if re.search(rf'\b{re.escape(kw)}\b', lower_text):
            comp_found.add(kw.upper())
    result["competences"] = sorted(list(comp_found))

    # ----------- Langues ----------
    # MODIF : on parse les langues en bloc texte et on extrait la liste + niveaux plus proprement
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

    # On essaie de récupérer le bloc langues dans le texte (par exemple la section LANGUES)
    langues_block = ""
    start_langues = False
    for line in raw_lines:
        if "langues" in line.lower():
            start_langues = True
            continue
        if start_langues:
            # Arrêt dès qu'on rencontre une ligne vide ou autre section majuscule
            if not line.strip() or re.match(r'^[A-Z\s]+$', line.strip()):
                break
            langues_block += line + "\n"

    if langues_block:
        result["langues"] = parse_langues_block(langues_block)

    # ----------- Formations ----------
    # MODIF : extraction plus large en cherchant les lignes après la section "FORMATIONS"
    formations = []
    start_formations = False
    for line in raw_lines:
        if "formations" in line.lower():
            start_formations = True
            continue
        if start_formations:
            if not line.strip() or re.match(r'^[A-Z\s]+$', line.strip()):
                break
            formations.append(line.strip())
    result["formations"] = [{"formation": f} for f in formations if f]

    # ----------- Expériences ----------
    experiences = []
    start_exp = False
    for line in raw_lines:
        if "experiences" in line.lower():
            start_exp = True
            continue
        if start_exp:
            if not line.strip() or re.match(r'^[A-Z\s]+$', line.strip()):
                break
            experiences.append(line.strip())
    result["experiences"] = [{"experience": e} for e in experiences if e]

    return result

if __name__ == "__main__":
    exemple_cv = """
    JEAN DUPONT
    15 rue des Lilas, 75014 Paris
    Téléphone : 06 12 34 56 78
    Email : jean.dupont@gmail.com

    FORMATIONS
    2022 - 2024 : BTS SIO - Lycée Turgot, Paris
    2021 : Bac STMG - Lycée Voltaire, Paris

    EXPERIENCES
    2023 : Stage - Développeur web chez WebAgency
    2022 : Projet personnel - Création d’un site e-commerce

    COMPÉTENCES
    HTML, CSS, PHP, MySQL, Python

    LANGUES
    Anglais B2, Espagnol A2
    """
    from pprint import pprint
    donnees = extract_info_cv(exemple_cv)
    pprint(donnees)
