import streamlit as st
from supabase import create_client, Client
from datetime import datetime, time, timedelta
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, MO, TU, WE, TH, FR, SA, SU
import uuid
import pandas as pd
import os
from streamlit_searchbox import st_searchbox
from io import BytesIO

st.set_page_config(page_title="Administrador", page_icon="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAADi0lEQVRIia1WPUsrQRSdfRohYpJSsVDR1lIUUVAQI8TGTsRCbBJBg1iYHyBiEwVJimhhk7UxgmKhIkHZKhgsxA8sTDBIFAlENCaZzW52975ifGvYncnzyTtFmL1n7jnZmZ25l8MYIwY4jrNYLDU1NaVSKZVKZTKZYrGIELLZbE1NTW1tbXV1dYqiKIoCACwRhGkQRVHTtI+PD57nnU4nK3dsbCwSiWCMVVUVRZEqRTEol8sY45WVFeafMiEYDEqSJMvy3w0AIBaLfV9ah91uv76+1jStmgEAbGxs/EBdx+7uLgDQDQDA7/ebc2ZnZ1lyc3Nz5iDP85UenwaapkUiEaqKKIosg0KhQI0LgqAoypeBJEkPDw/UqW63GwAGBwfNlNfrBYDu7m5qYjabLZVKnwYA0N/fT513fHwMAFtbW2YqGo0CwObmJjVxamqKLBSSZfn09JQ6CSFULBYBIJVKmSlRFAEgmUyycm9vbyVJQqwVQAg5nU4A0DQNABwORyU1OjqqUywDj8cDACidTrNmhMNhXWV5ebmS2t7e1qmlpSWWQqFQQDs7Oyw6nX7SVS4uLiqp5+dnnYrH4ywFQRCQz+ejci0tLUSCqFQuRWtrK4syIBAI/Lq5uaFyXq9XHxMJj8dDHivPF6HcbjdVJJFIoObmZip3dXWlLwL5PTw8ZFFHR0dUEZfLhSwWC5WDP8jlcmSQz+cNVD6fJwNSJ8wYGhr6Zfj+CBYWFhBCyWSysbHR4XBwHHd/f9/Q0NDX10fWJxaLcRxns9m6urqy2Wx9ff3IyIhZp7a2Fg0PD5sJQRDM90wulwuFQicnJ+bDBQA8z5t1ZmZm0Pz8vJkAAPNN6XK5np6eisWieduCweDr66tZZ3V1FYX5sCE6Pj5eLpfNsxFCd3d3rP0EgI6ODkMwGo2iRCJhiB4cHLCu7snJyZ6eHip1fn4eCAQMwbe3NwQAnZ2dlVFRFKk7Vh2Li4uGvZmYmAAAVC6X9/f39ejAwEC1HqQqDInxeFyWZUTKWXt7O4na7fafqSOErFar1WolY3LdfhYcWZYvLy9/rEtFOp3+qmikqK2vr/8v9b29PVVVKV0FtUv4V/j9fkpXgTEmJZB1e38TgUCA2Rfp71GlBFXH2dmZQZ1igDFWVfXl5WV6evr70j6f7/39Xe+F/mKAMS6VSgDw+Pi4trZmOIaV6O3tDYVCmUwGAFjd9W/hH7T1NboR6gAAAABJRU5ErkJggg==", layout="wide")

# --- VERIFICAR AUTENTICACIÓN ---
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("⚠️ Debes iniciar sesión primero")
    st.stop()

# Verificar si el usuario es administrador
if not st.session_state.get('is_admin', False):
    st.error("🚫 Acceso Denegado: Solo administradores pueden acceder a esta página")
    st.info("👤 Si necesitas acceso, contacta al administrador del sistema")
    st.stop()

# --- CONEXIÓN SUPABASE ---
url = "https://wabjivhfazhiufnqhdmq.supabase.co"
key = "sb_publishable_R-AaS0tqpbFL8aQu52b-xg_5djJvc_p"
supabase: Client = create_client(url, key)

# --- SIDEBAR CON INFO DEL USUARIO ---
with st.sidebar:
    st.success(f"👤 **{st.session_state.user_nombre}**")
    st.info(f"📧 {st.session_state.user_cargo}")
    if st.session_state.is_admin:
        st.warning("🔑 **ADMINISTRADOR**")
    
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("Inicio.py")

# --- LOGO ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("https://ik.imagekit.io/ydajulekbx/motorola_adecco_logo%20(2).svg", width=300)

st.title("🔧 Panel de Administración")

# --- CREAR PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["👥 Cargar Usuarios", "📝 Cargar Encuestas", "📊 Descargar Resultados"])

