import streamlit as st
import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from supabase import create_client
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval
import pydeck as pdk


st.title("GPS Actual + Selecciona Dirección Cercana")


# ── Conexión Supabase ──────────────────────────────────────────────
SUPABASE_URL = "https://wabjivhfazhiufnqhdmq.supabase.co"
SUPABASE_KEY = "sb_publishable_R-AaS0tqpbFL8aQu52b-xg_5djJvc_p"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ── CSS botón de carga ─────────────────────────────────────────────
st.markdown("""
<style>
@keyframes spin { to { transform: rotate(360deg); } }
.gps-loading-box {
    display: flex; flex-direction: column; align-items: center; gap: 14px;
    background: linear-gradient(135deg, #0d1b2a, #1b2a3b);
    border: 1px solid #0066ff; border-radius: 16px;
    padding: 28px 20px; margin: 1rem 0; text-align: center;
}
.gps-spinner {
    width: 52px; height: 52px;
    border: 5px solid #1b3a5c;
    border-top: 5px solid #00c6ff;
    border-radius: 50%;
    animation: spin 0.9s linear infinite;
}
.gps-loading-box p  { color: #00c6ff; font-size: 1rem; font-weight: 600; margin: 0; }
.gps-loading-box small { color: #6b8fa8; font-size: 0.82rem; }
</style>
""", unsafe_allow_html=True)


# ── 1. Captura GPS ─────────────────────────────────────────────────
if "my_lat" not in st.session_state:
    st.session_state["my_lat"] = None
    st.session_state["my_lon"] = None

if st.session_state["my_lat"] is None:

    if "gps_triggered" not in st.session_state:
        st.session_state["gps_triggered"] = False

    if not st.session_state["gps_triggered"]:
        st.markdown("<br>", unsafe_allow_html=True)
        col = st.columns([1, 3, 1])[1]
        if col.button("📡  Obtener mi ubicación GPS", use_container_width=True, type="primary"):
            st.session_state["gps_triggered"] = True
            st.rerun()
    else:
        st.markdown("""
        <div class="gps-loading-box">
            <div class="gps-spinner"></div>
            <p>🛰️ Obteniendo ubicación…</p>
            <small>Acepta el permiso del navegador cuando aparezca</small>
        </div>
        """, unsafe_allow_html=True)

        coords = streamlit_js_eval(
            js_expressions="""
                new Promise((resolve) => {
                    if (!navigator.geolocation) {
                        resolve({ error_code: 0, error_msg: "Tu navegador no soporta geolocalización." });
                        return;
                    }
                    navigator.geolocation.getCurrentPosition(
                        (pos) => resolve({
                            lat: pos.coords.latitude,
                            lon: pos.coords.longitude
                        }),
                        (err) => resolve({ error_code: err.code, error_msg: err.message }),
                        { enableHighAccuracy: true, timeout: 15000 }
                    );
                })
            """,
            key="get_gps"
        )

        if coords is not None:
            if isinstance(coords, dict) and "lat" in coords:
                st.session_state["my_lat"] = coords["lat"]
                st.session_state["my_lon"] = coords["lon"]
                st.session_state["gps_triggered"] = False
                st.rerun()

            elif isinstance(coords, dict) and "error_code" in coords:
                code = coords["error_code"]
                msg  = coords.get("error_msg", "Error desconocido")
                st.session_state["gps_triggered"] = False

                if code == 1:
                    st.warning(
                        "🔒 **Permiso de ubicación denegado.**\n\n"
                        "Debes permitir el acceso a la ubicación en tu navegador o celular:\n\n"
                        "Luego recarga la página e intenta de nuevo."
                    )
                elif code == 2:
                    st.error(
                        "📡 **No se pudo obtener tu posición.**\n\n"
                        "Posibles causas:\n"
                        "- **GPS apagado** en tu dispositivo → actívalo en Ajustes → Ubicación\n"
                        "- Sin señal GPS, WiFi o red móvil disponible\n"
                        "- Estás en un entorno sin cobertura\n\n"
                        "Enciende el GPS, conéctate a una red y vuelve a intentarlo."
                    )
                elif code == 3:
                    st.warning(
                        "⏱️ **Tiempo de espera agotado.**\n\n"
                        "El GPS tardó demasiado en responder. Verifica que:\n"
                        "- El GPS esté activado\n"
                        "- Tengas buena señal o conexión a internet\n\n"
                        "Luego haz clic en Reintentar."
                    )
                else:
                    st.error(f"❌ Error GPS inesperado: {msg}")

                if st.button("🔄 Reintentar"):
                    st.session_state.pop("get_gps", None)
                    st.rerun()

            else:
                st.error(f"❌ Respuesta inesperada del GPS: {coords}")
                st.session_state["gps_triggered"] = False
                if st.button("🔄 Reintentar"):
                    st.session_state.pop("get_gps", None)
                    st.rerun()

    st.stop()


