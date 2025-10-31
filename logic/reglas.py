def verificar_alertas(voltaje, corriente):
    alertas = []
    if corriente > 10:
        alertas.append("⚠️ Corriente demasiado alta (posible sobrecarga).")
    if voltaje < 200:
        alertas.append("⚠️ Voltaje bajo (posible caída de red).")
    if voltaje > 240:
        alertas.append("⚠️ Voltaje alto (riesgo para dispositivos).")
    return alertas
