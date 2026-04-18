-- AfterBuy Database Schema
-- Run this in the Supabase SQL editor to create all required tables.
-- Also create a Storage bucket named "item-images" with public read access.

CREATE TABLE IF NOT EXISTS items (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at      TIMESTAMPTZ DEFAULT now(),
    image_url       TEXT,
    source_type     TEXT DEFAULT 'photo',
    input_text      TEXT,
    brand           TEXT,
    category        TEXT,
    item_type       TEXT,
    title_guess     TEXT,
    color           TEXT,
    condition       TEXT,
    confidence_score FLOAT,
    extracted_metadata_json JSONB
);

CREATE TABLE IF NOT EXISTS market_comps (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    item_id         UUID REFERENCES items(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ DEFAULT now(),
    source          TEXT,
    comp_title      TEXT,
    comp_price      FLOAT,
    currency        TEXT DEFAULT 'USD',
    comp_url        TEXT,
    comp_condition  TEXT,
    comp_image_url  TEXT,
    similarity_score FLOAT,
    raw_json        JSONB
);

CREATE TABLE IF NOT EXISTS valuations (
    id                      UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    item_id                 UUID REFERENCES items(id) ON DELETE CASCADE,
    created_at              TIMESTAMPTZ DEFAULT now(),
    estimated_low           FLOAT,
    estimated_mid           FLOAT,
    estimated_high          FLOAT,
    suggested_listing_price FLOAT,
    confidence              TEXT,
    valuation_reason        TEXT,
    valuation_method        TEXT,
    comp_count              INTEGER
);

CREATE TABLE IF NOT EXISTS generated_listings (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    item_id             UUID REFERENCES items(id) ON DELETE CASCADE,
    created_at          TIMESTAMPTZ DEFAULT now(),
    platform            TEXT DEFAULT 'generic',
    title               TEXT,
    description         TEXT,
    condition_note      TEXT,
    suggested_price     FLOAT,
    attributes_json     JSONB,
    generation_reasoning TEXT
);

CREATE TABLE IF NOT EXISTS listing_publications (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    item_id             UUID REFERENCES items(id) ON DELETE CASCADE,
    created_at          TIMESTAMPTZ DEFAULT now(),
    platform            TEXT,
    publication_status  TEXT,
    external_listing_id TEXT,
    external_listing_url TEXT,
    raw_response_json   JSONB
);
