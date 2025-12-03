-- ================================
-- TABLE: districts
-- ================================
CREATE TABLE IF NOT EXISTS districts (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- ================================
-- TABLE: our_stations
-- ================================
CREATE TABLE IF NOT EXISTS our_stations (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    district_id INT REFERENCES districts(id),
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION
);

-- ================================
-- TABLE: competitor_stations
-- ================================
CREATE TABLE IF NOT EXISTS competitor_stations (
    id SERIAL PRIMARY KEY,
    station_name TEXT NOT NULL,
    brand TEXT,
    address TEXT,
    district_id INT REFERENCES districts(id),
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION
);

-- ================================
-- TABLE: fuel_prices (временной ряд)
-- ================================
CREATE TABLE IF NOT EXISTS fuel_prices (
    id SERIAL PRIMARY KEY,
    station_id INT REFERENCES competitor_stations(id),
    fuel_type TEXT NOT NULL,
    price NUMERIC(10,2),
    timestamp TIMESTAMP NOT NULL
);
