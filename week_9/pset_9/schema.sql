CREATE TABLE users (id INTEGER, username TEXT NOT NULL, hash TEXT NOT NULL, cash NUMERIC NOT NULL DEFAULT 10000.00, PRIMARY KEY(id));
CREATE UNIQUE INDEX users_username ON users (username);

CREATE TABLE symbols (id INTEGER, symbol TEXT NOT NULL,  exchange TEXT, exchangeSuffix TEXT, exchangeName TEXT, name TEXT NOT NULL, date TEXT, type TEXT, region TEXT, currency TEXT, isEnabled TEXT NOT NULL, PRIMARY KEY(id));
CREATE UNIQUE INDEX symbols_symbol ON symbols (symbol, name);

CREATE TABLE depo (id INTEGER UNIQUE, user_id INTEGER, symbol TEXT, share INTEGER, PRIMARY KEY(id));
CREATE UNIQUE INDEX depo_id ON depo (id);
CREATE INDEX depo_user_id ON depo (user_id);
CREATE INDEX depo_share ON depo (share);

CREATE TABLE log (id INTEGER UNIQUE, user_id INTEGER, symbol TEXT, share INTEGER, price NUMERIC, operation TEXT, date_time TEXT, PRIMARY KEY(id));
CREATE INDEX log_user_id ON log (user_id);