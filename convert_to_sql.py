"""
DIRECT CONVERSION: Your copied data → SQL
No scraping. Just parse what you pasted.
"""
from datetime import datetime

# ========== ALL YOUR DATA HARDCODED FROM SCREENSHOTS ==========

# BAC TYPE MAPPING (French name → code)
BAC_MAP = {
    "Sciences naturelles": "D",
    "Mathématiques": "C",
    "Lettres originales": "A", 
    "Lettres modernes": "LM",
    "Filière technique": "T",
    "Génie électrique": "GE",
    "Langues": "L",
}

BAC_AR = {
    "D": "علوم طبيعية", "C": "رياضيات", "A": "آداب أصلية",
    "LM": "آداب حديثة", "T": "تقني", "GE": "هندسة كهربائية", "L": "لغات",
}

# ESTABLISHMENT → CODE mapping
EST_MAP = {
    "Faculté de Médecine, de Pharmacie et d'OdontoStomatologie": "FMPOS",
    "Institut Supérieur du Numérique": "SUPNUM",
    "Nouakchott Business School": "NBS",
    "École Normale Supérieure": "ENS",
    "Institut Supérieur de Génie Industriel": "ISGI",
    "Faculté Oussoul ad‑Dine (Fondements de la Religion)": "USIAFO",
    "Université de Nouakchott - Faculté des Sciences et Techniques": "UNFST",
    "École Nationale Supérieure des Sciences de la Santé": "ENSSS",
    "Institut Supérieur d'Anglais": "ISA",
    "Grande Mahdara Chinguitiya": "GMC",
    "Universités du Maroc": "UNMA",
    "Institut Supérieur de Comptabilité et d'Administration des Entreprises": "ISCAE",
    "Université de Nouakchott - Faculté des Lettres et des Sciences Humaines": "UNFLSH",
    "Fondation Cheikh Zaïd Ben Sultan à Rabat": "FCZR",
    "Universités de Tunisie": "UNTN",
    "Université de Nouadhibou - Faculté des Sciences et Technologie": "UNDBFST",
    "Université de Nouakchott - Faculté des Sciences Juridiques et Politiques": "UNFSJP",
    "Université de Nouadhibou - Faculté de Droit, d'Économie et de Gestion": "UNDBFDEG",
    "Faculté de la Charia": "USIAFC",
    "Université de Nouakchott - Faculté d'économie et de gestion": "UNFEG",
    "Institut Supérieur des Études et Recherches Islamiques": "ISERI",
    "Faculté de Langue Arabe et Sciences Humaines": "USIAFA",
    "Institut Supérieur des Sciences de la Mer": "ISSM",
    "Universités d'Égypte": "UNEG",
    "Universités du Sénégal": "UNSN",
    "Groupe Polytechnique / Institut Supérieur de l'Énergie": "ISE",
    "Groupe Polytechnique / Institut Supérieur de Génie Civil": "ISGC",
    "Institut Supérieur de l'Enseignement Technologique de Rosso": "ISET",
    "Groupe Polytechnique / Institut Supérieur du Genie Mecanique": "ISGM",
    "Université de Nouadhibou - Faculté des Sciences Humaines et Sociales": "UNDBFSHS",
    "Universités d'Algérie": "UNDZ",
    "Institut Superieur de la Jeunesse et des Sports": "ISJS",
    "Université de Nouadhibou - Institut Supérieur de Biotechnologie": "ISBT",
    "Institut Supérieur Professionnel de Langues, de Traduction et d'Interprétariat": "ISPLTI",
    "Groupe Polytechnique / Institut Supérieur de Statistique": "ISS",
    "Académie Navale": "ACNAV",
    "Groupe Polytechnique / École Supérieure Polytechnique": "ESP",
    "Groupe Polytechnique / Institut Préparatoire aux Grandes Écoles d'Ingénieurs": "IPGEI",
}

COUNTRY_MAP = {"🇲🇷": "MR", "🇲🇦": "MA", "🇹🇳": "TN", "🇩🇿": "DZ", "🇸🇳": "SN", "🇪🇬": "EG"}

