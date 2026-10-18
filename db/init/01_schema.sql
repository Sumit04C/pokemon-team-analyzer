-- Reference data
CREATE TABLE generations (id INT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE types       (id INT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE games (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  generation_id INT REFERENCES generations(id)
);
CREATE TABLE pokemon (
  id INT PRIMARY KEY,            -- national dex number
  name TEXT NOT NULL
);
CREATE TABLE pokemon_types (
  pokemon_id INT REFERENCES pokemon(id),
  type_id INT REFERENCES types(id),
  slot INT,
  PRIMARY KEY (pokemon_id, type_id)
);

-- User data
CREATE TABLE playthroughs (
  id SERIAL PRIMARY KEY,
  player_name TEXT NOT NULL,
  game_id INT REFERENCES games(id),
  completed_on DATE,
  notes TEXT
);
CREATE TABLE team_members (
  playthrough_id INT REFERENCES playthroughs(id) ON DELETE CASCADE,
  slot INT CHECK (slot BETWEEN 1 AND 6),
  pokemon_id INT REFERENCES pokemon(id),
  nickname TEXT,
  level INT,
  PRIMARY KEY (playthrough_id, slot)
);