# ========== PESTAÑA 1: CARGAR USUARIOS ==========
with tab1:
    st.header("📥 Cargar Usuarios desde Excel")
    st.markdown("""
    **Formato requerido del archivo Excel:**
    - `Cedula` (número)
    - `Nombre` (texto)
    - `Cargo` (texto)
    - `Fecha` (fecha)
    - `Estado` (texto)
    """)
    
    uploaded_file_usuarios = st.file_uploader("Selecciona el archivo de usuarios", type=["xlsx", "xls"], key="usuarios_upload")
    
    if uploaded_file_usuarios is not None:
        try:
            df_usuarios = pd.read_excel(uploaded_file_usuarios)
            
            # Mostrar preview
            st.subheader("👀 Vista previa de los datos")
            st.dataframe(df_usuarios.head(10), use_container_width=True)
            st.info(f"Total de registros: {len(df_usuarios)}")
            
            # Renombrar columnas
            df_usuarios = df_usuarios.rename(columns={
                'Cedula': 'cedula', 
                'Nombre': 'nombre', 
                'Cargo': 'cargo', 
                'Fecha': 'fecha',
                'Estado': 'estado'
            })
            
            # Convertir fechas
            if 'fecha' in df_usuarios.columns:
                df_usuarios['fecha'] = pd.to_datetime(df_usuarios['fecha'], errors='coerce').dt.strftime('%Y-%m-%d')
            
            # Reemplazar NaN
            df_usuarios = df_usuarios.where(pd.notnull(df_usuarios), None)
            
            # Botón para cargar
            if st.button("✅ Cargar Usuarios a la Base de Datos", type="primary", use_container_width=True):
                with st.spinner("Cargando usuarios..."):
                    try:
                        registros = df_usuarios.to_dict('records')
                        
                        # Usar upsert para actualizar existentes y crear nuevos
                        # on_conflict especifica la columna que identifica registros únicos
                        response = supabase.table('usuarios').upsert(
                            registros,
                            on_conflict='cedula'  # Asume que 'cedula' es la clave primaria
                        ).execute()
                        
                        st.success(f"✅ Se procesaron {len(registros)} usuarios correctamente")
                        st.info("ℹ️ Los usuarios existentes fueron actualizados y los nuevos fueron creados")
                    except Exception as e:
                        st.error(f"❌ Error al procesar usuarios: {str(e)}")
        
        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {str(e)}")

# ========== PESTAÑA 2: CARGAR ENCUESTAS ==========
with tab2:
    st.header("📥 Cargar Encuestas desde Excel")
    st.markdown("""
    **Formato requerido del archivo Excel:**
    - `Pregunta` (texto)
    - `Lista` (texto)
    - `Correcta` (texto)
    - `Formulario` (texto)
    """)
    
    uploaded_file_encuestas = st.file_uploader("Selecciona el archivo de encuestas", type=["xlsx", "xls"], key="encuestas_upload")
    
    if uploaded_file_encuestas is not None:
        try:
            df_encuestas = pd.read_excel(uploaded_file_encuestas)
            
            # Mostrar preview
            st.subheader("👀 Vista previa de los datos")
            st.dataframe(df_encuestas.head(10), use_container_width=True)
            st.info(f"Total de registros: {len(df_encuestas)}")
            
            # Renombrar columnas
            df_encuestas = df_encuestas.rename(columns={
                'Pregunta': 'pregunta', 
                'Lista': 'lista', 
                'Correcta': 'correcta', 
                'Formulario': 'formulario'
            })
            
            # Reemplazar NaN
            df_encuestas = df_encuestas.where(pd.notnull(df_encuestas), None)
            
            # Botón para cargar
            if st.button("✅ Cargar Encuestas a la Base de Datos", type="primary", use_container_width=True):
                with st.spinner("Eliminando encuestas anteriores y cargando nuevas..."):
                    try:
                        # Paso 1: Eliminar todas las encuestas existentes
                        delete_response = supabase.table('encuestas').delete().neq('id', 0).execute()
                        st.info(f"🗑️ Encuestas anteriores eliminadas")
                        
                        # Paso 2: Insertar las nuevas encuestas
                        registros = df_encuestas.to_dict('records')
                        insert_response = supabase.table('encuestas').insert(registros).execute()
                        
                        st.success(f"✅ Se insertaron {len(registros)} encuestas nuevas correctamente")
                        st.info("ℹ️ Todas las encuestas anteriores fueron reemplazadas")
                    except Exception as e:
                        st.error(f"❌ Error al procesar encuestas: {str(e)}")
        
        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {str(e)}")

# ========== PESTAÑA 3: DESCARGAR RESULTADOS ==========
with tab3:
    st.header("📊 Descargar Resultados de Encuestas")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("Descarga los resultados de las encuestas en formato Excel")
    
    with col2:
        if st.button("🔄 Actualizar Datos", use_container_width=True):
            st.rerun()
    
    try:
        # Consultar datos de resultados
        response = supabase.table('resultados_encuestas').select('*').execute()
        
        if response.data:
            df_resultados = pd.DataFrame(response.data)
            
            # Mostrar la tabla
            st.subheader(f"📋 Resultados ({len(df_resultados)} registros)")
            st.dataframe(df_resultados, use_container_width=True, height=400)
            
            # Preparar descarga en Excel
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_resultados.to_excel(writer, sheet_name='Resultados', index=False)
            
            # Botón de descarga
            st.download_button(
                label="📥 Descargar Resultados en Excel",
                data=buffer.getvalue(),
                file_name=f"resultados_encuestas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.ms-excel",
                type="primary",
                use_container_width=True
            )
            
        else:
            st.warning("⚠️ No hay resultados disponibles")
    
    except Exception as e:
        st.error(f"❌ Error al cargar resultados: {str(e)}")