# ========== PARSE LICENCE FORMATIONS ==========
# Format: Establishment\nCODE\tFormation\tFlag\nCountry
licence_raw = """Faculté de Médecine, de Pharmacie et d'OdontoStomatologie
FMPOS	Médecine	🇲🇷 Mauritanie
Faculté de Médecine, de Pharmacie et d'OdontoStomatologie
FMPOS	Médecine dentaire	🇲🇷 Mauritanie
Faculté de Médecine, de Pharmacie et d'OdontoStomatologie
FMPOS	Pharmacie	🇲🇷 Mauritanie
Institut Supérieur du Numérique
SUPNUM	Développement des systèmes d'information	🇲🇷 Mauritanie
Institut Supérieur du Numérique
SUPNUM	Développement Web et Multimédia	🇲🇷 Mauritanie
Institut Supérieur du Numérique
SUPNUM	Ingénierie des données et statistiques	🇲🇷 Mauritanie
Institut Supérieur du Numérique
SUPNUM	Ingénierie des systèmes connectés et autonomes	🇲🇷 Mauritanie
Institut Supérieur du Numérique
SUPNUM	Réseaux, systèmes et sécurité	🇲🇷 Mauritanie
Groupe Polytechnique / Institut Préparatoire aux Grandes Écoles d'Ingénieurs
IPGEI	CPGE : Maths, Physique, Sciences de l'Ingénieur	🇲🇷 Mauritanie
Nouakchott Business School
NBS	Bachelor en Sciences de la Gestion	🇲🇷 Mauritanie
École Normale Supérieure
ENS	Arabe	🇲🇷 Mauritanie
École Normale Supérieure
ENS	CPGE d'application du Centre d'Agrégation	🇲🇷 Mauritanie
École Normale Supérieure
ENS	Etudes Islamiques	🇲🇷 Mauritanie
École Normale Supérieure
ENS	English Foreign Language (EFL)	🇲🇷 Mauritanie
École Normale Supérieure
ENS	Français Langue Etrangère (FLE)	🇲🇷 Mauritanie
École Normale Supérieure
ENS	Histoire et Géographie	🇲🇷 Mauritanie
École Normale Supérieure
ENS	Mathématiques et Informatique	🇲🇷 Mauritanie
École Normale Supérieure
ENS	Physique, Chimie et Technologie	🇲🇷 Mauritanie
École Normale Supérieure
ENS	Philosophie et Sociologie	🇲🇷 Mauritanie
École Normale Supérieure
ENS	Sciences de la Vie et de la Terre	🇲🇷 Mauritanie
Institut Supérieur de Génie Industriel
ISGI	Science des données	🇲🇷 Mauritanie
Institut Supérieur de Génie Industriel
ISGI	Finance des Technologies	🇲🇷 Mauritanie
Institut Supérieur de Génie Industriel
ISGI	Génie Industriel	🇲🇷 Mauritanie
Institut Supérieur de Génie Industriel
ISGI	Logistique et Transport	🇲🇷 Mauritanie
Institut Supérieur de Génie Industriel
ISGI	Mathématiques Appliquées à l'Economie et à la Finance	🇲🇷 Mauritanie
Institut Supérieur de Génie Industriel
ISGI	Management	🇲🇷 Mauritanie
Institut Supérieur de Génie Industriel
ISGI	Réseaux & Télécommunications	🇲🇷 Mauritanie
Faculté Oussoul ad‑Dine (Fondements de la Religion)
USIAFO	Coran et la Sunna	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Analyses Biologiques et Chimiques	🇲🇷 Mauritanie
École Nationale Supérieure des Sciences de la Santé
ENSSS	Anesthésie et Réanimation	🇲🇷 Mauritanie
Institut Supérieur d'Anglais
ISA	Anglais	🇲🇷 Mauritanie
Grande Mahdara Chinguitiya
GMC	Arabe	🇲🇷 Mauritanie
Universités du Maroc
UNMA	Architecture	🇲🇦 Maroc
Institut Supérieur de Comptabilité et d'Administration des Entreprises
ISCAE	Banques et Assurances	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Biologie (Biologie des Organismes et des Ecosystèmes)	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Biologie (Biologie Moléculaire et Physiologie)	🇲🇷 Mauritanie
École Nationale Supérieure des Sciences de la Santé
ENSSS	Biologie médicale	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Chimie	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Chinois	🇲🇷 Mauritanie
Fondation Cheikh Zaïd Ben Sultan à Rabat
FCZR	Classes préparatoires Abulcasis	🇲🇦 Maroc
Universités du Maroc
UNMA	Classes Préparatoires aux Grandes Ecoles d'Ingénieurs	🇲🇦 Maroc
Universités de Tunisie
UNTN	Classes Préparatoires aux Grandes Ecoles d'Ingénieurs	🇹🇳 Tunisie
Université de Nouadhibou - Faculté des Sciences et Technologie
UNDBFST	Développement des Systèmes d'Information	🇲🇷 Mauritanie
Institut Supérieur de Comptabilité et d'Administration des Entreprises
ISCAE	Développement Informatique	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Développement Local	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Developpement, Administration d'Intranet et Internet	🇲🇷 Mauritanie
Faculté Oussoul ad‑Dine (Fondements de la Religion)
USIAFO	doctrine et pensée islamiques	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences Juridiques et Politiques
UNFSJP	Droit (en arabe)	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences Juridiques et Politiques
UNFSJP	Droit (en français)	🇲🇷 Mauritanie
Université de Nouadhibou - Faculté de Droit, d'Économie et de Gestion
UNDBFDEG	Droit des Activités Maritimes et Portuaires	🇲🇷 Mauritanie
Université de Nouadhibou - Faculté de Droit, d'Économie et de Gestion
UNDBFDEG	Droit des Mines et des Hydrocarbures	🇲🇷 Mauritanie
Faculté de la Charia
USIAFC	Droit privé	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences Juridiques et Politiques
UNFSJP	Droit privé arabe / Droit des affaires et des sociétés	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences Juridiques et Politiques
UNFSJP	Droit privé arabe/Professions judiciaires et juridiques	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences Juridiques et Politiques
UNFSJP	Droit public arabe/Administration publique	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences Juridiques et Politiques
UNFSJP	Droit public arabe/sciences politiques	🇲🇷 Mauritanie
Faculté Oussoul ad‑Dine (Fondements de la Religion)
USIAFO	Droit public et politique de la charia	🇲🇷 Mauritanie
Université de Nouakchott - Faculté d'économie et de gestion
UNFEG	Economie - Publique / Technique de gestion de projets Publics	🇲🇷 Mauritanie
Université de Nouakchott - Faculté d'économie et de gestion
UNFEG	Economie - Publique/Gestion de l'administration Publique	🇲🇷 Mauritanie
Institut Supérieur des Études et Recherches Islamiques
ISERI	Economie islamique	🇲🇷 Mauritanie
Faculté de la Charia
USIAFC	Economie islamique	🇲🇷 Mauritanie
Université de Nouakchott - Faculté d'économie et de gestion
UNFEG	Economie-Gestion/Finance et Comptabilité	🇲🇷 Mauritanie
Université de Nouakchott - Faculté d'économie et de gestion
UNFEG	Economie-Gestion/Gestion des Entreprises	🇲🇷 Mauritanie
Faculté de Langue Arabe et Sciences Humaines
USIAFA	Éducation et psychologie	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Electronique - Electrotechnique - Automatique	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Environnement et développement durable	🇲🇷 Mauritanie
Institut Supérieur des Sciences de la Mer
ISSM	Environnement Marin et Etudes du Littoral	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Espagnole	🇲🇷 Mauritanie
Grande Mahdara Chinguitiya
GMC	Etude Islamique	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Etudes anglaises	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Etudes arabes	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Etudes françaises	🇲🇷 Mauritanie
Universités d'Égypte
UNEG	Facultés des sciences, des arts, des langues, des médias, de l'économie, du commerce, des affaires, de l'agriculture, des sciences politiques et du droit	🇪🇬 Égypte
Universités du Sénégal
UNSN	Facultés des sciences, des lettres, des langues, de la communication, de l'économie, du commerce, de la gestion, de l'agriculture, des sciences politiques et du droit.	🇸🇳 SN
Institut Supérieur de Comptabilité et d'Administration des Entreprises
ISCAE	Finance et Comptabilité	🇲🇷 Mauritanie
Institut Supérieur des Études et Recherches Islamiques
ISERI	Fondements de la religion	🇲🇷 Mauritanie
Grande Mahdara Chinguitiya
GMC	Fondements de la théologie islamique	🇲🇷 Mauritanie
Groupe Polytechnique / Institut Supérieur de l'Énergie
ISE	Génie Chimie et Génie des Procédés	🇲🇷 Mauritanie
Groupe Polytechnique / Institut Supérieur de Génie Civil
ISGC	Génie civil	🇲🇷 Mauritanie
Université de Nouadhibou - Faculté des Sciences et Technologie
UNDBFST	Génie des Procédés de Dessalement	🇲🇷 Mauritanie
Groupe Polytechnique / Institut Supérieur de l'Énergie
ISE	Génie Electrique et Energie Renouvelable	🇲🇷 Mauritanie
Institut Supérieur de l'Enseignement Technologique de Rosso
ISET	Génie Électromécanique	🇲🇷 Mauritanie
Université de Nouadhibou - Faculté des Sciences et Technologie
UNDBFST	Génie Energétique et Energies Renouvelables	🇲🇷 Mauritanie
Fondation Cheikh Zaïd Ben Sultan à Rabat
FCZR	Génie informatique	🇲🇦 Maroc
Groupe Polytechnique / Institut Supérieur du Genie Mecanique
ISGM	Génie Mécanique	🇲🇷 Mauritanie
Fondation Cheikh Zaïd Ben Sultan à Rabat
FCZR	Génie Pharmaceutique	🇲🇦 Maroc
Institut Supérieur de l'Enseignement Technologique de Rosso
ISET	Génie Rural	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Géographie	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Géologie Appliquée (Géologie Minière)	🇲🇷 Mauritanie
Université de Nouadhibou - Faculté des Sciences et Technologie
UNDBFST	Géologie et Mines	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Géologie fondamentale (Géosciences)	🇲🇷 Mauritanie
Université de Nouadhibou - Faculté de Droit, d'Économie et de Gestion
UNDBFDEG	Gestion des Activités Portuaires et Maritimes	🇲🇷 Mauritanie
Institut Supérieur de Comptabilité et d'Administration des Entreprises
ISCAE	Gestion des Ressources Humaines	🇲🇷 Mauritanie
Université de Nouadhibou - Faculté de Droit, d'Économie et de Gestion
UNDBFDEG	Gestion des Risques Environnementaux et du Littoral	🇲🇷 Mauritanie
Université de Nouakchott - Faculté d'économie et de gestion
UNFEG	Gestion: Banques et Assurances	🇲🇷 Mauritanie
Université de Nouakchott - Faculté d'économie et de gestion
UNFEG	Gestion: Finance et Comptabilité	🇲🇷 Mauritanie
Université de Nouakchott - Faculté d'économie et de gestion
UNFEG	Gestion: Gestion des Ressources Humaines	🇲🇷 Mauritanie
Institut Supérieur des Études et Recherches Islamiques
ISERI	Histoire et civilisation	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Histoire et civilisation	🇲🇷 Mauritanie
Faculté de Langue Arabe et Sciences Humaines
USIAFA	Histoire et civilisation	🇲🇷 Mauritanie
École Nationale Supérieure des Sciences de la Santé
ENSSS	Imagerie médicale et radiologie	🇲🇷 Mauritanie
Institut Supérieur de Comptabilité et d'Administration des Entreprises
ISCAE	Informatique de Gestion	🇲🇷 Mauritanie
Universités du Maroc
UNMA	Ingénierie et Sciences Technologiques	🇲🇦 Maroc
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Ingénierie Pétrole et GAZ	🇲🇷 Mauritanie
Université de Nouadhibou - Faculté des Sciences et Technologie
UNDBFST	Intelligence Artificielle	🇲🇷 Mauritanie
Institut Supérieur d'Anglais
ISA	International Communication Studies	🇲🇷 Mauritanie
Faculté de la Charia
USIAFC	Jurisprudence et principes	🇲🇷 Mauritanie
Institut Supérieur des Études et Recherches Islamiques
ISERI	Jurisprudence et ses principes	🇲🇷 Mauritanie
École Nationale Supérieure des Sciences de la Santé
ENSSS	Kinésithérapie	🇲🇷 Mauritanie
Faculté Oussoul ad‑Dine (Fondements de la Religion)
USIAFO	La Sunna et ses sciences	🇲🇷 Mauritanie
Institut Supérieur des Études et Recherches Islamiques
ISERI	Langue et littérature arabes	🇲🇷 Mauritanie
Faculté de Langue Arabe et Sciences Humaines
USIAFA	Langue et littérature arabes	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Langues Nationales et Linguistique	🇲🇷 Mauritanie
Faculté Oussoul ad‑Dine (Fondements de la Religion)
USIAFO	Le Coran et ses sciences	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Licence Biologie	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Licence Biologie - Géologie	🇲🇷 Mauritanie
Université de Nouakchott - Faculté d'économie et de gestion
UNFEG	Licence Économie - Gestion	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Licence Géologie	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Licence Informatique	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Licence Mathématiques - Applications - Informatique	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Licence Mathématiques - Physique - Informatique	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Licence Physique - Chimie	🇲🇷 Mauritanie
Universités de Tunisie
UNTN	License dans les universités tunisiennes	🇹🇳 Tunisie
Institut Supérieur des Sciences de la Mer
ISSM	Logistique et Gestion Portuaire	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Mathématiques - Applications	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Mathématiques - Informatique	🇲🇷 Mauritanie
Universités d'Algérie
UNDZ	Médecine dentaire	🇩🇿 Algérie
Universités du Sénégal
UNSN	Médecine dentaire	🇸🇳 SN
Universités de Tunisie
UNTN	Médecine dentaire	🇹🇳 Tunisie
Universités d'Algérie
UNDZ	Médecine Générale	🇩🇿 Algérie
Universités du Maroc
UNMA	Médecine Générale	🇲🇦 Maroc
Universités du Sénégal
UNSN	Médecine Générale	🇸🇳 SN
Universités de Tunisie
UNTN	Médecine Générale	🇹🇳 Tunisie
Fondation Cheikh Zaïd Ben Sultan à Rabat
FCZR	Médecine vétérinaire	🇲🇦 Maroc
Institut Supérieur des Études et Recherches Islamiques
ISERI	Médias et communication	🇲🇷 Mauritanie
Faculté de Langue Arabe et Sciences Humaines
USIAFA	Médias et communication	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Méthodes Informatiques Appliquées à la Gestion des Entreprises	🇲🇷 Mauritanie
Université de Nouadhibou - Faculté des Sciences Humaines et Sociales
UNDBFSHS	Migrations et Mouvements des Populations	🇲🇷 Mauritanie
École Nationale Supérieure des Sciences de la Santé
ENSSS	Orthophonie	🇲🇷 Mauritanie
Fondation Cheikh Zaïd Ben Sultan à Rabat
FCZR	Pharmacie	🇲🇦 Maroc
Universités d'Algérie
UNDZ	Pharmacie	🇩🇿 Algérie
Universités du Maroc
UNMA	Pharmacie	🇲🇦 Maroc
Universités du Sénégal
UNSN	Pharmacie	🇸🇳 SN
Universités de Tunisie
UNTN	Pharmacie	🇹🇳 Tunisie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Philosophie	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Physique Fondamentale	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Production d'Eau Potable et Environnement	🇲🇷 Mauritanie
Institut Supérieur de l'Enseignement Technologique de Rosso
ISET	Production et Protection Végétales	🇲🇷 Mauritanie
Institut Supérieur de l'Enseignement Technologique de Rosso
ISET	Production et Santé Animales	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Réseaux et Systèmes Communicants	🇲🇷 Mauritanie
Institut Supérieur de Comptabilité et d'Administration des Entreprises
ISCAE	Réseaux Informatiques et Télécommunications	🇲🇷 Mauritanie
Institut Supérieur de l'Enseignement Technologique de Rosso
ISET	Science et Technologie des Aliments	🇲🇷 Mauritanie
Universités du Maroc
UNMA	Sciences Agronomiques et Vétérinaires	🇲🇦 Maroc
Universités du Maroc
UNMA	Sciences Commerciales et de Gestion	🇲🇦 Maroc
Institut Superieur de la Jeunesse et des Sports
ISJS	Sciences et techniques des activités physiques et sportives	🇲🇷 Mauritanie
Institut Superieur de la Jeunesse et des Sports
ISJS	Sciences et techniques des activités socio-éducatives	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Sciences et Technologie des Aliments (Nutrition et Santé)	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Sciences et Technologie des Aliments (Technologies Alimentaires Spécifiques et Systèmes Management de la Qualité)	🇲🇷 Mauritanie
Université de Nouadhibou - Institut Supérieur de Biotechnologie
ISBT	Sciences Halieutiques et Biotechnologie Bleue	🇲🇷 Mauritanie
Institut Supérieur des Sciences de la Mer
ISSM	Sciences Halieutiques et Industries de la pêche	🇲🇷 Mauritanie
École Nationale Supérieure des Sciences de la Santé
ENSSS	Sciences infirmières	🇲🇷 Mauritanie
Fondation Cheikh Zaïd Ben Sultan à Rabat
FCZR	Sciences infirmières IAR	🇲🇦 Maroc
Fondation Cheikh Zaïd Ben Sultan à Rabat
FCZR	Sciences infirmières Imagerie	🇲🇦 Maroc
École Nationale Supérieure des Sciences de la Santé
ENSSS	Sciences maïeutiques	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Sciences Physiques	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Service social	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Sociologie	🇲🇷 Mauritanie
Groupe Polytechnique / Institut Supérieur de Statistique
ISS	Statistique	🇲🇷 Mauritanie
Institut Supérieur de Comptabilité et d'Administration des Entreprises
ISCAE	Statistique Appliquée à l'Economie	🇲🇷 Mauritanie
Université de Nouadhibou - Faculté des Sciences et Technologie
UNDBFST	Statistiques et Data Science	🇲🇷 Mauritanie
Institut Supérieur des Études et Recherches Islamiques
ISERI	Systèmes et professions judiciaires	🇲🇷 Mauritanie
Institut Supérieur de Comptabilité et d'Administration des Entreprises
ISCAE	Techniques Commerciales et Marketing	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Techniques de Prospection Géologique et Minière	🇲🇷 Mauritanie
Fondation Cheikh Zaïd Ben Sultan à Rabat
FCZR	Technologie de la Santé	🇲🇦 Maroc
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Technologies des Systèmes des Energies Renouvelables	🇲🇷 Mauritanie
Institut Supérieur Professionnel de Langues, de Traduction et d'Interprétariat
ISPLTI	Traduction Anglais/Arabe	🇲🇷 Mauritanie
Institut Supérieur Professionnel de Langues, de Traduction et d'Interprétariat
ISPLTI	Traduction Anglais/Francais	🇲🇷 Mauritanie
Institut Supérieur Professionnel de Langues, de Traduction et d'Interprétariat
ISPLTI	Traduction Arabe/Francais	🇲🇷 Mauritanie
École Nationale Supérieure des Sciences de la Santé
ENSSS	Tron commun	🇲🇷 Mauritanie
Grande Mahdara Chinguitiya
GMC	Tronc commun	🇲🇷 Mauritanie
Institut Supérieur des Études et Recherches Islamiques
ISERI	Tronc commun	🇲🇷 Mauritanie
Institut Supérieur de l'Enseignement Technologique de Rosso
ISET	Tronc commun	🇲🇷 Mauritanie
Faculté de Langue Arabe et Sciences Humaines
USIAFA	Tronc commun	🇲🇷 Mauritanie
Faculté de la Charia
USIAFC	Tronc commun	🇲🇷 Mauritanie
Faculté Oussoul ad‑Dine (Fondements de la Religion)
USIAFO	Tronc commun	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Turc	🇲🇷 Mauritanie"""

