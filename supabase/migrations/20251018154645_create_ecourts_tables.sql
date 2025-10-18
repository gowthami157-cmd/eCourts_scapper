/*
  # eCourts Scraper Database Schema

  1. New Tables
    - `states`
      - `code` (text, primary key) - State code from eCourts
      - `name` (text) - State name
      - `updated_at` (timestamptz) - Last update timestamp
    
    - `districts`
      - `id` (uuid, primary key)
      - `state_code` (text, foreign key) - Reference to states
      - `code` (text) - District code
      - `name` (text) - District name
      - `updated_at` (timestamptz)
    
    - `court_complexes`
      - `id` (uuid, primary key)
      - `state_code` (text) - Reference to states
      - `district_code` (text) - Reference to districts
      - `code` (text) - Court complex code
      - `name` (text) - Court complex name
      - `updated_at` (timestamptz)
    
    - `courts`
      - `id` (uuid, primary key)
      - `state_code` (text)
      - `district_code` (text)
      - `complex_code` (text)
      - `code` (text) - Court code
      - `name` (text) - Court name
      - `updated_at` (timestamptz)
    
    - `search_results`
      - `id` (uuid, primary key)
      - `case_id` (text) - CNR or case identifier
      - `search_type` (text) - CNR or DETAILS
      - `cnr` (text, nullable)
      - `case_details` (jsonb)
      - `found` (boolean)
      - `listed_today` (boolean)
      - `listed_tomorrow` (boolean)
      - `serial_number` (text, nullable)
      - `court_name` (text, nullable)
      - `next_hearing_date` (text, nullable)
      - `case_status` (text, nullable)
      - `full_result` (jsonb)
      - `searched_at` (timestamptz)
    
    - `cause_lists`
      - `id` (uuid, primary key)
      - `state_code` (text)
      - `district_code` (text)
      - `court_complex_code` (text)
      - `court_code` (text, nullable)
      - `date` (text)
      - `total_cases` (integer)
      - `cases` (jsonb)
      - `full_data` (jsonb)
      - `fetched_at` (timestamptz)

  2. Security
    - Enable RLS on all tables
    - Add policies for public read access (data is public court information)
*/

CREATE TABLE IF NOT EXISTS states (
  code text PRIMARY KEY,
  name text NOT NULL,
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS districts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  state_code text NOT NULL REFERENCES states(code) ON DELETE CASCADE,
  code text NOT NULL,
  name text NOT NULL,
  updated_at timestamptz DEFAULT now(),
  UNIQUE(state_code, code)
);

CREATE TABLE IF NOT EXISTS court_complexes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  state_code text NOT NULL,
  district_code text NOT NULL,
  code text NOT NULL,
  name text NOT NULL,
  updated_at timestamptz DEFAULT now(),
  UNIQUE(state_code, district_code, code)
);

CREATE TABLE IF NOT EXISTS courts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  state_code text NOT NULL,
  district_code text NOT NULL,
  complex_code text NOT NULL,
  code text NOT NULL,
  name text NOT NULL,
  updated_at timestamptz DEFAULT now(),
  UNIQUE(state_code, district_code, complex_code, code)
);

CREATE TABLE IF NOT EXISTS search_results (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  case_id text NOT NULL,
  search_type text NOT NULL,
  cnr text,
  case_details jsonb DEFAULT '{}'::jsonb,
  found boolean DEFAULT false,
  listed_today boolean DEFAULT false,
  listed_tomorrow boolean DEFAULT false,
  serial_number text,
  court_name text,
  next_hearing_date text,
  case_status text,
  full_result jsonb DEFAULT '{}'::jsonb,
  searched_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS cause_lists (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  state_code text NOT NULL,
  district_code text NOT NULL,
  court_complex_code text NOT NULL,
  court_code text,
  date text NOT NULL,
  total_cases integer DEFAULT 0,
  cases jsonb DEFAULT '[]'::jsonb,
  full_data jsonb DEFAULT '{}'::jsonb,
  fetched_at timestamptz DEFAULT now()
);

ALTER TABLE states ENABLE ROW LEVEL SECURITY;
ALTER TABLE districts ENABLE ROW LEVEL SECURITY;
ALTER TABLE court_complexes ENABLE ROW LEVEL SECURITY;
ALTER TABLE courts ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE cause_lists ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read access to states"
  ON states FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Public read access to districts"
  ON districts FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Public read access to court complexes"
  ON court_complexes FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Public read access to courts"
  ON courts FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Public read access to search results"
  ON search_results FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Public read access to cause lists"
  ON cause_lists FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE INDEX IF NOT EXISTS idx_districts_state_code ON districts(state_code);
CREATE INDEX IF NOT EXISTS idx_court_complexes_lookup ON court_complexes(state_code, district_code);
CREATE INDEX IF NOT EXISTS idx_courts_lookup ON courts(state_code, district_code, complex_code);
CREATE INDEX IF NOT EXISTS idx_search_results_case_id ON search_results(case_id);
CREATE INDEX IF NOT EXISTS idx_search_results_cnr ON search_results(cnr);
CREATE INDEX IF NOT EXISTS idx_cause_lists_lookup ON cause_lists(state_code, district_code, court_complex_code, date);
