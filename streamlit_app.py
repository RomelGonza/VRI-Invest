import json
import requests
import streamlit as st

DEFAULT_ENDPOINT = "https://cmsback.vridevops.site/api/grupos-reconocidos"


def build_payload(values):
    return {
        "data": {
            "nombre": values["nombre"],
            "anio": str(values["anio"]),
            "facultad": values["facultad"],
            "escuela": values["escuela"],
            "responsable": values["responsable"],
            "linea": values["linea"],
            "integrantes": values["integrantes"],
        }
    }


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
with st.form("registro"):
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
        "anio": int(anio),
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

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)
            if response.status_code in (200, 201):
                st.success("Registro guardado correctamente")
            else:
                st.error(f"Error: codigo {response.status_code}")
                try:
                    st.code(json.dumps(response.json(), ensure_ascii=False, indent=2), language="json")
                except ValueError:
                    st.text(response.text)
        except requests.RequestException as exc:
            st.error(f"Error critico de conexion: {exc}")