# ========== PARSE MASTER FORMATIONS ==========
master_raw = """Académie Navale
ACNAV	Énergie et propulsion	🇲🇷 Mauritanie
Académie Navale
ACNAV	Ingénieur en navigation maritime	🇲🇷 Mauritanie
École Normale Supérieure
ENS	Master d'agrégation en mathématiques	🇲🇷 Mauritanie
École Normale Supérieure
ENS	Master d'agrégation en physique - chimie	🇲🇷 Mauritanie
École Normale Supérieure
ENS	Master en éducation anglais langue étrangère	🇲🇷 Mauritanie
École Normale Supérieure
ENS	Master en éducation français langue étrangère	🇲🇷 Mauritanie
École Normale Supérieure
ENS	Master en éducation mathématique	🇲🇷 Mauritanie
École Normale Supérieure
ENS	Master en éducation physique-chimie	🇲🇷 Mauritanie
École Normale Supérieure
ENS	Master en éducation science de la vie et de la terre	🇲🇷 Mauritanie
Groupe Polytechnique / École Supérieure Polytechnique
ESP	Génie civil, Hydraulique et Environnement	🇲🇷 Mauritanie
Groupe Polytechnique / École Supérieure Polytechnique
ESP	Génie Électrique	🇲🇷 Mauritanie
Groupe Polytechnique / École Supérieure Polytechnique
ESP	Génie Mécanique	🇲🇷 Mauritanie
Groupe Polytechnique / École Supérieure Polytechnique
ESP	Informatique Réseaux et Télécommunications	🇲🇷 Mauritanie
Groupe Polytechnique / École Supérieure Polytechnique
ESP	Mines, Pétrole et Gaz	🇲🇷 Mauritanie
Groupe Polytechnique / École Supérieure Polytechnique
ESP	Statistique et Ingénierie des Données	🇲🇷 Mauritanie
Faculté de Médecine, de Pharmacie et d'OdontoStomatologie
FMPOS	Médecine	🇲🇷 Mauritanie
Faculté de Médecine, de Pharmacie et d'OdontoStomatologie
FMPOS	Médecine dentaire	🇲🇷 Mauritanie
Faculté de Médecine, de Pharmacie et d'OdontoStomatologie
FMPOS	Pharmacie	🇲🇷 Mauritanie
Grande Mahdara Chinguitiya
GMC	Master en jurisprudence malékite et questions contemporaines d'ijtihad	🇲🇷 Mauritanie
Institut Supérieur de Comptabilité et d'Administration des Entreprises
ISCAE	Finance Et Comptabilité - Finance Et Comptabilité	🇲🇷 Mauritanie
Institut Supérieur de Comptabilité et d'Administration des Entreprises
ISCAE	Informatique Appliquée À La Gestion (Master Conjoint Entre L'Iscae Et La Fst) - Informatique Appliquée À La Gestion	🇲🇷 Mauritanie
Institut Supérieur des Études et Recherches Islamiques
ISERI	Master en grammaire et morphologie	🇲🇷 Mauritanie
Institut Supérieur des Études et Recherches Islamiques
ISERI	Master en banque islamique	🇲🇷 Mauritanie
Institut Supérieur des Études et Recherches Islamiques
ISERI	Master en études coraniques	🇲🇷 Mauritanie
Institut Supérieur des Études et Recherches Islamiques
ISERI	Master en histoire et civilisation	🇲🇷 Mauritanie
Institut Supérieur des Études et Recherches Islamiques
ISERI	Master en fiqh malikite	🇲🇷 Mauritanie
Institut Supérieur des Études et Recherches Islamiques
ISERI	Master en fiqh judiciaire et des nawâzil	🇲🇷 Mauritanie
Institut Supérieur du Numérique
SUPNUM	Master En Cybersécurité	🇲🇷 Mauritanie
Institut Supérieur du Numérique
SUPNUM	Master En Ingénierie Des Données Et Apprentissage Automatique	🇲🇷 Mauritanie
Universités d'Algérie
UNDZ	Master dans les universités algériennes	🇩🇿 Algérie
Université de Nouakchott - Faculté d'économie et de gestion
UNFEG	Master Analyse Economique En Français - Analyse Et Politique Economique	🇲🇷 Mauritanie
Université de Nouakchott - Faculté d'économie et de gestion
UNFEG	Master Analyse Economique En Français - Chargé D'Etudes Economiques	🇲🇷 Mauritanie
Université de Nouakchott - Faculté d'économie et de gestion
UNFEG	Master Comptabilité, Contrôle Et Audit En Français - Comptabilité, Contrôle Et Audit - Professionnel	🇲🇷 Mauritanie
Université de Nouakchott - Faculté d'économie et de gestion
UNFEG	Master Comptabilité, Contrôle Et Audit En Français - Comptabilité, Contrôle Et Audit - Recherche	🇲🇷 Mauritanie
Université de Nouakchott - Faculté d'économie et de gestion
UNFEG	Master Econométrie Et Statistique Appliquée En Français - Econométrie	🇲🇷 Mauritanie
Université de Nouakchott - Faculté d'économie et de gestion
UNFEG	Master Econométrie Et Statistique Appliquée En Français - Ingénierie Statistique Et Economique	🇲🇷 Mauritanie
Université de Nouakchott - Faculté d'économie et de gestion
UNFEG	Master Finance En Arabe - Finance Internationale	🇲🇷 Mauritanie
Université de Nouakchott - Faculté d'économie et de gestion
UNFEG	Master Finance En Arabe - Finance Islamique	🇲🇷 Mauritanie
Université de Nouakchott - Faculté d'économie et de gestion
UNFEG	Master Monnaie, Banque Et Finance En Français - Monnaie, Banque Et Finance	🇲🇷 Mauritanie
Université de Nouakchott - Faculté d'économie et de gestion
UNFEG	Master Management En Français - Entrepreneuriat	🇲🇷 Mauritanie
Université de Nouakchott - Faculté d'économie et de gestion
UNFEG	Master Management En Français - Finance Et Fiscalité	🇲🇷 Mauritanie
Université de Nouakchott - Faculté d'économie et de gestion
UNFEG	Master Management En Français - Management Des Ressources Humaines	🇲🇷 Mauritanie
Université de Nouakchott - Faculté d'économie et de gestion
UNFEG	Master Management En Français - Management Stratégique Et Contrôle De Gestion	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Master Anglais - English And Culture Studies	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Master Géographie - Dynamique Du Littoral Désertique	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Master Histoire - Société Et Pouvoir Dans L'Espace Désertique Côtier À L'Époque Moderne	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Master Langue Arabe - Méthodologie De Recherche En Langue Et Littérature	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Master Littérature Française - Lettres Modernes Francophones	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Master Migration, Gouverance Foncière Et Térritoriale - Migration, Gouvernance Foncière Et Territoriale	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Master Philosophie - L'Homme Et La Philosophie	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Lettres et des Sciences Humaines
UNFLSH	Master Sociologie - Transformations Sociales Et Développement Local	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences Juridiques et Politiques
UNFSJP	Master Droit Des Affaires Et De L'Entreprise En Arabe - Droit Des Affaires Et De L'Entreprise	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences Juridiques et Politiques
UNFSJP	Master Droit Des Espaces Et Activités Maritimes En Français - Droit Des Espaces Et Activités Maritimes	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences Juridiques et Politiques
UNFSJP	Master Droit De L'Homme Et Droit Humanitaire En Arabe - Droit De L'Homme Et Droit Humanitaire	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences Juridiques et Politiques
UNFSJP	Master Droit Privé En Arabe - Droit Privé	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences Juridiques et Politiques
UNFSJP	Master Droit Public En Arabe - Droit Public	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences Juridiques et Politiques
UNFSJP	Master Relations Internationales En Arabe - Relations Internationales Et Diplomatie	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Master Biologie - Biologie Environnementale Et Ecosystèmes Sahéliens (Bees)	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Master Biologie - Biologie Moléculaire, Physiologie Et Biotechnologies (Bmpb)	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Master Biologie - Biologie Des Organismes Marins Et Valorisation Des Ressources Halieutiques (Bomvrh)	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Master Biologie - Phœniciculture & Intelligence Artificielle(Pia)	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Master Chimie - Chimie Des Matériaux (Cm)	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Master Chimie - Chimie Des Substances Naturelles (Sn)	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Master Eau Et Environnement - Eau Et Environnement (Ee)	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Master Géologie, Ressources Naturelles Et Environnement (Grene) - Géologie Appliquée : Option Mine (Geomin)	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Master Géologie, Ressources Naturelles Et Environnement (Grene) -Géologie Fondamentale : Option Géoscience	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Master Informatique	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Master Informatique - Bio-Informatique (Bioinfo)	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Master Informatique, Intelligence Artificielle	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Master Informatique - Intelligence Artificielle (Ia)- Machine learning et data science (MLDS)	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Master Informatique - Intelligence Artificielle (Ia)- Natural langage Processing & Computer Vision	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Master Informatique - Réseau Et Système Communiquant (Rsc)	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Master Informatique - Système D'Information (Si)	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Master Mathématiques Et Applications	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Master Mathématiques Et Applications - Ingénierie Mathématiques Et Calcul Scientifique (Imcs)	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Master Mathématiques Et Applications - Statistiques Et Sciences De Données (Ssd)	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Master Nutrition Humaine, Santé Et Sciences Des Aliments - Nutrition Santé (Ns)	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Master Nutrition Humaine, Santé Et Sciences Des Aliments - Technologie Des Aliments Systèmes De Management Et Contrôle Qualité (Ta-Smcq)	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Physique - Energies Renouvelables (Er)	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Physique - Mécanique Et Matériaux (2M)	🇲🇷 Mauritanie
Université de Nouakchott - Faculté des Sciences et Techniques
UNFST	Physique - Master Professionnel Génie Electrique (Mpge)	🇲🇷 Mauritanie
Universités du Maroc
UNMA	Master dans les universités marocaines	🇲🇦 Maroc
Universités de Tunisie
UNTN	Master dans les universités tunisiennes	🇹🇳 Tunisie
Faculté de Langue Arabe et Sciences Humaines
USIAFA	Master Langue Arabe Et Sciences Humaines - Grammaire Et Morphologie	🇲🇷 Mauritanie
Faculté de Langue Arabe et Sciences Humaines
USIAFA	Master Langue Arabe Et Sciences Humaines - Médias Et Communication	🇲🇷 Mauritanie
Faculté de la Charia
USIAFC	Master Charia - Droit Civil Et Des Affaires	🇲🇷 Mauritanie
Faculté de la Charia
USIAFC	Master Charia - Finance Islamique Et Transactions Bancaires	🇲🇷 Mauritanie
Faculté de la Charia
USIAFC	Master Charia - Fiqh Des Situations Contemporaines : Fondements Et Application	🇲🇷 Mauritanie
Faculté Oussoul ad‑Dine (Fondements de la Religion)
USIAFO	Master Fondements De La Religion - Études Du Hadith : Transmission Et Compréhension	🇲🇷 Mauritanie
Faculté Oussoul ad‑Dine (Fondements de la Religion)
USIAFO	Master Fondements De La Religion - Pensée Islamique Et Enjeux Contemporains	🇲🇷 Mauritanie"""

