"""
🍪 Produttivo Cookie Generator
Frontend Streamlit → API no Render
Com wake-up automático do serviço
"""

import streamlit as st
import requests
import time
from datetime import datetime

API_URL = st.secrets.get("API_URL", "https://produttivo-backend.onrender.com")

# ========================================
# FUNÇÕES
# ========================================

def acordar_api(max_tentativas=10) -> bool:
    """
    Faz ping na API até ela acordar.
    O Render free tier dorme após inatividade.
    """
    for i in range(max_tentativas):
        try:
            resp = requests.get(f"{API_URL}/health", timeout=10)
            if resp.status_code == 200:
                return True
        except:
            pass
        time.sleep(3)
    return False

def verificar_api() -> bool:
    """Verifica se API está online (sem esperar)"""
    try:
        resp = requests.get(f"{API_URL}/health", timeout=5)
        return resp.status_code == 200
    except:
        return False

# ========================================
# INTERFACE
# ========================================

def main():
    st.set_page_config(
        page_title="Produttivo Cookie Generator",
        page_icon="🍪",
        layout="wide"
    )

    st.title("🍪 Produttivo Cookie Generator")
    st.markdown("**Login automático e captura de cookie**")
    st.markdown("---")

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
        st.subheader("🔌 Status da API")

        api_online = verificar_api()
        if api_online:
            st.success("✅ API online")
        else:
            st.warning("😴 API dormindo (vai acordar ao gerar)")

        st.markdown("---")
        st.info("""
        **Como funciona:**
        1. Preencha email e senha
        2. Clique em "Gerar Cookie"
        3. Aguarde ~30-60 segundos
        4. Copie o cookie!

        💡 *Na primeira vez pode demorar mais
        pois o servidor precisa acordar.*
        """)

        if st.session_state.get('ultima_execucao'):
            st.markdown("---")
            st.caption(f"🕐 Último gerado:\n{st.session_state['ultima_execucao']}")

    # Área principal
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("🚀 Gerar Cookie")

        if not email or not senha:
            st.warning("⚠️ Preencha email e senha na barra lateral")
            st.stop()

        if st.button(
            "🎯 GERAR COOKIE",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.get('rodando', False)
        ):
            st.session_state['rodando'] = True
            st.session_state['cookie'] = None

            status = st.empty()

            # PASSO 1: Acorda a API se necessário
            if not verificar_api():
                status.warning("😴 Acordando o servidor... (pode levar até 30 segundos)")
                acordou = acordar_api(max_tentativas=15)
                if not acordou:
                    status.error("❌ Servidor não respondeu. Tente novamente em alguns segundos.")
                    st.session_state['rodando'] = False
                    st.rerun()
                    return

            # PASSO 2: Chama a API
            status.info("🔄 Fazendo login no Produttivo...")

            try:
                response = requests.post(
                    f"{API_URL}/gerar-cookie",
                    json={"email": email, "senha": senha},
                    timeout=180  # 3 minutos
                )

                if response.status_code == 200:
                    data = response.json()
                    if data["sucesso"]:
                        st.session_state['cookie'] = data["cookie"]
                        st.session_state['ultima_execucao'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        status.success("✅ Cookie gerado com sucesso!")
                    else:
                        status.error(f"❌ {data['mensagem']}")
                else:
                    status.error(f"❌ Erro na API: {response.status_code} — {response.text}")

            except requests.exceptions.Timeout:
                status.error("❌ Timeout — o login demorou mais de 3 minutos.")
            except requests.exceptions.ConnectionError:
                status.error("❌ Não foi possível conectar à API.")
            except Exception as e:
                status.error(f"❌ Erro inesperado: {str(e)}")

            st.session_state['rodando'] = False
            st.rerun()

    with col2:
        st.header("📊 Status")

        if st.session_state.get('rodando'):
            st.warning("🔄 Executando...")
        elif st.session_state.get('cookie'):
            st.success("✅ Cookie disponível!")
        else:
            st.info("⏳ Aguardando execução")

    # Exibe cookie
    if st.session_state.get('cookie') and not st.session_state.get('rodando'):
        st.markdown("---")
        st.header("🍪 Cookie Capturado")

        st.code(st.session_state['cookie'], language="text")

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="💾 Download .txt",
                data=st.session_state['cookie'],
                file_name=f"cookie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col2:
            if st.button("🔄 Gerar Novo Cookie", use_container_width=True):
                st.session_state['cookie'] = None
                st.rerun()

    st.markdown("---")
    st.caption("🔐 Credenciais usadas apenas para autenticação e não armazenadas")

# ========================================
# EXECUÇÃO
# ========================================

if __name__ == "__main__":
    if 'cookie' not in st.session_state:
        st.session_state['cookie'] = None
    if 'rodando' not in st.session_state:
        st.session_state['rodando'] = False
    if 'ultima_execucao' not in st.session_state:
        st.session_state['ultima_execucao'] = None

    main()
