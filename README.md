# Carga Strapi (Grupos reconocidos)

App en Streamlit para enviar un registro individual a un endpoint de Strapi.

## Requisitos

- Python 3.9+

## Instalacion

```bash
pip install -r requirements.txt
```

## Ejecutar

```bash
streamlit run streamlit_app.py
```

## Uso

1. Coloca tu token en el panel lateral.
2. Ajusta el endpoint si es necesario.
3. Usa "Probar conexion" para detectar los campos del endpoint.
4. Completa los datos del grupo o sube un JSON.
5. Selecciona los campos a enviar y, si necesitas, ajusta el nombre del campo en la API.
6. El JSON se compara con los campos del endpoint y muestra faltantes o extra.