# ========== PARSE ORIENTATION STATS (Licence section) ==========
orientation_licence = [
    ("License dans les universités tunisiennes", "Filière technique", 1, 2, 13.41),
    ("License dans les universités tunisiennes", "Génie électrique", 1, 3, 13.53),
    ("License dans les universités tunisiennes", "Lettres modernes", 2, 48, 12.85),
    ("License dans les universités tunisiennes", "Lettres originales", 2, 50, 14.48),
    ("License dans les universités tunisiennes", "Mathématiques", 4, 374, 11.12),
    ("License dans les universités tunisiennes", "Sciences naturelles", 23, 1562, 11.52),
    ("Médecine", "Mathématiques", 42, 177, 13.02),
    ("Médecine", "Sciences naturelles", 242, 317, 14.40),
    ("Médecine dentaire", "Mathématiques", 5, 196, 12.78),
    ("Médecine dentaire", "Sciences naturelles", 25, 352, 14.26),
    ("Pharmacie", "Mathématiques", 5, 317, 11.60),
    ("Pharmacie", "Sciences naturelles", 40, 441, 13.91),
    ("CPGE : Maths, Physique, Sciences de l'Ingénieur", "Mathématiques", 157, 256, 12.09),
    ("Réseaux, systèmes et sécurité", "Mathématiques", 11, 295, 11.73),
    ("Réseaux, systèmes et sécurité", "Sciences naturelles", 18, 413, 13.99),
    ("Développement des systèmes d'information", "Mathématiques", 33, 418, 10.70),
    ("Développement des systèmes d'information", "Sciences naturelles", 49, 483, 13.74),
    ("Ingénierie des données et statistiques", "Mathématiques", 28, 459, 10.34),
    ("Intelligence Artificielle", "Mathématiques", 21, 586, 10.00),
    ("Statistiques et Data Science", "Mathématiques", 17, 753, 10.00),
    ("Droit (en arabe)", "Lettres modernes", 511, 2018, 10.00),
    ("Droit (en arabe)", "Lettres originales", 1483, 4217, 10.00),
    ("Economie-Gestion/Gestion des Entreprises", "Lettres originales", 535, 4218, 10.00),
    ("Economie-Gestion/Gestion des Entreprises", "Sciences naturelles", 2060, 8043, 10.00),
    ("Biologie (Biologie Moléculaire et Physiologie)", "Sciences naturelles", 748, 7060, 10.06),
    ("Biologie (Biologie des Organismes et des Ecosystèmes)", "Sciences naturelles", 686, 8807, 10.00),
    ("Chimie", "Sciences naturelles", 345, 8809, 10.00),
    ("Physique Fondamentale", "Sciences naturelles", 118, 8808, 10.00),
    ("Sciences Physiques", "Sciences naturelles", 142, 8812, 10.00),
    ("Géologie fondamentale (Géosciences)", "Sciences naturelles", 346, 8691, 10.00),
    ("Tron commun", "Mathématiques", 21, 632, 10.00),
    ("Tron commun", "Sciences naturelles", 277, 1288, 11.90),
    ("Tron commun", "Lettres originales", 1121, 2663, 10.00),
    ("Anglais", "Lettres modernes", 63, 559, 10.01),
    ("Finance et Comptabilité", "Mathématiques", 8, 588, 10.00),
    ("Finance et Comptabilité", "Sciences naturelles", 70, 1487, 11.61),
    ("Bachelor en Sciences de la Gestion", "Mathématiques", 16, 655, 10.27),
    ("Bachelor en Sciences de la Gestion", "Sciences naturelles", 72, 1151, 12.10),
]


