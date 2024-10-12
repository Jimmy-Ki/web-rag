-- database: ./test.db

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    uuid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status INT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS chunks (
    uuid TEXT PRIMARY KEY,
    data BLOB NOT NULL,
    vector BLOB NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status INT NOT NULL DEFAULT 0,
    father_uuid TEXT,
    FOREIGN KEY (father_uuid) REFERENCES dirs(uuid)
);

CREATE TABLE IF NOT EXISTS files (
    uuid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    uploader TEXT NOT NULL,
    FOREIGN KEY (uploader) REFERENCES users(uuid)
);

CREATE TABLE IF NOT EXISTS groups (
    uuid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    owner TEXT NOT NULL,
    FOREIGN KEY (owner) REFERENCES users(uuid)
);

CREATE TABLE IF NOT EXISTS dirs (
    uuid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    owner TEXT NOT NULL,
    groupowner TEXT NOT NULL,
    status INT NOT NULL DEFAULT 0,
    FOREIGN KEY (owner) REFERENCES users(uuid),
    FOREIGN KEY (groupowner) REFERENCES groups(uuid)
);

CREATE TABLE IF NOT EXISTS apikeys (
    uuid TEXT PRIMARY KEY,
    key TEXT NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    owner TEXT NOT NULL,
    status INT NOT NULL DEFAULT 0,
    money INT NOT NULL DEFAULT 0,
    FOREIGN KEY (owner) REFERENCES users(uuid)
);