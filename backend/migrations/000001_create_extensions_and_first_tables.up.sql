CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS assistant (
    assistant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    config JSON NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
    public BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS thread (
    thread_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assistant_id UUID REFERENCES assistant(assistant_id) ON DELETE SET NULL,
    user_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
);

CREATE TABLE IF NOT EXISTS checkpoints (
    thread_id TEXT PRIMARY KEY,
    checkpoint BYTEA
);

CREATE TABLE IF NOT EXISTS pr_email (
    email_key VARCHAR(255) PRIMARY KEY, -- 使用PR URL作为键
    last_send_date TIMESTAMP WITH TIME ZONE NOT NULL -- 记录最后一次发送邮件的时间
);
