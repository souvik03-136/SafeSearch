CREATE TABLE IF NOT EXISTS crimes (
    id SERIAL PRIMARY KEY,
    record_id INT,
    agency_code TEXT,
    agency_name TEXT,
    agency_type TEXT,
    city TEXT,
    state TEXT,
    year INT,
    month TEXT,
    incident INT,
    crime_type TEXT,
    crime_solved BOOLEAN,
    victim_sex TEXT,
    victim_age INT,
    victim_race TEXT,
    victim_ethnicity TEXT,
    perpetrator_sex TEXT,
    perpetrator_age INT,
    perpetrator_race TEXT,
    perpetrator_ethnicity TEXT,
    relationship TEXT,
    weapon TEXT,
    victim_count INT,
    perpetrator_count INT,
    record_source TEXT
);


