import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta


st.set_page_config(page_title="Formulario de Encuesta", page_icon="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAADi0lEQVRIia1WPUsrQRSdfRohYpJSsVDR1lIUUVAQI8TGTsRCbBJBg1iYHyBiEwVJimhhk7UxgmKhIkHZKhgsxA8sTDBIFAlENCaZzW52975ifGvYncnzyTtFmL1n7jnZmZ25l8MYIwY4jrNYLDU1NaVSKZVKZTKZYrGIELLZbE1NTW1tbXV1dYqiKIoCACwRhGkQRVHTtI+PD57nnU4nK3dsbCwSiWCMVVUVRZEqRTEol8sY45WVFeafMiEYDEqSJMvy3w0AIBaLfV9ah91uv76+1jStmgEAbGxs/EBdx+7uLgDQDQDA7/ebc2ZnZ1lyc3Nz5iDP85UenwaapkUiEaqKKIosg0KhQI0LgqAoypeBJEkPDw/UqW63GwAGBwfNlNfrBYDu7m5qYjabLZVKnwYA0N/fT513fHwMAFtbW2YqGo0CwObmJjVxamqKLBSSZfn09JQ6CSFULBYBIJVKmSlRFAEgmUyycm9vbyVJQqwVQAg5nU4A0DQNABwORyU1OjqqUywDj8cDACidTrNmhMNhXWV5ebmS2t7e1qmlpSWWQqFQQDs7Oyw6nX7SVS4uLiqp5+dnnYrH4ywFQRCQz+ejci0tLUSCqFQuRWtrK4syIBAI/Lq5uaFyXq9XHxMJj8dDHivPF6HcbjdVJJFIoObmZip3dXWlLwL5PTw8ZFFHR0dUEZfLhSwWC5WDP8jlcmSQz+cNVD6fJwNSJ8wYGhr6Zfj+CBYWFhBCyWSysbHR4XBwHHd/f9/Q0NDX10fWJxaLcRxns9m6urqy2Wx9ff3IyIhZp7a2Fg0PD5sJQRDM90wulwuFQicnJ+bDBQA8z5t1ZmZm0Pz8vJkAAPNN6XK5np6eisWieduCweDr66tZZ3V1FYX5sCE6Pj5eLpfNsxFCd3d3rP0EgI6ODkMwGo2iRCJhiB4cHLCu7snJyZ6eHip1fn4eCAQMwbe3NwQAnZ2dlVFRFKk7Vh2Li4uGvZmYmAAAVC6X9/f39ejAwEC1HqQqDInxeFyWZUTKWXt7O4na7fafqSOErFar1WolY3LdfhYcWZYvLy9/rEtFOp3+qmikqK2vr/8v9b29PVVVKV0FtUv4V/j9fkpXgTEmJZB1e38TgUCA2Rfp71GlBFXH2dmZQZ1igDFWVfXl5WV6evr70j6f7/39Xe+F/mKAMS6VSgDw+Pi4trZmOIaV6O3tDYVCmUwGAFjd9W/hH7T1NboR6gAAAABJRU5ErkJggg==", layout="wide")


# --- CONEXIÓN A SUPABASE ---
url = "https://wabjivhfazhiufnqhdmq.supabase.co"
key = "sb_publishable_R-AaS0tqpbFL8aQu52b-xg_5djJvc_p"
supabase: Client = create_client(url, key)


@st.cache_data(ttl=600)
def cargar_preguntas():
    try:
        all_data = []
        page_size = 1000
        start = 0

        while True:
            response = supabase.table('encuestas').select('*').eq('formulario', 'Cuarta').range(start, start + page_size - 1).execute()

            if not response.data:
                break

            all_data.extend(response.data)

            if len(response.data) < page_size:
                break

            start += page_size

        return all_data
    except Exception as e:
        st.error(f"Error al cargar preguntas: {e}")
        return []


