import json
import requests
import streamlit as st

DEFAULT_ENDPOINT = "https://cmsback.vridevops.site/api/grupos-reconocidos"

DEFAULT_FIELD_MAP = {
    "nombre": "nombre",
    "anio": "anio",
    "facultad": "facultad",
    "escuela": "escuela",
    "responsable": "responsable",
    "linea": "linea",
    "integrantes": "integrantes",
    "monto": "monto",
}


def default_api_field_name(field):
    key = field.strip()
    key_lower = key.lower()
    if key_lower in DEFAULT_FIELD_MAP:
        return DEFAULT_FIELD_MAP[key_lower]
    return key_lower.replace(" ", "_")


def build_payload(data):
    return {"data": data}


def build_payload_from_record(record, fields, field_mapping):
    data = {}
    for field in fields:
        if field in record:
            data[field_mapping[field]] = record[field]
    return build_payload(data)


def parse_json_payload(json_text, json_file):
    raw_text = ""
    if json_file is not None:
        raw_text = json_file.getvalue().decode("utf-8")
    else:
        raw_text = json_text or ""

    if not raw_text.strip():
        return None, "Agrega un JSON en texto o carga un archivo."

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        return None, f"JSON invalido: {exc}"

    if isinstance(payload, dict):
        return [payload], None
    if isinstance(payload, list) and all(isinstance(item, dict) for item in payload):
        if not payload:
            return None, "El JSON no contiene registros."
        return payload, None

    return None, "El JSON debe ser un objeto o una lista de objetos."


def post_payload(endpoint, token, payload, timeout):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)
        return response, None
    except requests.RequestException as exc:
        return None, exc


def test_connection(endpoint, token, timeout):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        return requests.get(endpoint, headers=headers, timeout=timeout)
    except requests.RequestException as exc:
        return exc


st.set_page_config(page_title="Carga Strapi", layout="centered")

st.title("Carga a Strapi: grupos reconocidos")
st.caption("Envia un registro individual al endpoint configurado.")

with st.sidebar:
    st.header("Conexion")
    token = st.text_input("Token (Bearer)", type="password", placeholder="Pega tu token aqui")
    endpoint = st.text_input("Endpoint URL", value=DEFAULT_ENDPOINT)
    timeout = st.number_input("Timeout (segundos)", min_value=1, max_value=120, value=30, step=1)

    if st.button("Probar conexion"):
        result = test_connection(endpoint, token, timeout)
        if isinstance(result, requests.Response):
            st.write(f"Codigo: {result.status_code}")
            if result.status_code in (200, 201):
                st.success("Conexion OK")
            elif result.status_code in (401, 403):
                st.warning("Conexion OK, pero token no autorizado")
            else:
                st.info("Conexion OK, revisa el codigo y respuesta")
        else:
            st.error(f"Error de conexion: {result}")

st.subheader("Datos del grupo")
tabs = st.tabs(["Formulario", "JSON"])

with tabs[0]:
    with st.form("registro_form"):
        nombre = st.text_input("Nombre")
        anio = st.number_input("Anio", min_value=1900, max_value=2100, value=2025, step=1)
        facultad = st.text_input("Facultad")
        escuela = st.text_input("Escuela")
        responsable = st.text_input("Responsable")
        linea = st.text_input("Linea")
        integrantes = st.text_area("Integrantes", help="Uno por linea")
        show_payload = st.checkbox("Mostrar payload antes de enviar", value=False)
        submitted = st.form_submit_button("Enviar registro")

    if submitted:
        values = {
            "nombre": nombre.strip(),
            "anio": str(int(anio)),
            "facultad": facultad.strip(),
            "escuela": escuela.strip(),
            "responsable": responsable.strip(),
            "linea": linea.strip(),
            "integrantes": integrantes.strip(),
        }

        missing = [key for key, value in values.items() if not value]
        if missing:
            st.error(f"Campos vacios: {', '.join(missing)}")
        elif not endpoint.strip():
            st.error("Endpoint vacio")
        elif not token.strip():
            st.error("Token vacio")
        else:
            payload = build_payload(values)

            if show_payload:
                st.code(json.dumps(payload, ensure_ascii=False, indent=2), language="json")

            response, error = post_payload(endpoint, token, payload, timeout)
            if error:
                st.error(f"Error critico de conexion: {error}")
            elif response.status_code in (200, 201):
                st.success("Registro guardado correctamente")
            else:
                st.error(f"Error: codigo {response.status_code}")
                try:
                    st.code(json.dumps(response.json(), ensure_ascii=False, indent=2), language="json")
                except ValueError:
                    st.text(response.text)

