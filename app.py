# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3
import os
import base64
from PIL import Image

# Configurazione pagina Streamlit
st.set_page_config(page_title="Portale Religioso", page_icon="🙏", layout="wide")

# Creazione cartella media per salvare le immagini caricate
MEDIA_DIR = "media"
if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)

# --- FUNZIONE PER RIDIMENSIONARE E SALVARE LE IMMAGINI ---
def save_uploaded_image(immagine_file):
    if immagine_file is not None:
        img_path = os.path.join(MEDIA_DIR, immagine_file.name)
        img = Image.open(immagine_file)
        
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        max_size = (1000, 1000)
        img.thumbnail(max_size)
        
        img.save(img_path, "JPEG", optimize=True, quality=85)
        return img_path
    return ""

# --- FUNZIONE PER IMPOSTARE LO SFONDO ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE DATABASE SQLITE ---
def get_connection():
    conn = sqlite3.connect("religione.db")
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Tabella Preghiere
    c.execute('''CREATE TABLE IF NOT EXISTS preghiere 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, titolo TEXT, testo TEXT, immagine TEXT)''')
    
    c.execute("PRAGMA table_info(preghiere)")
    columns = [column[1] for column in c.fetchall()]
    if "immagine" not in columns:
        c.execute("ALTER TABLE preghiere ADD COLUMN immagine TEXT")

    # Tabella Racconti
    c.execute('''CREATE TABLE IF NOT EXISTS racconti 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, titolo TEXT, testo TEXT, immagine TEXT)''')
    
    # Tabella Link
    c.execute('''CREATE TABLE IF NOT EXISTS link_esterni 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, titolo TEXT, url TEXT, descrizione TEXT)''')
    
    conn.commit()
    conn.close()

init_db()

# --- GESTIONE STATO SESSIONE (LOGIN) ---
if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

# --- MENU E AREA RISERVATA NELLA SIDEBAR ---
st.sidebar.title("📌 Navigazione")
scelta_pagina = st.sidebar.radio("Scegli la sezione:", [
    "🏠 Home",
    "📖 Preghiere", 
    "📚 Racconti", 
    "🔗 Link Utili", 
    "⚙️ Area Gestione (Carica/Modifica)"
])

st.sidebar.markdown("---")
st.sidebar.title("🔒 Area Riservata")
PASSWORD_CORRETTA = "1234"  # Puoi cambiare la password qui se desideri

if not st.session_state.autenticato:
    with st.sidebar.form("form_login_sidebar"):
        password_inserita = st.text_input("Password Amministratore", type="password")
        submit_login = st.form_submit_button("Accedi")
        
        if submit_login:
            if password_inserita == PASSWORD_CORRETTA:
                st.session_state.autenticato = True
                st.success("Accesso effettuato!")
                st.rerun()
            else:
                st.error("Password errata.")
else:
    st.sidebar.success("✅ Amministratore Connesso")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.autenticato = False
        st.rerun()

st.sidebar.markdown("---")

