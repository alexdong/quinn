  -- Users table
  CREATE TABLE users (
      id TEXT PRIMARY KEY,
      created_at INTEGER NOT NULL,  -- Unix timestamp
      updated_at INTEGER NOT NULL,  -- Unix timestamp
      name TEXT,
      email_addresses TEXT NOT NULL,  -- JSON array
      settings TEXT  -- JSON blob
  );

  -- Conversations table
  CREATE TABLE conversations (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      created_at INTEGER NOT NULL,  -- Unix timestamp
      updated_at INTEGER NOT NULL,  -- Unix timestamp
      title TEXT,
      status TEXT DEFAULT 'active',
      total_cost REAL DEFAULT 0.0,
      message_count INTEGER DEFAULT 0,
      metadata TEXT,  -- JSON blob
      FOREIGN KEY (user_id) REFERENCES users (id)
  );

  -- Messages table (removed timestamp field)
  CREATE TABLE messages (
      id TEXT PRIMARY KEY,
      conversation_id TEXT NOT NULL,
      user_id TEXT NOT NULL,
      created_at INTEGER NOT NULL,      -- Unix timestamp
      last_updated_at INTEGER NOT NULL, -- Unix timestamp
      system_prompt TEXT DEFAULT '',
      user_content TEXT DEFAULT '',
      assistant_content TEXT DEFAULT '',
      metadata TEXT,  -- JSON MessageMetrics
      FOREIGN KEY (conversation_id) REFERENCES conversations (id),
      FOREIGN KEY (user_id) REFERENCES users (id)
  );

  -- Emails table
  CREATE TABLE emails (
      id TEXT PRIMARY KEY,
      conversation_id TEXT NOT NULL,
      created_at INTEGER NOT NULL,
      direction TEXT NOT NULL,
      from_email TEXT NOT NULL,
      to_addrs TEXT NOT NULL,
      cc_addrs TEXT NOT NULL,
      bcc_addrs TEXT NOT NULL,
      subject TEXT,
      text TEXT,
      html TEXT,
      headers TEXT,
      FOREIGN KEY (conversation_id) REFERENCES conversations (id)
  );
  CREATE INDEX idx_emails_conversation_created_at
      ON emails (conversation_id, created_at);
