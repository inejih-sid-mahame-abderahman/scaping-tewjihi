-- =============================================
-- TEWJIHI PLATFORM - MESRS Seed Data
-- Generated: 2026-06-15T17:43:02.942747
-- Year: 2025
-- =============================================

-- ========== BAC TYPES ==========
INSERT INTO bac_types (code, name_ar, name_fr, created_at) VALUES ('D', 'علوم طبيعية', 'Sciences naturelles', NOW()) ON CONFLICT (code) DO NOTHING;
INSERT INTO bac_types (code, name_ar, name_fr, created_at) VALUES ('C', 'رياضيات', 'Mathématiques', NOW()) ON CONFLICT (code) DO NOTHING;
INSERT INTO bac_types (code, name_ar, name_fr, created_at) VALUES ('A', 'آداب أصلية', 'Lettres originales', NOW()) ON CONFLICT (code) DO NOTHING;
INSERT INTO bac_types (code, name_ar, name_fr, created_at) VALUES ('LM', 'آداب حديثة', 'Lettres modernes', NOW()) ON CONFLICT (code) DO NOTHING;
INSERT INTO bac_types (code, name_ar, name_fr, created_at) VALUES ('T', 'تقني', 'Filière technique', NOW()) ON CONFLICT (code) DO NOTHING;
INSERT INTO bac_types (code, name_ar, name_fr, created_at) VALUES ('GE', 'هندسة كهربائية', 'Génie électrique', NOW()) ON CONFLICT (code) DO NOTHING;
INSERT INTO bac_types (code, name_ar, name_fr, created_at) VALUES ('L', 'لغات', 'Langues', NOW()) ON CONFLICT (code) DO NOTHING;

-- ========== ESTABLISHMENTS ==========

-- ========== FORMATIONS (Licence) ==========

-- ========== FORMATIONS (Master) ==========

-- ========== ORIENTATION RESULTS ==========
