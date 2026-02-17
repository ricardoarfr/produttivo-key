"""
🍪 Produttivo Cookie Generator
Com detecção inteligente de ambiente
"""

import streamlit as st
import asyncio
import subprocess
import sys
import os
import platform
from datetime import datetime
from typing import Optional, Tuple

# ========================================
# DETECÇÃO DE AMBIENTE
# ========================================

@st.cache_resource
def detectar_ambiente() -> dict:
    """
    Detecta o ambiente de execução e retorna informações
    para guiar a instalação correta.
    """
    info = {
        "sistema": platform.system(),           # Linux, Windows, Darwin
        "python": sys.version,
        "is_streamlit_cloud": os.path.exists("/mount/src"),
        "is_colab": "COLAB_GPU" in os.environ or "COLAB_RELEASE_TAG" in os.environ,
        "is_linux": platform.system() == "Linux",
        "chromium_path": None,
        "playwright_ok": False,
    }

    # Tenta encontrar Chromium já instalado no sistema
    chromium_paths = [
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
    ]

    for path in chromium_paths:
        if os.path.exists(path):
            info["chromium_path"] = path
            break

    # Verifica se playwright já está instalado
    try:
        import playwright
        info["playwright_ok"] = True
    except ImportError:
        info["playwright_ok"] = False

    return info

# ========================================
# INSTALAÇÃO INTELIGENTE
# ========================================

@st.cache_resource
def configurar_playwright() -> Tuple[bool, str]:
    """
    Instala Playwright de forma adequada para o ambiente detectado.
    Roda apenas UMA VEZ graças ao @st.cache_resource.
    """
    env = detectar_ambiente()
    logs = []

    logs.append(f"🖥️ Sistema: {env['sistema']}")
    logs.append(f"☁️ Streamlit Cloud: {env['is_streamlit_cloud']}")
    logs.append(f"📓 Google Colab: {env['is_colab']}")
    logs.append(f"🌐 Chromium no sistema: {env['chromium_path'] or 'Não encontrado'}")

    try:
        # PASSO 1: Instala pacote Python do Playwright
        logs.append("📦 Instalando pacote playwright...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "playwright", "-q"],
            check=True,
            capture_output=True
        )
        logs.append("✅ Pacote instalado!")

        # PASSO 2: Estratégia de instalação do browser
        if env["is_colab"]:
            # No Colab: instala com deps de sistema
            logs.append("📓 Ambiente Colab detectado - instalando com deps...")
            subprocess.run(
                ["playwright", "install", "chromium"],
                check=True, capture_output=True
            )
            subprocess.run(
                ["playwright", "install-deps", "chromium"],
                check=True, capture_output=True
            )

        elif env["is_streamlit_cloud"]:
            # No Streamlit Cloud: tenta instalar com --with-deps
            logs.append("☁️ Streamlit Cloud detectado - instalando chromium...")
            resultado = subprocess.run(
                ["playwright", "install", "chromium", "--with-deps"],
                capture_output=True,
                text=True
            )
            if resultado.returncode != 0:
                # Fallback: tenta sem --with-deps
                logs.append("⚠️ Tentando instalação alternativa...")
                subprocess.run(
                    ["playwright", "install", "chromium"],
                    check=True, capture_output=True
                )

        else:
            # Local (Windows/Mac/Linux): instalação padrão
            logs.append(f"💻 Ambiente local ({env['sistema']}) - instalação padrão...")
            subprocess.run(
                ["playwright", "install", "chromium"],
                check=True, capture_output=True
            )

        logs.append("✅ Playwright configurado com sucesso!")
        return True, "\n".join(logs)

    except Exception as e:
        logs.append(f"❌ Erro: {str(e)}")
        return False, "\n".join(logs)

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
                and request.method == "GET"
                and cookie_capturado is None):
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
                    '--disable-setuid-sandbox',
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
        log(f"❌ Erro no navegador: {str(e)}")
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

    # Detecta ambiente
    env = detectar_ambiente()

    # Configura Playwright (só na primeira vez)
    with st.spinner("⚙️ Verificando dependências..."):
        ok, install_log = configurar_playwright()

    if not ok:
        st.error("❌ Falha ao configurar o navegador.")

        with st.expander("🔍 Ver detalhes do erro"):
            st.code(install_log, language="bash")
            st.info(f"""
            **Ambiente detectado:**
            - Sistema: `{env['sistema']}`
            - Streamlit Cloud: `{env['is_streamlit_cloud']}`
            - Google Colab: `{env['is_colab']}`
            - Chromium no sistema: `{env['chromium_path'] or 'Não encontrado'}`
            """)
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

        # Info do ambiente
        with st.expander("🖥️ Ambiente"):
            st.caption(f"""
            Sistema: `{env['sistema']}`
            Streamlit Cloud: `{env['is_streamlit_cloud']}`
            Colab: `{env['is_colab']}`
            """)

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
