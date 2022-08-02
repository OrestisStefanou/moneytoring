CREATE TABLE AppUser (
	user_id TEXT PRIMARY KEY,
	username TEXT NOT NULL,
	email TEXT NOT NULL UNIQUE,
	password TEXT NOT NULL UNIQUE
);

CREATE TABLE Requisition (
	id TEXT PRIMARY KEY,
    user_id   TEXT NOT NULL,
    institution_id TEXT NOT NULL,
    institution_name TEXT NOT NULL,
	link TEXT NOT NULL,
	status TEXT NOT NULL,
	max_historical_days INT,
	accepted_at TEXT,
	expires_at TEXT,
    FOREIGN KEY (user_id)
    REFERENCES AppUser (user_id) 
       ON DELETE CASCADE
);

CREATE TABLE BankAccount (
	account_id TEXT PRIMARY KEY,
	requisition_id TEXT NOT NULL,
	name TEXT NOT NULL,
	currency TEXT NOT NULL,
    FOREIGN KEY (requisition_id)
    REFERENCES Requisition (id) 
       ON DELETE CASCADE
);

CREATE TABLE AccountTransaction (
	id TEXT PRIMARY KEY,
	account_id TEXT NOT NULL,
	amount TEXT NOT NULL,
	currency TEXT NOT NULL,
	information TEXT NOT NULL,
	debtor_name TEXT,
	code TEXT NOT NULL,
	created_date TEXT NOT NULL,
	booking_date TEXT,
	booking_day INT,
	booking_month INT,
	booking_year INT,
	category TEXT,
	custom_category TEXT,
    FOREIGN KEY (account_id)
    REFERENCES BankAccount (account_id) 
       ON DELETE CASCADE
);