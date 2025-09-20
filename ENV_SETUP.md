# Configuração de Variáveis de Ambiente

Este projeto utiliza variáveis de ambiente para configurações sensíveis. Siga os passos abaixo para configurar seu ambiente.

## 1. Criar o arquivo .env

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```bash
# =============================================================================
# CONFIGURAÇÕES DE BANCO DE DADOS
# =============================================================================
# URL completa de conexão com o banco PostgreSQL
# Formato: postgresql://usuario:senha@host:porta/nome_do_banco
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/your_database

# =============================================================================
# CONFIGURAÇÕES DE AUTENTICAÇÃO JWT
# =============================================================================
# Chave secreta para assinar e verificar tokens JWT
# IMPORTANTE: Use uma chave forte e única em produção
JWT_SECRET_KEY=your_super_secret_jwt_key_here

# =============================================================================
# CONFIGURAÇÕES DE EMAIL SMTP
# =============================================================================
# Email remetente para envio de mensagens
SMTP_SENDER_EMAIL=your_email@gmail.com

# Senha de aplicativo do Gmail (não a senha normal da conta)
SMTP_SENDER_PASSWORD=your_gmail_app_password_here

# Email destinatário padrão
SMTP_RECIPIENT_EMAIL=recipient@example.com

# Servidor SMTP
SMTP_SERVER=smtp.gmail.com

# Porta SMTP (587 para TLS, 465 para SSL)
SMTP_PORT=587

# =============================================================================
# CONFIGURAÇÕES DE OAUTH2 GOOGLE
# =============================================================================
# ID do cliente OAuth2 do Google Cloud Console
GOOGLE_CLIENT_ID=your-client-id.googleusercontent.com

# Chave secreta do cliente OAuth2 do Google Cloud Console
GOOGLE_CLIENT_SECRET=your-client-secret

# URI de redirecionamento OAuth2
GOOGLE_REDIRECT_URI=urn:ietf:wg:oauth:2.0:oob

# Escopos necessários para Gmail API
GOOGLE_SCOPES=https://www.googleapis.com/auth/gmail.send

# =============================================================================
# CONFIGURAÇÕES DE AMBIENTE
# =============================================================================
# Ambiente atual (development, staging, production)
ENVIRONMENT=development

# Debug mode (true/false)
DEBUG=true

# =============================================================================
# CONFIGURAÇÕES DE CORS
# =============================================================================
# URLs permitidas para CORS (separadas por vírgula)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

## 2. Personalizar as Configurações

### Banco de Dados
- Atualize `DATABASE_URL` com as credenciais do seu banco PostgreSQL
- Certifique-se de que o banco está rodando e acessível

### JWT
- **IMPORTANTE**: Altere `JWT_SECRET_KEY` para uma chave secreta forte e única
- Em produção, use uma chave gerada aleatoriamente com pelo menos 32 caracteres

### Email SMTP
- Atualize `SMTP_SENDER_EMAIL` com o email que enviará as mensagens
- Configure `SMTP_SENDER_PASSWORD` com a senha de aplicativo do Gmail
- Atualize `SMTP_RECIPIENT_EMAIL` com o email destinatário padrão

### OAuth2 Google (Opcional)
- Configure no Google Cloud Console
- Atualize `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET`

### CORS
- Adicione as URLs do seu frontend em `CORS_ORIGINS`
- Separe múltiplas URLs com vírgula

## 3. Instalar Dependências

```bash
uv sync
```

## 4. Verificar Configuração

O arquivo `src/settings.py` carrega automaticamente as variáveis de ambiente e valida as configurações obrigatórias em produção.

## Segurança

- ✅ O arquivo `.env` está no `.gitignore` e não será commitado
- ✅ Use valores diferentes para cada ambiente (desenvolvimento, produção)
- ✅ Em produção, use variáveis de ambiente do sistema ou serviços de gerenciamento de segredos
- ✅ Nunca commite credenciais reais no código

## Troubleshooting

Se você encontrar erros relacionados a variáveis de ambiente:

1. Verifique se o arquivo `.env` existe na raiz do projeto
2. Confirme que as variáveis estão com os nomes corretos
3. Certifique-se de que não há espaços extras nos valores
4. Reinicie o servidor após alterar o arquivo `.env`
