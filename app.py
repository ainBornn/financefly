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
                # Render a client-side button that opens the Pluggy widget in a new window
                # (opening from a user click avoids popup blockers)
                safe_html = """
                <div>
                    <p>Clique no botão para abrir o widget do Pluggy (abre em nova janela).</p>
                    <button id="open-pluggy" style="padding:10px 16px;font-size:16px;">Abrir Pluggy</button>
                    <div id="pluggy-fallback" style="margin-top:8px;color:#b00;display:none;">Se o popup não abrir, permita popups no navegador e tente novamente.</div>
                </div>
                <script>
                    document.getElementById('open-pluggy').addEventListener('click', function(){
                        const win = window.open('', 'pluggy_connect', 'width=520,height=720');
                        if (!win) {
                            document.getElementById('pluggy-fallback').style.display = 'block';
                            return;
                        }
                        // Write the HTML into the popup and load Pluggy script
                        const html = `<!doctype html><html><head><meta charset='utf-8'><title>Pluggy Connect</title></head><body><div id='root'></div><script src='https://cdn.pluggy.ai/pluggy-connect/v2.9.2/pluggy-connect.js'></script><script>document.addEventListener('DOMContentLoaded', function(){ try { const connect = new PluggyConnect({token: "__CONNECT_TOKEN__"}); if (typeof connect.open === 'function') { connect.open(); } else { document.body.innerHTML = '<p>Plugin carregado mas "connect.open" não disponível.</p>'; } } catch(e){ document.body.innerHTML = '<p>Erro ao abrir Pluggy: '+String(e)+'</p>'; } });</script></body></html>`;
                        win.document.open();
                        win.document.write(html);
                        win.document.close();
                    });
                </script>
                """
                # inject the token safely to avoid interfering with JS braces
                safe_html = safe_html.replace('__CONNECT_TOKEN__', token)
                st.components.v1.html(safe_html, height=130)
        print("✅ STEP 13: Widget Pluggy renderizado", flush=True)
except Exception as e:
    print("🔥 ERRO no widget Pluggy:", e, flush=True)
    traceback.print_exc()

print("✅ STEP FINAL: Script finalizado com sucesso", flush=True)
sys.stdout.flush()
