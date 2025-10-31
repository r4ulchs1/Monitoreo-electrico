import streamlit as st
from function.funciones import simular_datos, calcular_consumo_total
from logic.reglas import verificar_alertas

st.set_page_config(page_title="SmartEnergy", page_icon="⚡", layout="wide")

st.title("⚡ SmartEnergy - Monitor de Consumo Eléctrico")

# Simulación
datos = simular_datos()
energia_total = calcular_consumo_total(datos["potencia"])

col1, col2 = st.columns(2)
col1.metric("Energía total (kWh)", f"{energia_total:.2f}")
col2.metric("Consumo promedio (W)", f"{datos['potencia'].mean():.2f}")

st.line_chart(datos["potencia"], use_container_width=True)

st.subheader("Alertas detectadas")
for v, i in zip(datos["voltaje"], datos["corriente"]):
    alertas = verificar_alertas(v, i)
    for alerta in alertas:
        st.error(alerta)
