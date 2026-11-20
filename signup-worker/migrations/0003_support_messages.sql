-- Support page contact form submissions (POST /api/support). The D1 row is
-- the record; forwarded_at marks a successful forward to the Layer5 Cloud
-- form queue, so a NULL means the message can still be replayed.
CREATE TABLE IF NOT EXISTS support_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  subject TEXT NOT NULL,
  message TEXT NOT NULL,
  details TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL,
  source_page TEXT NOT NULL DEFAULT '',
  forwarded_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_support_messages_created ON support_messages (created_at);
