# 🚀 GUIA DE DEPLOY - STREAMLIT CLOUD

## 📋 Configuração Completa Passo a Passo

### PARTE 1: Google Cloud Console

#### 1️⃣ Criar Projeto no Google Cloud

1. Acesse: https://console.cloud.google.com/
2. Clique em **"Select a project"** (topo da página)
3. Clique em **"NEW PROJECT"**
4. Nome do projeto: `produttivo-cookie-generator`
5. Clique em **"CREATE"**

---

#### 2️⃣ Habilitar APIs Necessárias

1. No menu lateral, vá em **"APIs & Services"** > **"Library"**
2. Procure e habilite as seguintes APIs:
   - **Google Drive API** (clique em "ENABLE")
   - Aguarde alguns segundos para ativar

---

#### 3️⃣ Criar Credenciais OAuth 2.0

1. Vá em **"APIs & Services"** > **"Credentials"**
2. Clique em **"+ CREATE CREDENTIALS"**
3. Selecione **"OAuth client ID"**

**Se aparecer aviso "OAuth consent screen required":**

4. Clique em **"CONFIGURE CONSENT SCREEN"**
5. Selecione **"External"** (para qualquer conta Google)
6. Clique em **"CREATE"**
7. Preencha:
   - **App name:** `Produttivo Cookie Generator`
   - **User support email:** seu email
   - **Developer contact:** seu email
8. Clique em **"SAVE AND CONTINUE"** até o final
9. Clique em **"BACK TO DASHBOARD"**

**Agora crie as credenciais:**

10. Volte em **"Credentials"**
11. Clique em **"+ CREATE CREDENTIALS"** > **"OAuth client ID"**
12. Application type: **"Desktop app"**
13. Name: `Produttivo Desktop Client`
14. Clique em **"CREATE"**

**IMPORTANTE - Anote os valores:**

```
Client ID: xxxxxxxxx.apps.googleusercontent.com
Client Secret: xxxxxxxxxxxxxxxxx
```

⚠️ **GUARDE ESTES VALORES!** Você vai precisar deles no Streamlit Cloud.

---

### PARTE 2: GitHub

#### 1️⃣ Estrutura do Repositório

Seu repositório deve ter:

```
produttivo-app/
├── streamlit_colab_final.py    # App principal
├── login_cookie.ipynb           # Notebook para Colab
├── requirements.txt             # Dependências
└── README.md                    # Documentação
```

#### 2️⃣ Upload dos Arquivos

1. Faça upload dos arquivos que criei para você:
   - `streamlit_colab_final.py`
   - `login_cookie.ipynb`
   - `requirements_cloud.txt` (renomeie para `requirements.txt`)

2. Commit e push:

```bash
git add .
git commit -m "Add Streamlit app with Colab integration"
git push origin main
```

---

### PARTE 3: Streamlit Cloud

#### 1️⃣ Deploy do App

1. Acesse: https://share.streamlit.io/
2. Faça login com GitHub
3. Clique em **"New app"**
4. Selecione:
   - **Repository:** `ricardoarfr/produttivo-app`
   - **Branch:** `main`
   - **Main file path:** `streamlit_colab_final.py`
5. Clique em **"Advanced settings..."**

---

#### 2️⃣ Configurar Secrets

Na seção **"Secrets"**, cole este conteúdo:

```toml
# Google OAuth Credentials
GOOGLE_CLIENT_ID = "SEU_CLIENT_ID_AQUI.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "SEU_CLIENT_SECRET_AQUI"

# Credenciais Produttivo (opcional - pode preencher na interface)
PRODUTTIVO_EMAIL = "financeiro@rfsolucoestelecom.com.br"
PRODUTTIVO_SENHA = "Novo*789"
```

**SUBSTITUA:**
- `SEU_CLIENT_ID_AQUI` → Client ID do Google Cloud
- `SEU_CLIENT_SECRET_AQUI` → Client Secret do Google Cloud

---

#### 3️⃣ Deploy

1. Clique em **"Deploy!"**
2. Aguarde 2-3 minutos
3. Seu app estará online! 🎉

---

### PARTE 4: Configurar OAuth Redirect

⚠️ **IMPORTANTE:** Após o deploy, você precisa adicionar a URL do Streamlit nas configurações OAuth:

#### Passos:

1. Copie a URL do seu app (ex: `https://seu-app.streamlit.app`)
2. Volte no **Google Cloud Console**
3. Vá em **"APIs & Services"** > **"Credentials"**
4. Clique no **OAuth 2.0 Client ID** que você criou
5. Em **"Authorized redirect URIs"**, clique em **"+ ADD URI"**
6. Adicione: `http://localhost` (para testes locais)
7. Clique em **"SAVE"**

---

### PARTE 5: Testar o App

1. Acesse a URL do seu app no Streamlit Cloud
2. Preencha email e senha do Produttivo
3. Clique em **"GERAR COOKIE"**
4. Na primeira vez, você será redirecionado para autenticação Google
5. Aceite as permissões
6. Um notebook será criado no seu Google Drive
7. Abra o link do Colab que aparece
8. Execute o notebook (Runtime > Run all)
9. Copie o cookie que aparece! 🍪

---

## 🐛 Troubleshooting

### Erro: "Redirect URI mismatch"

**Solução:** Adicione a URL do Streamlit Cloud nas **Authorized redirect URIs** do Google Cloud Console.

---

### Erro: "Invalid client"

**Solução:** Verifique se copiou corretamente o Client ID e Client Secret nos Secrets do Streamlit.

---

### Notebook não executa automaticamente

**Isso é esperado!** A API do Google Colab não permite execução automática por questões de segurança. Você precisa:

1. Abrir o link do notebook
2. Clicar em "Runtime" > "Run all"
3. Aguardar execução
4. Copiar o cookie

---

## 📝 Resumo dos Secrets

No Streamlit Cloud, você precisa configurar:

```toml
GOOGLE_CLIENT_ID = "..."           # Do Google Cloud Console
GOOGLE_CLIENT_SECRET = "..."       # Do Google Cloud Console
PRODUTTIVO_EMAIL = "..."           # Email do Produttivo
PRODUTTIVO_SENHA = "..."           # Senha do Produttivo
```

---

## ✅ Checklist Final

Antes de testar, confirme:

- [ ] Projeto criado no Google Cloud
- [ ] Google Drive API habilitada
- [ ] OAuth 2.0 Client criado (Desktop app)
- [ ] Client ID e Secret anotados
- [ ] Arquivos enviados para GitHub
- [ ] App deployado no Streamlit Cloud
- [ ] Secrets configurados no Streamlit
- [ ] OAuth Redirect URI configurada (se necessário)

---

**Pronto! Seu app está online e funcionando! 🎉**

Em caso de dúvidas, consulte a documentação ou abra uma issue no GitHub.
