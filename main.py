from function.funciones import simular_datos, calcular_consumo_total
from logic.reglas import verificar_alertas

def main():
    datos = simular_datos()
    energia_total = calcular_consumo_total(datos["potencia"])

    print("=== Simulación de Consumo Eléctrico ===")
    print(f"Energía total: {energia_total:.2f} kWh\n")

    print("Alertas:")
    for v, i in zip(datos["voltaje"], datos["corriente"]):
        alertas = verificar_alertas(v, i)
        for a in alertas:
            print(a)

if __name__ == "__main__":
    main()
