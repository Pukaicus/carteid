import xml.etree.ElementTree as ET
from datetime import datetime
import xml.dom.minidom

def create_xml(data_dict, filename):
    root = ET.Element('CV')

    date_elem = ET.SubElement(root, 'date_creation')
    date_elem.text = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    identite = ET.SubElement(root, 'Identite')
    ET.SubElement(identite, 'Nom').text = str(data_dict.get('nom', 'Inconnu'))
    ET.SubElement(identite, 'Prenom').text = str(data_dict.get('prenom', 'Inconnu'))
    ET.SubElement(identite, 'Email').text = str(data_dict.get('email', 'Inconnu'))
    ET.SubElement(identite, 'Telephone').text = str(data_dict.get('telephone', 'Inconnu'))
    ET.SubElement(identite, 'Adresse').text = str(data_dict.get('adresse', 'Inconnu'))
    ET.SubElement(identite, 'DateNaissance').text = str(data_dict.get('date_naissance', 'Inconnu'))

    # Ajout de la Carte d'identité si elle existe dans data_dict
    if any(key in data_dict for key in ['numero_carte', 'sexe', 'nationalite']):
        carte_id = ET.SubElement(root, 'CarteIdentite')
        ET.SubElement(carte_id, 'NumeroCarte').text = str(data_dict.get('numero_carte', 'Inconnu'))
        ET.SubElement(carte_id, 'Sexe').text = str(data_dict.get('sexe', 'Inconnu'))
        ET.SubElement(carte_id, 'Nationalite').text = str(data_dict.get('nationalite', 'Inconnu'))
        ET.SubElement(carte_id, 'LieuNaissance').text = str(data_dict.get('lieu_naissance', 'Inconnu'))
        ET.SubElement(carte_id, 'DateExpiration').text = str(data_dict.get('date_expiration', 'Inconnu'))
        # Ajoute d'autres champs si nécessaire ici

    competences = ET.SubElement(root, 'Competences')
    for comp in data_dict.get('competences', []):
        ET.SubElement(competences, 'Competence').text = str(comp)

    langues = ET.SubElement(root, 'Langues')
    for langue in data_dict.get('langues', []):
        if isinstance(langue, (tuple, list)) and len(langue) == 2:
            nom = str(langue[0])
            niveau = str(langue[1])
        elif isinstance(langue, dict):
            nom = str(langue.get('langue', 'Inconnu'))
            niveau = str(langue.get('niveau', 'Inconnu'))
        else:
            nom = str(langue)
            niveau = ''
        ET.SubElement(langues, 'Langue', niveau=niveau).text = nom

    experiences = ET.SubElement(root, 'Experiences')
    for exp in data_dict.get('experiences', []):
        experience = ET.SubElement(experiences, 'Experience')
        ET.SubElement(experience, 'Poste').text = str(exp.get('poste', 'Inconnu'))
        ET.SubElement(experience, 'Entreprise').text = str(exp.get('entreprise', 'Inconnu'))
        ET.SubElement(experience, 'Debut').text = str(exp.get('debut', 'Inconnu'))
        ET.SubElement(experience, 'Fin').text = str(exp.get('fin', 'Inconnu'))
        ET.SubElement(experience, 'Description').text = str(exp.get('description', ''))

    formations = ET.SubElement(root, 'Formations')
    for form in data_dict.get('formations', []):
        formation = ET.SubElement(formations, 'Formation')
        ET.SubElement(formation, 'Diplome').text = str(form.get('diplome', 'Inconnu'))
        ET.SubElement(formation, 'Etablissement').text = str(form.get('etablissement', 'Inconnu'))
        ET.SubElement(formation, 'Annee').text = str(form.get('annee', 'Inconnu'))

    # Préttifier le XML avant d’écrire
    xml_str = ET.tostring(root, encoding='utf-8')
    pretty_xml = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="  ")

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

def create_xml_string(data_dict):
    root = ET.Element('CV')

    date_elem = ET.SubElement(root, 'date_creation')
    date_elem.text = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    identite = ET.SubElement(root, 'Identite')
    ET.SubElement(identite, 'Nom').text = str(data_dict.get('nom', 'Inconnu'))
    ET.SubElement(identite, 'Prenom').text = str(data_dict.get('prenom', 'Inconnu'))
    ET.SubElement(identite, 'Email').text = str(data_dict.get('email', 'Inconnu'))
    ET.SubElement(identite, 'Telephone').text = str(data_dict.get('telephone', 'Inconnu'))
    ET.SubElement(identite, 'Adresse').text = str(data_dict.get('adresse', 'Inconnu'))
    ET.SubElement(identite, 'DateNaissance').text = str(data_dict.get('date_naissance', 'Inconnu'))

    if any(key in data_dict for key in ['numero_carte', 'sexe', 'nationalite']):
        carte_id = ET.SubElement(root, 'CarteIdentite')
        ET.SubElement(carte_id, 'NumeroCarte').text = str(data_dict.get('numero_carte', 'Inconnu'))
        ET.SubElement(carte_id, 'Sexe').text = str(data_dict.get('sexe', 'Inconnu'))
        ET.SubElement(carte_id, 'Nationalite').text = str(data_dict.get('nationalite', 'Inconnu'))
        ET.SubElement(carte_id, 'LieuNaissance').text = str(data_dict.get('lieu_naissance', 'Inconnu'))
        ET.SubElement(carte_id, 'DateExpiration').text = str(data_dict.get('date_expiration', 'Inconnu'))

    competences = ET.SubElement(root, 'Competences')
    for comp in data_dict.get('competences', []):
        ET.SubElement(competences, 'Competence').text = str(comp)

    langues = ET.SubElement(root, 'Langues')
    for langue in data_dict.get('langues', []):
        if isinstance(langue, (tuple, list)) and len(langue) == 2:
            nom = str(langue[0])
            niveau = str(langue[1])
        elif isinstance(langue, dict):
            nom = str(langue.get('langue', 'Inconnu'))
            niveau = str(langue.get('niveau', 'Inconnu'))
        else:
            nom = str(langue)
            niveau = ''
        ET.SubElement(langues, 'Langue', niveau=niveau).text = nom

    experiences = ET.SubElement(root, 'Experiences')
    for exp in data_dict.get('experiences', []):
        experience = ET.SubElement(experiences, 'Experience')
        ET.SubElement(experience, 'Poste').text = str(exp.get('poste', 'Inconnu'))
        ET.SubElement(experience, 'Entreprise').text = str(exp.get('entreprise', 'Inconnu'))
        ET.SubElement(experience, 'Debut').text = str(exp.get('debut', 'Inconnu'))
        ET.SubElement(experience, 'Fin').text = str(exp.get('fin', 'Inconnu'))
        ET.SubElement(experience, 'Description').text = str(exp.get('description', ''))

    formations = ET.SubElement(root, 'Formations')
    for form in data_dict.get('formations', []):
        formation = ET.SubElement(formations, 'Formation')
        ET.SubElement(formation, 'Diplome').text = str(form.get('diplome', 'Inconnu'))
        ET.SubElement(formation, 'Etablissement').text = str(form.get('etablissement', 'Inconnu'))
        ET.SubElement(formation, 'Annee').text = str(form.get('annee', 'Inconnu'))

    # Retourne XML sous forme lisible
    xml_str = ET.tostring(root, encoding='utf-8')
    pretty_xml = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="  ")
    return pretty_xml
