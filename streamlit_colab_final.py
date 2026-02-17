"""
🍪 Produttivo Cookie Generator
Interface Streamlit + Google Colab API
"""

import streamlit as st
import os
import json
import time
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
import io
import requests
import pickle

# ========================================
# CONFIGURAÇÕES
# ========================================

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
]

# URL do notebook no GitHub
GITHUB_NOTEBOOK_URL = "https://raw.githubusercontent.com/ricardoarfr/produttivo-app/main/login_cookie.ipynb"

CREDENTIALS_FILE = 'token.pickle'

# ========================================
# FUNÇÕES DE AUTENTICAÇÃO
# ========================================

def get_credentials():
    """Obtém credenciais OAuth do Streamlit Secrets"""
    creds = None
    
    # Tenta carregar credenciais salvas
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # Se não tem credenciais válidas, faz novo login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except:
                creds = None
        
        if not creds:
            # Usa credenciais do Streamlit Secrets
            client_config = {
                "installed": {
                    "client_id": st.secrets["GOOGLE_CLIENT_ID"],
                    "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
                }
            }
            
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)
            
            # Salva credenciais
            with open(CREDENTIALS_FILE, 'wb') as token:
                pickle.dump(creds, token)
    
    return creds

def authenticate_drive():
    """Autentica no Google Drive"""
    try:
        creds = get_credentials()
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        st.error(f"❌ Erro na autenticação: {e}")
        return None

# ========================================
# FUNÇÕES DO GOOGLE DRIVE
# ========================================

def download_notebook_from_github():
    """Baixa notebook do GitHub"""
    try:
        response = requests.get(GITHUB_NOTEBOOK_URL)
        response.raise_for_status()
        return response.text
    except Exception as e:
        st.error(f"❌ Erro ao baixar notebook: {e}")
        return None

