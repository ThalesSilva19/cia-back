-- =============================================================================
-- SCRIPT DE VERIFICAÇÃO DO BANCO DE DADOS
-- Verifica se as atualizações foram aplicadas corretamente
-- =============================================================================

-- Verificar se a tabela password_reset_token existe
SELECT 
    CASE 
        WHEN COUNT(*) > 0 THEN '✅ Tabela password_reset_token existe'
        ELSE '❌ Tabela password_reset_token NÃO existe'
    END as status
FROM information_schema.tables 
WHERE table_name = 'password_reset_token';

-- Verificar estrutura da tabela password_reset_token
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'password_reset_token'
ORDER BY ordinal_position;

-- Verificar índices da tabela password_reset_token
SELECT 
    indexname,
    CASE 
        WHEN indexdef LIKE '%UNIQUE%' THEN '✅ Índice único'
        ELSE '✅ Índice normal'
    END as tipo
FROM pg_indexes 
WHERE tablename = 'password_reset_token' 
AND indexname LIKE 'ix_password_reset_token_%';

-- Verificar índices da tabela seat
SELECT 
    indexname,
    CASE 
        WHEN indexdef LIKE '%UNIQUE%' THEN '✅ Índice único'
        ELSE '✅ Índice normal'
    END as tipo
FROM pg_indexes 
WHERE tablename = 'seat' 
AND indexname LIKE 'ix_seat_%';

-- Verificar índices da tabela user
SELECT 
    indexname,
    CASE 
        WHEN indexdef LIKE '%UNIQUE%' THEN '✅ Índice único'
        ELSE '✅ Índice normal'
    END as tipo
FROM pg_indexes 
WHERE tablename = 'user' 
AND indexname LIKE 'ix_user_%';

-- Verificar foreign keys
SELECT 
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
AND (tc.table_name = 'password_reset_token' OR tc.table_name = 'seat');

-- Verificar tipo da coluna status na tabela seat
SELECT 
    column_name,
    data_type,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'seat' 
AND column_name = 'status';

-- Resumo final
SELECT '=============================================================================' as separador;
SELECT 'VERIFICAÇÃO CONCLUÍDA' as status;
SELECT 'Se todas as verificações acima mostram ✅, o banco está atualizado corretamente!' as mensagem;
SELECT '=============================================================================' as separador;
