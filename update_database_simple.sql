-- =============================================================================
-- SCRIPT SIMPLES DE ATUALIZAÇÃO DO BANCO DE DADOS
-- Apenas os comandos essenciais das duas últimas revisões
-- =============================================================================

-- Criar tabela password_reset_token
CREATE TABLE IF NOT EXISTS password_reset_token (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id),
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    used VARCHAR(10) NOT NULL DEFAULT 'false',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar índices se não existirem
CREATE INDEX IF NOT EXISTS ix_password_reset_token_id ON password_reset_token (id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_password_reset_token_token ON password_reset_token (token);

-- Ajustar coluna status da tabela seat se necessário
ALTER TABLE seat ALTER COLUMN status TYPE VARCHAR(20);

-- Criar índices na tabela seat se não existirem
CREATE UNIQUE INDEX IF NOT EXISTS ix_seat_code ON seat (code);
CREATE INDEX IF NOT EXISTS ix_seat_id ON seat (id);

-- Criar índices na tabela user se não existirem
CREATE UNIQUE INDEX IF NOT EXISTS ix_user_email ON "user" (email);
CREATE INDEX IF NOT EXISTS ix_user_id ON "user" (id);
CREATE INDEX IF NOT EXISTS ix_user_phone_number ON "user" (phone_number);

-- Adicionar foreign key se não existir
ALTER TABLE seat DROP CONSTRAINT IF EXISTS seat_user_id_fkey;
ALTER TABLE seat ADD CONSTRAINT seat_user_id_fkey FOREIGN KEY (user_id) REFERENCES "user" (id);

SELECT 'Atualização concluída com sucesso!' as status;
