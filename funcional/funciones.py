import numpy as np

def simular_consumo(dispositivo, horas=24):
    if dispositivo == "Refrigeradora":
        corriente = np.random.uniform(1.5, 3, horas)
    elif dispositivo == "Televisor":
        corriente = np.random.uniform(0.5, 1.2, horas)
    elif dispositivo == "Computadora":
        corriente = np.random.uniform(0.8, 2, horas)
    elif dispositivo == "Lavadora":
        corriente = np.random.uniform(2, 6, horas)
    else:
        corriente = np.random.uniform(0.5, 3, horas)

    voltaje = np.random.normal(220, 5, horas)
    potencia = voltaje * corriente
    energia_total = np.sum(potencia) / 1000  # Wh → kWh
    return {
        "horas": np.arange(horas),
        "voltaje": voltaje,
        "corriente": corriente,
        "potencia": potencia,
        "energia_total": energia_total
    }

def calcular_promedio(lista_consumos):
    return np.mean(lista_consumos)
