CREATE TABLE IF NOT EXISTS 'contacts'(
    'id' INTEGER PRIMARY KEY NOT NULL,
    'nome' VARCHAR(30) NOT NULL,
    'cognome' VARCHAR(30) NOT NULL,
	'blocked' INT NOT NULL DEFAULT 0,
	CONSTRAINT ChkBlocked CHECK (blocked IN (0, 1))
);