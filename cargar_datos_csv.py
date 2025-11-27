import csv
from datetime import datetime, timezone

from db.queries import insertar_consumo
from db.supabase_client import get_supabase

supabase = get_supabase()


def obtener_o_crear_dispositivo(nombre: str) -> int:
    # Buscar dispositivo existente
    resp = supabase.table("dispositivo").select("*").eq("nombre", nombre).execute()

    if resp.data and len(resp.data) > 0:
        print(f"✓ Dispositivo '{nombre}' ya existe (ID: {resp.data[0]['id']})")
        return resp.data[0]["id"]

    # Crear nuevo dispositivo
    nuevo_disp = {
        "nombre": nombre,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    resp_insert = supabase.table("dispositivo").insert(nuevo_disp).execute()

    if resp_insert.data and len(resp_insert.data) > 0:
        nuevo_id = resp_insert.data[0]["id"]
        print(f"✓ Dispositivo '{nombre}' creado (ID: {nuevo_id})")
        return nuevo_id
    else:
        raise Exception(f"Error al crear dispositivo '{nombre}'")


def convertir_dia_a_fecha(dia_texto: str) -> str:
    dias_map = {
        "Lunes": "2025-01-06",
        "Martes": "2025-01-07",
        "Miércoles": "2025-01-08",
        "Jueves": "2025-01-09",
        "Viernes": "2025-01-10",
        "Sábado": "2025-01-11",
        "Domingo": "2025-01-12",
    }
    return dias_map.get(dia_texto, "2025-01-06")


def cargar_csv_a_supabase(archivo_csv: str = "data/consumo.csv"):
    """
    Lee el archivo CSV y carga los datos a Supabase
    """
    print(f"\n🔄 Cargando datos desde {archivo_csv}...\n")

    # Mapeo de dispositivos a sus IDs
    dispositivos_ids = {}

    # Leer CSV
    with open(archivo_csv, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=";")

        contador = 0
        errores = 0

        for row in reader:
            try:
                dispositivo_nombre = row["dispositivo"]

                # Obtener o crear dispositivo
                if dispositivo_nombre not in dispositivos_ids:
                    dispositivos_ids[dispositivo_nombre] = obtener_o_crear_dispositivo(
                        dispositivo_nombre
                    )

                dispositivo_id = dispositivos_ids[dispositivo_nombre]

                # Convertir día a fecha
                dia = convertir_dia_a_fecha(row["dia"])
                hora = float(row["hora"])
                voltaje = float(row["voltaje"])
                corriente = float(row["corriente"])

                # Insertar consumo
                resultado = insertar_consumo(
                    dispositivo_id=dispositivo_id,
                    dia=dia,
                    hora=hora,
                    voltaje=voltaje,
                    corriente=corriente,
                )

                if resultado:
                    contador += 1
                    if contador % 50 == 0:
                        print(f"  ✓ {contador} registros insertados...")
                else:
                    errores += 1

            except Exception as e:
                print(f"  ✗ Error en fila: {row} - {str(e)}")
                errores += 1

    print(f"\n✅ Carga completada:")
    print(f"   - Registros insertados: {contador}")
    print(f"   - Errores: {errores}")
    print(f"   - Dispositivos creados/usados: {len(dispositivos_ids)}")


if __name__ == "__main__":
    print("=" * 60)
    print("  SCRIPT DE CARGA DE DATOS - Sistema de Monitoreo Eléctrico")
    print("=" * 60)

    try:
        cargar_csv_a_supabase()
        print("\n✅ Proceso completado exitosamente!")
        print("\nAhora puedes ejecutar: streamlit run dashboard.py")

    except Exception as e:
        print(f"\n❌ Error fatal: {str(e)}")
        print("\nVerifica:")
        print("  1. Que el archivo .env tenga SUPABASE_URL y SUPABASE_KEY correctos")
        print(
            "  2. Que las tablas 'dispositivo' y 'consumo_electrico' existan en Supabase"
        )
        print("  3. Que el archivo data/consumo.csv exista")