@st.cache_data(ttl=600)
def cargar_usuarios():
    try:
        cargos = ['ESPECIALISTA DE EXPERIENCIA', 'MERCHANDISER (EXPERT)', 'ENTRENADOR', 'ENTRENADOR MASTER', 'ENTRENADOR JUNIOR', 'ENTRENADOR INTEGRAL']
        all_data = []
        page_size = 1000
        start = 0

        while True:
            response = supabase.table('usuarios').select('*').in_('cargo', cargos).range(start, start + page_size - 1).execute()

            if not response.data:
                break

            all_data.extend(response.data)

            if len(response.data) < page_size:
                break

            start += page_size

        return all_data
    except Exception as e:
        st.error(f"Error al cargar usuarios: {e}")
        return []


def cargar_resultados_encuestas(cedula_evaluado, tipo_encuesta):
    try:
        response = supabase.table('resultados_encuestas').select('*').eq('cedula_evaluado', cedula_evaluado).eq('tipo_encuesta', tipo_encuesta).execute()
        return response.data
    except Exception as e:
        st.error(f"Error al cargar resultados de encuestas: {e}")
        return []


# --- SIDEBAR ---
with st.sidebar:
    if st.button("🔄 Recargar Preguntas", use_container_width=True):
        cargar_preguntas.clear()
        cargar_usuarios.clear()
        st.rerun()


# --- LOGO ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("https://ik.imagekit.io/ydajulekbx/motorola_adecco_logo%20(2).svg", width=300)


st.title("📝 Encuesta - Cuarta Evaluación")


usuarios = cargar_usuarios()
preguntas_data = cargar_preguntas()


if not preguntas_data:
    st.warning("⚠️ No se encontraron preguntas para la encuesta 'Cuarta Evaluación'")
    st.stop()


st.markdown("---")


# ──────────────────────────────────────────
# SELECCIONAR USUARIO A EVALUAR (por cédula)
# ──────────────────────────────────────────
st.markdown("### 👤 Selecciona el usuario a evaluar:")

col1, col2 = st.columns([1, 2])

cargos_filtrados_evaluado = ['ESPECIALISTA DE EXPERIENCIA', 'MERCHANDISER (EXPERT)']

with col1:
    cedula_input_evaluado = st.text_input("Ingresa la cédula del usuario a evaluar", key="cedula_evaluado_input")

