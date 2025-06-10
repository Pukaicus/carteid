def is_carte_identite(text):
    text_lower = text.lower()
    keywords = ['république française', "carte d'identité", 'nationalité', 'nom', 'prénom', "date d'expiration", 'sexe']
    return sum(1 for kw in keywords if kw in text_lower) >= 3

def is_cv(text):
    text_lower = text.lower()
    keywords = ['curriculum vitae', 'expérience', 'formation', 'diplôme', 'stage', 'compétences', 'poste', 'profil']
    return sum(1 for kw in keywords if kw in text_lower) >= 3

def detect_document_type(text):
    if is_carte_identite(text):
        return "carte_identite"
    elif is_cv(text):
        return "cv"
    else:
        return None  
