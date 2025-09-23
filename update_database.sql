-- =============================================================================
-- SCRIPT DE ATUALIZAÇÃO DO BANCO DE DADOS
-- Compilado das duas últimas revisões do Alembic
-- =============================================================================
-- Revisão: d7b45543f0a9 - create password reset token table
-- Revisão: 94c0b7e4794a - add password reset token table
-- =============================================================================

-- =============================================================================
-- REVISÃO: d7b45543f0a9 - create password reset token table
-- =============================================================================

-- Alterar coluna status da tabela seat
ALTER TABLE seat ALTER COLUMN status TYPE VARCHAR(20);

-- Alterar colunas de timestamp da tabela seat
ALTER TABLE seat ALTER COLUMN created_at TYPE TIMESTAMP;
ALTER TABLE seat ALTER COLUMN created_at DROP NOT NULL;
ALTER TABLE seat ALTER COLUMN created_at DROP DEFAULT;

ALTER TABLE seat ALTER COLUMN updated_at TYPE TIMESTAMP;
ALTER TABLE seat ALTER COLUMN updated_at DROP NOT NULL;
ALTER TABLE seat ALTER COLUMN updated_at DROP DEFAULT;

-- Remover constraint única antiga e criar índices
DROP CONSTRAINT IF EXISTS seat_code_key;
CREATE UNIQUE INDEX ix_seat_code ON seat (code);
CREATE INDEX ix_seat_id ON seat (id);

-- Adicionar foreign key para user_id na tabela seat
ALTER TABLE seat ADD CONSTRAINT seat_user_id_fkey FOREIGN KEY (user_id) REFERENCES "user" (id);

-- Alterar colunas de timestamp da tabela user
ALTER TABLE "user" ALTER COLUMN created_at TYPE TIMESTAMP;
ALTER TABLE "user" ALTER COLUMN created_at DROP NOT NULL;
ALTER TABLE "user" ALTER COLUMN created_at DROP DEFAULT;

ALTER TABLE "user" ALTER COLUMN updated_at TYPE TIMESTAMP;
ALTER TABLE "user" ALTER COLUMN updated_at DROP NOT NULL;
ALTER TABLE "user" ALTER COLUMN updated_at DROP DEFAULT;

-- Remover constraint única antiga e criar índices na tabela user
DROP CONSTRAINT IF EXISTS user_email_key;
CREATE UNIQUE INDEX ix_user_email ON "user" (email);
CREATE INDEX ix_user_id ON "user" (id);
CREATE INDEX ix_user_phone_number ON "user" (phone_number);

-- =============================================================================
-- REVISÃO: 94c0b7e4794a - add password reset token table
-- =============================================================================

-- Criar tabela password_reset_token
CREATE TABLE password_reset_token (
    id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used VARCHAR(10) NOT NULL,
    created_at TIMESTAMP,
    CONSTRAINT password_reset_token_pkey PRIMARY KEY (id),
    CONSTRAINT password_reset_token_user_id_fkey FOREIGN KEY (user_id) REFERENCES "user" (id)
);

-- Criar índices para a tabela password_reset_token
CREATE INDEX ix_password_reset_token_id ON password_reset_token (id);
CREATE UNIQUE INDEX ix_password_reset_token_token ON password_reset_token (token);

-- =============================================================================
-- VERIFICAÇÕES PÓS-EXECUÇÃO
-- =============================================================================

-- Verificar se as tabelas foram criadas/modificadas corretamente
SELECT 'Verificando tabela password_reset_token...' as status;
SELECT COUNT(*) as total_tables FROM information_schema.tables WHERE table_name = 'password_reset_token';

SELECT 'Verificando índices da tabela seat...' as status;
SELECT indexname FROM pg_indexes WHERE tablename = 'seat' AND indexname LIKE 'ix_seat_%';

SELECT 'Verificando índices da tabela user...' as status;
SELECT indexname FROM pg_indexes WHERE tablename = 'user' AND indexname LIKE 'ix_user_%';

SELECT 'Verificando índices da tabela password_reset_token...' as status;
SELECT indexname FROM pg_indexes WHERE tablename = 'password_reset_token' AND indexname LIKE 'ix_password_reset_token_%';

-- =============================================================================
-- FIM DO SCRIPT
-- =============================================================================
SELECT 'Script de atualização executado com sucesso!' as status;
