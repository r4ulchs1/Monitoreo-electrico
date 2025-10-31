import numpy as np

def simular_datos():
    horas = np.arange(24)
    voltaje = np.random.normal(220, 5, 24)
    corriente = np.random.uniform(0.5, 10, 24)
    potencia = voltaje * corriente
    return {"horas": horas, "voltaje": voltaje, "corriente": corriente, "potencia": potencia}

def calcular_consumo_total(potencia):
    return np.sum(potencia) / 1000
