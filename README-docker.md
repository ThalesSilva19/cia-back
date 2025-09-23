# Docker PostgreSQL Setup

## Configuração do Banco de Dados

Este projeto utiliza Docker para executar um banco de dados PostgreSQL localmente.

### Informações de Conexão

- **Host**: localhost
- **Porta**: 5433 (evita conflito com PostgreSQL local na porta 5432)
- **Database**: cia_db
- **Usuário**: cia_user
- **Senha**: cia_password

### Comandos Úteis

#### Iniciar o banco de dados
```bash
docker-compose up -d
```

#### Parar o banco de dados
```bash
docker-compose down
```

#### Ver logs do container
```bash
docker-compose logs postgres
```

#### Conectar ao banco via psql
```bash
docker exec -it cia_postgres psql -U cia_user -d cia_db
```

#### Conectar via cliente externo
```bash
# Método 1: Usando variável de ambiente para senha
PGPASSWORD=cia_password psql -h localhost -p 5433 -U cia_user -d cia_db

# Método 2: psql pedirá a senha interativamente
psql -h localhost -p 5433 -U cia_user -d cia_db
# Digite a senha quando solicitado: cia_password
```

### Estrutura dos Arquivos

- `docker-compose.yaml`: Configuração do container PostgreSQL
- `init.sql`: Script de inicialização (opcional)
- `README-docker.md`: Este arquivo de documentação

### Notas Importantes

1. O PostgreSQL está configurado para usar a porta 5433 para evitar conflito com qualquer instalação local do PostgreSQL
2. Os dados são persistidos em um volume Docker chamado `cia-app-back_postgres_data`
3. O script `init.sql` é executado automaticamente na primeira inicialização do container
4. A rede Docker `cia_network` é criada automaticamente para isolamento

### Solução de Problemas

#### Erro "cia_user failed password"
Se você receber este erro, significa que há um problema de autenticação. Para resolver:

1. **Verifique se está usando a senha correta**: `cia_password`
2. **Use a variável de ambiente para senha**:
   ```bash
   PGPASSWORD=cia_password psql -h localhost -p 5433 -U cia_user -d cia_db
   ```
3. **Se o problema persistir, recrie o container**:
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

#### Conflito de porta
Se houver conflito de porta, verifique se há outro serviço usando a porta 5433:
```bash
ss -tulpn | grep :5433
```

#### Limpar completamente os dados
Para limpar completamente os dados e recriar o banco:
```bash
docker-compose down -v
docker-compose up -d
```