# --- PAGINA 0: HOME PAGE GRAFICA E ACCOGLIENTE CON SFONDO ---
if scelta_pagina == "🏠 Home":
    bg_path = os.path.join(MEDIA_DIR, "background.jpg")
    if os.path.exists(bg_path):
        set_png_as_page_bg(bg_path)

    st.markdown(
        """
        <div style="background-color: rgba(255, 255, 255, 0.75); padding: 30px; border-radius: 15px; text-align: center; border: 1px solid #e1e4e8; margin-bottom: 20px;">
            <h1 style="color: #2c3e50; font-family: sans-serif; margin-bottom: 10px;">🕊️ Benvenuto nel Portale di Spiritualità</h1>
            <p style="font-size: 1.2rem; color: #555; font-style: italic;">"La preghiera è il respiro dell'anima, un rifugio di pace e di luce."</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*), titolo FROM preghiere ORDER BY id DESC LIMIT 1")
    res_p = c.fetchone()
    num_p = res_p[0] if res_p else 0
    ultima_p = res_p[1] if res_p and res_p[1] else "Nessuna"

    c.execute("SELECT COUNT(*), titolo FROM racconti ORDER BY id DESC LIMIT 1")
    res_r = c.fetchone()
    num_r = res_r[0] if res_r else 0
    ultimo_r = res_r[1] if res_r and res_r[1] else "Nessuno"

    c.execute("SELECT COUNT(*) FROM link_esterni")
    res_l = c.fetchone()
    num_l = res_l[0] if res_l else 0

    conn.close()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div style="border: 2px solid #d4edda; background-color: rgba(248, 255, 249, 0.85); padding: 20px; border-radius: 10px; text-align: center; height: 200px;">
                <h3>📖 Preghiere</h3>
                <p style="font-size: 1.5rem; font-weight: bold; color: #28a745; margin: 10px 0;">{num_p} inserite</p>
                <p style="font-size: 0.9rem; color: #666;">Ultima aggiunta:<br><b>{ultima_p}</b></p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style="border: 2px solid #d1ecf1; background-color: rgba(240, 248, 255, 0.85); padding: 20px; border-radius: 10px; text-align: center; height: 200px;">
                <h3>📚 Racconti</h3>
                <p style="font-size: 1.5rem; font-weight: bold; color: #17a2b8; margin: 10px 0;">{num_r} inseriti</p>
                <p style="font-size: 0.9rem; color: #666;">Ultimo racconto:<br><b>{ultimo_r}</b></p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div style="border: 2px solid #fff3cd; background-color: rgba(255, 253, 245, 0.85); padding: 20px; border-radius: 10px; text-align: center; height: 200px;">
                <h3>🔗 Link Utili</h3>
                <p style="font-size: 1.5rem; font-weight: bold; color: #ffc107; margin: 10px 0;">{num_l} collegati</p>
                <p style="font-size: 0.9rem; color: #666;">Risorse esterne e siti di interesse spirituale.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background-color: rgba(255, 255, 255, 0.75); padding: 15px; border-radius: 10px;">
            <p>💡 <b>Come iniziare:</b> Usa il menu laterale a sinistra per sfogliare le sezioni o per aggiungere, modificare e cancellare i tuoi contenuti tramite l'Area Gestione.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- PAGINA 1: PREGHIERE ---
elif scelta_pagina == "📖 Preghiere":
    st.header("📖 Raccolta Preghiere")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, titolo, testo, immagine FROM preghiere ORDER BY id DESC")
    preghiere = c.fetchall()
    conn.close()

    if preghiere:
        st.sidebar.subheader("📋 Elenco Preghiere")
        titles = [p[1] for p in preghiere]
        scelta_preghiera = st.sidebar.radio("Seleziona voce:", ["Visualizza Tutte"] + titles)
        
        if scelta_preghiera == "Visualizza Tutte":
            for item_id, titolo, testo, img_path in preghiere:
                with st.expander(titolo):
                    if img_path and os.path.exists(img_path):
                        img = Image.open(img_path)
                        st.image(img, use_container_width=True)
                    st.write(testo)
        else:
            for item_id, titolo, testo, img_path in preghiere:
                if titolo == scelta_preghiera:
                    st.subheader(titolo)
                    if img_path and os.path.exists(img_path):
                        img = Image.open(img_path)
                        st.image(img, use_container_width=True)
                    st.write(testo)
    else:
        st.info("Nessuna preghiera inserita al momento.")

# --- PAGINA 2: RACCONTI ---
elif scelta_pagina == "📚 Racconti":
    st.header("📚 Racconti e Riflessioni")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, titolo, testo, immagine FROM racconti ORDER BY id DESC")
    racconti = c.fetchall()
    conn.close()

    if racconti:
        st.sidebar.subheader("📋 Elenco Racconti")
        titles = [r[1] for r in racconti]
        scelta_racconto = st.sidebar.radio("Seleziona voce:", ["Visualizza Tutti"] + titles)
        
        if scelta_racconto == "Visualizza Tutti":
            for item_id, titolo, testo, img_path in racconti:
                st.subheader(titolo)
                if img_path and os.path.exists(img_path):
                    img = Image.open(img_path)
                    st.image(img, use_container_width=True)
                st.write(testo)
                st.markdown("---")
        else:
            for item_id, titolo, testo, img_path in racconti:
                if titolo == scelta_racconto:
                    st.subheader(titolo)
                    if img_path and os.path.exists(img_path):
                        img = Image.open(img_path)
                        st.image(img, use_container_width=True)
                    st.write(testo)
    else:
        st.info("Nessun racconto inserito al momento.")

# --- PAGINA 3: LINK UTILI ---
elif scelta_pagina == "🔗 Link Utili":
    st.header("🔗 Siti di Interesse e Risorse")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, titolo, url, descrizione FROM link_esterni ORDER BY id DESC")
    links = c.fetchall()
    conn.close()

    if links:
        st.sidebar.subheader("📋 Elenco Link")
        titles = [l[1] for l in links]
        scelta_link = st.sidebar.radio("Seleziona voce:", ["Visualizza Tutti"] + titles)
        
        if scelta_link == "Visualizza Tutti":
            for item_id, titolo, url, descrizione in links:
                st.markdown(f"### [{titolo}]({url})")
                if descrizione:
                    st.write(descrizione)
                st.markdown("---")
        else:
            for item_id, titolo, url, descrizione in links:
                if titolo == scelta_link:
                    st.markdown(f"### [{titolo}]({url})")
                    if descrizione:
                        st.write(descrizione)
                    st.markdown("---")
    else:
        st.info("Nessun link inserito al momento.")

# --- PAGINA 4: PANNELLO DI GESTIONE (PROTETTO) ---
elif scelta_pagina == "⚙️ Area Gestione (Carica/Modifica)":
    st.header("⚙️ Area Gestione Contenuti")
    
    # Se non è autenticato, mostra un avviso e blocca l'accesso
    if not st.session_state.autenticato:
        st.warning("🔒 **Area Protetta**: Per accedere agli strumenti di caricamento, modifica e cancellazione, devi prima inserire la password amministratore nella **barra laterale a sinistra**.")
    
    # Se è autenticato, mostra tutti gli strumenti di gestione
    else:
        st.success("✅ Accesso amministrativo attivo. Puoi procedere con la gestione dei contenuti.")
        st.markdown("---")
        
        modo_gestione = st.radio("Seleziona operazione:", ["➕ Inserisci Nuovo", "✏️ Modifica o Elimina Esistente"])

        # 1. INSERISCI NUOVO
        if modo_gestione == "➕ Inserisci Nuovo":
            tipo_contenuto = st.selectbox("Cosa vuoi caricare?", ["Preghiera", "Racconto", "Link Utile"])

            if tipo_contenuto == "Preghiera":
                with st.form("form_preghiera_nuova"):
                    titolo = st.text_input("Titolo della Preghiera")
                    testo = st.text_area("Testo della Preghiera")
                    immagine_file = st.file_uploader("Carica un'immagine associata (opzionale)", type=["jpg", "jpeg", "png", "jfif", "webp", "bmp"])
                    submit = st.form_submit_button("Salva Preghiera")

                    if submit and titolo and testo:
                        img_path = save_uploaded_image(immagine_file)
                        conn = get_connection()
                        c = conn.cursor()
                        c.execute("INSERT INTO preghiere (titolo, testo, immagine) VALUES (?, ?, ?)", (titolo, testo, img_path))
                        conn.commit()
                        conn.close()
                        st.success("Preghiera salvata con successo!")

            elif tipo_contenuto == "Racconto":
                with st.form("form_racconto_nuovo"):
                    titolo = st.text_input("Titolo del Racconto")
                    testo = st.text_area("Testo del Racconto")
                    immagine_file = st.file_uploader("Carica un'immagine (opzionale)", type=["jpg", "jpeg", "png", "jfif", "webp", "bmp"])
                    submit = st.form_submit_button("Salva Racconto")

                    if submit and titolo and testo:
                        img_path = save_uploaded_image(immagine_file)
                        conn = get_connection()
                        c = conn.cursor()
                        c.execute("INSERT INTO racconti (titolo, testo, immagine) VALUES (?, ?, ?)", (titolo, testo, img_path))
                        conn.commit()
                        conn.close()
                        st.success("Racconto salvato con successo!")

            elif tipo_contenuto == "Link Utile":
                with st.form("form_link_nuovo"):
                    titolo = st.text_input("Nome del Sito / Titolo Link")
                    url = st.text_input("URL (es. https://www.vatican.va)")
                    descrizione = st.text_area("Descrizione (opzionale)")
                    submit = st.form_submit_button("Salva Link")

                    if submit and titolo and url:
                        conn = get_connection()
                        c = conn.cursor()
                        c.execute("INSERT INTO link_esterni (titolo, url, descrizione) VALUES (?, ?, ?)", (titolo, url, descrizione))
                        conn.commit()
                        conn.close()
                        st.success("Link salvato con successo!")

        # 2. MODIFICA O ELIMINA ESISTENTE
        elif modo_gestione == "✏️ Modifica o Elimina Esistente":
            cat_mod = st.selectbox("Seleziona la categoria da modificare/eliminare:", ["Preghiera", "Racconto", "Link Utile"])
            conn = get_connection()
            c = conn.cursor()

            if cat_mod == "Preghiera":
                c.execute("SELECT id, titolo, testo, immagine FROM preghiere")
                elementi = c.fetchall()
                conn.close()

                if elementi:
                    mapping = {elem[1]: elem for elem in elementi}
                    scelta_titolo = st.selectbox("Scegli la preghiera da modificare:", list(mapping.keys()))
                    item_id, current_title, current_text, current_img = mapping[scelta_titolo]

                    with st.form("form_modifica_preghiera"):
                        nuovo_titolo = st.text_input("Modifica Titolo", value=current_title)
                        nuovo_testo = st.text_area("Modifica Testo", value=current_text)
                        
                        st.write(f"Immagine attuale: `{current_img if current_img else 'Nessuna'}`")
                        if current_img and os.path.exists(current_img):
                            st.image(current_img, width=150)
                        
                        nuova_immagine_file = st.file_uploader("Sostituisci immagine (lascia vuoto per non cambiare)", type=["jpg", "jpeg", "png", "jfif", "webp", "bmp"])
                        rimuovi_img = st.checkbox("Elimina immagine esistente")

                        col1, col2 = st.columns(2)
                        salva_modifiche = col1.form_submit_button("Salva Modifiche")
                        elimina_item = col2.form_submit_button("Elimina Preghiera")

                        conn = get_connection()
                        c = conn.cursor()
                        if salva_modifiche:
                            img_path = current_img
                            if rimuovi_img:
                                img_path = ""
                            elif nuova_immagine_file is not None:
                                img_path = save_uploaded_image(nuova_immagine_file)

                            c.execute("UPDATE preghiere SET titolo = ?, testo = ?, immagine = ? WHERE id = ?", 
                                      (nuovo_titolo, nuovo_testo, img_path, item_id))
                            conn.commit()
                            conn.close()
                            st.success("Preghiera aggiornata con successo! Ricarica la pagina.")
                        elif elimina_item:
                            c.execute("DELETE FROM preghiere WHERE id = ?", (item_id,))
                            conn.commit()
                            conn.close()
                            st.success("Preghiera eliminata con successo! Ricarica la pagina.")
                else:
                    st.info("Nessuna preghiera disponibile per la modifica.")

            elif cat_mod == "Racconto":
                c.execute("SELECT id, titolo, testo, immagine FROM racconti")
                elementi = c.fetchall()
                conn.close()

                if elementi:
                    mapping = {elem[1]: elem for elem in elementi}
                    scelta_titolo = st.selectbox("Scegli il racconto da modificare:", list(mapping.keys()))
                    item_id, current_title, current_text, current_img = mapping[scelta_titolo]

                    with st.form("form_modifica_racconto"):
                        nuovo_titolo = st.text_input("Modifica Titolo", value=current_title)
                        nuovo_testo = st.text_area("Modifica Testo", value=current_text)
                        
                        st.write(f"Immagine attuale: `{current_img if current_img else 'Nessuna'}`")
                        if current_img and os.path.exists(current_img):
                            st.image(current_img, width=150)
                        
                        nuova_immagine_file = st.file_uploader("Sostituisci immagine (lascia vuoto per non cambiare)", type=["jpg", "jpeg", "png", "jfif", "webp", "bmp"])
                        rimuovi_img = st.checkbox("Elimina immagine esistente")

                        col1, col2 = st.columns(2)
                        salva_modifiche = col1.form_submit_button("Salva Modifiche")
                        elimina_item = col2.form_submit_button("Elimina Racconto")

                        conn = get_connection()
                        c = conn.cursor()
                        if salva_modifiche:
                            img_path = current_img
                            if rimuovi_img:
                                img_path = ""
                            elif nuova_immagine_file is not None:
                                img_path = save_uploaded_image(nuova_immagine_file)

                            c.execute("UPDATE racconti SET titolo = ?, testo = ?, immagine = ? WHERE id = ?", 
                                      (nuovo_titolo, nuovo_testo, img_path, item_id))
                            conn.commit()
                            conn.close()
                            st.success("Racconto aggiornato con successo! Ricarica la pagina.")
                        elif elimina_item:
                            c.execute("DELETE FROM racconti WHERE id = ?", (item_id,))
                            conn.commit()
                            conn.close()
                            st.success("Racconto eliminato con successo! Ricarica la pagina.")
                else:
                    st.info("Nessun racconto disponibile per la modifica.")

            elif cat_mod == "Link Utile":
                c.execute("SELECT id, titolo, url, descrizione FROM link_esterni")
                elementi = c.fetchall()
                conn.close()

                if elementi:
                    mapping = {elem[1]: elem for elem in elementi}
                    scelta_titolo = st.selectbox("Scegli il link da modificare:", list(mapping.keys()))
                    item_id, current_title, current_url, current_desc = mapping[scelta_titolo]

                    with st.form("form_modifica_link"):
                        nuovo_titolo = st.text_input("Modifica Nome Sito", value=current_title)
                        nuovo_url = st.text_input("Modifica URL", value=current_url)
                        nuova_desc = st.text_area("Modifica Descrizione", value=current_desc if current_desc else "")

                        col1, col2 = st.columns(2)
                        salva_modifiche = col1.form_submit_button("Salva Modifiche")
                        elimina_item = col2.form_submit_button("Elimina Link")

                        conn = get_connection()
                        c = conn.cursor()
                        if salva_modifiche:
                            c.execute("UPDATE link_esterni SET titolo = ?, url = ?, descrizione = ? WHERE id = ?", 
                                      (nuovo_titolo, nuovo_url, nuova_desc, item_id))
                            conn.commit()
                            conn.close()
                            st.success("Link aggiornato con successo! Ricarica la pagina.")
                        elif elimina_item:
                            c.execute("DELETE FROM link_esterni WHERE id = ?", (item_id,))
                            conn.commit()
                            conn.close()
                            st.success("Link eliminato con successo! Ricarica la pagina.")
                else:
                    st.info("Nessun link disponibile per la modifica.")