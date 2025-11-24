from datetime import datetime

import pandas as pd

from .supabase_client import get_supabase

supabase = get_supabase()

# ======================================
#     OBTENER DATOS
# ======================================


def obtener_dispositivos():
    resp = supabase.table("dispositivo").select("*").execute()
    return resp.data or []


def obtener_consumos_por_dia(dia: str):
    resp = (
        supabase.table("consumo_electrico")
        .select("*")
        .eq("dia", dia)
        .order("hora", desc=False)
        .execute()
    )

    data = resp.data or []
    return pd.DataFrame(data)


def obtener_todos_los_consumos():
    resp = supabase.table("consumo_electrico").select("*").execute()
    return pd.DataFrame(resp.data or [])


# ======================================
#        INSERTAR DATOS
# ======================================


def insertar_consumo(
    dispositivo_id: int, dia: str, hora: float, voltaje: float, corriente: float
):
    data = {
        "dispositivo_id": dispositivo_id,
        "dia": dia,
        "hora": hora,
        "voltaje": voltaje,
        "corriente": corriente,
        "created_at": datetime.utcnow().isoformat(),
    }

    resp = supabase.table("consumo_electrico").insert(data).execute()
    return resp.data


def insertar_alerta(consumo_id: int, tipo: str, mensaje: str):
    data = {
        "consumo_id": consumo_id,
        "tipo": tipo,
        "mensaje": mensaje,
        "fecha": datetime.utcnow().isoformat(),
    }

    resp = supabase.table("alertas").insert(data).execute()
    return resp.data


# ======================================
#    UTILIDADES
# ======================================


def obtener_consumos_formateados_por_dia(dia: str):
    resp = (
        supabase.table("consumo_electrico")
        .select(
            """
            id,
            dia,
            hora,
            voltaje,
            corriente,
            dispositivo:dispositivo_id (id, nombre)
        """
        )
        .eq("dia", dia)
        .execute()
    )

    data = []

    for item in resp.data or []:
        disp = item.get("dispositivo")
        dispositivo_nombre = disp["nombre"] if isinstance(disp, dict) else "Desconocido"

        data.append(
            {
                "id": item["id"],
                "dia": item["dia"],
                "hora": item["hora"],
                "voltaje": item["voltaje"],
                "corriente": item["corriente"],
                "dispositivo": dispositivo_nombre,
            }
        )

    return pd.DataFrame(data)
