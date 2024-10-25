CREATE TABLE IF NOT EXISTS tokens(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    refresh_token TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

CREATE OR REPLACE FUNCTION save_refresh_token(p_user_id UUID,
p_refresh_token TEXT, p_expires_at TIMESTAMP)
RETURNS VOID AS $$
BEGIN
  INSERT INTO tokens(user_id, refresh_token, expires_at)
  VALUES (p_user_id, p_refresh_token, p_expires_at);
END;
$$ LANGUAGE plpgsql;

