"""
🍪 Produttivo Cookie Generator
Interface Streamlit + Google Colab API
OAuth via URL (compatível com Streamlit Cloud)
"""

import streamlit as st
import json
import time
import io
import requests
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError

# ========================================
# CONFIGURAÇÕES
# ========================================

SCOPES = [
    'https://www.googleapis.com/auth/drive.file'
]

GITHUB_NOTEBOOK_URL = "https://raw.githubusercontent.com/ricardoarfr/produttivo-key/main/login_cookie.ipynb"

REDIRECT_URI = "https://rf-extractor-key.streamlit.app/"

# ========================================
# FUNÇÕES DE AUTENTICAÇÃO OAUTH (SEM BROWSER)
# ========================================

def get_oauth_flow():
    """Cria o fluxo OAuth com configurações do Streamlit Secrets"""
    client_config = {
        "web": {
            "client_id": st.secrets["GOOGLE_CLIENT_ID"],
            "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI]
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    return flow

def get_auth_url():
    """Gera URL de autorização OAuth"""
    flow = get_oauth_flow()
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    st.session_state['oauth_state'] = state
    return auth_url

def exchange_code_for_token(code):
    """Troca o código de autorização por token de acesso"""
    flow = get_oauth_flow()
    flow.fetch_token(code=code)
    return flow.credentials

def get_credentials_from_session():
    """Recupera credenciais salvas na session"""
    if 'google_credentials' not in st.session_state:
        return None

    creds_data = st.session_state['google_credentials']
    creds = Credentials(
        token=creds_data['token'],
        refresh_token=creds_data.get('refresh_token'),
        token_uri=creds_data['token_uri'],
        client_id=creds_data['client_id'],
        client_secret=creds_data['client_secret'],
        scopes=creds_data['scopes']
    )
    return creds

def save_credentials_to_session(creds):
    """Salva credenciais na session do Streamlit"""
    st.session_state['google_credentials'] = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': list(creds.scopes) if creds.scopes else SCOPES
    }

def is_authenticated():
    """Verifica se usuário está autenticado"""
    return 'google_credentials' in st.session_state

# ========================================
# CAPTURA DO CÓDIGO OAUTH NA URL
# ========================================

def check_oauth_callback():
    """Verifica se há código OAuth na URL e processa"""
    query_params = st.query_params

    if 'code' in query_params and not is_authenticated():
        code = query_params['code']

        with st.spinner("🔄 Finalizando autenticação..."):
            try:
                creds = exchange_code_for_token(code)
                save_credentials_to_session(creds)
                st.query_params.clear()
                st.success("✅ Autenticado com sucesso!")
                time.sleep(1)
                st.rerun()

            except Exception as e:
                st.error(f"❌ Erro ao autenticar: {e}")

# ========================================
# FUNÇÕES DO GOOGLE DRIVE
# ========================================

def download_notebook_from_github():
    """Baixa notebook do GitHub"""
    try:
        response = requests.get(GITHUB_NOTEBOOK_URL, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        st.error(f"❌ Erro ao baixar notebook do GitHub: {e}")
        return None

def create_colab_notebook(creds, notebook_content, email, senha):
    """Cria notebook no Google Drive com credenciais injetadas"""

    # Parse do notebook
    notebook_json = json.loads(notebook_content)

    # Injeta credenciais na célula correta
    for cell in notebook_json['cells']:
        source = cell.get('source', '')
        if isinstance(source, list):
            source_str = ''.join(source)
        else:
            source_str = source

        if 'EMAIL' in source_str and 'SENHA' in source_str:
            new_source = source_str.replace(
                'EMAIL = "financeiro@rfsolucoestelecom.com.br"',
                f'EMAIL = "{email}"'
            ).replace(
                'SENHA = "Novo*789"',
                f'SENHA = "{senha}"'
            )
            cell['source'] = new_source

    modified_content = json.dumps(notebook_json, indent=2).encode('utf-8')

    # Cria serviço do Drive
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': f'login_produttivo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.ipynb',
        'mimeType': 'application/vnd.google.colaboratory'
    }

    media = MediaIoBaseUpload(
        io.BytesIO(modified_content),
        mimetype='application/vnd.google.colaboratory',
        resumable=True
    )

    try:
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()

        return file

    except HttpError as error:
        st.error(f"❌ Erro ao criar notebook no Drive: {error}")
        return None

# ========================================
# INTERFACE STREAMLIT
# ========================================

def main():
    st.set_page_config(
        page_title="Produttivo Cookie Generator",
        page_icon="🍪",
        layout="wide"
    )

    st.title("🍪 Produttivo Cookie Generator")
    st.markdown("**Geração automática via Google Colab**")
    st.markdown("---")

    # Verifica callback OAuth
    check_oauth_callback()

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurações")

        st.subheader("🔐 Credenciais Produttivo")
        email = st.text_input(
            "Email",
            value=st.secrets.get("PRODUTTIVO_EMAIL", ""),
        )
        senha = st.text_input(
            "Senha",
            value=st.secrets.get("PRODUTTIVO_SENHA", ""),
            type="password"
        )

        st.markdown("---")

        # Status Google OAuth
        st.subheader("🔑 Google OAuth")
        if is_authenticated():
            st.success("✅ Autenticado!")
            if st.button("🔓 Desconectar"):
                del st.session_state['google_credentials']
                st.rerun()
        else:
            st.warning("⚠️ Não autenticado")

        st.markdown("---")

        # Status secrets
        if st.secrets.get("GOOGLE_CLIENT_ID"):
            st.success("✅ Client ID configurado")
        else:
            st.error("❌ GOOGLE_CLIENT_ID não configurado")

        if st.secrets.get("GOOGLE_CLIENT_SECRET"):
            st.success("✅ Client Secret configurado")
        else:
            st.error("❌ GOOGLE_CLIENT_SECRET não configurado")

    # Área principal
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("🚀 Gerador de Cookie")

        # PASSO 1: Autenticar com Google
        if not is_authenticated():
            st.info("**Passo 1:** Autentique com sua conta Google para começar.")

            if st.button("🔗 Autenticar com Google", type="primary", use_container_width=True):
                auth_url = get_auth_url()
                st.markdown(f"""
                ### Clique no link para autorizar:
                👉 **[Autenticar com Google]({auth_url})**

                Após autorizar, você voltará automaticamente para cá.
                """)

        # PASSO 2: Gerar cookie
        else:
            st.success("✅ Google autenticado! Pronto para gerar o cookie.")

            if not email or not senha:
                st.warning("⚠️ Preencha email e senha na barra lateral")
                st.stop()

            if st.button("🎯 GERAR COOKIE", type="primary", use_container_width=True):

                progress = st.empty()

                # Baixar notebook
                progress.info("1️⃣ Baixando notebook do GitHub...")
                notebook_content = download_notebook_from_github()

                if not notebook_content:
                    st.stop()

                progress.success("✅ Notebook baixado!")
                time.sleep(0.5)

                # Criar no Drive
                progress.info("2️⃣ Criando notebook no Google Colab...")
                creds = get_credentials_from_session()
                colab_file = create_colab_notebook(creds, notebook_content, email, senha)

                if not colab_file:
                    st.stop()

                progress.empty()

                # Resultado
                st.success("🎉 Notebook criado com sucesso!")
                st.markdown("---")

                st.markdown(f"""
                ### 📋 Próximos Passos:

                **1. Abra o notebook no Colab:**

                👉 [Clique aqui para abrir]({colab_file['webViewLink']})

                **2. Execute todas as células:**
                - Menu: `Runtime` → `Run all`
                - Aguarde ~30 segundos

                **3. Copie o cookie:**
                - Aparece no final entre as linhas `══════`
                """)

    with col2:
        st.header("📊 Status")

        st.markdown("**Checklist:**")

        if st.secrets.get("GOOGLE_CLIENT_ID") and st.secrets.get("GOOGLE_CLIENT_SECRET"):
            st.success("✅ Google configurado")
        else:
            st.error("❌ Google não configurado")

        if is_authenticated():
            st.success("✅ Google autenticado")
        else:
            st.warning("⏳ Aguardando autenticação")

        if email and senha:
            st.success("✅ Credenciais Produttivo")
        else:
            st.warning("⏳ Preencha email e senha")

    st.markdown("---")
    st.caption("🔐 Autenticação segura via Google OAuth 2.0")

# ========================================
# EXECUÇÃO
# ========================================

if __name__ == "__main__":
    main()
