# 🍪 Produttivo Cookie Generator

Interface web para geração automática de cookies de autenticação do Produttivo via Google Colab.

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![Google Colab](https://img.shields.io/badge/Colab-F9AB00?style=for-the-badge&logo=googlecolab&color=525252)](https://colab.research.google.com)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

---

## 📋 Índice

- [Sobre](#sobre)
- [Como Funciona](#como-funciona)
- [Demo](#demo)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Deploy no Streamlit Cloud](#deploy-no-streamlit-cloud)
- [Uso](#uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [FAQ](#faq)
- [Troubleshooting](#troubleshooting)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

---

## 🎯 Sobre

Este projeto automatiza a geração de cookies de autenticação do **Produttivo** através de uma interface web moderna construída com Streamlit e integração com Google Colab.

### ✨ Características

- ✅ Interface web intuitiva com Streamlit
- ✅ Autenticação OAuth 2.0 com Google
- ✅ Integração com Google Colab para execução segura
- ✅ Captura automática de cookies de sessão
- ✅ Deploy fácil no Streamlit Cloud
- ✅ Sem necessidade de infraestrutura própria
- ✅ Logs detalhados do processo

---

## 🔄 Como Funciona

```
┌─────────────────┐
│  STREAMLIT      │  1. Usuário preenche credenciais
│  (Interface)    │  2. Clica em "Gerar Cookie"
└────────┬────────┘
         │
         │ 3. Autentica via OAuth
         │
         ▼
┌─────────────────┐
│  GOOGLE DRIVE   │  4. Cria notebook com credenciais
│  API            │     injetadas
└────────┬────────┘
         │
         │ 5. Retorna link do Colab
         │
         ▼
┌─────────────────┐
│  GOOGLE COLAB   │  6. Usuário executa notebook
│  (Execução)     │  7. Playwright faz login
│                 │  8. Captura cookie
└────────┬────────┘
         │
         │ 9. Cookie exibido
         │
         ▼
┌─────────────────┐
│  USUÁRIO        │  10. Copia e usa o cookie
│  (Resultado)    │
└─────────────────┘
```

---

## 🎬 Demo

**Live Demo:** [https://produttivo-cookie-gen.streamlit.app](https://produttivo-cookie-gen.streamlit.app) *(substitua pela sua URL)*

![Screenshot](docs/screenshot.png) *(adicione um screenshot quando possível)*

---

## 📦 Instalação

### Pré-requisitos

- Python 3.8+
- Conta Google (para OAuth)
- Projeto no Google Cloud Console
- Conta no GitHub

### Clone o Repositório

```bash
git clone https://github.com/ricardoarfr/produttivo-app.git
cd produttivo-app
```

### Instale as Dependências

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuração

### 1. Google Cloud Console

Siga o **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)** completo para:

1. Criar projeto no Google Cloud
2. Habilitar Google Drive API
3. Criar credenciais OAuth 2.0
4. Obter Client ID e Client Secret

### 2. Variáveis de Ambiente

Crie um arquivo `.streamlit/secrets.toml`:

```toml
# Google OAuth Credentials
GOOGLE_CLIENT_ID = "seu-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "seu-client-secret"

# Credenciais Produttivo (opcional)
PRODUTTIVO_EMAIL = "seu-email@exemplo.com"
PRODUTTIVO_SENHA = "sua-senha"
```

⚠️ **NUNCA** faça commit deste arquivo! Ele já está no `.gitignore`.

---

## 🚀 Deploy no Streamlit Cloud

### Passo a Passo Rápido:

1. **Fork este repositório** ou faça push para seu GitHub

2. **Acesse** [share.streamlit.io](https://share.streamlit.io)

3. **Configure o deploy:**
   - Repository: `ricardoarfr/produttivo-app`
   - Branch: `main`
   - Main file: `streamlit_colab_final.py`

4. **Adicione os Secrets** (Advanced settings):
   ```toml
   GOOGLE_CLIENT_ID = "..."
   GOOGLE_CLIENT_SECRET = "..."
   PRODUTTIVO_EMAIL = "..."
   PRODUTTIVO_SENHA = "..."
   ```

5. **Deploy!** 🎉

📖 **Guia completo:** Consulte [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md) para instruções detalhadas.

---

## 💻 Uso

### Interface Web

1. Acesse o app (local ou Streamlit Cloud)
2. Preencha email e senha do Produttivo
3. Clique em **"GERAR COOKIE"**
4. Autentique com Google (primeira vez)
5. Abra o link do Colab que aparece
6. Execute o notebook (Runtime > Run all)
7. Copie o cookie gerado! 🍪

### Executar Localmente

```bash
streamlit run streamlit_colab_final.py
```

O app abrirá em `http://localhost:8501`

---

## 📁 Estrutura do Projeto

```
produttivo-app/
├── streamlit_colab_final.py    # App Streamlit principal
├── login_cookie.ipynb          # Notebook para Google Colab
├── requirements.txt            # Dependências Python
├── README.md                   # Este arquivo
├── DEPLOY_GUIDE.md             # Guia de deploy detalhado
├── .gitignore                  # Arquivos ignorados pelo Git
└── .streamlit/
    └── secrets.toml.example    # Exemplo de configuração
```

---

## ❓ FAQ

### **P: Por que o notebook não executa automaticamente?**

**R:** A API pública do Google Colab não permite execução automática por questões de segurança. Você precisa abrir o link e executar manualmente.

---

### **P: O cookie expira?**

**R:** Sim, cookies de sessão geralmente expiram após algumas horas ou dias. Você precisará gerar um novo quando expirar.

---

### **P: Posso automatizar 100%?**

**R:** Para automação total, seria necessário rodar o Playwright em um servidor próprio ao invés do Colab. Entre em contato se precisar dessa solução.

---

### **P: É seguro?**

**R:** Sim! Suas credenciais são processadas via OAuth do Google e executadas em ambiente isolado do Colab. Nunca são armazenadas permanentemente.

---

### **P: Funciona com autenticação de dois fatores (2FA)?**

**R:** Atualmente não. O script assume login simples com email/senha.

---

## 🐛 Troubleshooting

### Erro: "Invalid client"

**Solução:** Verifique se o Client ID e Client Secret estão corretos no arquivo `secrets.toml`.

---

### Erro: "Redirect URI mismatch"

**Solução:** No Google Cloud Console, adicione `http://localhost` nas **Authorized redirect URIs**.

---

### Erro: "API not enabled"

**Solução:** Habilite a **Google Drive API** no Google Cloud Console.

---

### Cookie não capturado

**Possíveis causas:**
- Credenciais incorretas
- Site do Produttivo offline
- Timeout muito curto

**Solução:** Verifique os logs no notebook do Colab para detalhes.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! 

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto é fornecido "como está", sem garantias de qualquer tipo.

---

## 🙏 Créditos

- **Streamlit** - Framework de interface web
- **Google Colab** - Ambiente de execução
- **Playwright** - Automação de navegador
- **Produttivo** - Plataforma alvo

---

## 📞 Suporte

Encontrou um bug? Tem uma sugestão?

- 🐛 [Abra uma issue](https://github.com/ricardoarfr/produttivo-app/issues)
- 💬 [Discussões](https://github.com/ricardoarfr/produttivo-app/discussions)

---

## ⭐ Star o Projeto

Se este projeto foi útil para você, considere dar uma ⭐!

---

**Desenvolvido com ❤️ para automação de workflows**

*Última atualização: Fevereiro 2026*