with col2:
    usuario_evaluado = None
    if cedula_input_evaluado.strip():
        usuario_evaluado = next(
            (u for u in usuarios
             if str(u.get('cedula', '')).strip() == cedula_input_evaluado.strip()
             and u['cargo'] in cargos_filtrados_evaluado),
            None
        )
        if usuario_evaluado:
            st.success(f"✅ **{usuario_evaluado['nombre']}** — {usuario_evaluado['cargo']}")

            # ✅ VALIDAR ENCUESTA "TERCERA" (6 DÍAS DE ESPERA)
            try:
                # response = supabase.table('resultados_encuestas')\
                #     .select('created_at')\
                #     .eq('cedula_evaluado', int(usuario_evaluado['cedula']))\
                #     .eq('tipo_encuesta', 'Tercera')\
                #     .order('created_at', desc=True)\
                #     .limit(1)\
                #     .execute()

                # if not response.data:
                #     st.error("❌ Este usuario NO ha completado la encuesta **'Tercera'**")
                #     st.warning("⚠️ Debe completar primero la encuesta 'Tercera' antes de acceder a la 'Cuarta'")
                #     st.stop()
                # else:
                #     fecha_tercera_encuesta_str = response.data[0]['created_at']
                #     fecha_tercera_encuesta = datetime.fromisoformat(fecha_tercera_encuesta_str.replace('Z', '+00:00'))
                #     fecha_tercera_encuesta_local = fecha_tercera_encuesta.astimezone().date()
                #     fecha_actual = datetime.now().date()
                #     dias_desde_tercera = (fecha_actual - fecha_tercera_encuesta_local).days

                #     # if dias_desde_tercera < 6:
                #     #     dias_faltantes = 6 - dias_desde_tercera
                #     if dias_desde_tercera <= 0:
                #         dias_faltantes = 0 - dias_desde_tercera
                #         st.warning(f"⏳ **Este usuario completó la 'Tercera' encuesta hace {dias_desde_tercera} día(s)**")
                #         st.error(f"❌ Debe esperar **{dias_faltantes} día(s) más** para poder realizar la 'Cuarta' encuesta")
                #         st.info(f"📅 Fecha de la Tercera encuesta: **{fecha_tercera_encuesta_local.strftime('%d/%m/%Y')}**")
                #         st.info(f"📅 Podrá realizar la Cuarta encuesta a partir del: **{(fecha_tercera_encuesta_local + timedelta(days=6)).strftime('%d/%m/%Y')}**")
                #         st.stop()
                #     else:
                #         st.success(f"✅ Han pasado **{dias_desde_tercera} días** desde la Tercera encuesta")
                #         st.info(f"📅 Fecha de la Tercera encuesta: **{fecha_tercera_encuesta_local.strftime('%d/%m/%Y')}**")

                #         # # ✅ VERIFICAR SI YA RESPONDIÓ LA "CUARTA" ENCUESTA
                #         # response_cuarta = supabase.table('resultados_encuestas')\
                #         #     .select('created_at')\
                #         #     .eq('cedula_evaluado', int(usuario_evaluado['cedula']))\
                #         #     .eq('tipo_encuesta', 'Cuarta')\
                #         #     .execute()

                #         # if response_cuarta.data:
                #         #     st.warning("⚠️ Este usuario YA completó la encuesta 'Cuarta'")
                #         #     st.info(f"📅 Fecha de completación: **{datetime.fromisoformat(response_cuarta.data[0]['created_at'].replace('Z', '+00:00')).astimezone().strftime('%d/%m/%Y %H:%M')}**")

                #         #     if st.checkbox("⚠️ Permitir re-evaluación (esto creará un nuevo registro)"):
                #         #         st.warning("🔄 Se permitirá una nueva evaluación")
                #         #     else:
                #         #         st.stop()

                True

            except Exception as e:
                st.error(f"❌ Error al verificar encuestas anteriores: {e}")
                st.stop()
        else:
            st.error("❌ No se encontró ningún usuario con esa cédula o no tiene el cargo permitido")


# ──────────────────────────────────────────
# SELECCIONAR USUARIO EVALUADOR (por cédula)
# ──────────────────────────────────────────
st.markdown("### 👤 Selecciona el usuario evaluador:")

col1, col2 = st.columns([1, 2])
with col1:
    cargos_filtrados_evaluador = ['ENTRENADOR', 'ENTRENADOR MASTER','ENTRENADOR JUNIOR']
    opciones_usuarios_evaluador = [f"{user['nombre']} - {user['cargo']}" for user in usuarios if user['cargo'] in cargos_filtrados_evaluador]
    usuario_seleccionado_evaluador = st.selectbox("Selecciona un evaluador", options=["-- Selecciona --"] + opciones_usuarios_evaluador)


with col2:
    if usuario_seleccionado_evaluador != "-- Selecciona --":
        usuario_evaluador = next((user for user in usuarios if f"{user['nombre']} - {user['cargo']}" == usuario_seleccionado_evaluador), None)
        if usuario_evaluador:
            cedula_evaluador = st.text_input("Cédula del usuario evaluador", value=usuario_evaluador.get('cedula', ''), disabled=True)
    else:
        cedula_evaluador = st.text_input("Cédula del usuario evaluador", value="", disabled=True)
        usuario_evaluador = None

st.markdown("---")
st.markdown("### 📋 Formato de la encuesta")

col1, col2 = st.columns([1, 2])
with col1:
    forma_encuesta = st.radio(
        "¿Cómo se realizó la encuesta?",
        options=["PRESENCIAL", "VIRTUAL"],
        key="forma_encuesta",
        horizontal=True,
    )


