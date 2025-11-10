import streamlit as st
import numpy as np
from funcional.funciones import simular_consumo, calcular_promedio
from logica.reglas import verificar_alertas

st.set_page_config(page_title="SmartEnergy Dashboard", page_icon="⚡", layout="wide")

st.title("⚡ SmartEnergy - Monitoreo de Consumo Eléctrico Doméstico")

# --- Interactividad ---
st.sidebar.header("Configuración de Simulación")
dispositivos = st.sidebar.multiselect(
    "Selecciona los dispositivos a monitorear:",
    ["Refrigeradora", "Televisor", "Computadora", "Lavadora"],
    default=["Refrigeradora", "Televisor"]
)
horas = st.sidebar.slider("Horas de simulación", 6, 24, 12)
st.sidebar.write("Haz clic en 'Actualizar' para correr la simulación.")
if st.sidebar.button("Actualizar simulación"):
    st.experimental_rerun()


# --- Simulación de datos ---
resultados = {}
for disp in dispositivos:
    resultados[disp] = simular_consumo(disp, horas)


# --- Panel de métricas ---
st.subheader("Resumen general de consumo")
cols = st.columns(len(dispositivos))
for idx, disp in enumerate(dispositivos):
    cols[idx].metric(
        disp,
        f"{resultados[disp]['energia_total']:.2f} kWh",
        help=f"Consumo total de {disp}"
    )


# --- Gráficos ---
st.subheader("Potencia eléctrica por dispositivo")
for disp in dispositivos:
    st.line_chart(resultados[disp]["potencia"], use_container_width=True, height=200)


# --- Análisis lógico de alertas ---
st.subheader("Alertas detectadas")
for disp in dispositivos:
    for v, i in zip(resultados[disp]["voltaje"], resultados[disp]["corriente"]):
        alertas = verificar_alertas(v, i)
        for alerta in alertas:
            st.error(f"{disp}: {alerta}")


# --- Promedio general ---
promedio = calcular_promedio([r["energia_total"] for r in resultados.values()])
st.success(f"💡 Consumo promedio general: {promedio:.2f} kWh")
