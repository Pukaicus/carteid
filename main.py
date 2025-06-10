import os
from extract_cv import extract_info_cv
from extract_id import extract_info_id
from xml_utils import create_xml
from detect_type import detect_document_type  # ✔️ Corrigé ici
from ocr_utils import ocr_file  # Assure-toi d’avoir ce fichier
from config import INPUT_FOLDER, OUTPUT_FOLDER  # Assure-toi que ces variables sont bien définies

valid_extensions = ('.jpg', '.jpeg', '.png', '.pdf')

for root_dir, dirs, files in os.walk(INPUT_FOLDER):
    for filename in files:
        if filename.lower().endswith(valid_extensions):
            filepath = os.path.join(root_dir, filename)
            print(f"📄 Traitement du fichier : {filepath}")
            text = ocr_file(filepath)

            doc_type = detect_document_type(text)

            if doc_type == "id_card":
                info = extract_info_id(text)
                out_xml = os.path.join(OUTPUT_FOLDER, os.path.splitext(filename)[0] + '_carte.xml')
                create_xml(info, out_xml)
                print(f"✅ Carte d'identité analysée et enregistrée : {out_xml}")

            elif doc_type == "cv":
                info = extract_info_cv(text)
                out_xml = os.path.join(OUTPUT_FOLDER, os.path.splitext(filename)[0] + '_cv.xml')
                create_xml(info, out_xml)
                print(f"✅ CV analysé et enregistré : {out_xml}")

            else:
                print(f"❌ Type de document non reconnu pour : {filename}")
