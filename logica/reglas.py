def verificar_alertas(voltaje, corriente):
    alertas = []

    VOLTAJE_MIN = 200
    VOLTAJE_MAX = 230
    CORRIENTE_MAX = 10

    if voltaje < VOLTAJE_MIN:
        alertas.append("⚠️ Voltaje bajo - posible caída de tensión")
    elif voltaje > VOLTAJE_MAX:
        alertas.append("⚠️ Voltaje alto - posible sobrecarga")

    if corriente > CORRIENTE_MAX:
        alertas.append("🔥 Corriente excesiva - posible sobrecalentamiento")

    if corriente > 0 and voltaje / corriente > 300:
        alertas.append("❗ Relación V/I anómala detectada")

    return alertas
