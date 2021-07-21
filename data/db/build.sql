CREATE TABLE IF NOT EXISTS guilds (
    GuildID BIGINT PRIMARY KEY,
    Prefix TEXT DEFAULT '?',
    Currency TEXT CHARACTER SET utf8 DEFAULT '€',
    Lang VARCHAR(2) DEFAULT 'en',
    IsPremium TINYINT(1) DEFAULT 0,
    DisabledCommands TEXT DEFAULT '',
    Failrates TEXT DEFAULT 'beg:10|fish:5|crime:60|rob:40',
    ShopPrices TEXT DEFAULT 'fishing_rod:8000|lock:25000|gun:40000|bomb:2500'
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS userData (
	RowID INT AUTO_INCREMENT PRIMARY KEY,
	GuildID BIGINT,
    UserID BIGINT,
	Cash BIGINT DEFAULT 0,
	Bank BIGINT DEFAULT 0,
	Netto BIGINT DEFAULT 0,
	CurrentJob TEXT DEFAULT 'unemployed',
	Inventory TEXT DEFAULT '',
	Messages INT DEFAULT 0,
	Experience INT DEFAULT 0,
	XpLevel INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS guildWorkPayouts (
    RowID INT AUTO_INCREMENT PRIMARY KEY,
    GuildID BIGINT,
    JobNaam text,
    UnlockLvl TINYINT,
    Loon INT
);

CREATE TABLE IF NOT EXISTS guildPayouts (
    GuildID BIGINT PRIMARY KEY,
    FOREIGN KEY (GuildID) REFERENCES guilds(GuildID),
    Payouts TEXT DEFAULT 'bedel:20,120|fish:80,320|crime:850,3000',
    PayoutsCasino TEXT DEFAULT 'blackjack:0,7000|roulette:0,2000|slots:0,4000|poker:0,3000|coinflip:0,1500|crash:0,2000|higherlower:0,1500|horse:0,3500|russianroulette:0,5000|tictactoe:0,1000'
);

CREATE TABLE IF NOT EXISTS guildCooldows (
    GuildID BIGINT PRIMARY KEY,
    FOREIGN KEY (GuildID) REFERENCES guilds(GuildID),
    Command TEXT,
    Cooldown INT,
    TimesPerCycle TINYINT DEFAULT 1
);

CREATE TABLE IF NOT EXISTS userCooldowns (
    RowID INT AUTO_INCREMENT PRIMARY KEY,
	GuildID BIGINT,
    UserID BIGINT,
    Command TEXT,
    Cooldown TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    TimesPerCycle TINYINT DEFAULT 1
);