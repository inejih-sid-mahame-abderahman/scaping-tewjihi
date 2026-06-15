-- =============================================
-- TEWJIHI PLATFORM - MESRS Data Seed
-- Generated: 2026-06-15T17:35:11.763991
-- Year: 2025
-- =============================================

-- ========== BAC TYPES ==========
INSERT INTO bac_types (code, name_ar, name_fr, created_at) VALUES ('Sciences naturelles', '', 'D', NOW()) ON CONFLICT (code) DO UPDATE SET name_fr = EXCLUDED.name_fr;
INSERT INTO bac_types (code, name_ar, name_fr, created_at) VALUES ('Mathématiques', '', 'C', NOW()) ON CONFLICT (code) DO UPDATE SET name_fr = EXCLUDED.name_fr;
INSERT INTO bac_types (code, name_ar, name_fr, created_at) VALUES ('Lettres originales', '', 'A', NOW()) ON CONFLICT (code) DO UPDATE SET name_fr = EXCLUDED.name_fr;
INSERT INTO bac_types (code, name_ar, name_fr, created_at) VALUES ('Lettres modernes', '', 'LM', NOW()) ON CONFLICT (code) DO UPDATE SET name_fr = EXCLUDED.name_fr;
INSERT INTO bac_types (code, name_ar, name_fr, created_at) VALUES ('Filière technique', '', 'T', NOW()) ON CONFLICT (code) DO UPDATE SET name_fr = EXCLUDED.name_fr;
INSERT INTO bac_types (code, name_ar, name_fr, created_at) VALUES ('Génie électrique', '', 'GE', NOW()) ON CONFLICT (code) DO UPDATE SET name_fr = EXCLUDED.name_fr;
INSERT INTO bac_types (code, name_ar, name_fr, created_at) VALUES ('Langues', '', 'L', NOW()) ON CONFLICT (code) DO UPDATE SET name_fr = EXCLUDED.name_fr;
INSERT INTO bac_types (code, name_ar, name_fr, created_at) VALUES ('Etude Islamique', '', 'O', NOW()) ON CONFLICT (code) DO UPDATE SET name_fr = EXCLUDED.name_fr;

-- ========== ESTABLISHMENTS ==========

-- ========== FORMATIONS ==========

-- ========== ORIENTATION RESULTS ==========
