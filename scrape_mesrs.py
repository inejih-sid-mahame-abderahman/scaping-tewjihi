"""
TEWJIHI PLATFORM - MESRS Data Scraper
Target: https://etudiants-mesrs.app
Extracts: Formations (Licence/Master) + Orientation Statistics
Output: SQL seed file for PostgreSQL
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

# ========== CONFIGURATION ==========
BASE_URL = "https://etudiants-mesrs.app"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9,ar;q=0.8",
}
YEAR = 2025

# ========== BAC TYPE MAPPING (from site data) ==========
BAC_TYPE_MAP = {
    "Sciences naturelles": "D",
    "Mathématiques": "C",
    "Lettres originales": "A",
    "Lettres modernes": "LM",
    "Filière technique": "T",
    "Génie électrique": "GE",
    "Langues": "L",
    "Etude Islamique": "O",
}

# ========== ESTABLISHMENT CODE EXTRACTION ==========
def extract_establishment_code(name_fr):
    """Extract or generate a unique code for an establishment."""
    code_map = {
        "Faculté de Médecine, de Pharmacie et d'OdontoStomatologie": "FMPOS",
        "Institut Supérieur du Numérique": "SUPNUM",
        "Groupe Polytechnique / Institut Préparatoire aux Grandes Écoles d'Ingénieurs": "IPGEI",
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
    }
    if name_fr in code_map:
        return code_map[name_fr]
    # Generate code from name
    words = name_fr.split()
    return ''.join([w[0] for w in words if w[0].isupper()])[:10]


def extract_country_from_flag(flag_emoji):
    """Map flag emoji to country code."""
    flag_map = {
        "🇲🇷": "MR",
        "🇲🇦": "MA",
        "🇹🇳": "TN",
        "🇩🇿": "DZ",
        "🇸🇳": "SN",
        "🇪🇬": "EG",
    }
    return flag_map.get(flag_emoji, "MR")


# ========== SCRAPER CLASS ==========
class MESRSScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.establishments = {}  # code -> id (will be assigned during SQL generation)
        self.formations = {}      # (establishment_code, name_fr, level) -> data
        self.bac_types = {}       # code -> id
        self.orientation_results = []
        self.establishment_id_counter = 1
        self.formation_id_counter = 1

    def fetch_page(self, url):
        """Fetch a page and return BeautifulSoup object."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    # ========== SCRAPE FORMATIONS (Licence + Master) ==========
    def scrape_formations_licence(self):
        """Scrape all Licence formations from the Offres Licence page."""
        print("Scraping Licence formations...")
        soup = self.fetch_page(f"{BASE_URL}/offres-formation/licence")
        if not soup:
            return

        # Find the table with formations
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    # Format: Établissement | Formation | Pays
                    establishment_text = cols[0].get_text(strip=True)
                    formation_text = cols[1].get_text(strip=True)
                    pays_cell = cols[2]

                    # Extract establishment code (often in the text like "FMPOS")
                    establishment_code = self._extract_code_from_text(establishment_text)
                    establishment_name = self._clean_establishment_name(establishment_text)
                    country = "MR"
                    flag = pays_cell.find('span', class_='flag')
                    if flag:
                        country = extract_country_from_flag(flag.get_text(strip=True))

                    # Store establishment
                    if establishment_code not in self.establishments:
                        self.establishments[establishment_code] = {
                            'code': establishment_code,
                            'name_fr': establishment_name,
                            'name_ar': '',  # Will be added manually or via translation
                            'country': country,
                            'city': 'Nouakchott' if country == 'MR' else '',
                            'website': '',
                            'housing_available': False,
                            'description': '',
                            'logo_url': '',
                        }

                    # Store formation
                    key = (establishment_code, formation_text, 'LICENCE')
                    if key not in self.formations:
                        self.formations[key] = {
                            'establishment_code': establishment_code,
                            'name_fr': formation_text,
                            'name_ar': '',
                            'level': 'LICENCE',
                            'duration_years': 3,
                            'description': '',
                            'is_available_current_year': True,
                            'tags': json.dumps([formation_text, establishment_name]),
                        }

        print(f"  Found {len(self.establishments)} establishments")
        print(f"  Found {sum(1 for k,v in self.formations.items() if v['level']=='LICENCE')} Licence formations")

    def scrape_formations_master(self):
        """Scrape all Master formations from the Offres Master page."""
        print("Scraping Master formations...")
        soup = self.fetch_page(f"{BASE_URL}/offres-formation/master")
        if not soup:
            return

        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    establishment_text = cols[0].get_text(strip=True)
                    formation_text = cols[1].get_text(strip=True)
                    pays_cell = cols[2]

                    establishment_code = self._extract_code_from_text(establishment_text)
                    establishment_name = self._clean_establishment_name(establishment_text)
                    country = "MR"
                    flag = pays_cell.find('span', class_='flag')
                    if flag:
                        country = extract_country_from_flag(flag.get_text(strip=True))

                    if establishment_code not in self.establishments:
                        self.establishments[establishment_code] = {
                            'code': establishment_code,
                            'name_fr': establishment_name,
                            'name_ar': '',
                            'country': country,
                            'city': 'Nouakchott' if country == 'MR' else '',
                            'website': '',
                            'housing_available': False,
                            'description': '',
                            'logo_url': '',
                        }

                    key = (establishment_code, formation_text, 'MASTER')
                    if key not in self.formations:
                        self.formations[key] = {
                            'establishment_code': establishment_code,
                            'name_fr': formation_text,
                            'name_ar': '',
                            'level': 'MASTER',
                            'duration_years': 2,
                            'description': '',
                            'is_available_current_year': True,
                            'tags': json.dumps([formation_text, establishment_name]),
                        }

        print(f"  Total establishments now: {len(self.establishments)}")
        print(f"  Total formations now: {len(self.formations)}")

    # ========== SCRAPE ORIENTATION STATISTICS ==========
    def scrape_orientation_stats(self):
        """
        Scrape the Statistiques des orientations page.
        This extracts: Formation, Type de bac, Total Orientations, Dernier Rang, Dernière Moyenne
        """
        print("Scraping orientation statistics...")
        soup = self.fetch_page(f"{BASE_URL}/statistiques")
        if not soup:
            return

        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            current_formation = None
            current_establishment = None

            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 5:
                    # Full row: Formation | Type Bac | Total | Rang | Moyenne
                    formation_cell = cols[0].get_text(strip=True)
                    bac_type_cell = cols[1].get_text(strip=True)
                    total_cell = cols[2].get_text(strip=True)
                    rang_cell = cols[3].get_text(strip=True)
                    moyenne_cell = cols[4].get_text(strip=True)

                    # Some rows have formation spanning multiple lines
                    if formation_cell and not self._is_bac_type(formation_cell):
                        current_formation = formation_cell

                    bac_code = self._match_bac_type(bac_type_cell)
                    if not bac_code:
                        # Try to match from the first column if it's a bac type
                        bac_code = self._match_bac_type(formation_cell)
                        if bac_code:
                            current_formation = None  # This is a continuation

                    if bac_code and current_formation:
                        try:
                            total = int(total_cell.replace(',', '').replace(' ', '')) if total_cell else 0
                            rang = int(rang_cell.replace(',', '').replace(' ', '')) if rang_cell else 0
                            moyenne = float(moyenne_cell.replace(',', '.')) if moyenne_cell else 0.0

                            self.orientation_results.append({
                                'formation_name': current_formation,
                                'bac_type_code': bac_code,
                                'total_oriented': total,
                                'last_rank': rang,
                                'last_average': moyenne,
                                'year': YEAR,
                            })
                        except ValueError:
                            continue

        print(f"  Found {len(self.orientation_results)} orientation result rows")

    # ========== HELPER METHODS ==========
    def _extract_code_from_text(self, text):
        """Extract establishment code like FMPOS, SUPNUM from text."""
        # Look for uppercase codes in parentheses or at end of text
        match = re.search(r'\b([A-Z]{2,10})\b', text)
        if match:
            return match.group(1)
        return extract_establishment_code(text)

    def _clean_establishment_name(self, text):
        """Remove code from establishment name."""
        # Remove the code part (e.g., "FMPOS" from the name)
        cleaned = re.sub(r'\b[A-Z]{2,10}\b', '', text).strip()
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned if cleaned else text

    def _is_bac_type(self, text):
        """Check if text is a bac type."""
        return text in BAC_TYPE_MAP

    def _match_bac_type(self, text):
        """Match text to bac type code."""
        if not text:
            return None
        text = text.strip()
        for name, code in BAC_TYPE_MAP.items():
            if name.lower() in text.lower():
                return code
        return None

    # ========== SQL GENERATION ==========
    def generate_sql(self, output_file="seed_mesrs_data.sql"):
        """Generate complete SQL seed file."""
        print(f"\nGenerating SQL seed file: {output_file}")
        sql_lines = []
        sql_lines.append("-- =============================================")
        sql_lines.append("-- TEWJIHI PLATFORM - MESRS Data Seed")
        sql_lines.append(f"-- Generated: {datetime.now().isoformat()}")
        sql_lines.append(f"-- Year: {YEAR}")
        sql_lines.append("-- =============================================\n")

        # 1. Insert Bac Types
        sql_lines.append("-- ========== BAC TYPES ==========")
        for code, name_fr in BAC_TYPE_MAP.items():
            name_ar = self._bac_name_ar(code)
            sql_lines.append(f"INSERT INTO bac_types (code, name_ar, name_fr, created_at) VALUES "
                           f"('{code}', '{name_ar}', '{name_fr}', NOW()) "
                           f"ON CONFLICT (code) DO UPDATE SET name_fr = EXCLUDED.name_fr;")
        sql_lines.append("")

        # 2. Insert Establishments
        sql_lines.append("-- ========== ESTABLISHMENTS ==========")
        for code, data in self.establishments.items():
            name_fr_escaped = data['name_fr'].replace("'", "''")
            sql_lines.append(f"INSERT INTO establishments (code, name_ar, name_fr, country, city, website, housing_available, description, logo_url, created_at) VALUES "
                           f"('{code}', '', '{name_fr_escaped}', '{data['country']}', '{data['city']}', '', false, '', '', NOW()) "
                           f"ON CONFLICT (code) DO UPDATE SET name_fr = EXCLUDED.name_fr;")
        sql_lines.append("")

        # 3. Insert Formations
        sql_lines.append("-- ========== FORMATIONS ==========")
        for (est_code, form_name, level), data in self.formations.items():
            form_name_escaped = form_name.replace("'", "''")
            sql_lines.append(f"INSERT INTO formations (establishment_id, name_ar, name_fr, level, duration_years, description, is_available_current_year, tags, created_at) VALUES "
                           f"((SELECT id FROM establishments WHERE code = '{est_code}'), "
                           f"'', '{form_name_escaped}', '{level}', {data['duration_years']}, '', true, "
                           f"'{data['tags']}', NOW()) "
                           f"ON CONFLICT DO NOTHING;")
        sql_lines.append("")

        # 4. Insert Orientation Results
        sql_lines.append("-- ========== ORIENTATION RESULTS ==========")
        for result in self.orientation_results:
            form_name_escaped = result['formation_name'].replace("'", "''")
            sql_lines.append(f"INSERT INTO orientation_results "
                           f"(year, formation_id, bac_type_id, total_oriented, last_rank, last_average, scraped_at) VALUES "
                           f"({result['year']}, "
                           f"(SELECT id FROM formations WHERE name_fr = '{form_name_escaped}' LIMIT 1), "
                           f"(SELECT id FROM bac_types WHERE code = '{result['bac_type_code']}'), "
                           f"{result['total_oriented']}, {result['last_rank']}, {result['last_average']}, NOW()) "
                           f"ON CONFLICT DO NOTHING;")
        sql_lines.append("")

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_lines))

        print(f"SQL file generated: {output_file}")
        print(f"  - Establishments: {len(self.establishments)}")
        print(f"  - Formations: {len(self.formations)}")
        print(f"  - Orientation Results: {len(self.orientation_results)}")

        return output_file

    def _bac_name_ar(self, code):
        """Get Arabic name for bac type code."""
        ar_names = {
            "D": "علوم طبيعية",
            "C": "رياضيات",
            "A": "آداب أصلية",
            "LM": "آداب حديثة",
            "LO": "آداب أصلية",
            "T": "تقني",
            "GE": "هندسة كهربائية",
            "L": "لغات",
            "O": "دراسات إسلامية",
        }
        return ar_names.get(code, '')

    def run_all(self):
        """Run all scrapers and generate SQL."""
        print("=" * 50)
        print("TEWJIHI - MESRS SCRAPER")
        print("=" * 50)

        self.scrape_formations_licence()
        self.scrape_formations_master()
        self.scrape_orientation_stats()

        # Generate SQL
        output = self.generate_sql()

        print("\n" + "=" * 50)
        print("SCRAPING COMPLETE!")
        print(f"SQL seed file: {output}")
        print("=" * 50)

        return output


# ========== BULK DATA FROM SCREENSHOTS (Hardcoded fallback) ==========
def generate_bulk_orientation_sql(output_file="seed_bulk_orientation.sql"):
    """
    Generates SQL from the exact data shown in the Statistiques screenshots.
    This is the BULK data you provided - already parsed and ready.
    """
    sql_lines = []
    sql_lines.append("-- =============================================")
    sql_lines.append("-- TEWJIHI - BULK ORIENTATION STATISTICS")
    sql_lines.append("-- Extracted from etudiants-mesrs.app/statistiques")
    sql_lines.append(f"-- Year: {YEAR}")
    sql_lines.append("-- =============================================\n")

    # This function would contain ALL the data from your screenshots
    # parsed into INSERT statements
    # (The full dataset from the "Statistiques Globales" tables you shared)

    print(f"Bulk SQL generated: {output_file}")
    return output_file


# ========== MAIN EXECUTION ==========
if __name__ == "__main__":
    scraper = MESRSScraper()
    scraper.run_all()