"""
🍪 Produttivo Cookie Generator
Playwright direto no Streamlit Cloud
Com cache inteligente para não reinstalar sempre
"""

import streamlit as st
import asyncio
import subprocess
import sys
import os
from datetime import datetime
from typing import Optional

# ========================================
# CACHE DE INSTALAÇÃO DO PLAYWRIGHT
# ========================================

@st.cache_resource
def instalar_playwright():
    """
    Instala Playwright UMA VEZ e mantém em cache.
    @st.cache_resource garante que só roda na primeira vez
    ou quando o servidor reinicia.
    """
    try:
        # Instala o pacote playwright
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "playwright", "-q"],
            check=True,
            capture_output=True
        )

        # Instala o Chromium
        subprocess.run(
            ["playwright", "install", "chromium"],
            check=True,
            capture_output=True
        )

        # Instala dependências do sistema
        subprocess.run(
            ["playwright", "install-deps", "chromium"],
            check=True,
            capture_output=True
        )

        return True

    except Exception as e:
        return False

# ========================================
# FUNÇÕES DE LOGIN
# ========================================

def extrair_cookie_produttivo(cookie_header: str) -> Optional[str]:
    """Extrai apenas o _produttivo_session do header"""
    if cookie_header:
        for par in cookie_header.split('; '):
            if '=' in par:
                nome, valor = par.split('=', 1)
                if nome.strip() == '_produttivo_session':
                    return valor
    return None

async def fazer_login(email: str, senha: str, log_callback=None) -> Optional[str]:
    """Executa login e retorna cookie"""
    from playwright.async_api import async_playwright

    cookie_capturado = None

    def log(msg):
        if log_callback:
            log_callback(msg)

    async def capturar_request(request):
        nonlocal cookie_capturado
        if (request.url == "https://app.produttivo.com.br/works"
                and request.method == "GET"):
            headers = await request.all_headers()
            cookie_header = headers.get('cookie', '')
            if cookie_header:
                cookie_capturado = extrair_cookie_produttivo(cookie_header)
                if cookie_capturado:
                    log("🎯 Cookie capturado!")

    try:
        async with async_playwright() as p:

            log("🚀 Iniciando navegador...")
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )

            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            context.set_default_timeout(60000)
            page = await context.new_page()
            page.on("request", capturar_request)

            log("🌐 Acessando Produttivo...")
            await page.goto(
                "https://app.produttivo.com.br/auth/sign_in",
                wait_until="domcontentloaded",
                timeout=60000
            )
            await page.wait_for_timeout(3000)

            log("📧 Preenchendo email...")
            await page.wait_for_selector(
                'input[type="email"], input[name="email"]',
                timeout=30000
            )
            await page.fill('input[type="email"], input[name="email"]', email)
            await page.wait_for_timeout(1000)

            log("🔑 Preenchendo senha...")
            await page.fill('input[type="password"]', senha)
            await page.wait_for_timeout(2000)

            log("🖱️ Clicando em login...")
            try:
                await page.click('button:has-text("Login")', timeout=5000)
            except:
                try:
                    await page.click('button[type="submit"]', timeout=5000)
                except:
                    await page.press('input[type="password"]', 'Enter')

            log("⏳ Aguardando autenticação...")
            await page.wait_for_timeout(8000)

            url_atual = page.url
            log(f"🔍 URL atual: {url_atual}")

            if "sign_in" not in url_atual:
                log("✅ Login bem-sucedido!")
                await page.wait_for_timeout(3000)
                await browser.close()
                return cookie_capturado
            else:
                log("❌ Login falhou - verifique suas credenciais")
                await browser.close()
                return None

    except Exception as e:
        log(f"❌ Erro: {str(e)}")
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
    st.markdown("**Login automático e captura de cookie**")
    st.markdown("---")

    # Instala Playwright (só na primeira vez)
    with st.spinner("⚙️ Verificando dependências..."):
        ok = instalar_playwright()
        if not ok:
            st.error("❌ Falha ao instalar Playwright. Tente recarregar a página.")
            st.stop()

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
        st.info("""
        **Como funciona:**
        1. Preencha email e senha
        2. Clique em "Gerar Cookie"
        3. Aguarde ~30 segundos
        4. Copie o cookie gerado!
        """)

        # Última execução
        if st.session_state.get('ultima_execucao'):
            st.markdown("---")
            st.caption(f"🕐 Último cookie gerado:\n{st.session_state['ultima_execucao']}")

    # Área principal
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("🚀 Gerar Cookie")

        if not email or not senha:
            st.warning("⚠️ Preencha email e senha na barra lateral")
            st.stop()

        if st.button("🎯 GERAR COOKIE", type="primary", use_container_width=True,
                     disabled=st.session_state.get('rodando', False)):

            st.session_state['rodando'] = True

            # Container de logs
            st.markdown("### 📋 Log:")
            log_area = st.empty()
            logs = []

            def adicionar_log(msg):
                timestamp = datetime.now().strftime("%H:%M:%S")
                logs.append(f"[{timestamp}] {msg}")
                log_area.code("\n".join(logs), language="bash")

            # Executa login
            cookie = asyncio.run(fazer_login(email, senha, adicionar_log))

            st.session_state['rodando'] = False

            if cookie:
                st.session_state['cookie'] = cookie
                st.session_state['ultima_execucao'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                st.rerun()
            else:
                st.error("❌ Não foi possível capturar o cookie. Verifique os logs acima.")

    with col2:
        st.header("📊 Status")

        if st.session_state.get('rodando'):
            st.warning("🔄 Executando...")
        elif st.session_state.get('cookie'):
            st.success("✅ Cookie disponível!")
        else:
            st.info("⏳ Aguardando execução")

    # Exibe cookie capturado
    if st.session_state.get('cookie') and not st.session_state.get('rodando'):
        st.markdown("---")
        st.header("🍪 Cookie Capturado")

        st.code(st.session_state['cookie'], language="text")

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="💾 Download como .txt",
                data=st.session_state['cookie'],
                file_name=f"cookie_produttivo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )

        with col2:
            if st.button("🔄 Gerar Novo Cookie", use_container_width=True):
                st.session_state['cookie'] = None
                st.rerun()

    st.markdown("---")
    st.caption("🔐 Suas credenciais são usadas apenas para autenticação e não são armazenadas")

# ========================================
# EXECUÇÃO
# ========================================

if __name__ == "__main__":
    # Inicializa session state
    if 'cookie' not in st.session_state:
        st.session_state['cookie'] = None
    if 'rodando' not in st.session_state:
        st.session_state['rodando'] = False
    if 'ultima_execucao' not in st.session_state:
        st.session_state['ultima_execucao'] = None

    main()
