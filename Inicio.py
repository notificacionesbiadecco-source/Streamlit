import streamlit as st
from supabase import create_client, Client
import pandas as pd
import os

st.set_page_config(
    page_title="Login - Motorola",
    page_icon="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAADi0lEQVRIia1WPUsrQRSdfRohYpJSsVDR1lIUUVAQI8TGTsRCbBJBg1iYHyBiEwVJimhhk7UxgmKhIkHZKhgsxA8sTDBIFAlENCaZzW52975ifGvYncnzyTtFmL1n7jnZmZ25l8MYIwY4jrNYLDU1NaVSKZVKZTKZYrGIELLZbE1NTW1tbXV1dYqiKIoCACwRhGkQRVHTtI+PD57nnU4nK3dsbCwSiWCMVVUVRZEqRTEol8sY45WVFeafMiEYDEqSJMvy3w0AIBaLfV9ah91uv76+1jStmgEAbGxs/EBdx+7uLgDQDQDA7/ebc2ZnZ1lyc3Nz5iDP85UenwaapkUiEaqKKIosg0KhQI0LgqAoypeBJEkPDw/UqW63GwAGBwfNlNfrBYDu7m5qYjabLZVKnwYA0N/fT513fHwMAFtbW2YqGo0CwObmJjVxamqKLBSSZfn09JQ6CSFULBYBIJVKmSlRFAEgmUyycm9vbyVJQqwVQAg5nU4A0DQNABwORyU1OjqqUywDj8cDACidTrNmhMNhXWV5ebmS2t7e1qmlpSWWQqFQQDs7Oyw6nX7SVS4uLiqp5+dnnYrH4ywFQRCQz+ejci0tLUSCqFQuRWtrK4syIBAI/Lq5uaFyXq9XHxMJj8dDHivPF6HcbjdVJJFIoObmZip3dXWlLwL5PTw8ZFFHR0dUEZfLhSwWC5WDP8jlcmSQz+cNVD6fJwNSJ8wYGhr6Zfj+CBYWFhBCyWSysbHR4XBwHHd/f9/Q0NDX10fWJxaLcRxns9m6urqy2Wx9ff3IyIhZp7a2Fg0PD5sJQRDM90wulwuFQicnJ+bDBQA8z5t1ZmZm0Pz8vJkAAPNN6XK5np6eisWieduCweDr66tZZ3V1FYX5sCE6Pj5eLpfNsxFCd3d3rP0EgI6ODkMwGo2iRCJhiB4cHLCu7snJyZ6eHip1fn4eCAQMwbe3NwQAnZ2dlVFRFKk7Vh2Li4uGvZmYmAAAVC6X9/f39ejAwEC1HqQqDInxeFyWZUTKWXt7O4na7fafqSOErFar1WolY3LdfhYcWZYvLy9/rEtFOp3+qmikqK2vr/8v9b29PVVVKV0FtUv4V/j9fkpXgTEmJZB1e38TgUCA2Rfp71GlBFXH2dmZQZ1igDFWVfXl5WV6evr70j6f7/39Xe+F/mKAMS6VSgDw+Pi4trZmOIaV6O3tDYVCmUwGAFjd9W/hH7T1NboR6gAAAABJRU5ErkJggg==",
    layout="wide"
)

# --- CONFIGURACIÓN SUPABASE ---
SUPABASE_URL = "https://wabjivhfazhiufnqhdmq.supabase.co"
SUPABASE_KEY = "sb_publishable_R-AaS0tqpbFL8aQu52b-xg_5djJvc_p"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- CREDENCIALES DEL ADMINISTRADOR ---
ADMIN_NOMBRE = "Admin"
ADMIN_CEDULA = "1234567890"
ADMIN_CARGO = "ADMINISTRADOR"

# --- FUNCIÓN DE AUTENTICACIÓN CON SUPABASE ---
def autenticar_usuario_supabase(cedula_usuario, cedula_password):
    """Verifica si la cédula como usuario y contraseña coinciden en Supabase o si es el admin."""
    try:
        # Verificar primero si es el administrador
        if cedula_usuario == ADMIN_CEDULA and cedula_password == ADMIN_CEDULA:
            return {
                "cedula": ADMIN_CEDULA,
                "nombre": ADMIN_NOMBRE,
                "nombre_usuario": ADMIN_CEDULA,
                "cargo": ADMIN_CARGO,
                "is_admin": True
            }
        
        # Verificar que ambas cédulas sean iguales
        if cedula_usuario != cedula_password:
            return None
        
        # Si no es admin, buscar en la base de datos
        cedula_int = int(cedula_usuario)
        
        # Consultar el usuario por cédula
        response = supabase.table('usuarios').select('*').eq('cedula', cedula_int).execute()
        
        if response.data and len(response.data) > 0:
            usuario = response.data[0]
            return {
                "cedula": str(usuario['cedula']),
                "nombre": usuario['nombre'],
                "nombre_usuario": str(usuario['cedula']),
                "cargo": usuario['cargo'],
                "fecha": usuario['fecha'],
                "is_admin": False
            }
        
        return None
    except ValueError:
        # Si la cédula no es un número válido, verificar si es el admin
        if cedula_usuario == ADMIN_CEDULA and cedula_password == ADMIN_CEDULA:
            return {
                "cedula": ADMIN_CEDULA,
                "nombre": ADMIN_NOMBRE,
                "nombre_usuario": ADMIN_CEDULA,
                "cargo": ADMIN_CARGO,
                "is_admin": True
            }
        return None
    except Exception as e:
        st.error(f"Error al autenticar: {e}")
        return None


