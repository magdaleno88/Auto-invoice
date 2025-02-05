import os
import xml.etree.ElementTree as ET

def identificar_tipo_factura(xml_path):
    categorias = {
        "Comida": ["alimentos", "comida", "restaurante", "consumo de alimentos"],
        "Hospedaje": ["hotel", "hospedaje"],
        "Transporte": ["transporte", "taxi", "uber", "autobus"],
        "Casetas": ["caseta", "peaje"],
        "Electrónicos": ["electrónicos", "laptop", "tablet", "smartphone", "herramientas"]
    }

    # Cargar y analizar el archivo XML
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        return f"Error al analizar el archivo XML: {e}"
    except FileNotFoundError:
        return "Archivo no encontrado."

    # Extraer el texto relevante de las etiquetas
    texto_xml = []
    for elem in root.iter():
        if elem.text:
            texto_xml.append(elem.text.lower())

    # Buscar coincidencias de palabras clave en el XML
    for categoria, palabras_clave in categorias.items():
        for palabra in palabras_clave:
            if any(palabra in texto for texto in texto_xml):
                return categoria

    return "No identificado"

# Programa principal
ruta_archivo = input("Introduce la ruta del archivo XML: ")
if not os.path.exists(ruta_archivo):
    print("La ruta proporcionada no existe.")
else:
    resultado = identificar_tipo_factura(ruta_archivo)
    print(f"El archivo XML pertenece a la categoría: {resultado}")
