# Guia de Conexão via Interface Gráfica

## Configurações para DBeaver, pgAdmin, DataGrip, etc.

### ✅ Configurações Corretas:

| Campo | Valor |
|-------|-------|
| **Host/Server** | `localhost` |
| **Port** | `5433` |
| **Database** | `cia_db` |
| **Username** | `cia_user` |
| **Password** | `cia_password` |

### 🔧 Configurações Avançadas:

- **SSL Mode**: `disable` (ou `prefer`)
- **Connection Timeout**: `30` segundos
- **Authentication Method**: `password` (ou deixar padrão)

### 🚨 Problemas Comuns e Soluções:

#### 1. Erro "password authentication failed"
**Causa**: Senha incorreta ou configuração de autenticação
**Solução**: 
- Verifique se a senha é exatamente: `cia_password`
- Certifique-se de que está usando a porta `5433` (não 5432)

#### 2. Erro "connection refused"
**Causa**: Container não está rodando
**Solução**:
```bash
docker-compose up -d
docker ps  # Verificar se está rodando
```

#### 3. Erro "database does not exist"
**Causa**: Nome do banco incorreto
**Solução**: Use exatamente `cia_db`

### 🧪 Teste de Conexão via Terminal:

Antes de usar a interface gráfica, teste via terminal:

```bash
# Teste básico
PGPASSWORD=cia_password psql -h localhost -p 5433 -U cia_user -d cia_db -c "SELECT 'Conexão OK!' as status;"

# Teste com informações detalhadas
PGPASSWORD=cia_password psql -h localhost -p 5433 -U cia_user -d cia_db -c "SELECT current_user, current_database(), version();"
```

### 📋 Checklist de Verificação:

- [ ] Container PostgreSQL está rodando (`docker ps`)
- [ ] Porta 5433 está sendo usada (não 5432)
- [ ] Username: `cia_user` (exato)
- [ ] Password: `cia_password` (exato)
- [ ] Database: `cia_db` (exato)
- [ ] Host: `localhost` ou `127.0.0.1`

### 🔄 Se Ainda Não Funcionar:

1. **Recrie o container**:
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

2. **Verifique os logs**:
   ```bash
   docker-compose logs postgres
   ```

3. **Teste a conexão**:
   ```bash
   PGPASSWORD=cia_password psql -h localhost -p 5433 -U cia_user -d cia_db
   ```

### 💡 Dicas Importantes:

- **NÃO** use a porta 5432 (essa é do PostgreSQL local)
- **SEMPRE** use a porta 5433
- A senha é case-sensitive: `cia_password` (não `CIA_PASSWORD`)
- O username é case-sensitive: `cia_user` (não `CIA_USER`)