# --- INTERFAZ DE LOGIN ---
def mostrar_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.image("https://ik.imagekit.io/ydajulekbx/motorola_adecco_logo%20(2).svg", width=300)
        st.title("🔐 Iniciar Sesión")
        st.markdown("### Evaluaciones Motorola")
        
        with st.form("login_form"):
            cedula_usuario = st.text_input("👤 Cédula (Usuario)", placeholder="Ingresa tu número de cédula")
            cedula_password = st.text_input("🔑 Cédula (Contraseña)", type="password", placeholder="Ingresa tu número de cédula")
            submit = st.form_submit_button("🚀 Ingresar", use_container_width=True)
            
            if submit:
                if not cedula_usuario or not cedula_password:
                    st.error("⚠️ Por favor ingresa tu cédula en ambos campos")
                else:
                    usuario = autenticar_usuario_supabase(cedula_usuario, cedula_password)
                    
                    if usuario:
                        # Guardar en session state
                        st.session_state.authenticated = True
                        st.session_state.user_cedula = usuario['cedula']
                        st.session_state.user_nombre = usuario['nombre']
                        st.session_state.user_nombre_usuario = usuario['nombre_usuario']
                        st.session_state.user_cargo = usuario['cargo']
                        st.session_state.user_fecha = usuario.get('fecha', '')
                        st.session_state.is_admin = usuario['is_admin']
                        st.success(f"✅ Bienvenido {usuario['nombre']}")
                        st.rerun()
                    else:
                        st.error("❌ Cédula incorrecta o no registrada")
        
        st.markdown("---")
        st.info("""
        **ℹ️ Instrucciones:**
        - Ingresa tu número de cédula como usuario
        - Ingresa tu número de cédula como contraseña
        - Ambos campos deben contener la misma cédula
        - La cédula debe estar registrada en la base de datos
        """)


# --- FUNCIÓN DE LOGOUT ---
def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


# --- MAIN ---
def main():
    # Inicializar session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        mostrar_login()
    else:
        # Mostrar barra lateral con info del usuario
        with st.sidebar:
            st.success(f"👤 **{st.session_state.user_nombre}**")
            st.info(f"📄 **Cédula:** {st.session_state.user_cedula}")
            st.info(f"💼 **Cargo:** {st.session_state.user_cargo}")
            
            # Mostrar badge de admin si aplica
            if st.session_state.is_admin:
                st.warning("🔑 **ADMINISTRADOR**")
            
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                logout()
        
        # Mostrar contenido principal (Inicio)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.image("https://ik.imagekit.io/ydajulekbx/motorola_adecco_logo%20(2).svg", width=200)
        
        with col2:
            st.markdown("""
            <div style='text-align: center; padding: 20px;'>
                <h1 style='color: #003366;'>Sistema de Evaluaciones</h1>
                <h3 style='color: #666;'>Formularios de Evaluación</h3>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Información adicional con botones clickeables
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.info("### 📝 Primer Formulario")
            if st.button("🔗 Ir al Formulario", use_container_width=True, key="btn_formulario_1"):
                st.switch_page("pages/1_📝_Primera.py")

        with col2:
            st.info("### 📝 Segundo Formulario")
            if st.button("🔗 Ir al Formulario", use_container_width=True, key="btn_formulario_2"):
                st.switch_page("pages/2_📝_Segunda.py")

        with col3:
            st.info("### 📝 Tercer Formulario")
            if st.button("🔗 Ir al Formulario", use_container_width=True, key="btn_formulario_3"):
                st.switch_page("pages/3_📝_Tercera.py")

        with col4:
            st.info("### 📝 Cuarto Formulario")
            if st.button("🔗 Ir al Formulario", use_container_width=True, key="btn_formulario_4"):
                st.switch_page("pages/4_📝_Cuarta.py")


if __name__ == "__main__":
    main()
