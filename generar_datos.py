import csv
import random
import os

os.makedirs("data", exist_ok=True)

dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
dispositivos = ["Refrigeradora", "Televisor", "Computadora", "Lavadora"]
horas = range(1, 25)

archivo_csv = "data/consumo.csv"

with open(archivo_csv, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file, delimiter=";")
    writer.writerow(["dia", "hora", "dispositivo", "voltaje", "corriente"])

    for dia in dias:
        for hora in horas:
            for dispositivo in dispositivos:
                
                voltaje = random.uniform(210, 230)
                corriente = random.uniform(1.0, 5.0)

                if random.random() < 0.08:
                    voltaje = random.uniform(241, 255)
                if random.random() < 0.08:
                    voltaje = random.uniform(180, 199)
                if random.random() < 0.05:
                    corriente = random.uniform(10, 15)

                writer.writerow([dia, hora, dispositivo, round(voltaje, 2), round(corriente, 2)])

print(f"Archivo : {archivo_csv}")
