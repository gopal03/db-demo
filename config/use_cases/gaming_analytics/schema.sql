CREATE TABLE IF NOT EXISTS Players (
    player_id VARCHAR(36) NOT NULL,
    username VARCHAR(100) NOT NULL,
    level_group VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    signup_date TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (player_id)
);

CREATE TABLE IF NOT EXISTS Sessions (
    session_id VARCHAR(36) NOT NULL,
    game_mode VARCHAR(50) NOT NULL,
    server_region VARCHAR(50) NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NULL,
    PRIMARY KEY (session_id)
);

CREATE TABLE IF NOT EXISTS TelemetryEvents (
    event_id VARCHAR(36) NOT NULL,
    player_id VARCHAR(36) NOT NULL,
    session_id VARCHAR(36) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    score BIGINT NOT NULL,
    latency_ms BIGINT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (event_id)
);

CREATE TABLE IF NOT EXISTS PlayerPlayedSession (
    player_id VARCHAR(36) NOT NULL,
    session_id VARCHAR(36) NOT NULL,
    joined_at TIMESTAMPTZ NOT NULL,
    FOREIGN KEY (player_id) REFERENCES Players(player_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES Sessions(session_id) ON DELETE CASCADE,
    PRIMARY KEY (player_id, session_id)
);
