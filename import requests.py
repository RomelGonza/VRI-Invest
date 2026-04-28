import os
import requests
import pandas as pd
import time

TOKEN = os.getenv("STRAPI_TOKEN", "")
ENDPOINT_URL = "https://cmsback.vridevops.site/api/grupos-reconocidos" 

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

datos = [
    {
        "Nombre": "GRUPO DE INVESTIGACIÓN DE BIO DISPONIBILIDAD-IBIS",
        "Anio": 2025,
        "Facultad": "CIENCIAS AGRARIAS",
        "Escuela": "Ingeniería Agroindustrial",
        "Responsable": "Dra. Marianela Collin Cutimbo",
        "Linea": "Recursos naturales y medio ambiente",
        "Integrantes": "Dr. Juan Marcos Aro Aro\nDra. Nancy Yaneth Mayta Quispe\nDra. Beatriz Vilma Mamani Mamani\nDra. Nicaela Pilar Terroba Quispe\nDr. Allan Steve Nahuincopa Vergara"
    },
    {
        "Nombre": "GRUPO DE INVESTIGACIÓN EN SALUD ANIMAL (GIENSA)",
        "Anio": 2025,
        "Facultad": "MEDICINA VETERINARIA Y ZOOTECNIA",
        "Escuela": "Medicina Veterinaria y Zootecnia",
        "Responsable": "Dr. Pedro Ubaldo Colla Añasco",
        "Linea": "Salud Animal",
        "Integrantes": "Dr. Celso Zapata Coacalla\nDr. Renan Dilton Hañari Quispe\nDr. Hugo Vilcanqui Mamani\nDra. Mery Luz Aliaga Tapia"
    },
    {
        "Nombre": "GRUPO DE INNOVACIÓN Y ESTUDIOS ECONÓMICO SOCIALES (GIIES)",
        "Anio": 2025,
        "Facultad": "INGENIERÍA ECONÓMICA",
        "Escuela": "Ingeniería Económica",
        "Responsable": "Dr. Roberto Arpi Mayta",
        "Linea": "Economía y Desarrollo",
        "Integrantes": "Dr. Rene Paz Paredes Mamani\nDr. Raúl Rojas Apaza\nDra. Carmen Nieves Quispe Lino\nDr. Efrain Franco Chura Zea\nDr. Henry Aldo Sucari Turpo\nDr. Sabino Edgar Mamani Choque\nDr. William Gilmer Parillo Mamani\nDr. Julio Jesús Espinoza Caldin"
    },
    {
        "Nombre": "GRUPO DE INVESTIGACIÓN INNOVANDO-FIE",
        "Anio": 2025,
        "Facultad": "INGENIERÍA ECONÓMICA",
        "Escuela": "Ingeniería Económica",
        "Responsable": "Dra. Maria del Pilar Blanco Espezia",
        "Linea": "Políticas públicas y desarrollo regional",
        "Integrantes": "Dra. Carmen Nieves Quispe Lino\nDr. Edwin Catacora Vidangos\nDr. Efrain Franco Chura Zea"
    },
    {
        "Nombre": "COLECTIVO INTERDISCIPLINARIO DE INVESTIGACIÓN-ACCIÓN TRANSFORMADORA",
        "Anio": 2025,
        "Facultad": "CIENCIAS SOCIALES",
        "Escuela": "Sociología",
        "Responsable": "Dr. Gustavo Medina Vilca",
        "Linea": "Sociedad Cultural y Comunicación",
        "Integrantes": "Dr. Percy Huata Panca\nDr. Samuel Gallegos Copa\nDra. Danitza Luisa Sardón Ari\nDr. Alcides Huamani Peralta\nDr. Félix Abelardo Arizaca Torreblanca\nINVEST. COLABORADORES:\nMaria Eugenia Robles Bengoa\nLieve Vangehuchten"
    },
    {
        "Nombre": "SINERGIA MULTIDISCIPLINAR PARA EL DESARROLLO EDUCATIVO Y SOCIAL (SIMUDES)",
        "Anio": 2025,
        "Facultad": "CIENCIAS DE LA EDUCACIÓN",
        "Escuela": "Educación Secundaria",
        "Responsable": "Dra. Indira Iracema Gómez Arteta",
        "Linea": "Educación y dinámica educativa",
        "Integrantes": "Dra. Brígida Bonifaz Valdez\nDra. Myrna Cleofe Sánchez Rossel"
    },
    {
        "Nombre": "INVESTIGADORES DEL TITICACA PARA EL PROGRESO ACADÉMICO Y CIENTÍFICO (INTIPAC)",
        "Anio": 2025,
        "Facultad": "CIENCIAS DE LA EDUCACIÓN",
        "Escuela": "Educación Secundaria",
        "Responsable": "Dra. Rebeca Alanoca Gutiérrez",
        "Linea": "Innovación educativa y practicas pedagógicas. - Desarrollo Humano y calidad de vida. - Nuevas tecnologías - informática de software, bases de datos e Inteligencia de negocios",
        "Integrantes": "Dr. Yuselino Maquera Maquera\nDr. Oliver Amadeo Vilca Huayta\nDra. Zara Turpo Puma\nDr. Eder Pacori Zapana\nColaboradores:\nDr. Osbaldo Washington Turpo Gebera\nDr. Miguel Angel Gutierrez Machaca"
    },
    {
        "Nombre": "SOCIEDAD CIENTÍFICA PARA EL DESARROLLO DE EDUCACIÓN TRANSDISCIPLINARIA",
        "Anio": 2025,
        "Facultad": "CIENCIAS DE LA EDUCACIÓN",
        "Escuela": "Educación Primaria",
        "Responsable": "Dr. Wilson Gregorio Sucari Turpo",
        "Linea": "Educación y dinámica educativa",
        "Integrantes": "Dr. Salvador Hancco Aguilar\nDr. Reynaldo Cutipa Luque\nDra. Diana Agueda Vargas Velásquez"
    },
    {
        "Nombre": "CONEXIÓN A LA CIENCIA",
        "Anio": 2025,
        "Facultad": "CIENCIAS DE LA EDUCACIÓN",
        "Escuela": "Educación Primaria",
        "Responsable": "Dr. Fredy Sosa Gutiérrez",
        "Linea": "Innovación educativa y uso de tecnologías. - Formación y desarrollo profesional docente. - Evaluación y calidad educativa. - Equidad e Inclusión educativa - Currículo y diseño pedagógico",
        "Integrantes": "Dra. Yobana Milagros Calisín Chambilla\nM. Sc. Juan Alexander Condori Palomino\nDr. Henry Mark Vilca Apaza\nM. Sc. Estanislao Pacompia Cari\nDra. Yessica Dominga Díaz Villancuyl"
    },
    {
        "Nombre": "FIGM INGENIEROS EN ACCIÓN",
        "Anio": 2025,
        "Facultad": "INGENIERÍA GEOLÓGICA Y METALÚRGICA",
        "Escuela": "Ingeniería Geológica",
        "Responsable": "Dra. Sofia Lourdes Benavente Fernández",
        "Linea": "Geometalurgia y Medio Ambiente. Geociencias y medio ambiente",
        "Integrantes": "Dr. Julio Alfredo Maquera Gil\nDra. Fabiola Coya Huanca\nOswaldo L. Maynas Mamani\nDr. Ernesto Samuel Mamani Canqui\nDr. Alfredo Mamani Canqui\nCOLABORADOR:\nDr. Ronald Quispe Vilca\nDr. Agustín Victor Vélez Velez\nMilagros Pinzas López\nRoxana Nila Medrano Pari\nDr. Boris Espinoza Salmon"
    },
    {
        "Nombre": "REPENSANDO EL DERECHO",
        "Anio": 2025,
        "Facultad": "CIENCIAS JURÍDICAS Y POLÍTICAS",
        "Escuela": "Derecho",
        "Responsable": "Dr. Juan Casazola Ccama",
        "Linea": "Derecho",
        "Integrantes": "Dra. Irene Huanca Gonzales\nDr. Michael Espinoza Colla\nMtto. Galbarino Rosinaldo Ponce Flores"
    },
    {
        "Nombre": "GRUPO DE INVESTIGACIÓN ELECTROQUÍMICA Y MATERIALES - GIEM",
        "Anio": 2025,
        "Facultad": "INGENIERÍA QUÍMICA",
        "Escuela": "Ingeniería Química",
        "Responsable": "Dr. Teófilo Donaires Flores",
        "Linea": "Tecnologías ambientales y recursos naturales. - Tecnologías de materiales",
        "Integrantes": "Dra. Edith Tello Palma\nDr. Wilfredo Fernando Villanueva\nDr. Wilfredo Fernando Villanueva Pacho\nDra. Marleni Yovanna Valencia Pacho\nDr. Luis Alberto Supo Quispe\nJosé Néstor Mamani Quispe"
    },
    {
        "Nombre": "GRUPO DE INVESTIGACIÓN DE ALIMENTOS FUNCIONALES Y SALUD GIAFS",
        "Anio": 2025,
        "Facultad": "INGENIERÍA QUÍMICA",
        "Escuela": "Ingeniería Química",
        "Responsable": "Dra. Edith Tello Palma",
        "Linea": "Alimentación y Nutrición Humana",
        "Integrantes": "Dra. Myrian Eugenia Pacheco Tanaka\nDr. Wilfredo Fernando Villanueva\nDra. Adelaida Giovanna Viza Salas\nDra. Luz Marina Teves Flores\nDra. Aida Jiménez Cutipa"
    },
    {
        "Nombre": "GRUPO DE INVESTIGACIÓN EN SIMULACIÓN Y MODELAMIENTO DE PROCESOS ELECTRO-HIDROMETALÚRGICOS Y MINEROS - SIMPEM",
        "Anio": 2025,
        "Facultad": "INGENIERÍA QUÍMICA",
        "Escuela": "Ingeniería Química",
        "Responsable": "Dr. José Néstor Mamani Quispe",
        "Linea": "Ingeniería de procesos. Metalurgia extractiva",
        "Integrantes": "Dr. Hipólito Córdova Gutiérrez\nDra. Ruth Armida Meza Damas\nDr. Teófilo Donaires Flores\nCOLABORADORES:\nCinthya Dayana Salas Asencio\nClaudia Alexandra Melgarejo Bolivar"
    },
    {
        "Nombre": "INNOVACIÓN MULTIDISCIPLINARIA EN ACCIONES SOCIOAMBIENTALES (IMAS)",
        "Anio": 2025,
        "Facultad": "INGENIERÍA AGRÍCOLA",
        "Escuela": "Ingeniería Agrícola",
        "Responsable": "Dr. José Antonio Mamani Gómez",
        "Linea": "Educación Ambiental. - gestión hídrica urbana, tecnologías verdes. - Participación comunitaria, desarrollo sostenible. - Infraestructura verde y adaptación al cambio climático.",
        "Integrantes": "Dr. Celso Augusto Guimaries Santos\nDr. Pedro Christopher Rau Lavado\nDra. Joselyn Lisbeth Villa Cavero\nDr. Roberto Alfaro Alejo\nDra. Danitza Luisa Sardón Ari\nDra. Zesy Yadayda Sardon Ari\nCOLABORADORES:\nEdiluz Yaquelin Labra Quispe\nJulio Cesar Huallahualla Ramos\nJeferson Enrique Tapia Barrantes\nLuis Angel Maquera Quispe"
    },
    {
        "Nombre": "GRUPO DE INVESTIGACIÓN EN GEOTECNOLOGIAS APLICADAS A RECURSOS HIDRICOS Y RIESGOS DE DESASTRES - GIGARH-RD",
        "Anio": 2025,
        "Facultad": "INGENIERÍA AGRÍCOLA",
        "Escuela": "Ingeniería Agrícola",
        "Responsable": "Dr. Wilber Fermin Laqui Vilca",
        "Linea": "Geomático y sensores remotos. - Ingeniería y gestión de recursos hídricos. - Gestión de recursos y desastres.",
        "Integrantes": "Dr. Roberto Alfaro Alejo\nDr. Yony Angel Laqui Vilca\nDra. Milanes Mabel Zapana Quispe\nCOLABORADORES:\nIng. Ulises Ccama Ticona\nRicardo Zubieta Barragán\nDarwin Dávalos Mamani Mancilla\nMariela Coaquira Valeriano\nSeidhy Melany Sonco Ticona"
    },
    {
        "Nombre": "GIISA - GRUPO ITERDISCIPLINARIO DE INVESTIGACIÓN EN SUSTENTABILIDAD Y ANÁLISIS",
        "Anio": 2025,
        "Facultad": "INGENIERÍA AGRÍCOLA",
        "Escuela": "Ingeniería Agrícola",
        "Responsable": "Dr. Roberto Alfaro Alejo",
        "Linea": "Ciencias de ríos, Recursos hídricos, medio ambiente. - Economía, políticas públicas. - Economía y negocios. - Sistemas, tecnología",
        "Integrantes": "Dr. Rene Paz Paredes Mamani\nDr. Marco Félix Romaní Mori\nDr. Oliver Amadeo Vilca Huayta\nDr. Ever Amadeo Vilca Huayta"
    },
    {
        "Nombre": "GRUPO DE INVESTIGACIÓN EN ARQUITECTURA, MATERIALES ALTERNATIVOS Y SOSTENIBILIDAD - ARQUIMAS",
        "Anio": 2025,
        "Facultad": "INGENIERÍA CIVIL Y ARQUITECTURA",
        "Escuela": "Arquitectura y Urbanismo",
        "Responsable": "Dr. Hugo Anselmo Ccama Condori",
        "Linea": "Arquitectura, Confort Ambiental y Eficiencias Energética",
        "Integrantes": "Dra. Leydia Cinthia Aza Medina\nDra. Diana Karen Pari Quispe\nDra. Estela Karem Samamé Samamé\nDra. Pamela Celeste Gutierrez Salas\nDr. Jhon Steve Valeriano Larico\nDra. Sandra Marisol Maquera Ramos"
    },
    {
        "Nombre": "GRUPO DE INVESTIGACIÓN EN SISTEMAS INTEGRADOS PARA ENTORNOS INTELIGENTES",
        "Anio": 2025,
        "Facultad": "INGENIERÍA MECÁNICA ELÉCTRICA, ELECTRÓNICA Y SISTEMAS",
        "Escuela": "Ingeniería Electrónica",
        "Responsable": "Dr. Euler Edson Apaza Medina",
        "Linea": "Tecnología, Ingeniería, electrónica, redes de datos, 5G, IoT, Automática y tecnología",
        "Integrantes": "Dr. Jasmany Ruelas Chambi\nDr. Lucio Quispe Apaza\nDr. Eddy Torres Mamani\nDra. Yobana Milagros Calisín Chambilla\nIng. Ester Carolina Mendoza Yarest\nIng. Susan Machaca Condori\nIng. Eygner Calcina Quispe"
    },
    {
        "Nombre": "GIICDA - GRUPO DE INVESTIGACIÓN EN SISTEMAS INTELIGENTES ARTIFICIAL Y CIENCIA DE DATOS APLICADA",
        "Anio": 2025,
        "Facultad": "INGENIERÍA MECÁNICA ELÉCTRICA, ELECTRÓNICA Y SISTEMAS",
        "Escuela": "Ingeniería de Sistemas",
        "Responsable": "Dr. Aldo Hernán Zanabria Gálvez",
        "Linea": "Inteligencia Artificial Aplicada - Ciencia de Datos para el Desarrollo Territorial - Transformación Digital y Gobierno Electrónico - Turismo e Inteligencia - Gestión del Talento Humano Inteligente y Gestión de Tecnologías - Educación Digital.",
        "Integrantes": "Dr. Alfredo Pelayo Calatayud Mendoza\nDr. Mario Silva Dueñas\nDr. Oliver Amadeo Vilca Huayta\nDr. Pablo Tapia Catacora\nDr. Adolfo Carlos Jiménez Cutipa\nCOLABORADORES:\nClaudia Alexandra Melgarejo Bolivar\nMtro. Edwin Mestanza Yucra"
    }
]


df_prueba = pd.DataFrame(datos)

print("Iniciando prueba de conexion y carga con Strapi...\n")

for index, row in df_prueba.iterrows():
    payload = {
        "data": {
            "nombre": str(row["Nombre"]),
            "anio": str(row["Anio"]),         
            "facultad": str(row["Facultad"]),
            "escuela": str(row["Escuela"]),
            "responsable": str(row["Responsable"]),
            "linea": str(row["Linea"]),
            "integrantes": str(row["Integrantes"])
        }
    }

    try:
        response = requests.post(ENDPOINT_URL, json=payload, headers=headers, timeout=30)
        if response.status_code in [200, 201]:
            print(f"Exito en Registro {index + 1}: '{row['Nombre']}' guardado correctamente.")
        else:
            print(f"Error en Registro {index + 1}: Codigo {response.status_code}")
            try:
                print(f"Detalle del servidor: {response.json()}\n")
            except Exception:
                print(f"Detalle del servidor (texto): {response.text}\n")
    except Exception as e:
        print(f"Error critico de conexion: {e}")

    time.sleep(0.5)

print("\nPrueba finalizada. Por favor, revisa el panel de Strapi para confirmar.")