# ── 2. Coordenadas capturadas ──────────────────────────────────────
my_lat = st.session_state["my_lat"]
my_lon = st.session_state["my_lon"]

st.markdown("""
<div style="
    background: linear-gradient(135deg, #0d3b2e, #0a2e1f);
    border: 1px solid #00c875; border-radius: 12px;
    padding: 14px 20px; margin-bottom: 1rem;
    text-align: center; color: #00c875;
    font-size: 1rem; font-weight: 700;
">✅ Ubicación capturada exitosamente</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
col1.metric("📍 Latitud",  f"{my_lat:.6f}")
col2.metric("📍 Longitud", f"{my_lon:.6f}")

if st.button("🔄 Actualizar ubicación"):
    st.session_state["my_lat"] = None
    st.session_state["my_lon"] = None
    st.session_state.pop("get_gps", None)
    st.session_state["gps_triggered"] = False
    st.rerun()


# ── Mapa con marcador pequeño (pydeck, sin token) ─────────────────
layer = pdk.Layer(
    "ScatterplotLayer",
    data=[{"lat": my_lat, "lon": my_lon}],
    get_position="[lon, lat]",
    get_color=[220, 50, 50, 200],
    get_radius=20,
    radius_min_pixels=6,
    radius_max_pixels=18,
    pickable=True,
)

view_state = pdk.ViewState(
    latitude=my_lat,
    longitude=my_lon,
    zoom=15,
    pitch=0,
)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
))


# ── 3. Lista de direcciones ────────────────────────────────────────
direcciones = [
    "Calle 100 #10-20, Bogotá, Colombia",
    "Carrera 7 #50-10, Bogotá, Colombia",
    "Av. 19 #125-45, Bogotá, Colombia",
    "Carrera 103b # 154 - 61, Bogotá, Colombia",
]


@st.cache_data
def geocode_lista(dirs):
    geolocator = Nominatim(user_agent="dairon_geoapp")
    return [geolocator.geocode(d) for d in dirs]


with st.spinner("🗺️ Geocodificando direcciones…"):
    lugares = geocode_lista(direcciones)


# ── 4. Selectbox ───────────────────────────────────────────────────
opciones_dir = [d for d, p in zip(direcciones, lugares) if p]
dir_seleccionada = st.selectbox("Selecciona una dirección:", opciones_dir)


if dir_seleccionada:
    idx = opciones_dir.index(dir_seleccionada)
    lugar_sel = lugares[idx]

    # ── 5. Guardar en Supabase ─────────────────────────────────────
    if "registro_guardado" not in st.session_state:
        st.session_state["registro_guardado"] = False

    if st.session_state["registro_guardado"]:
        st.success("✅ Registro guardado correctamente en Supabase")

        # ✅ CORREGIDO — if normal, no expresión ternaria
        if st.session_state.get("mostrar_balloons"):
            st.balloons()
            st.session_state["mostrar_balloons"] = False

        if st.button("🔄 Actualizar ubicación", key="btn_actualizar_post_guardado"):
            st.session_state["my_lat"] = None
            st.session_state["my_lon"] = None
            st.session_state.pop("get_gps", None)
            st.session_state["gps_triggered"] = False
            st.session_state["registro_guardado"] = False
            st.rerun()

    else:
        if st.button("💾 Guardar registro en servidor"):
            registro = {
                "created_at":             datetime.now().isoformat(),
                "lat_actual":             my_lat,
                "lon_actual":             my_lon,
                "direccion_seleccionada": dir_seleccionada,
            }
            try:
                response = supabase.table("registros_gps").insert(registro).execute()
                if response.data:
                    st.session_state["registro_guardado"] = True
                    st.session_state["mostrar_balloons"] = True
                    st.rerun()
                else:
                    st.error("❌ No se pudo guardar el registro")
            except Exception as e:
                st.error(f"❌ Error al guardar: {e}")

    # # ── 6. Historial ───────────────────────────────────────────────
    # with st.expander("📋 Ver historial de registros"):
    #     try:
    #         response = supabase.table("registros_gps") \
    #                            .select("*") \
    #                            .order("created_at", desc=True) \
    #                            .limit(50) \
    #                            .execute()
    #         if response.data:
    #             df_hist = pd.DataFrame(response.data)
    #             st.dataframe(df_hist, use_container_width=True)
    #         else:
    #             st.info("Aún no hay registros guardados.")
    #     except Exception as e:
    #         st.error(f"❌ Error al cargar historial: {e}")
