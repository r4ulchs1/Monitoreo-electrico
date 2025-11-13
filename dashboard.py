import streamlit as st
import pandas as pd
from funcional.funciones import calcular_promedio
from logica.reglas import verificar_alertas

st.set_page_config(page_title="SmartEnergy", page_icon="⚡", layout="wide")

st.title("⚡Monitoreo de Consumo Eléctrico Doméstico")

# --- Cargar datos ---
@st.cache_data
def cargar_datos():
    df = pd.read_csv("data/consumo.csv", sep=";")
    return df

df = cargar_datos()

# --- barra latreal ---
st.sidebar.header("Configuración")

dias = sorted(df["dia"].unique())
dispositivos = sorted(df["dispositivo"].unique())

dia_seleccionado = st.sidebar.selectbox("Selecciona el día", dias)
dispositivos_seleccionados = st.sidebar.multiselect(
    "Selecciona los dispositivos:",
    dispositivos,
    default=dispositivos[:2]
)


# --- Filtrar datos ---
datos_filtrados = df[(df["dia"] == dia_seleccionado) & (df["dispositivo"].isin(dispositivos_seleccionados))]

if datos_filtrados.empty:
    st.warning("No hay datos disponibles para los filtros seleccionados.")
    st.stop()


# --- Cálculo de energía (P = V * I) ---
datos_filtrados["potencia"] = datos_filtrados["voltaje"] * datos_filtrados["corriente"]
energia_total = datos_filtrados.groupby("dispositivo")["potencia"].sum() / 1000  # kWh aprox.


# --- Panel de métricas ---
st.subheader(f"Resumen general - Día {dia_seleccionado}")
cols = st.columns(len(dispositivos_seleccionados))
for idx, disp in enumerate(dispositivos_seleccionados):
    valor = energia_total.get(disp, 0)
    cols[idx].metric(disp, f"{valor:.2f} kWh", help=f"Consumo total de {disp}")


# --- Gráficos ---
st.subheader("Potencia eléctrica por dispositivo")

cols = st.columns(2)
for idx, disp in enumerate(dispositivos_seleccionados):
    df_disp = datos_filtrados[datos_filtrados["dispositivo"] == disp]
    with cols[idx % 2]:
        st.markdown(f"### 📟 {disp}")
        st.line_chart(df_disp.set_index("hora")["potencia"], use_container_width=True, height=250)



# --- Alertas ---
st.subheader("Alertas detectadas")
for _, row in datos_filtrados.iterrows():
    alertas = verificar_alertas(row["voltaje"], row["corriente"])
    for alerta in alertas:
        st.error(f"{row['dispositivo']} (hora {int(row['hora'])}): {alerta}")


# --- Promedio general ---
promedio = calcular_promedio(list(energia_total.values))
st.success(f"💡 Consumo promedio general: {promedio:.2f} kWh")
