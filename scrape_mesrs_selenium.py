"""
TEWJIHI PLATFORM - MESRS Scraper (Selenium)
Target: https://etudiants-mesrs.app
Renders JavaScript then extracts all data
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from datetime import datetime

BASE_URL = "https://etudiants-mesrs.app"
YEAR = 2025

# ========== BAC TYPE MAPPING ==========
BAC_TYPE_MAP = {
    "Sciences naturelles": "D",
    "Mathématiques": "C",
    "Lettres originales": "A",
    "Lettres modernes": "LM",
    "Filière technique": "T",
    "Génie électrique": "GE",
    "Langues": "L",
}

BAC_TYPE_AR = {
    "D": "علوم طبيعية", "C": "رياضيات", "A": "آداب أصلية",
    "LM": "آداب حديثة", "T": "تقني", "GE": "هندسة كهربائية", "L": "لغات",
}

ESTABLISHMENT_CODE_MAP = {
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

FLAG_COUNTRY = {
    "🇲🇷": "MR", "🇲🇦": "MA", "🇹🇳": "TN",
    "🇩🇿": "DZ", "🇸🇳": "SN", "🇪🇬": "EG",
}


class MESRSScraper:
    def __init__(self):
        print("Launching browser...")
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)

        self.establishments = {}
        self.formations_licence = []
        self.formations_master = []
        self.orientation_results = []

    def fetch_page(self, url, wait_for_table=True):
        """Load page and return BeautifulSoup after JS render."""
        print(f"  Loading: {url}")
        self.driver.get(url)
        time.sleep(3)  # Wait for JS to render

        if wait_for_table:
            try:
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            except:
                print(f"  ⚠️ No table found on {url}")

        # Scroll to bottom to trigger lazy loading
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        html = self.driver.page_source
        return BeautifulSoup(html, 'html.parser')

    def _get_est_code(self, name):
        """Get establishment code from name."""
        for full_name, code in ESTABLISHMENT_CODE_MAP.items():
            if full_name.lower() in name.lower() or name.lower() in full_name.lower():
                return code
        # Try to find uppercase code in text
        import re
        match = re.search(r'\b([A-Z]{2,10})\b', name)
        if match:
            return match.group(1)
        # Generate from initials
        words = name.split()
        return ''.join([w[0] for w in words if w[0].isupper()])[:10]

    def _get_country(self, text):
        """Extract country from flag emoji."""
        for flag, code in FLAG_COUNTRY.items():
            if flag in text:
                return code
        return "MR"

    def scrape_formations_licence(self):
        """Scrape Licence formations."""
        print("\n📋 Scraping LICENCE formations...")
        soup = self.fetch_page(f"{BASE_URL}/offres-formation/licence")

        tables = soup.find_all('table')
        print(f"  Found {len(tables)} tables")

        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    est_text = cols[0].get_text(strip=True)
                    form_text = cols[1].get_text(strip=True)
                    pays_text = cols[2].get_text(strip=True)

                    est_code = self._get_est_code(est_text)
                    country = self._get_country(pays_text)

                    # Clean establishment name (remove code)
                    est_name = est_text
                    if est_code in est_name:
                        est_name = est_name.replace(est_code, '').strip()

                    if est_code not in self.establishments:
                        self.establishments[est_code] = {
                            'code': est_code,
                            'name_fr': est_name or est_text,
                            'country': country,
                        }

                    self.formations_licence.append({
                        'est_code': est_code,
                        'name_fr': form_text,
                        'country': country,
                    })

        print(f"  ✅ {len(self.establishments)} establishments")
        print(f"  ✅ {len(self.formations_licence)} Licence formations")

    def scrape_formations_master(self):
        """Scrape Master formations."""
        print("\n📋 Scraping MASTER formations...")
        soup = self.fetch_page(f"{BASE_URL}/offres-formation/master")

        tables = soup.find_all('table')
        print(f"  Found {len(tables)} tables")

        for table in tables:
            rows = table.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    est_text = cols[0].get_text(strip=True)
                    form_text = cols[1].get_text(strip=True)
                    pays_text = cols[2].get_text(strip=True)

                    est_code = self._get_est_code(est_text)
                    country = self._get_country(pays_text)

                    est_name = est_text
                    if est_code in est_name:
                        est_name = est_name.replace(est_code, '').strip()

                    if est_code not in self.establishments:
                        self.establishments[est_code] = {
                            'code': est_code,
                            'name_fr': est_name or est_text,
                            'country': country,
                        }

                    self.formations_master.append({
                        'est_code': est_code,
                        'name_fr': form_text,
                        'country': country,
                    })

        print(f"  ✅ {len(self.establishments)} total establishments")
        print(f"  ✅ {len(self.formations_master)} Master formations")

    def scrape_orientation_stats(self):
        """Scrape Statistiques des orientations."""
        print("\n📊 Scraping orientation statistics...")
        soup = self.fetch_page(f"{BASE_URL}/statistiques")

        tables = soup.find_all('table')
        print(f"  Found {len(tables)} tables")

        current_formation = None

        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 5:
                    col1 = cols[0].get_text(strip=True)
                    col2 = cols[1].get_text(strip=True)
                    col3 = cols[2].get_text(strip=True)
                    col4 = cols[3].get_text(strip=True)
                    col5 = cols[4].get_text(strip=True)

                    # Check if col1 is a formation name or bac type
                    bac_code = None
                    for name, code in BAC_TYPE_MAP.items():
                        if name.lower() in col1.lower():
                            bac_code = code
                            break
                        if name.lower() in col2.lower():
                            bac_code = code
                            break

                    if not bac_code:
                        # It's a formation name
                        if col1 and len(col1) > 3:
                            current_formation = col1
                        continue

                    if bac_code and current_formation:
                        try:
                            total = int(col3.replace('\xa0', '').replace(' ', '').replace(',', '')) if col3 else 0
                            rank = int(col4.replace('\xa0', '').replace(' ', '').replace(',', '')) if col4 else 0
                            avg = float(col5.replace(',', '.').replace('\xa0', '')) if col5 else 0.0

                            self.orientation_results.append({
                                'formation_name': current_formation,
                                'bac_type_code': bac_code,
                                'total_oriented': total,
                                'last_rank': rank,
                                'last_average': avg,
                                'year': YEAR,
                            })
                        except ValueError as e:
                            pass  # Skip unparseable rows

        print(f"  ✅ {len(self.orientation_results)} orientation result rows")

    def generate_sql(self, output_file="seed_mesrs_data.sql"):
        """Generate SQL seed file."""
        print(f"\n📝 Generating SQL: {output_file}")

        sql = []
        sql.append("-- =============================================")
        sql.append("-- TEWJIHI PLATFORM - MESRS Seed Data")
        sql.append(f"-- Generated: {datetime.now().isoformat()}")
        sql.append(f"-- Year: {YEAR}")
        sql.append("-- =============================================\n")

        # BAC TYPES
        sql.append("-- ========== BAC TYPES ==========")
        for name_fr, code in BAC_TYPE_MAP.items():
            name_ar = BAC_TYPE_AR.get(code, '')
            name_fr_esc = name_fr.replace("'", "''")
            sql.append(f"INSERT INTO bac_types (code, name_ar, name_fr, created_at) VALUES "
                       f"('{code}', '{name_ar}', '{name_fr_esc}', NOW()) "
                       f"ON CONFLICT (code) DO NOTHING;")
        sql.append("")

        # ESTABLISHMENTS
        sql.append("-- ========== ESTABLISHMENTS ==========")
        for code, data in self.establishments.items():
            name_esc = data['name_fr'].replace("'", "''")
            country = data.get('country', 'MR')
            sql.append(f"INSERT INTO establishments (code, name_ar, name_fr, country, city, website, housing_available, description, logo_url, created_at) VALUES "
                       f"('{code}', '', '{name_esc}', '{country}', '', '', false, '', '', NOW()) "
                       f"ON CONFLICT (code) DO NOTHING;")
        sql.append("")

        # FORMATIONS - LICENCE
        sql.append("-- ========== FORMATIONS (Licence) ==========")
        for f in self.formations_licence:
            name_esc = f['name_fr'].replace("'", "''")
            sql.append(f"INSERT INTO formations (establishment_id, name_ar, name_fr, level, duration_years, description, is_available_current_year, tags, created_at) VALUES "
                       f"((SELECT id FROM establishments WHERE code = '{f['est_code']}'), "
                       f"'', '{name_esc}', 'LICENCE', 3, '', true, '[]', NOW()) "
                       f"ON CONFLICT DO NOTHING;")
        sql.append("")

        # FORMATIONS - MASTER
        sql.append("-- ========== FORMATIONS (Master) ==========")
        for f in self.formations_master:
            name_esc = f['name_fr'].replace("'", "''")
            sql.append(f"INSERT INTO formations (establishment_id, name_ar, name_fr, level, duration_years, description, is_available_current_year, tags, created_at) VALUES "
                       f"((SELECT id FROM establishments WHERE code = '{f['est_code']}'), "
                       f"'', '{name_esc}', 'MASTER', 2, '', true, '[]', NOW()) "
                       f"ON CONFLICT DO NOTHING;")
        sql.append("")

        # ORIENTATION RESULTS
        sql.append("-- ========== ORIENTATION RESULTS ==========")
        for r in self.orientation_results:
            name_esc = r['formation_name'].replace("'", "''")
            sql.append(f"INSERT INTO orientation_results "
                       f"(year, formation_id, bac_type_id, total_oriented, last_rank, last_average, scraped_at) VALUES "
                       f"({r['year']}, "
                       f"(SELECT id FROM formations WHERE name_fr = '{name_esc}' LIMIT 1), "
                       f"(SELECT id FROM bac_types WHERE code = '{r['bac_type_code']}'), "
                       f"{r['total_oriented']}, {r['last_rank']}, {r['last_average']}, NOW()) "
                       f"ON CONFLICT DO NOTHING;")
        sql.append("")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql))

        print(f"\n✅ SQL file saved: {output_file}")
        print(f"   Bac Types: {len(BAC_TYPE_MAP)}")
        print(f"   Establishments: {len(self.establishments)}")
        print(f"   Formations Licence: {len(self.formations_licence)}")
        print(f"   Formations Master: {len(self.formations_master)}")
        print(f"   Orientation Results: {len(self.orientation_results)}")

    def close(self):
        self.driver.quit()

    def run_all(self):
        print("=" * 60)
        print("🔍 TEWJIHI - MESRS SCRAPER (Selenium)")
        print("=" * 60)

        self.scrape_formations_licence()
        self.scrape_formations_master()
        self.scrape_orientation_stats()

        self.generate_sql()
        self.close()

        print("\n" + "=" * 60)
        print("🎉 DONE! Import with:")
        print("   psql -U your_user -d tewjihi -f seed_mesrs_data.sql")
        print("=" * 60)


if __name__ == "__main__":
    scraper = MESRSScraper()
    scraper.run_all()