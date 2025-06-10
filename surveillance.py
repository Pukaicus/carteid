import os
import time
from ocr_utils import ocr_file
from detect_type import detect_document_type
from extract_cv import extract_info_cv
from extract_id import extract_info_id
from xml_utils import save_to_xml 
from config import INPUT_DIR_ID, INPUT_DIR_CV, OUTPUT_DIR  

# 📂 Chemins vers les dossiers à surveiller
input_folders = [INPUT_DIR_ID, INPUT_DIR_CV]

# 📁 Dossier de sortie des fichiers XML
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 🧠 Mémoriser les fichiers déjà traités
fichiers_deja_traite = set()

def traitement_fichier(filepath):
    print(f"📄 Traitement du fichier : {filepath}")

    try:
        text = ocr_file(filepath)
        doc_type = detect_document_type(text)

        if doc_type == "carte_identite":
            info = extract_info_id(text)
            suffix = '_carte'
        elif doc_type == "cv":
            info = extract_info_cv(text)
            suffix = '_cv'
        else:
            print("❓ Type de document non reconnu.")
            return

        nom_fichier = os.path.splitext(os.path.basename(filepath))[0]
        out_xml = os.path.join(OUTPUT_DIR, nom_fichier + suffix + '.xml')
        save_to_xml(info, out_xml)
        print(f"✅ XML créé : {out_xml}")

    except (IOError, OSError) as file_error:
        print(f"🛑 Erreur fichier {filepath} : {file_error}")
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")

# 🔁 Boucle de surveillance
while True:
    for folder in input_folders:
        try:
            fichiers = [f for f in os.listdir(folder) if f.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg'))]
            for f in fichiers:
                chemin = os.path.join(folder, f)
                if chemin not in fichiers_deja_traite:
                    traitement_fichier(chemin)
                    fichiers_deja_traite.add(chemin)
        except FileNotFoundError as e:
            print(f"📁 Dossier introuvable : {folder} - {e}")
    time.sleep(5)
