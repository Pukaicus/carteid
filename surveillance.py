import os
import time
from ocr_utils import ocr_file
from delect_type import is_carte_identite
from extract_cv import extract_info_cv
from extract_id import extract_info_carte_id
from xml_utils import create_xml

# 📂 Chemins vers les dossiers à surveiller
input_folders = [
    r'D:\carteid_cv\CV',
    r'D:\carteid_cv\carte identité'
]

# 📁 Dossier de sortie des fichiers XML
output_folder = r'D:\carteid_cv\xml'
os.makedirs(output_folder, exist_ok=True)

# 🧠 Mémoriser les fichiers déjà traités
fichiers_deja_traite = set()

def traitement_fichier(filepath):
    print(f"📄 Traitement du fichier : {filepath}")
    text = ocr_file(filepath)

    if is_carte_identite(text):
        info = extract_info_carte_id(text)
        suffix = '_carte'
    else:
        info = extract_info_cv(text)
        suffix = '_cv'

    nom_fichier = os.path.splitext(os.path.basename(filepath))[0]
    out_xml = os.path.join(output_folder, nom_fichier + suffix + '.xml')
    create_xml(info, out_xml)
    print(f"✅ XML créé : {out_xml}")

# 🔁 Boucle de surveillance
while True:
    for folder in input_folders:
        fichiers = [f for f in os.listdir(folder) if f.lower().endswith(('.pdf','.png','.jpg','.jpeg'))]
        for f in fichiers:
            chemin = os.path.join(folder, f)
            if chemin not in fichiers_deja_traite:
                traitement_fichier(chemin)
                fichiers_deja_traite.add(chemin)
    time.sleep(5)  # vérifie toutes les 5 secondes
