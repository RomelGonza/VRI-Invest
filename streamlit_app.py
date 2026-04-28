import json
import requests
import streamlit as st

DEFAULT_ENDPOINT = "https://cmsback.vridevops.site/api/grupos-reconocidos"

SYSTEM_FIELDS = {"id", "createdAt", "updatedAt", "publishedAt", "documentId"}

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


def match_endpoint_field(field, endpoint_fields):
    normalized = default_api_field_name(field)
    if normalized in endpoint_fields:
        return normalized
    if field in endpoint_fields:
        return field
    return normalized


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


def build_probe_url(endpoint):
    if "?" in endpoint:
        return f"{endpoint}&pagination[pageSize]=1"
    return f"{endpoint}?pagination[pageSize]=1"


def extract_fields_from_record(record):
    if not isinstance(record, dict):
        return [], {}

    if "attributes" in record and isinstance(record["attributes"], dict):
        attributes = record["attributes"]
        fields = [key for key in attributes.keys() if key not in SYSTEM_FIELDS]
        return sorted(fields), attributes

    fields = [key for key in record.keys() if key not in SYSTEM_FIELDS]
    sample = {key: record[key] for key in fields}
    return sorted(fields), sample


def extract_fields_from_response(payload):
    if isinstance(payload, dict) and "data" in payload:
        data = payload["data"]
        if isinstance(data, list) and data:
            return extract_fields_from_record(data[0])
        if isinstance(data, dict):
            return extract_fields_from_record(data)

    if isinstance(payload, list) and payload:
        return extract_fields_from_record(payload[0])

    if isinstance(payload, dict):
        return extract_fields_from_record(payload)

    return [], {}


def fetch_endpoint_fields(endpoint, token, timeout):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    probe_url = build_probe_url(endpoint)
    try:
        response = requests.get(probe_url, headers=headers, timeout=timeout)
    except requests.RequestException as exc:
        return None, None, exc

    if response.status_code not in (200, 201):
        return None, None, f"Codigo {response.status_code}"

    try:
        payload = response.json()
    except ValueError:
        return None, None, "Respuesta no es JSON"

    fields, sample = extract_fields_from_response(payload)
    if not fields:
        return None, None, "No se detectaron campos en el endpoint"
    return fields, sample, None


def test_connection(endpoint, token, timeout):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        return requests.get(endpoint, headers=headers, timeout=timeout)
    except requests.RequestException as exc:
        return exc


def coerce_value(value):
    if isinstance(value, str):
        trimmed = value.strip()
        if not trimmed:
            return ""
        if trimmed.startswith("{") or trimmed.startswith("["):
            try:
                return json.loads(trimmed)
            except json.JSONDecodeError:
                return trimmed
        return trimmed
    return value


def render_dynamic_fields(fields, sample, use_sample_values=False):
    values = {}
    for field in fields:
        sample_value = sample.get(field) if isinstance(sample, dict) else None
        default_value = sample_value if use_sample_values else None
        label = field.replace("_", " ").title()
        key = f"field_{field}"

        if isinstance(sample_value, bool):
            values[field] = st.checkbox(label, value=bool(default_value), key=key)
        elif isinstance(sample_value, int) and not isinstance(sample_value, bool):
            value = default_value if isinstance(default_value, int) else 0
            values[field] = st.number_input(label, value=value, step=1, key=key)
        elif isinstance(sample_value, float):
            value = default_value if isinstance(default_value, float) else 0.0
            values[field] = st.number_input(label, value=value, step=0.01, key=key)
        elif isinstance(sample_value, (list, dict)):
            raw = json.dumps(sample_value, ensure_ascii=False, indent=2) if default_value else ""
            values[field] = st.text_area(label, value=raw, key=key)
        else:
            raw_value = "" if default_value is None else str(default_value)
            if field.lower() in {"integrantes", "descripcion", "detalle"} or "\n" in raw_value:
                values[field] = st.text_area(label, value=raw_value, key=key)
            else:
                values[field] = st.text_input(label, value=raw_value, key=key)

    return values


st.set_page_config(page_title="Carga Strapi", layout="centered")

if "endpoint_fields" not in st.session_state:
    st.session_state.endpoint_fields = []
    st.session_state.endpoint_sample = {}
    st.session_state.endpoint_url = ""
    st.session_state.endpoint_error = None