# ──────────────────────────────────────────
# FORMULARIO DE PREGUNTAS
# ──────────────────────────────────────────
st.markdown("---")
st.info("👉 Selecciona una respuesta para cada pregunta y haz clic en **Enviar** para ver tu puntuación.")


respuestas_usuario = {}

for idx, pregunta in enumerate(preguntas_data):
    pregunta_texto = pregunta.get('pregunta', '')
    opciones_str = pregunta.get('lista', '')
    respuesta_correcta = pregunta.get('correcta', '')

    opciones = [opcion.strip() for opcion in opciones_str.strip('[]').split('&') if opcion.strip()]

    st.markdown(f"### {idx + 1}. {pregunta_texto}")

    respuesta = st.radio(
        label=f"Opciones para pregunta {idx + 1}",
        options=opciones,
        key=f"pregunta_{idx}",
        label_visibility="collapsed"
    )

    respuestas_usuario[idx] = {
        'respuesta_usuario': respuesta,
        'respuesta_correcta': respuesta_correcta.strip(),
        'pregunta': pregunta_texto
    }


st.markdown("---")


with st.form("formulario_encuesta"):

    submitted = st.form_submit_button("✅ Enviar Encuesta", use_container_width=True, type="primary")

    if submitted:

        # Validar que ambos usuarios estén seleccionados
        if not usuario_evaluado:
            st.error("❌ Debes ingresar una cédula válida para el usuario a evaluar")
            st.stop()

        if not usuario_evaluador:
            st.error("❌ Debes ingresar una cédula válida para el evaluador")
            st.stop()

        # Calcular el puntaje
        correctas = 0
        total_preguntas = len(respuestas_usuario)

        for idx, datos in respuestas_usuario.items():
            if datos['respuesta_usuario'] == datos['respuesta_correcta']:
                correctas += 1

        puntaje = (correctas / total_preguntas) * 100

        # Guardar resultados en la base de datos
        try:
            registros_a_insertar = []

            for idx, datos in respuestas_usuario.items():
                es_correcta = datos['respuesta_usuario'] == datos['respuesta_correcta']

                registro = {
                    'nombre_evaluador': usuario_evaluador['nombre'],
                    'cedula_evaluador': int(usuario_evaluador['cedula']),
                    'cargo_evaluador': usuario_evaluador['cargo'],
                    'nombre_evaluado': usuario_evaluado['nombre'],
                    'cedula_evaluado': int(usuario_evaluado['cedula']),
                    'cargo_evaluado': usuario_evaluado['cargo'],
                    'pregunta': datos['pregunta'],
                    'respuesta_seleccionada': datos['respuesta_usuario'],
                    'respuesta': datos['respuesta_correcta'],
                    'respuesta_correcta': es_correcta,
                    'puntaje': int(puntaje),
                    'tipo_encuesta': 'Cuarta',
                    'forma_encuesta': forma_encuesta,
                }
                registros_a_insertar.append(registro)

            supabase.table('resultados_encuestas').insert(registros_a_insertar).execute()

            st.balloons()
            st.success("## 🎉 ¡Encuesta Enviada y Guardada!")

        except Exception as e:
            st.error(f"❌ Error al guardar los resultados: {e}")
            st.stop()

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Correctas", f"{correctas}/{total_preguntas}")
        with col_b:
            st.metric("Puntaje", f"{puntaje:.1f}%")
        with col_c:
            if puntaje >= 70:
                st.metric("Estado", "✅ Aprobado")
            else:
                st.metric("Estado", "❌ No Aprobado")

        with st.expander("📊 Ver Detalles de Respuestas"):
            for idx, datos in respuestas_usuario.items():
                es_correcta = datos['respuesta_usuario'] == datos['respuesta_correcta']
                icono = "✅" if es_correcta else "❌"

                st.markdown(f"**{icono} Pregunta {idx + 1}:** {datos['pregunta']}")
                st.markdown(f"- **Tu respuesta:** {datos['respuesta_usuario']}")
                if not es_correcta:
                    st.markdown(f"- **Respuesta correcta:** {datos['respuesta_correcta']}")
                st.markdown("---")