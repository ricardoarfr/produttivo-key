"""
🍪 Produttivo Cookie Generator
Playwright com Chromium do sistema (packages.txt)
"""

import streamlit as st
import asyncio
import subprocess
import sys
import os
from datetime import datetime
from typing import Optional

# ========================================
# INSTALAÇÃO DO PLAYWRIGHT (UMA VEZ)
# ========================================

@st.cache_resource
def configurar_playwright():
    """
    Instala playwright e aponta para o Chromium do sistema.
    Roda apenas UMA VEZ graças ao @st.cache_resource.
    """
    try:
        # Instala apenas o pacote Python do playwright (sem baixar browser)
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "playwright", "-q"],
            check=True,
            capture_output=True
        )

        # Instala apenas o chromium do playwright
        resultado = subprocess.run(
            ["playwright", "install", "chromium", "--with-deps"],
            capture_output=True,
            text=True
        )

        return True, "Playwright configurado com sucesso"

    except Exception as e:
        return False, str(e)

# ========================================
# LOGIN COM PLAYWRIGHT
# ========================================

def extrair_cookie_produttivo(cookie_header: str) -> Optional[str]:
    """Extrai apenas o _produttivo_session"""
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
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--single-process',
                ]
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

            log("🖱️ Enviando login...")
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
            log(f"🔍 URL: {url_atual}")

            if "sign_in" not in url_atual:
                log("✅ Login bem-sucedido!")
                await page.wait_for_timeout(3000)
                await browser.close()
                return cookie_capturado
            else:
                log("❌ Login falhou - verifique as credenciais")
                await browser.close()
                return None

    except Exception as e:
        log(f"❌ Erro: {str(e)}")
        return None

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

    # Configura Playwright (só na primeira vez)
    with st.spinner("⚙️ Verificando dependências..."):
        ok, msg = configurar_playwright()
        if not ok:
            st.error(f"❌ Falha ao configurar: {msg}")
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
        4. Copie o cookie!
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

            st.markdown("### 📋 Log:")
            log_area = st.empty()
            logs = []

            def adicionar_log(msg):
                timestamp = datetime.now().strftime("%H:%M:%S")
                logs.append(f"[{timestamp}] {msg}")
                log_area.code("\n".join(logs), language="bash")

            cookie = asyncio.run(fazer_login(email, senha, adicionar_log))

            st.session_state['rodando'] = False

            if cookie:
                st.session_state['cookie'] = cookie
                st.session_state['ultima_execucao'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                st.rerun()
            else:
                st.error("❌ Não foi possível capturar o cookie.")

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