def esc(s):
    return s.replace("'", "''")

def generate_sql():
    sql = []
    sql.append("-- =============================================")
    sql.append("-- TEWJIHI - COMPLETE SEED DATA")
    sql.append(f"-- Generated: {datetime.now().isoformat()}")
    sql.append("-- =============================================\n")
    
    # BAC TYPES
    sql.append("-- ========== BAC TYPES ==========")
    for name, code in BAC_MAP.items():
        ar = BAC_AR.get(code, '')
        sql.append(f"INSERT INTO bac_types (code, name_ar, name_fr, created_at) VALUES ('{code}', '{ar}', '{esc(name)}', NOW()) ON CONFLICT (code) DO NOTHING;")
    sql.append("")
    
    # PARSE & INSERT ESTABLISHMENTS + FORMATIONS
    establishments_seen = set()
    formations_seen = set()
    
    def parse_formations(raw_text, level):
        lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
        i = 0
        while i < len(lines):
            line = lines[i]
            # Check if it's an establishment name (no tab)
            if '\t' not in line and i+1 < len(lines) and '\t' in lines[i+1]:
                est_name = line
                i += 1
                # Parse formation lines for this establishment
                while i < len(lines) and '\t' in lines[i]:
                    parts = lines[i].split('\t')
                    code = parts[0].strip() if len(parts) > 0 else ""
                    form_name = parts[1].strip() if len(parts) > 1 else ""
                    country_text = parts[2].strip() if len(parts) > 2 else ""
                    
                    # Determine country
                    country = "MR"
                    for flag, cc in COUNTRY_MAP.items():
                        if flag in country_text:
                            country = cc
                            break
                    
                    if code and code not in establishments_seen:
                        establishments_seen.add(code)
                        # Clean est_name - remove the code if appended
                        clean_name = est_name
                        if code in est_name:
                            clean_name = est_name.replace(code, '').strip()
                        sql.append(f"INSERT INTO establishments (code, name_ar, name_fr, country, city, created_at) VALUES ('{code}', '', '{esc(clean_name)}', '{country}', '', NOW()) ON CONFLICT (code) DO NOTHING;")
                    
                    if form_name and code:
                        key = (code, form_name, level)
                        if key not in formations_seen:
                            formations_seen.add(key)
                            dur = 3 if level == 'LICENCE' else 2
                            sql.append(f"INSERT INTO formations (establishment_id, name_ar, name_fr, level, duration_years, is_available_current_year, created_at) VALUES ((SELECT id FROM establishments WHERE code='{code}'), '', '{esc(form_name)}', '{level}', {dur}, true, NOW()) ON CONFLICT DO NOTHING;")
                    
                    i += 1
            else:
                i += 1
    
    sql.append("-- ========== LICENCE FORMATIONS ==========")
    parse_formations(licence_raw, 'LICENCE')
    
    sql.append("\n-- ========== MASTER FORMATIONS ==========")
    parse_formations(master_raw, 'MASTER')
    
    # ORIENTATION RESULTS
    sql.append("\n-- ========== ORIENTATION RESULTS (Licence) ==========")
    for form_name, bac_name, total, rank, avg in orientation_licence:
        bac_code = BAC_MAP.get(bac_name, '')
        if bac_code:
            sql.append(f"INSERT INTO orientation_results (year, formation_id, bac_type_id, total_oriented, last_rank, last_average, scraped_at) VALUES (2025, (SELECT id FROM formations WHERE name_fr='{esc(form_name)}' LIMIT 1), (SELECT id FROM bac_types WHERE code='{bac_code}'), {total}, {rank}, {avg}, NOW()) ON CONFLICT DO NOTHING;")
    
    # Write
    with open('seed_complete.sql', 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql))
    
    print(f"✅ Done! seed_complete.sql")
    print(f"   Bac types: {len(BAC_MAP)}")
    print(f"   Establishments: {len(establishments_seen)}")
    print(f"   Formations: {len(formations_seen)}")
    print(f"   Orientation results: {len(orientation_licence)}")

if __name__ == "__main__":
    generate_sql()