from datetime import datetime

import pandas as pd
import streamlit as st

from db.queries import insertar_consumo, obtener_consumos_por_dia, obtener_dispositivos
from funcional.funciones import calcular_promedio
from logica.reglas import verificar_alertas

st.set_page_config(page_title="SmartEnergy Dashboard", page_icon="⚡", layout="wide")

st.title("⚡ SmartEnergy - Monitoreo de Consumo Eléctrico Doméstico")


#consumos por día

st.sidebar.header("📊 Configuración de Visualización")

dia_seleccionado = st.sidebar.date_input("Selecciona el día:")
dia_str = dia_seleccionado.strftime("%Y-%m-%d")

# datos
df = obtener_consumos_por_dia(dia_str)


if df is not None and not df.empty:
    columnas_obligatorias = ["hora", "voltaje", "corriente"]
    faltan = [c for c in columnas_obligatorias if c not in df.columns]

    if faltan:
        st.error(f"Faltan columnas obligatorias en los datos: {faltan}")
        st.stop()

    # calcular potencia
    df["potencia"] = df["voltaje"] * df["corriente"]

    # dispositivos
    dispositivos_disponibles = []
    if "dispositivo_id" in df.columns:
        dispositivos_db = obtener_dispositivos()
        mapa_dispositivos = {d["id"]: d["nombre"] for d in dispositivos_db}
        df["dispositivo"] = df["dispositivo_id"].map(mapa_dispositivos)
        dispositivos_disponibles = sorted(df["dispositivo"].unique())

    if dispositivos_disponibles:
        dispositivos_seleccionados = st.sidebar.multiselect(
            "Selecciona los dispositivos:",
            dispositivos_disponibles,
            default=dispositivos_disponibles[:2]
            if len(dispositivos_disponibles) >= 2
            else dispositivos_disponibles,
        )

        if not dispositivos_seleccionados:
            st.warning("⚠️ Por favor selecciona al menos un dispositivo.")
            st.stop()

        # filtra por disp seleccionado
        df_filtrado = df[df["dispositivo"].isin(dispositivos_seleccionados)]
    else:
        df_filtrado = df
        dispositivos_seleccionados = ["Datos generales"]

    # calculo de enrg por dispositivo
    if "dispositivo" in df_filtrado.columns:
        energia_total = (
            df_filtrado.groupby("dispositivo")["potencia"].sum() / 1000
        )  # kWh
    else:
        energia_total = {"Total": df_filtrado["potencia"].sum() / 1000}

#metricas

    st.subheader(f"📅 Resumen General - {dia_seleccionado.strftime('%d/%m/%Y')}")

    cols = st.columns(len(dispositivos_seleccionados))
    for idx, disp in enumerate(dispositivos_seleccionados):
        valor = energia_total.get(disp, 0)
        cols[idx].metric(
            label=disp,
            value=f"{valor:.2f} kWh",
            help=f"Consumo total de {disp} en el día",
        )

    #graf protencia

    st.subheader("📈 Potencia Eléctrica por Dispositivo")

    # indiv
    cols_graficos = st.columns(2)

    for idx, disp in enumerate(dispositivos_seleccionados):
        df_disp = df_filtrado[df_filtrado["dispositivo"] == disp]

        if not df_disp.empty:
            with cols_graficos[idx % 2]:
                st.markdown(f"### 📟 {disp}")

                # potencia
                st.line_chart(
                    df_disp.set_index("hora")["potencia"],
                    use_container_width=True,
                    height=250,
                )
                col1, col2, col3 = st.columns(3)
                col1.metric("Max", f"{df_disp['potencia'].max():.1f} W")
                col2.metric("Min", f"{df_disp['potencia'].min():.1f} W")
                col3.metric("Prom", f"{df_disp['potencia'].mean():.1f} W")

    # Comprarativo

    st.subheader("📊 Comparación de Voltaje y Corriente")

    tab1, tab2 = st.tabs(["⚡ Voltaje", "🔌 Corriente"])

    with tab1:
        #voltaje
        df_voltaje_pivot = df_filtrado.pivot_table(
            index="hora", columns="dispositivo", values="voltaje"
        )
        st.line_chart(df_voltaje_pivot, use_container_width=True, height=300)

    with tab2:
        # intensidad
        df_corriente_pivot = df_filtrado.pivot_table(
            index="hora", columns="dispositivo", values="corriente"
        )
        st.line_chart(df_corriente_pivot, use_container_width=True, height=300)

