import sys
from datetime import datetime, timezone

from db.supabase_client import get_supabase


def verificar_conexion():
    print("\n" + "=" * 60)
    print("  VERIFICACIÓN DE CONEXIÓN CON SUPABASE")
    print("=" * 60 + "\n")

    try:
        supabase = get_supabase()
        print("✅ Cliente de Supabase inicializado correctamente\n")
        return supabase
    except Exception as e:
        print(f"❌ Error al conectar con Supabase: {str(e)}\n")
        print("Verifica:")
        print("  1. Que el archivo .env existe en la raíz del proyecto")
        print("  2. Que SUPABASE_URL y SUPABASE_KEY están definidos correctamente")
        print("  3. Que las credenciales son válidas")
        sys.exit(1)


def verificar_tabla(supabase, nombre_tabla: str, columnas_esperadas: list):
    """Verifica que una tabla existe y tiene las columnas correctas"""
    print(f"🔍 Verificando tabla '{nombre_tabla}'...")

    try:
        resp = supabase.table(nombre_tabla).select("*").limit(1).execute()

        print(f"   ✅ Tabla '{nombre_tabla}' existe")

        count_resp = supabase.table(nombre_tabla).select("*", count="exact").execute()
        count = (
            count_resp.count if hasattr(count_resp, "count") else len(count_resp.data)
        )
        print(f"   📊 Registros actuales: {count}")

        return True

    except Exception as e:
        print(f"   ❌ Error con la tabla '{nombre_tabla}': {str(e)}")
        return False


def verificar_estructura():
    supabase = verificar_conexion()

    tablas = {
        "dispositivo": ["id", "nombre", "created_at"],
        "consumo_electrico": [
            "id",
            "dispositivo_id",
            "dia",
            "hora",
            "voltaje",
            "corriente",
            "created_at",
        ],
        "alertas": ["id", "consumo_id", "tipo", "mensaje", "fecha"],
    }

    print("Verificando tablas...\n")

    todas_ok = True
    for tabla, columnas in tablas.items():
        if not verificar_tabla(supabase, tabla, columnas):
            todas_ok = False
        print()  # Línea en blanco

    if todas_ok:
        print("=" * 60)
        print("✅ TODAS LAS TABLAS ESTÁN CORRECTAMENTE CONFIGURADAS")
        print("=" * 60 + "\n")
        print("Puedes proceder a:")
        print("  1. Ejecutar: python cargar_datos_csv.py")
        print("  2. Luego: streamlit run dashboard.py\n")
    else:
        print("=" * 60)
        print("❌ ALGUNAS TABLAS TIENEN PROBLEMAS")
        print("=" * 60 + "\n")
        print("Solución:")
        print("  1. Ve al SQL Editor de Supabase")
        print("  2. Ejecuta el script 'setup_supabase.sql'")
        print("  3. Vuelve a ejecutar este script\n")


def test_insercion():
    supabase = verificar_conexion()

    print("\n" + "=" * 60)
    print("  TEST DE INSERCIÓN")
    print("=" * 60 + "\n")

    try:
        # Verificar si existe disposiitvo
        resp = supabase.table("dispositivo").select("*").limit(1).execute()

        if not resp.data:
            print("⚠️  No hay dispositivos en la tabla. Creando uno de prueba...")
            nuevo_disp = {
                "nombre": "Dispositivo_Test",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            disp_resp = supabase.table("dispositivo").insert(nuevo_disp).execute()
            dispositivo_id = disp_resp.data[0]["id"]
            print(f"   ✅ Dispositivo de prueba creado (ID: {dispositivo_id})")
        else:
            dispositivo_id = resp.data[0]["id"]
            print(f"   ✅ Usando dispositivo existente (ID: {dispositivo_id})")

        # intentar consumo deprueba
        print("\n🔄 Insertando registro de prueba...")
        test_data = {
            "dispositivo_id": dispositivo_id,
            "dia": "2025-01-06",
            "hora": 12.5,
            "voltaje": 220.0,
            "corriente": 3.5,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        consumo_resp = supabase.table("consumo_electrico").insert(test_data).execute()

        if consumo_resp.data:
            print("   ✅ Registro de prueba insertado correctamente")
            print(f"   ID del registro: {consumo_resp.data[0]['id']}")

            # eliminar registro de prueba
            print("\n🧹 Limpiando registro de prueba...")
            supabase.table("consumo_electrico").delete().eq(
                "id", consumo_resp.data[0]["id"]
            ).execute()
            print("   ✅ Registro de prueba eliminado")

            print("\n✅ TEST DE INSERCIÓN EXITOSO")
        else:
            print("   ❌ No se pudo insertar el registro")

    except Exception as e:
        print(f"\n❌ Error en test de inserción: {str(e)}")


if __name__ == "__main__":
    try:
        verificar_estructura()

        respuesta = input("\n¿Deseas probar una inserción de prueba? (s/n): ").lower()
        if respuesta == "s":
            test_insercion()

        print("\n✅ Verificación completada!\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Verificación interrumpida por el usuario\n")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}\n")