st.title("Carga a Strapi: VRI grupos de investigacion")
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
                fields, sample, error = fetch_endpoint_fields(endpoint, token, timeout)
                if error:
                    st.session_state.endpoint_fields = []
                    st.session_state.endpoint_sample = {}
                    st.session_state.endpoint_url = endpoint
                    st.session_state.endpoint_error = error
                    st.warning(f"No se pudo detectar campos: {error}")
                else:
                    st.session_state.endpoint_fields = fields
                    st.session_state.endpoint_sample = sample
                    st.session_state.endpoint_url = endpoint
                    st.session_state.endpoint_error = None
                    st.success(f"Campos detectados: {len(fields)}")
            elif result.status_code in (401, 403):
                st.warning("Conexion OK, pero token no autorizado")
            else:
                st.info("Conexion OK, revisa el codigo y respuesta")
        else:
            st.error(f"Error de conexion: {result}")

    if st.session_state.endpoint_fields and st.session_state.endpoint_url == endpoint:
        st.caption(f"Campos en endpoint: {', '.join(st.session_state.endpoint_fields)}")

st.subheader("Datos del grupo")
tabs = st.tabs(["Formulario", "JSON"])

with tabs[0]:
    with st.form("registro_form"):
        endpoint_fields = st.session_state.endpoint_fields
        endpoint_sample = st.session_state.endpoint_sample

        if endpoint_fields:
            st.info("Campos cargados desde el endpoint.")
            values = render_dynamic_fields(endpoint_fields, endpoint_sample, use_sample_values=False)
        else:
            st.warning("No hay campos del endpoint. Usa 'Probar conexion' en la barra lateral.")
            values = {
                "nombre": st.text_input("Nombre"),
                "anio": st.number_input("Anio", min_value=1900, max_value=2100, value=2025, step=1),
                "facultad": st.text_input("Facultad"),
                "escuela": st.text_input("Escuela"),
                "responsable": st.text_input("Responsable"),
                "linea": st.text_input("Linea"),
                "integrantes": st.text_area("Integrantes", help="Uno por linea"),
            }

        show_payload = st.checkbox("Mostrar payload antes de enviar", value=False)
        submitted = st.form_submit_button("Enviar registro")

    if submitted:
        if not endpoint.strip():
            st.error("Endpoint vacio")
        elif not token.strip():
            st.error("Token vacio")
        else:
            if endpoint_fields:
                data = {field: coerce_value(values.get(field, "")) for field in endpoint_fields}
            else:
                data = {
                    "nombre": str(values.get("nombre", "")).strip(),
                    "anio": str(int(values.get("anio", 0))),
                    "facultad": str(values.get("facultad", "")).strip(),
                    "escuela": str(values.get("escuela", "")).strip(),
                    "responsable": str(values.get("responsable", "")).strip(),
                    "linea": str(values.get("linea", "")).strip(),
                    "integrantes": str(values.get("integrantes", "")).strip(),
                }

            payload = build_payload(data)

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

        endpoint_fields = st.session_state.endpoint_fields
        endpoint_field_set = set(endpoint_fields)

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

        normalized_fields = {field: match_endpoint_field(field, endpoint_fields) for field in all_fields}
        normalized_field_set = set(normalized_fields.values())
        if endpoint_fields:
            missing_fields = sorted(endpoint_field_set - normalized_field_set)
            extra_fields = sorted(normalized_field_set - endpoint_field_set)
            if missing_fields:
                st.warning(f"Faltan campos del endpoint en el JSON: {', '.join(missing_fields)}")
            if extra_fields:
                st.warning(f"Campos del JSON no existen en el endpoint: {', '.join(extra_fields)}")

        if endpoint_fields:
            default_fields = [
                field for field in all_fields if normalized_fields[field] in endpoint_field_set
            ]
        else:
            default_fields = all_fields

        fields = st.multiselect("Campos a enviar", options=all_fields, default=default_fields)
        edit_field_names = st.checkbox("Editar nombres de campo (API)", value=False)

        field_mapping = {}
        if edit_field_names:
            st.write("Mapa de campos")
            for field in fields:
                field_mapping[field] = st.text_input(
                    f"{field} ->",
                    value=match_endpoint_field(field, endpoint_fields),
                    key=f"map_{field}",
                )
        else:
            for field in fields:
                field_mapping[field] = match_endpoint_field(field, endpoint_fields)

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