#Aletras

    st.subheader("⚠️ Alertas Detectadas")

    alertas_encontradas = False

    for _, row in df_filtrado.iterrows():
        alertas = verificar_alertas(row["voltaje"], row["corriente"])
        if alertas:
            alertas_encontradas = True
            dispositivo_nombre = row.get("dispositivo", "Desconocido")
            hora_int = int(row["hora"])

            for alerta in alertas:
                st.error(f"🚨 **{dispositivo_nombre}** (hora {hora_int}): {alerta}")

    if not alertas_encontradas:
        st.success("✅ No se detectaron alertas para el día seleccionado.")

    with st.expander("📋 Ver datos detallados"):
        st.dataframe(
            df_filtrado[
                ["hora", "dispositivo", "voltaje", "corriente", "potencia"]
            ].sort_values("hora"),
            use_container_width=True,
        )

else:
    st.info("ℹ️ No hay datos registrados para este día.")


# insercion de datos manual

st.markdown("---")
st.subheader("📝 Registrar Consumo Manual")

dispositivos = obtener_dispositivos()

if not dispositivos:
    st.warning("⚠️ No hay dispositivos registrados en la base de datos.")
    st.info(
        "💡 Ejecuta `python cargar_datos_csv.py` para insertar dispositivos y datos de prueba."
    )
    st.stop()
else:
    mapa_dispositivos = {d["nombre"]: d["id"] for d in dispositivos}

    col1, col2 = st.columns(2)

    with col1:
        dispositivo_nombre = st.selectbox(
            "Dispositivo:", list(mapa_dispositivos.keys())
        )
        voltaje = st.number_input(
            "Voltaje (V):", min_value=0.0, max_value=500.0, step=0.1, value=220.0
        )
        corriente = st.number_input(
            "Corriente (A):", min_value=0.0, max_value=100.0, step=0.1, value=2.0
        )

    with col2:
        dia_manual = st.date_input("Día del registro:", value=dia_seleccionado)
        hora_manual = st.time_input("Hora del registro:")

    dispositivo_id = mapa_dispositivos[dispositivo_nombre]
    dia_insert = dia_manual.strftime("%Y-%m-%d")
    hora_float = hora_manual.hour + hora_manual.minute / 60

    # resumen
    st.info(
        f"📊 Vista previa: {dispositivo_nombre} - {voltaje}V × {corriente}A = {voltaje * corriente:.2f}W"
    )


# boton

if st.button("➕ Insertar Registro", type="primary"):
    nuevo = insertar_consumo(
        dispositivo_id=dispositivo_id,
        dia=dia_insert,
        hora=hora_float,
        voltaje=voltaje,
        corriente=corriente,
    )

    if nuevo:
        # calcular potencia
        potencia = voltaje * corriente

        #verificar alertcas (LOGICA)
        reglas = verificar_alertas(voltaje, corriente)

        st.success("✅ Registro insertado correctamente.")
        st.write(f"**⚡ Potencia calculada:** {potencia:.2f} W")

        if reglas:
            st.write("### ⚠️ Alertas detectadas:")
            for r in reglas:
                st.warning(r)
        else:
            st.info("✅ No se detectaron alertas para este registro.")

        st.rerun()

    else:
        st.error("❌ Error al insertar el registro. Verifica la conexión a Supabase.")


# footer

st.markdown("---")
st.caption(
    "⚡ SmartEnergy Dashboard - Sistema de Monitoreo Eléctrico Doméstico · Proyecto académico"
)