with tabs[1]:
    st.caption("Sube un JSON (objeto o lista) y selecciona los campos a enviar.")
    st.code(
        '{\n  "Nombre": "Test 1: Modelos Predictivos en Educacion",\n  "Anio": 2026,\n'
        '  "Facultad": "Ingenieria",\n  "Escuela": "Estadistica e Informatica",\n'
        '  "Monto": 2500.50,\n  "Linea": "Machine Learning",\n'
        '  "Responsable": "",\n  "Integrantes": "Ana Torres\\nLuis Gomez"\n}',
        language="json",
    )

    json_file = st.file_uploader("Archivo JSON", type=["json"])
    json_text = st.text_area("JSON", height=200, placeholder="Pega aqui el JSON")

    records, parse_error = parse_json_payload(json_text, json_file)
    if parse_error:
        st.error(parse_error)
    else:
        record_count = len(records)
        st.write(f"Registros detectados: {record_count}")

        send_all = False
        if record_count > 1:
            send_all = st.checkbox(f"Enviar todos los registros ({record_count})", value=False)

        if record_count > 1:
            preview_index = st.number_input(
                "Indice para vista previa",
                min_value=1,
                max_value=record_count,
                value=1,
                step=1,
            )
            selected_record = records[int(preview_index) - 1]
        else:
            selected_record = records[0]

        if send_all:
            all_fields = sorted({key for record in records for key in record.keys()})
        else:
            all_fields = list(selected_record.keys())

        fields = st.multiselect("Campos a enviar", options=all_fields, default=all_fields)
        edit_field_names = st.checkbox("Editar nombres de campo (API)", value=False)

        field_mapping = {}
        if edit_field_names:
            st.write("Mapa de campos")
            for field in fields:
                field_mapping[field] = st.text_input(
                    f"{field} ->",
                    value=default_api_field_name(field),
                    key=f"map_{field}",
                )
        else:
            for field in fields:
                field_mapping[field] = default_api_field_name(field)

        show_payload_json = st.checkbox(
            "Mostrar payload antes de enviar",
            value=False,
            key="show_payload_json",
        )

        preview_payload = build_payload_from_record(selected_record, fields, field_mapping)
        if show_payload_json:
            st.code(json.dumps(preview_payload, ensure_ascii=False, indent=2), language="json")

        if st.button("Enviar registro JSON"):
            if not fields:
                st.error("Selecciona al menos un campo.")
            elif not endpoint.strip():
                st.error("Endpoint vacio")
            elif not token.strip():
                st.error("Token vacio")
            else:
                if send_all:
                    progress = st.progress(0)
                    success_count = 0
                    error_count = 0

                    for index, record in enumerate(records, start=1):
                        payload = build_payload_from_record(record, fields, field_mapping)
                        response, error = post_payload(endpoint, token, payload, timeout)
                        if error:
                            error_count += 1
                            st.error(f"Registro {index}: error de conexion: {error}")
                        elif response.status_code in (200, 201):
                            success_count += 1
                        else:
                            error_count += 1
                            st.error(f"Registro {index}: codigo {response.status_code}")

                        progress.progress(index / record_count)

                    st.write(f"Exitos: {success_count} | Errores: {error_count}")
                else:
                    payload = build_payload_from_record(selected_record, fields, field_mapping)
                    response, error = post_payload(endpoint, token, payload, timeout)
                    if error:
                        st.error(f"Error critico de conexion: {error}")
                    elif response.status_code in (200, 201):
                        st.success("Registro guardado correctamente")
                    else:
                        st.error(f"Error: codigo {response.status_code}")
                        try:
                            st.code(
                                json.dumps(response.json(), ensure_ascii=False, indent=2),
                                language="json",
                            )
                        except ValueError:
                            st.text(response.text)
