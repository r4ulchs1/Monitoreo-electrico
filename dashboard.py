from datetime import datetime

import pandas as pd
import streamlit as st

# ===============================
# Importar capas de lógica
# ===============================
from db.queries import insertar_consumo, obtener_consumos_por_dia, obtener_dispositivos
from funcional.funciones import calcular_potencia_df
from logica.reglas import verificar_alertas

# ==========================================================
#                          UI
# ==========================================================

st.set_page_config(page_title="Monitoreo Eléctrico", layout="wide")

st.title("⚡ Sistema de Monitoreo Eléctrico — Dashboard")


# ==========================================================
#          SECCIÓN 1: Seleccionar fecha para consultar
# ==========================================================

st.subheader("📅 Consultar consumos por día")

dia_seleccionado = st.date_input("Selecciona el día:")
dia_str = dia_seleccionado.strftime("%Y-%m-%d")

df = obtener_consumos_por_dia(dia_str)

if df is not None and not df.empty:
    # Validar columnas obligatorias
    columnas_obligatorias = ["hora", "voltaje", "corriente"]
    faltan = [c for c in columnas_obligatorias if c not in df.columns]

    if faltan:
        st.error(f"Faltan columnas obligatorias en los datos: {faltan}")
        st.stop()

    st.write("### Resultados")
    st.dataframe(df)

    st.line_chart(df.set_index("hora")[["voltaje", "corriente"]], height=300)

else:
    st.info("No hay datos registrados para este día.")


# ==========================================================
#        SECCIÓN 2: Insertar registro manual
# ==========================================================

st.subheader("📝 Registrar consumo manual")

dispositivos = obtener_dispositivos()

if not dispositivos:
    st.warning("No hay dispositivos registrados en la base de datos.")
    st.stop()  # DETIENE la ejecución del script aquí
else:
    mapa_dispositivos = {d["nombre"]: d["id"] for d in dispositivos}

    col1, col2 = st.columns(2)

    with col1:
        dispositivo_nombre = st.selectbox(
            "Dispositivo:", list(mapa_dispositivos.keys())
        )
        voltaje = st.number_input(
            "Voltaje (V):", min_value=0.0, max_value=500.0, step=0.1
        )
        corriente = st.number_input(
            "Corriente (A):", min_value=0.0, max_value=100.0, step=0.1
        )

    with col2:
        dia_manual = st.date_input("Día del registro:")
        hora_manual = st.time_input("Hora del registro:")

    dispositivo_id = mapa_dispositivos[dispositivo_nombre]
    dia_insert = dia_manual.strftime("%Y-%m-%d")
    hora_float = hora_manual.hour + hora_manual.minute / 60


# ==========================================================
#        BOTÓN DE INSERTAR
# ==========================================================

if st.button("➕ Insertar registro"):
    nuevo = insertar_consumo(
        dispositivo_id=dispositivo_id,
        dia=dia_insert,
        hora=hora_float,
        voltaje=voltaje,
        corriente=corriente,
    )

    if nuevo:
        # Programación funcional
        potencia = calcular_potencia_df(voltaje, corriente)

        # Programación lógica
        reglas = verificar_alertas(voltaje, corriente)

        st.success("Registro insertado correctamente.")
        st.write("Potencia generada:", potencia, "W")

        if reglas:
            for r in reglas:
                st.warning("⚠ " + r)

    else:
        st.error("Error al insertar el registro.")


# ==========================================================
#        FOOTER
# ==========================================================

st.markdown("---")
st.caption("Sistema de Monitoreo Eléctrico — Proyecto académico")
