def verificar_alertas(voltaje, corriente):
    alertas = []
    if corriente > 10:
        alertas.append("⚠️ Corriente excesiva detectada.")
    if voltaje < 200:
        alertas.append("⚠️ Voltaje bajo.")
    if voltaje > 240:
        alertas.append("⚠️ Voltaje alto.")
    return alertas