def create_colab_notebook(service, notebook_content, email, senha):
    """Cria notebook no Google Drive com credenciais injetadas"""
    
    # Parse do notebook
    notebook_json = json.loads(notebook_content)
    
    # Injeta credenciais na última célula
    for cell in notebook_json['cells']:
        if 'EMAIL' in cell.get('source', [''])[0]:
            # Substitui credenciais
            new_source = []
            for line in cell['source']:
                line = line.replace('EMAIL = "financeiro@rfsolucoestelecom.com.br"', 
                                  f'EMAIL = "{email}"')
                line = line.replace('SENHA = "Novo*789"', 
                                  f'SENHA = "{senha}"')
                new_source.append(line)
            cell['source'] = new_source
    
    # Converte de volta para string
    modified_content = json.dumps(notebook_json, indent=2)
    
    # Cria arquivo temporário
    file_metadata = {
        'name': f'login_produttivo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.ipynb',
        'mimeType': 'application/vnd.google.colaboratory'
    }
    
    # Upload
    media = MediaFileUpload(
        io.BytesIO(modified_content.encode()),
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
        st.error(f"❌ Erro ao criar notebook: {error}")
        return None

def get_notebook_output(service, file_id):
    """Tenta extrair output do notebook (limitação: não é trivial via API)"""
    
    # NOTA: A API do Google Drive não fornece acesso direto aos outputs
    # de execução de notebooks Colab. Precisamos de uma abordagem diferente.
    
    st.warning("⚠️ A API do Google Colab não permite execução automática direta.")
    st.info("💡 O notebook foi criado no seu Google Drive. Você precisa abri-lo manualmente no Colab para executar.")
    
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
    
    # CSS
    st.markdown("""
    <style>
    .big-button {
        font-size: 20px;
        font-weight: bold;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🍪 Produttivo Cookie Generator")
    st.markdown("**Geração automática via Google Colab**")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        st.subheader("🔐 Credenciais Produttivo")
        email = st.text_input(
            "Email",
            value=st.secrets.get("PRODUTTIVO_EMAIL", ""),
            type="default"
        )
        senha = st.text_input(
            "Senha",
            value=st.secrets.get("PRODUTTIVO_SENHA", ""),
            type="password"
        )
        
        st.markdown("---")
        
        st.info("""
        **Como funciona:**
        
        1. Clique em "Gerar Cookie"
        2. Autentique com Google (primeira vez)
        3. Notebook será criado no Drive
        4. Abra o link do Colab
        5. Execute o notebook
        6. Copie o cookie gerado
        """)
        
        st.markdown("---")
        
        # Check de configuração
        if not st.secrets.get("GOOGLE_CLIENT_ID"):
            st.error("❌ Configure GOOGLE_CLIENT_ID")
        else:
            st.success("✅ Client ID configurado")
        
        if not st.secrets.get("GOOGLE_CLIENT_SECRET"):
            st.error("❌ Configure GOOGLE_CLIENT_SECRET")
        else:
            st.success("✅ Client Secret configurado")
    
    # Área principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🚀 Gerador de Cookie")
        
        if not email or not senha:
            st.warning("⚠️ Preencha email e senha na barra lateral")
            st.stop()
        
        if st.button("🎯 GERAR COOKIE", type="primary", use_container_width=True):
            
            with st.spinner("🔄 Processando..."):
                
                # 1. Autenticar no Google Drive
                progress_text = st.empty()
                progress_text.info("1️⃣ Autenticando no Google Drive...")
                
                service = authenticate_drive()
                
                if not service:
                    st.error("❌ Falha na autenticação")
                    st.stop()
                
                progress_text.success("✅ Autenticado com sucesso!")
                time.sleep(1)
                
                # 2. Baixar notebook do GitHub
                progress_text.info("2️⃣ Baixando notebook do GitHub...")
                
                notebook_content = download_notebook_from_github()
                
                if not notebook_content:
                    st.error("❌ Falha ao baixar notebook")
                    st.stop()
                
                progress_text.success("✅ Notebook baixado!")
                time.sleep(1)
                
                # 3. Criar notebook no Drive
                progress_text.info("3️⃣ Criando notebook no Google Colab...")
                
                colab_file = create_colab_notebook(service, notebook_content, email, senha)
                
                if not colab_file:
                    st.error("❌ Falha ao criar notebook")
                    st.stop()
                
                progress_text.success("✅ Notebook criado!")
                
                # 4. Exibir link
                st.markdown("---")
                st.success("✅ Notebook criado com sucesso!")
                
                st.markdown(f"""
                ### 📝 Próximos Passos:
                
                1. **Abra o notebook no Colab:**
                   
                   🔗 [{colab_file['webViewLink']}]({colab_file['webViewLink']})
                
                2. **Execute todas as células** (Runtime > Run all)
                
                3. **Copie o cookie** que aparece no final
                
                4. **Use o cookie** nas suas requisições!
                """)
                
                st.info("💡 **Dica:** O cookie será exibido entre as linhas de =======")
    
    with col2:
        st.header("📊 Status")
        
        # Verifica se está configurado
        has_google_creds = bool(
            st.secrets.get("GOOGLE_CLIENT_ID") and 
            st.secrets.get("GOOGLE_CLIENT_SECRET")
        )
        
        has_produttivo_creds = bool(email and senha)
        
        if has_google_creds and has_produttivo_creds:
            st.success("✅ Tudo configurado!")
        else:
            st.warning("⚠️ Configuração incompleta")
        
        st.markdown("---")
        
        st.markdown("### 🔧 Requisitos:")
        st.markdown(f"""
        - {'✅' if has_google_creds else '❌'} Google OAuth configurado
        - {'✅' if has_produttivo_creds else '❌'} Credenciais Produttivo
        """)
    
    # Footer
    st.markdown("---")
    st.caption("🔐 Seus dados são processados de forma segura via Google Cloud")

# ========================================
# EXECUÇÃO
# ========================================

if __name__ == "__main__":
    main()
