import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

from ocr_utils import ocr_file
from detect_type import detect_document_type
from extract_cv import extract_info_cv
from extract_id import extract_info_id
from xml_utils import create_xml

# ✅ Attente que le fichier soit complètement disponible
def wait_until_ready(filepath, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with open(filepath, 'rb') as f:
                f.read()
            return True
        except Exception:
            time.sleep(0.5)
    return False

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        filepath = event.src_path
        print(f"Nouveau fichier détecté : {filepath}")

        # ✅ Attente que le fichier soit prêt
        if not wait_until_ready(filepath):
            print(f"Erreur : Le fichier {filepath} n'est pas prêt après 10 secondes.")
            return

        # OCR
        text = ocr_file(filepath)

        # Nettoyage simple du texte
        text = text.replace('\n', ' ').replace('\r', ' ').strip()

        # ✅ Détection homogène du type de document
        doc_type = detect_document_type(text)
        print(f"Type détecté : {doc_type}")

        if doc_type not in ['cv', 'carte_identite']:
            print(f"[IGNORÉ] Type de document non reconnu pour : {filepath}")
            return

        # Extraction des infos selon le type détecté
        if doc_type == 'cv':
            info = extract_info_cv(text)
        elif doc_type == 'carte_identite':
            info = extract_info_id(text)

        # Préparation nom fichier XML
        base_name = os.path.splitext(os.path.basename(filepath))[0]
        output_dir = 'xml'
        os.makedirs(output_dir, exist_ok=True)
        xml_filename = os.path.join(output_dir, f"{base_name}.xml")

        # Création fichier XML
        create_xml(info, xml_filename)
        print(f"Fichier XML créé : {xml_filename}")

if __name__ == "__main__":
    paths_to_watch = ["CV", "carte identité"]

    event_handler = NewFileHandler()
    observer = Observer()

    for path in paths_to_watch:
        observer.schedule(event_handler, path=path, recursive=False)
        print(f"Surveillance activée sur : {path}")

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Arrêt de la surveillance.")
        observer.stop()
    observer.join()
