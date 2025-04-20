DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS challenges;
DROP TABLE IF EXISTS notices;
DROP TABLE IF EXISTS solves;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  email TEXT,
  comment TEXT,
  nationality TEXT,
  score INTEGER DEFAULT 0,
  ranking INTEGER DEFAULT 0
);

CREATE TABLE challenges (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  category TEXT,
  message TEXT,
  difficulty TEXT,
  score INTEGER,
  flag TEXT
);

CREATE TABLE notices (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  date TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE solves (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  challenge_id INTEGER,
  solved_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES users(id),
  FOREIGN KEY(challenge_id) REFERENCES challenges(id)
);

-- Preloaded Wargames
INSERT INTO challenges (title, category, message, difficulty, score, flag) VALUES
('FM Band Eavesdropper', 'RF Eavesdropping', 'Capture and demodulate an FM signal carrying sensitive audio using SDR.', 'Easy', 100, 'RF{fm_audio_captured}'),
('LoRa Replay Attack', 'IoT Protocols', 'Intercept a LoRaWAN packet and replay it to trigger unauthorized action.', 'Medium', 200, 'RF{lora_replayed}'),
('BLE Sniffer', 'Bluetooth LE', 'Use a BLE sniffer to capture pairing information and identify target device.', 'Easy', 100, 'RF{ble_sniffed}'),
('DVB-S2 Hijack', 'Satellite Signals', 'Find the key vulnerability in an unsecured DVB-S2 command channel.', 'Hard', 300, 'RF{dvb_command_executed}'),
('ADS-B Spoofing', 'Aviation RF', 'Inject a fake aircraft into an ADS-B receiver’s tracking system.', 'Hard', 300, 'RF{adsb_injected}'),
('GSM Intercept', 'Mobile Communications', 'Capture and analyze GSM downlink traffic to recover plaintext.', 'Hard', 300, 'RF{gsm_cleardata_found}'),
('RFID Cloning', 'Physical Access', 'Use SDR to clone a 125kHz RFID badge.', 'Medium', 200, 'RF{rfid_clone_success}'),
('Jamming Detection', 'RF Jamming', 'Identify a narrowband jamming signal in a noisy spectrum.', 'Medium', 200, 'RF{jammer_located}'),
('Signal Deobfuscation', 'Modulation Analysis', 'Analyze a signal and identify its modulation scheme.', 'Easy', 100, 'RF{modulation_identified}'),
('Drone Signal Override', '2.4GHz Hacking', 'Override a drone’s control signal and force a safe landing.', 'Hard', 300, 'RF{drone_captured}');

-- Preloaded accounts (admin / user)
INSERT INTO users (username, password, email, comment, nationality, score, ranking)
VALUES 
('admin', 'pbkdf2:sha256:600000$admin$e86c1d537e5f1e40d3d8b616e594859aaf67f7f44518de3e2a91f35f70f44da2', 'admin@hackers.com', 'Admin account', 'South Korea', 0, 0),
('user', 'pbkdf2:sha256:600000$user$7f3a9a1a1ed2743be2934f1148a92a471d2a6b86bb13a32b4f822d384e008eda', 'user@hackers.com', 'Standard user account', 'United States', 0, 0);