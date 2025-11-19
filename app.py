import os
import sys
import traceback
import streamlit as st

# =========================================================
# CONFIG STREAMLIT (deve ser o primeiro comando Streamlit)
# =========================================================
try:
    st.set_page_config(page_title="Financefly Connector", page_icon="💸", layout="centered")
    print("✅ STEP 2: Configuração do Streamlit OK", flush=True)
except Exception as e:
    print("🔥 ERRO ao configurar Streamlit:", e, flush=True)
    traceback.print_exc()

print("🚀 STEP 0: app.py iniciado com sucesso", flush=True)

try:
    from modules.validator import startup_validation
    from modules.pluggy import create_connect_token
    from modules.db import save_client
    print("✅ STEP 1: Imports concluídos", flush=True)
except Exception as e:
    print("🔥 ERRO nos imports:", e, flush=True)
    traceback.print_exc()
    st.error(f"Erro ao importar módulos: {e}")

# =========================================================
# (Config moved earlier to ensure it's the first Streamlit command)
# =========================================================

# =========================================================
# STARTUP SAFE
# =========================================================
try:
    with st.spinner("Inicializando ambiente..."):
        startup_validation()
    print("✅ STEP 3: startup_validation() executado", flush=True)
except Exception as e:
    print("🔥 ERRO no startup_validation:", e, flush=True)
    traceback.print_exc()
    st.warning(f"Aviso durante inicialização: {e}")

# =========================================================
# SESSION STATE
# =========================================================
try:
    if "connect_token" not in st.session_state:
        st.session_state.connect_token = None
    if "form_data" not in st.session_state:
        st.session_state.form_data = {"name": "", "email": ""}
    if "item_processed" not in st.session_state:
        st.session_state.item_processed = False
    print("✅ STEP 4: Session state inicializado", flush=True)
except Exception as e:
    print("🔥 ERRO no session_state:", e, flush=True)
    traceback.print_exc()

# =========================================================
# VERIFICAÇÃO URL (itemId)
# =========================================================
try:
    params = st.query_params
    item_id = params.get("itemId") if params else None
    print(f"🔍 STEP 5: Params detectados: {params}", flush=True)

    if item_id and not st.session_state.item_processed:
        print(f"📦 STEP 6: itemId detectado: {item_id}", flush=True)

        name = st.session_state.form_data.get("name", "")
        email = st.session_state.form_data.get("email", "")

        if name and email:
            save_client(name, email, item_id)
            print("✅ STEP 7: save_client() executado", flush=True)
            st.success("Conta conectada com sucesso!")
        else:
            print("⚠️ STEP 7.1: itemId sem nome/email", flush=True)
            st.warning("itemId recebido, mas nome/email não foram preenchidos.")

        st.session_state.item_processed = True
except Exception as e:
    print("🔥 ERRO no processamento de itemId:", e, flush=True)
    traceback.print_exc()

# =========================================================
# UI / FORM
# =========================================================
try:
    st.title("Financefly Connector")
    st.caption("Conecte sua conta bancária via Pluggy com segurança.")
    print("✅ STEP 8: UI renderizada", flush=True)

    with st.form("client_form"):
        name = st.text_input("Nome completo", st.session_state.form_data["name"])
        email = st.text_input("E-mail", st.session_state.form_data["email"])
        submit = st.form_submit_button("Conectar conta")

    print("✅ STEP 9: Form renderizado", flush=True)
except Exception as e:
    print("🔥 ERRO ao renderizar form:", e, flush=True)
    traceback.print_exc()

# =========================================================
# SUBMIT
# =========================================================
try:
    if submit:
        print("🟢 STEP 10: Botão submit acionado", flush=True)
        if not name or not email:
            print("⚠️ Campos vazios no submit", flush=True)
            st.warning("Preencha todos os campos.")
        else:
            st.session_state.form_data = {"name": name, "email": email}
            token = create_connect_token(client_user_id=email)
            st.session_state.connect_token = token
            print("✅ STEP 11: Token Pluggy gerado", flush=True)
except Exception as e:
    print("🔥 ERRO no submit:", e, flush=True)
    traceback.print_exc()

# =========================================================
# WIDGET PLUGGY
# =========================================================
try:
    if st.session_state.connect_token:
        st.info("Abrindo o Pluggy Connect…")
        print("✅ STEP 12: Exibindo widget Pluggy", flush=True)

        # Open Pluggy Connect in a new window to avoid iframe sandboxing issues
        token = st.session_state.connect_token
        # The injected script will open a popup and write an HTML page that loads the Pluggy script
        html = f"""
        <script>
        (function() {{
            try {{
                var w = window.open('', '_blank');
                if (!w) {{
                    document.body.innerHTML += '<p style="color:orange">Popup blocked. Please allow popups for this site and try again.</p>';
                    console.error('Popup blocked - allow popups and reload.');
                    return;
                }}
                var doc = w.document;
                var token = "{token}";
                var html = `<!doctype html><html><head><meta charset="utf-8"><title>Pluggy Connect</title></head><body>`
                         + `<div id="pluggy-root"></div>`
                         + `<script src="https://cdn.pluggy.ai/pluggy-connect/v2.9.2/pluggy-connect.js"></script>`
                         + `<script>`
                         + `try {{ const connect = new PluggyConnect({{ connectToken: token, includeSandbox: false, language: 'pt', theme: 'dark' }}); if (connect && typeof connect.open === 'function') {{ connect.open(); }} else {{ console.error('PluggyConnect not available or connect.open is not a function', connect); document.body.innerHTML += '<p style="color:red">Erro: o widget Pluggy não pôde ser iniciado. Verifique bloqueadores (adblock) e se o script foi carregado.</p>'; }} }} catch(e) {{ console.error('Erro ao iniciar Pluggy:', e); document.body.innerHTML += '<p style="color:red">Erro JS: ' + String(e) + '</p>'; }}`
                         + `</` + `script>`
                         + `</body></html>`;
                doc.open();
                doc.write(html);
                doc.close();
            }} catch (err) {{
                console.error('Erro ao abrir a janela do Pluggy:', err);
                document.body.innerHTML += '<p style="color:red">Erro ao abrir o Pluggy Connect: ' + String(err) + '</p>';
            }}
        }})();
        </script>
        """
        st.components.v1.html(html, height=50)
        print("✅ STEP 13: Widget Pluggy renderizado", flush=True)
except Exception as e:
    print("🔥 ERRO no widget Pluggy:", e, flush=True)
    traceback.print_exc()

print("✅ STEP FINAL: Script finalizado com sucesso", flush=True)
sys.stdout.flush()
