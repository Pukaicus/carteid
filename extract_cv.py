import re
import spacy
from ocr_utils import clean_text
from xml_utils import create_xml
from nlp_model import nlp  # Utilisation du modèle centralisé


def extract_info_cv(text):
    text = clean_text(text)
    doc = nlp(text)

    prenom = nom = email = phone = adresse = "Inconnu"
    experiences = []
    formations = []
    competences = []

    # Email
    match_email = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    if match_email:
        email = match_email.group()

    # Téléphone
    match_phone = re.search(r"(?:\+33|0)[1-9](?:[\s.-]?\d{2}){4}", text)
    if match_phone:
        phone = match_phone.group()

    # Adresse (simplifiée)
    match_adresse = re.search(r"\d{1,4}\s+\w+(?:\s+\w+)*\s+(?:rue|avenue|boulevard|allée|impasse|chemin|place)\s+\w+", text, re.IGNORECASE)
    if match_adresse:
        adresse = match_adresse.group()

    # Prénom/Nom via entité spaCy
    for ent in doc.ents:
        if ent.label_ == "PER":
            noms = ent.text.strip().split()
            if len(noms) >= 2:
                prenom = noms[0]
                nom = " ".join(noms[1:])
            elif len(noms) == 1:
                nom = noms[0]
            break

    # Analyse des sections
    lignes = text.split('\n')
    current_section = None
    temp_block = []

    def flush_block():
        block = "\n".join(temp_block).strip()
        return block if len(block) > 3 else None

    for line in lignes:
        ligne = line.strip()
        ligne_lower = ligne.lower()

        if any(k in ligne_lower for k in ["compétence", "skills"]):
            if current_section == "experiences":
                exp = flush_block()
                if exp:
                    experiences.append(exp)
                temp_block = []
            elif current_section == "formations":
                form = flush_block()
                if form:
                    formations.append(form)
                temp_block = []

            current_section = "competences"
            continue

        elif any(k in ligne_lower for k in ["expérience", "experience", "professionnelle", "stage", "emploi"]):
            if current_section == "competences":
                comp = flush_block()
                if comp:
                    competences.append(comp)
                temp_block = []
            elif current_section == "formations":
                form = flush_block()
                if form:
                    formations.append(form)
                temp_block = []

            current_section = "experiences"
            continue

        elif any(k in ligne_lower for k in ["formation", "diplôme", "diplome", "education", "étude"]):
            if current_section == "experiences":
                exp = flush_block()
                if exp:
                    experiences.append(exp)
                temp_block = []
            elif current_section == "competences":
                comp = flush_block()
                if comp:
                    competences.append(comp)
                temp_block = []

            current_section = "formations"
            continue

        elif ligne == "":
            if current_section == "experiences":
                exp = flush_block()
                if exp:
                    experiences.append(exp)
                temp_block = []
            elif current_section == "formations":
                form = flush_block()
                if form:
                    formations.append(form)
                temp_block = []
            elif current_section == "competences":
                comp = flush_block()
                if comp:
                    competences.append(comp)
                temp_block = []

            current_section = None
            continue

        if current_section:
            temp_block.append(ligne)

    # Dernier bloc à ajouter
    if current_section == "experiences":
        exp = flush_block()
        if exp:
            experiences.append(exp)
    elif current_section == "formations":
        form = flush_block()
        if form:
            formations.append(form)
    elif current_section == "competences":
        comp = flush_block()
        if comp:
            competences.append(comp)

    return {
        "type": "cv",
        "prenom": prenom,
        "nom": nom,
        "email": email,
        "telephone": phone,
        "adresse": adresse,
        "experiences": experiences,
        "formations": formations,
        "competences": competences
    }


def process_cv(file_path, text):
    info = extract_info_cv(text)
    xml_path = file_path.replace(".png", ".xml").replace(".jpg", ".xml").replace(".jpeg", ".xml").replace(".pdf", ".xml")
    create_xml(xml_path, info)
