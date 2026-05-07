CREATE TYPE vehicle_status AS ENUM ('active', 'inactive', 'maintenance');

CREATE TABLE IF NOT EXISTS vehicles (
    id         SERIAL PRIMARY KEY,
    plate      VARCHAR(20)    NOT NULL UNIQUE,
    model      VARCHAR(100)   NOT NULL,
    driver     VARCHAR(100),
    status     vehicle_status NOT NULL DEFAULT 'active',
    created_at TIMESTAMP      NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS positions (
    id          SERIAL PRIMARY KEY,
    vehicle_id  INTEGER          NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    latitude    DOUBLE PRECISION NOT NULL,
    longitude   DOUBLE PRECISION NOT NULL,
    speed_kmh   DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    recorded_at TIMESTAMP        NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fuel_logs (
    id          SERIAL PRIMARY KEY,
    vehicle_id  INTEGER          NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    fuel_level  DOUBLE PRECISION NOT NULL CHECK (fuel_level BETWEEN 0 AND 100),
    fuel_litres DOUBLE PRECISION,
    logged_at   TIMESTAMP        NOT NULL DEFAULT NOW()
);

INSERT INTO vehicles (plate, model, driver, status) VALUES
    ('NRW-1234', 'Mercedes Sprinter',  'Hans Müller',  'active'),
    ('NRW-5678', 'Volkswagen Crafter', 'Ayse Yilmaz',  'active'),
    ('KLE-0042', 'Ford Transit',       NULL,           'maintenance');

INSERT INTO positions (vehicle_id, latitude, longitude, speed_kmh) VALUES
    (1, 51.2217, 6.7762, 95.0),
    (2, 51.5100, 7.4600, 110.0);

INSERT INTO fuel_logs (vehicle_id, fuel_level, fuel_litres) VALUES
    (1, 72.5, 54.0),
    (2, 88.0, 66.0);