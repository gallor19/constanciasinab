import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import datetime
import io
import zipfile

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Gestor de Constancias INAB",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. OCULTAR ELEMENTOS POR DEFECTO DE STREAMLIT ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            <footer>{visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- CREDENCIALES DE ACCESO ---
USUARIOS_VALIDOS = {
    "CERUIZ98": "gallor19"
}

# --- 3. CONTROL DE AUTENTICACIÓN (CENTRALIZADO) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = ""

# TÍTULO PRINCIPAL
st.markdown(
    "<h1 style='text-align: center; color: #1E8449;'>🌳 Generador de Constancias Laborales - INAB</h1>",
    unsafe_allow_html=True
)
st.markdown("---")

# Si no está autenticado, mostrar formulario de login centrado
if not st.session_state.autenticado:
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.subheader("🔒 Iniciar Sesión")
        with st.form("login_form_central"):
            usuario_input = st.text_input("Usuario:")
            password_input = st.text_input("Contraseña:", type="password")
            submit_login = st.form_submit_button("Ingresar", use_container_width=True)
            
            if submit_login:
                if usuario_input in USUARIOS_VALIDOS and USUARIOS_VALIDOS[usuario_input] == password_input:
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = usuario_input
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")
    st.stop()

# --- 4. PANEL SUPERIOR DE USUARIO AUTENTICADO ---
col_u1, col_u2 = st.columns([4, 1])
with col_u1:
    st.success(f"👤 Sesión activa: **{st.session_state.usuario_actual}**")
with col_u2:
    if st.button("Cerrar Sesión", use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.usuario_actual = ""
        st.rerun()

st.markdown("---")

# --- 5. CUERPO PRINCIPAL (Gestión de Archivos) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Cargar Plantilla")
    uploaded_doc = st.file_uploader("Selecciona tu archivo Word (.docx)", type=["docx"])
    with st.expander("Ver instrucciones de la plantilla"):
        st.write("Usa etiquetas entre llaves dobles en tu Word, por ejemplo: `{{nombre}}`, `{{dpi}}`, `{{puesto}}`.")

with col2:
    st.subheader("2. Cargar Base de Datos")
    uploaded_excel = st.file_uploader("Selecciona tu archivo Excel (.xlsx)", type=["xlsx"])
    if uploaded_excel:
        df_temp = pd.read_excel(uploaded_excel)
        with st.expander(f"Ver vista previa (Total registros: {len(df_temp)})"):
            st.dataframe(df_temp.head())

st.markdown("---")

# --- 6. LÓGICA DE PROCESAMIENTO Y GENERACIÓN (Modificado para Web/RAM) ---
if uploaded_excel and uploaded_doc:
    st.success("✅ Archivos listos. Puedes proceder a generar las constancias.")
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🚀 GENERAR Y COMPRIMIR CONSTANCIAS", use_container_width=True):
            df = pd.read_excel(uploaded_excel)
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for index, row in df.iterrows():
                    context = row.to_dict()
                    doc = DocxTemplate(uploaded_doc)
                    doc.render(context)
                    
                    nombre_empleado = str(row.get('nombre', f'empleado_{index}')).strip()
                    nombre_archivo = f"Constancia_{nombre_empleado}.docx"
                    
                    # Generar y guardar el documento en memoria RAM (BytesIO)
                    doc_io = io.BytesIO()
                    doc.save(doc_io)
                    doc_io.seek(0)
                    
                    # Añadir al ZIP directamente desde la memoria
                    zip_file.writestr(nombre_archivo, doc_io.getvalue())
            
            st.balloons()
            st.success("¡Todas las constancias se han generado con éxito!")
            
            st.download_button(
                label="📥 Descargar Archivo ZIP con las Constancias",
                data=zip_buffer.getvalue(),
                file_name=f"constancias_inab_{datetime.date.today()}.zip",
                mime="application/zip",
                use_container_width=True
            )
else:
    st.info("💡 Por favor, carga ambos archivos (Word y Excel) para habilitar el botón de generación.")
