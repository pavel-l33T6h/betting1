#/bin/bash

psql -U bets -d bets << EOF
CREATE TYPE outcome AS ENUM ('fst_win', 'snd_win');
CREATE TABLE bets (
    id SERIAL,
    event_id VARCHAR(64) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    outcome outcome NOT NULL,
    UNIQUE(event_id)
);
EOF