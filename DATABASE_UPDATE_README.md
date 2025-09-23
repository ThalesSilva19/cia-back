# 📊 Atualização do Banco de Dados

Este diretório contém scripts SQL para atualizar sua base de dados com as duas últimas revisões do Alembic.

## 📁 Arquivos Disponíveis

### 1. `update_database.sql` - Script Completo
- **Descrição**: Script detalhado com todas as operações das duas últimas revisões
- **Uso**: Para atualizações completas e detalhadas
- **Revisões incluídas**:
  - `d7b45543f0a9` - create password reset token table
  - `94c0b7e4794a` - add password reset token table

### 2. `update_database_simple.sql` - Script Simplificado
- **Descrição**: Script simplificado com apenas os comandos essenciais
- **Uso**: Para atualizações rápidas e seguras
- **Vantagem**: Usa `IF NOT EXISTS` para evitar erros se já executado

### 3. `verify_database.sql` - Script de Verificação
- **Descrição**: Verifica se as atualizações foram aplicadas corretamente
- **Uso**: Execute após aplicar as atualizações para confirmar o sucesso

## 🚀 Como Usar

### Opção 1: Script Simplificado (Recomendado)
```bash
psql -h localhost -U seu_usuario -d sua_database -f update_database_simple.sql
```

### Opção 2: Script Completo
```bash
psql -h localhost -U seu_usuario -d sua_database -f update_database.sql
```

### Verificação
```bash
psql -h localhost -U seu_usuario -d sua_database -f verify_database.sql
```

## 📋 O que é Atualizado

### Tabela `password_reset_token` (NOVA)
```sql
CREATE TABLE password_reset_token (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id),
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    used VARCHAR(10) NOT NULL DEFAULT 'false',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Índices Adicionados
- `ix_password_reset_token_id` - Índice na coluna id
- `ix_password_reset_token_token` - Índice único na coluna token
- `ix_seat_code` - Índice único na coluna code da tabela seat
- `ix_seat_id` - Índice na coluna id da tabela seat
- `ix_user_email` - Índice único na coluna email da tabela user
- `ix_user_id` - Índice na coluna id da tabela user
- `ix_user_phone_number` - Índice na coluna phone_number da tabela user

### Modificações na Tabela `seat`
- Coluna `status` alterada para `VARCHAR(20)`
- Foreign key adicionada para `user_id`

## ⚠️ Importante

1. **Backup**: Sempre faça backup do banco antes de executar os scripts
2. **Teste**: Execute primeiro em ambiente de teste
3. **Verificação**: Use o script de verificação para confirmar o sucesso
4. **Logs**: Verifique os logs do PostgreSQL para possíveis erros

## 🔧 Troubleshooting

### Erro: "relation already exists"
- Use o script `update_database_simple.sql` que tem `IF NOT EXISTS`

### Erro: "permission denied"
- Certifique-se de que o usuário tem permissões adequadas
- Execute como superusuário se necessário

### Erro: "foreign key constraint fails"
- Verifique se a tabela `user` existe e tem dados válidos

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs do PostgreSQL
2. Execute o script de verificação
3. Confirme se todas as tabelas base existem
4. Verifique permissões do usuário do banco
