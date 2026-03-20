import streamlit as st
import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from supabase import create_client
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval

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
        # Botón grande nativo de Streamlit
        st.markdown("<br>", unsafe_allow_html=True)
        col = st.columns([1, 3, 1])[1]
        if col.button("📍  Obtener mi ubicación GPS", use_container_width=True, type="primary"):
            st.session_state["gps_triggered"] = True
            st.rerun()
    else:
        # Mostrar spinner y ejecutar JS de geolocalización
        st.markdown("""
        <div class="gps-loading-box">
            <div class="gps-spinner"></div>
            <p>🛰️ Obteniendo ubicación…</p>
            <small>Acepta el permiso del navegador cuando aparezca</small>
        </div>
        """, unsafe_allow_html=True)

        # ✅ streamlit_js_eval ejecuta JS real en el navegador y retorna el resultado a Python
        coords = streamlit_js_eval(
            js_expressions="""
                new Promise((resolve, reject) => {
                    if (!navigator.geolocation) {
                        reject("GPS no disponible");
                        return;
                    }
                    navigator.geolocation.getCurrentPosition(
                        (pos) => resolve({
                            lat: pos.coords.latitude,
                            lon: pos.coords.longitude
                        }),
                        (err) => reject(err.message),
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
            else:
                st.error(f"❌ Error GPS: {coords}")
                st.session_state["gps_triggered"] = False
                if st.button("🔄 Reintentar"):
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
col1.metric(" Latitud",  f"{my_lat:.6f}")
col2.metric("📍 Longitud", f"{my_lon:.6f}")

# Botón para volver a capturar
# ✅ Después — elimina solo si existe
if st.button("🔄 Actualizar ubicación"):
    st.session_state["my_lat"] = None
    st.session_state["my_lon"] = None
    st.session_state.pop("get_gps", None)   # ← no explota si no existe
    st.session_state["gps_triggered"] = False
    st.rerun()

map_data = pd.DataFrame([{"lat": my_lat, "lon": my_lon}])
st.map(map_data, zoom=15)

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
    # lat_sel, lon_sel = lugar_sel.latitude, lugar_sel.longitude

    # dist = geodesic((my_lat, my_lon), (lat_sel, lon_sel)).km
    # st.success(f"✅ **{dir_seleccionada}** — Distancia: {dist:.2f} km")

    # df_mapa = pd.DataFrame([
    #     {"lat": my_lat,  "lon": my_lon},
    #     {"lat": lat_sel, "lon": lon_sel}
    # ])
    # st.map(df_mapa, zoom=13)

    # ── 5. Guardar en Supabase ─────────────────────────────────────
    if st.button("💾 Guardar registro en servidor"):
        registro = {
            "created_at":             datetime.now().isoformat(),
            "lat_actual":             my_lat,
            "lon_actual":             my_lon,
            "direccion_seleccionada": dir_seleccionada,
            # "lat_destino":            lat_sel,
            # "lon_destino":            lon_sel,
            # "distancia_km":           round(dist, 4)
        }
        try:
            response = supabase.table("registros_gps").insert(registro).execute()
            if response.data:
                st.success("✅ Registro guardado correctamente en Supabase")
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