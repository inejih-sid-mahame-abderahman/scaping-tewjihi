"""
TEWJIHI PLATFORM - MESRS Scraper (FIXED)
Correct URLs + Multiple detection strategies
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from datetime import datetime

# ========== CORRECT URLS ==========
BASE_URL = "https://etudiants-mesrs.app"
URLS = {
    "licence_formations": f"{BASE_URL}/license-offers",
    "master_formations": f"{BASE_URL}/master-offers",
    "orientation_stats": f"{BASE_URL}/affectations-stats",
}

YEAR = 2025

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


class MESRSScraper:
    def __init__(self):
        print("🚀 Launching browser...")
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        # REMOVED headless so we can debug

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

        self.establishments = {}
        self.formations = []  # Combined licence + master
        self.orientation_results = []

    def wait_for_content(self, timeout=10):
        """Wait for ANY table or data container to appear."""
        time.sleep(3)  # Initial wait
        try:
            self.wait.until(lambda d: len(d.find_elements(By.TAG_NAME, "table")) > 0 or 
                                      len(d.find_elements(By.CSS_SELECTOR, "[class*='table']")) > 0 or
                                      len(d.find_elements(By.CSS_SELECTOR, "[class*='row']")) > 5)
            return True
        except:
            return False

    def print_debug_info(self, url):
        """Print debug info about current page."""
        print(f"  URL: {url}")
        print(f"  Title: {self.driver.title}")
        
        # Count elements
        tables = self.driver.find_elements(By.TAG_NAME, "table")
        trs = self.driver.find_elements(By.TAG_NAME, "tr")
        divs = self.driver.find_elements(By.TAG_NAME, "div")
        
        print(f"  Tables: {len(tables)}, TRs: {len(trs)}, DIVs: {len(divs)}")
        
        # Print class names of potential data containers
        for elem in self.driver.find_elements(By.CSS_SELECTOR, "[class*='table'], [class*='data'], [class*='card'], [class*='list']"):
            cls = elem.get_attribute("class")
            if cls:
                print(f"  Container class: {cls[:100]}")

    def scrape_licence_formations(self):
        """Scrape from /license-offers"""
        print("\n📋 LICENCE FORMATIONS")
        url = URLS["licence_formations"]
        self.driver.get(url)
        
        if not self.wait_for_content():
            print("  ⚠️ No content loaded in time")
            self.print_debug_info(url)
            self.driver.save_screenshot("debug_licence.png")
            return
        
        self.print_debug_info(url)
        self._extract_formations("LICENCE")

    def scrape_master_formations(self):
        """Scrape from /master-offers"""
        print("\n📋 MASTER FORMATIONS")
        url = URLS["master_formations"]
        self.driver.get(url)
        
        if not self.wait_for_content():
            print("  ⚠️ No content loaded in time")
            self.print_debug_info(url)
            self.driver.save_screenshot("debug_master.png")
            return
        
        self.print_debug_info(url)
        self._extract_formations("MASTER")

    def _extract_formations(self, level):
        """Try multiple strategies to extract formation data from any table."""
        
        # Strategy 1: Look for traditional HTML tables
        tables = self.driver.find_elements(By.TAG_NAME, "table")
        
        for table in tables:
            rows = table.find_elements(By.TAG_NAME, "tr")
            print(f"  Processing table with {len(rows)} rows")
            
            for i, row in enumerate(rows):
                if i == 0:  # Skip header
                    continue
                    
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 2:
                    col_texts = [c.text.strip() for c in cols]
                    
                    # Try to extract: Establishment | Formation | Country
                    est_text = col_texts[0] if len(col_texts) > 0 else ""
                    form_text = col_texts[1] if len(col_texts) > 1 else ""
                    
                    if form_text and len(form_text) > 3:
                        est_code = self._extract_code(est_text)
                        
                        if est_code not in self.establishments:
                            self.establishments[est_code] = {
                                'code': est_code,
                                'name_fr': est_text,
                                'country': 'MR',
                            }
                        
                        self.formations.append({
                            'est_code': est_code,
                            'name_fr': form_text,
                            'level': level,
                        })
        
        # Strategy 2: Look for div-based tables (common in React/Vue apps)
        if not self.formations:
            print("  Trying div-based table detection...")
            rows = self.driver.find_elements(By.CSS_SELECTOR, "[class*='row'], [class*='tr'], [class*='item']")
            print(f"  Found {len(rows)} potential row elements")
            
            for row in rows:
                text = row.text.strip()
                if text and len(text) > 10:
                    # Try to split by newlines or common separators
                    parts = [p.strip() for p in text.split('\n') if p.strip()]
                    if len(parts) >= 2:
                        print(f"  Row text: {' | '.join(parts[:3])}")

    def scrape_orientation_stats(self):
        """Scrape from /affectations-stats"""
        print("\n📊 ORIENTATION STATISTICS")
        url = URLS["orientation_stats"]
        self.driver.get(url)
        
        if not self.wait_for_content():
            print("  ⚠️ No content loaded in time")
            self.print_debug_info(url)
            self.driver.save_screenshot("debug_stats.png")
            return
        
        self.print_debug_info(url)
        
        # Try to extract from tables
        tables = self.driver.find_elements(By.TAG_NAME, "table")
        current_formation = None
        
        for table in tables:
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 5:
                    col_texts = [c.text.strip() for c in cols]
                    
                    # Check if first column is a formation name or bac type
                    col1 = col_texts[0]
                    col2 = col_texts[1] if len(col_texts) > 1 else ""
                    
                    bac_code = None
                    for name, code in BAC_TYPE_MAP.items():
                        if name.lower() in col1.lower() or name.lower() in col2.lower():
                            bac_code = code
                            break
                    
                    if bac_code and current_formation:
                        try:
                            total = int(col_texts[2].replace('\xa0','').replace(' ','').replace(',','')) if len(col_texts) > 2 else 0
                            rank = int(col_texts[3].replace('\xa0','').replace(' ','').replace(',','')) if len(col_texts) > 3 else 0
                            avg = float(col_texts[4].replace(',','.').replace('\xa0','')) if len(col_texts) > 4 else 0.0
                            
                            self.orientation_results.append({
                                'formation_name': current_formation,
                                'bac_type_code': bac_code,
                                'total_oriented': total,
                                'last_rank': rank,
                                'last_average': avg,
                                'year': YEAR,
                            })
                        except ValueError:
                            pass
                    elif col1 and len(col1) > 3 and not bac_code:
                        current_formation = col1

        print(f"  Found {len(self.orientation_results)} statistics rows")

    def _extract_code(self, text):
        """Extract or find establishment code."""
        # Look for ALL CAPS code (2-10 letters)
        match = re.search(r'\b([A-Z]{2,10})\b', text)
        if match:
            return match.group(1)
        # Generate from words
        words = text.split()
        return ''.join([w[0] for w in words if w and w[0].isupper()])[:10]

    def generate_sql(self, output_file="seed_mesrs_fixed.sql"):
        """Generate SQL from scraped data."""
        print(f"\n📝 Writing SQL to {output_file}")
        
        sql = []
        sql.append(f"-- TEWJIHI MESRS Seed Data")
        sql.append(f"-- Generated: {datetime.now().isoformat()}")
        sql.append("")
        
        # Bac Types
        sql.append("-- BAC TYPES")
        for name_fr, code in BAC_TYPE_MAP.items():
            name_ar = BAC_TYPE_AR.get(code, '')
            sql.append(f"INSERT INTO bac_types (code, name_ar, name_fr, created_at) "
                       f"VALUES ('{code}', '{name_ar}', '{name_fr.replace(chr(39), chr(39)+chr(39))}', NOW()) "
                       f"ON CONFLICT (code) DO NOTHING;")
        sql.append("")
        
        # Establishments
        sql.append("-- ESTABLISHMENTS")
        for code, data in self.establishments.items():
            name = data['name_fr'].replace("'", "''")
            sql.append(f"INSERT INTO establishments (code, name_ar, name_fr, country, city, created_at) "
                       f"VALUES ('{code}', '', '{name}', '{data.get('country','MR')}', '', NOW()) "
                       f"ON CONFLICT (code) DO NOTHING;")
        sql.append("")
        
        # Formations
        sql.append("-- FORMATIONS")
        for f in self.formations:
            name = f['name_fr'].replace("'", "''")
            sql.append(f"INSERT INTO formations (establishment_id, name_ar, name_fr, level, duration_years, created_at) "
                       f"VALUES ((SELECT id FROM establishments WHERE code='{f['est_code']}'), "
                       f"'', '{name}', '{f['level']}', {3 if f['level']=='LICENCE' else 2}, NOW()) "
                       f"ON CONFLICT DO NOTHING;")
        sql.append("")
        
        # Orientation Results
        sql.append("-- ORIENTATION RESULTS")
        for r in self.orientation_results:
            name = r['formation_name'].replace("'", "''")
            sql.append(f"INSERT INTO orientation_results "
                       f"(year, formation_id, bac_type_id, total_oriented, last_rank, last_average, scraped_at) "
                       f"VALUES ({r['year']}, "
                       f"(SELECT id FROM formations WHERE name_fr='{name}' LIMIT 1), "
                       f"(SELECT id FROM bac_types WHERE code='{r['bac_type_code']}'), "
                       f"{r['total_oriented']}, {r['last_rank']}, {r['last_average']}, NOW()) "
                       f"ON CONFLICT DO NOTHING;")
        sql.append("")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql))
        
        print(f"✅ Done: {len(self.establishments)} establishments, "
              f"{len(self.formations)} formations, "
              f"{len(self.orientation_results)} stats")

    def run(self):
        print("=" * 60)
        print("TEWJIHI MESRS SCRAPER")
        print("=" * 60)
        
        self.scrape_licence_formations()
        self.scrape_master_formations()
        self.scrape_orientation_stats()
        
        self.generate_sql()
        
        input("\nPress Enter to close browser...")
        self.driver.quit()


if __name__ == "__main__":
    scraper = MESRSScraper()
    scraper.run()