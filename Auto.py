
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support import expected_conditions as EC
from pywinauto import Application
import pygetwindow as gw
import time
#-----------------------------
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import sys
import argparse


# Recibimos los datos de la interface
parser = argparse.ArgumentParser()

parser.add_argument("option1", type=str, help="Departamento")
parser.add_argument("option2", type=str, help="Clase")
parser.add_argument("selected_text2", type=str, help="Solicitud de viaticos")
parser.add_argument("date1", type=str, help="Fecha inicio")
parser.add_argument("date2", type=str, help="Fecha fin")
parser.add_argument("selected_caso", type=str, help="Primera opción de texto")
parser.add_argument("selected_cliente", type=str, help="Primera opción de texto")
parser.add_argument("selected_folder", type=str, help="Primera opción de texto")
parser.add_argument("selected_email", type=str, help="Primera opción de texto")
parser.add_argument("selected_password", type=str, help="Primera opción de texto")



args = parser.parse_args()

# Le damos el formato adecuado a las fechas que vienen de la interface
fecha_objeto1 = datetime.strptime(args.date1, "%Y-%m-%d")
fecha_inicio = fecha_objeto1.strftime("%d/%m/%Y")
fecha_objeto2 = datetime.strptime(args.date2, "%Y-%m-%d")
fecha_fin = fecha_objeto2.strftime("%d/%m/%Y")

print(f"Departamento: {args.option1}")
print(f"Clase: {args.option2}")
print(f"Option3: {args.selected_text2}")
print(f"Date1: {fecha_inicio}")
print(f"Date2: {fecha_fin}")
print(f"ruta del folder: {args.selected_folder}")
print(f"Email: {args.selected_email}")
print(f"Contraseña: {args.selected_password}")
print(f"caso: {args.selected_caso}")
print(f"cliente: {args.selected_cliente}")

t=0.2
#---------------------Extraccion de datos de facturas----------------
# Definir la carpeta donde se encuentran los archivos XML
carpeta = args.selected_folder  # Cambia esta ruta a la carpeta donde tienes los archivos XML

# Definir los espacios de nombres (siempre es necesario para CFDI)
namespaces = {
    'cfdi': 'http://www.sat.gob.mx/cfd/4',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital',
    'implocal': 'http://www.sat.gob.mx/implocal'  # Asegúrate de que este coincida con el XML
}

#-----------------Función para procesar un archivo XML---------------------------
def procesar_xml(archivo):
    tree = ET.parse(archivo)
    root = tree.getroot()
    #--------------Extraemos el subtotoal
   
    subtotal = root.get('SubTotal')
    if subtotal:
        subtotal_float = float(subtotal)
        print(f"Total encontrado: {subtotal_float}")
        
    else:
        print("No se encontró el atributo 'Total' en el XML.")

    

            

    #--------------Estraer el ISH
    ish = 0
    traslado_local = root.find('.//implocal:TrasladosLocales', namespaces)
    if traslado_local is not None:
        ish = float(traslado_local.attrib.get('Importe', 0))

    #--------------Extraer IVA
    try:
        # Asegurarnos de que los espacios de nombres son válidos
        if not namespaces or 'cfdi' not in namespaces:
            raise ValueError("Namespaces inválidos o ausentes.")

        # Buscar elementos <cfdi:Traslado> con Impuesto="002" (IVA)
        traslados = root.findall('.//cfdi:Traslado[@Impuesto="002"]', namespaces)
        
        if traslados:
            # Intentar extraer el valor del atributo Importe
            for traslado in traslados:
                iva = traslado.get('Importe')
                if iva:
                    try:
                        iva = float(iva)
                        print(f"IVA encontrado: {iva}")
    
                    except ValueError:
                        print(f"Error al convertir el IVA a float: {iva}")
                        continue
                else:
                    print("El atributo 'Importe' no está presente en el traslado.")
        else:
            print("No se encontró IVA en el XML.")
            
    except Exception as e:
            print(f"Error al procesar el XML: {e}")

    #------------Extraer el folio fiscal (UUID)
    uuid = root.find('.//tfd:TimbreFiscalDigital', namespaces).attrib['UUID']

    #------------Extraer la fecha de emisión
    fecha_emision = root.attrib['Fecha']
    #------------Convertir fecha a objeto datetime
    fecha_objeto = datetime.strptime(fecha_emision, "%Y-%m-%dT%H:%M:%S")
    #------------Dar formato a la fecha de emisión
    fecha = fecha_objeto.strftime("%d/%m/%Y")

    #------------Impuestos
    impuestos='16%' 

    #------------Extraer el nombre del emisor
    nombre_emisor = root.find('.//cfdi:Emisor', namespaces).attrib['Nombre']

    #------------Cambiar la extensión del archivo XML a PDF
    archivo_pdf = os.path.splitext(archivo)[0] + '.pdf'

    # ---------extraer el nombre------------
    prenombre = os.path.splitext(archivo)[0] 
    nombre = os.path.basename(prenombre)
    print(f'El nombre del archivo es {nombre}')

     #-----------Verificar si el archivo PDF existe
    if not os.path.exists(archivo_pdf):
        raise FileNotFoundError(f"El archivo PDF correspondiente a {archivo} no se encontró.")

    if ish != 0:
        subtotal_float += iva
        impuestos = 'Exento'
        iva = 0

    if iva == 0:
        impuestos = 'Exento'
    # Retornar la información extraída
    return {
        'archivo_xml': archivo,
        'archivo_pdf': archivo_pdf,
        'ruta_pdf': os.path.abspath(archivo_pdf),
        'subtotal': subtotal_float,
        'uuid': uuid,
        'fecha_emision': fecha_emision,
        'fecha':fecha,
        'nombre_emisor': nombre_emisor,
        'iva':iva,
        'ish': ish,
        'impuestos':impuestos,
        'nombre':nombre
         
        
    }

#--------------------Esta funcion se encarga de recorrer las lineas y poner datos---------------
def procesar_linea_factura(driver, datos, tiempo_espera):
    """
    Procesa una línea de factura utilizando los datos extraídos del XML.
    """
    action = ActionChains(driver)
    t=tiempo_espera
    for a in range(29):
            opcion = a  # Cambia esto por la condición real
            match opcion:
                case 0:
                    #-----Indicador-----
                    print("Ejecutando acción para la opción 0")
                    action = ActionChains(driver)
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                case 1:
                    #-----Fecha-----
                    # Asegúrate de que el campo está enfocado
                    print("Ejecutando acción para la opción 1")
                    time.sleep(t)
                    action.send_keys(datos['fecha']).perform()
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()  # Pasa al siguiente campo
                    
                case 2:
                    #-----Categoria-----
                    print("Ejecutando acción para la opción 2")
                    time.sleep(t+0.1)
                    action.send_keys("PASAJES Y TRANSPORTACION").perform()
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                    
                case 3:
                    #-----Solicitud de viaticos-----
                    print("Ejecutando acción para la opción 3")
                    time.sleep(t)
                    action.send_keys(args.selected_text2).perform()
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                    
                case 4:
                    #-----Moneda-----
                    print("Ejecutando acción para la opción 4")
                    time.sleep(t)
                    action.send_keys("MXN").perform()
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                case 5:
                    #-----Importe extranjero-----
                    print("Ejecutando acción para la opción 5")
                    time.sleep(t)
                    action.send_keys(datos['subtotal']).perform()
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                case 6:
                    #-----Tipo de cambio-----
                    print("Ejecutando acción para la opción 6")
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                case 7:
                    #-----Importe-----
                    print("Ejecutando acción para la opción 7")
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                case 8:
                    #-----Impuestos-----
                    print("Ejecutando acción para la opción 8")
                    time.sleep(t)
                    action.send_keys(datos['impuestos']).perform()
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                case 9:
                    #-----Importe de impuestos-----
                    print("Ejecutando acción para la opción 9")
                    time.sleep(t+0.2)
                    action.send_keys(datos['iva']).perform()
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                case 10:
                    #-----Imp bruto-----
                    print("Ejecutando acción para la opción 10")
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                case 11:
                    #-----Adjuntar archivo-----
                    # Damos click en el campo de subir archivo para que se despliegue el boton
                    if datos['archivo_xml'] == None:
                        print("Saltamos acción para la opción 11")
                        time.sleep(t)
                        action.send_keys(Keys.TAB).perform()
                    else: 
                        print("Ejecutando acción para la opción 11")   
                        campo_subir = driver.find_element(By.NAME, "expmediaitem_display")
                        time.sleep(1)
                        campo_subir.click()
                        
                    
                        # Presionamos el boton se + para subir el archivo
                        subir = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//a[@data-helperbuttontype='new']"))
                        )
                        subir.click()
                        
                        
                        time.sleep(1)
                        # Guarda el identificador de la ventana principal
                        main_window = driver.current_window_handle

                        # Cambia el foco a la nueva ventana
                        driver.switch_to.window(driver.window_handles[1])

                        #Refrescar
                        driver.refresh()

                        # Ahora estás en la ventana emergente, realiza las acciones para subir el PDF
                        #Damos clic en subir archivo de la ventana emergente
                        campo_entrada2 = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.ID, "mediafile_fs"))  # Ajusta el selector según corresponda
                        )
                        campo_entrada2.click()


                        time.sleep(1)

                        # Interactúa con la ventana de selección de archivos
                        app = Application(backend='win32').connect(title='Abrir', visible_only=False)  # Cambia el patrón según corresponda
                        dialog = app.window(title_re='Abrir')  # Cambia según el título de la ventana
                        dialog.Edit.set_edit_text(datos['ruta_pdf'])
                        dialog['Abrir'].click_input()  # Asegúrate de que el botón tenga el nombre correcto (puede ser "Abrir")

                        # Espera a que el archivo se cargue o se complete el proceso
                        time.sleep(2)

                        # Cierra la aplicación
                        app.kill()
                        #-----------------------------------------S

                        # Cambia el foco a la nueva ventana
                        driver.switch_to.window(driver.window_handles[1])

                        #Damos clic en guardar archivo de la ventana emergente
                        guardar_boton = driver.find_element(By.ID, "submitter")
                        guardar_boton.click()
                        time.sleep(2.4)
                        #Tratamos la alerta en caso de que subamos un archivo repetido
                        if len(driver.window_handles) > 1:  # Verifica si hay más de una ventana
                            try:
                                alert = driver.switch_to.alert  # Intentar cambiar al foco de la alerta
                                alert.accept()  # Aceptar la alerta
                                print("Alerta aceptada.")
                            except NoAlertPresentException:
                                # Si no hay alerta, se continúa normalmente
                                print("No hay alerta, continuando el proceso.")
                        else:
                            print("No hay ventana emergente para interactuar.")

                        time.sleep(2)
                        # Cierra la ventana emergente o vuelve al foco de la ventana principal

                        # Cambia el enfoque de vuelta a la ventana principal
                        driver.switch_to.window(main_window)            
                        time.sleep(2)
                        action.send_keys(Keys.TAB).perform()
                case 12:
                    #-----Caso-----
                    print("Ejecutando acción para la opción 12")
                    time.sleep(t)
                    action.send_keys(args.selected_caso).perform()
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                case 13:
                    #-----Congreso medico-----
                    print("Ejecutando acción para la opción 13")
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                case 14:
                    #-----Nota-----
                    print("Ejecutando acción para la opción 14")
                    time.sleep(t)
                    if datos['nombre']:
                        action.send_keys(datos['nombre']).perform()
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                case 15:
                    #-----Departamento-----
                    print("Ejecutando acción para la opción 15")
                    time.sleep(t)
                    action.send_keys(args.option1).perform()
                    time.sleep(t+0.2)
                    action.send_keys(Keys.TAB).perform()
                case 16:
                    #-----Clase-----
                    print("Ejecutando acción para la opción 16")
                    time.sleep(t)
                    action.send_keys(args.option2).perform()
                    time.sleep(t+0.2)
                    action.send_keys(Keys.TAB).perform()
                case 17:
                    #-----Ubicacion-----
                    print("Ejecutando acción para la opción 17")
                    time.sleep(t)
                    action.send_keys("TULTITLAN").perform()
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                case 18:
                    #-----Cliente-----
                    print("Ejecutando acción para la opción 18")
                    #>>
                    time.sleep(t)
                    action.send_keys(args.selected_cliente).perform()
                    time.sleep(t+1.2) 
                    action.send_keys(Keys.TAB).perform()
                    time.sleep(t+0.6)
                    if args.selected_cliente != "":
                        action.send_keys(Keys.TAB).perform()
                        time.sleep(t+0.2)
                        action.send_keys(Keys.TAB).perform()
                    
                case 19:
                    #-----Recibo-----
                    print("Ejecutando acción para la opción 19")
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                case 20:
                    #-----Tarjeta corporativa-----
                    print("Ejecutando acción para la opción 20")
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                case 21:
                    #-----Proveedor-----
                    print("Ejecutando acción para la opción 21")
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                case 22:
                    #-----Tipo de operacion-----
                    print("Ejecutando acción para la opción 22")
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                case 23:
                    #-----Proveedor sustituto-----
                    print("Ejecutando acción para la opción 23")
                    time.sleep(t)
                    action.send_keys(datos['nombre_emisor']).perform()
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                case 24:
                    #-----LD asociado-----
                    print("Ejecutando acción para la opción 24")
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                case 25:
                    #-----Corporate card-----
                    print("Ejecutando acción para la opción 25")
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                case 26:
                    #-----Folio fiscal-----
                    print("Ejecutando acción para la opción 26")
                    time.sleep(t)
                    action.send_keys(datos['uuid']).perform()
                    time.sleep(t)
                    action.send_keys(Keys.TAB).perform()
                case 27:
                    #-----Fecha de emision UIID-----
                    print("Ejecutando acción para la opción 27")
                    time.sleep(t)
                    action.send_keys(datos['fecha_emision']).perform()
                    time.sleep(t)
                case 28:
                    #-----Fecha de emision agregar-----
                    print("Ejecutando acción para la opción 28")
                    time.sleep(t)
                    agregar = driver.find_element(By.ID, 'expense_addedit')
                    agregar.click() 
                    time.sleep(t)
        
                            
                case _:
                    print("Opción no reconocida")


#------------------Procesamos el reembolso------------------------

def manejar_reembolso(driver, t):
    """
    Maneja el proceso de obtener el reembolso, verificar si es positivo,
    crear el diccionario de datos y procesar la línea de factura.
    """
    print("Calculando reembolso")
    # Obtener el texto del elemento de reembolso
    reembolso = driver.find_element(By.ID, 'amount_val').text

    # Convertir el texto del reembolso en un número flotante
    reembolso_n = float(reembolso.replace(',', '').replace('-', ''))

    # Procesar si el reembolso es mayor que cero
    if reembolso_n > 0:
        datos = {
            'archivo_xml': None,
            'archivo_pdf': "",
            'ruta_pdf': "",
            'subtotal': reembolso_n,
            'uuid': "",
            'fecha_emision': "",
            'fecha':'05/12/2024',
            'nombre_emisor':"",
            'iva':0,
            'ish': 0,
            'impuestos':'Exento',
            'nombre':""
        }


        # Procesar la línea de factura
        procesar_linea_factura(driver, datos, t)
        time.sleep(2.2)

        # Manejar la posible alerta del navegador
        try:
            alert = driver.switch_to.alert
            alert.accept()
            print("Alerta aceptada.")
        except NoAlertPresentException:
            print("No hay alerta, continuando el proceso.")

    print("Reembolso:", reembolso)





#-----------------Recorremos la pagina hasta llegar a la zona de facturas---------

# Configurar el navegador (asegúrate de tener ChromeDriver en el PATH o proporcionar la ruta completa)
driver = webdriver.Chrome()

# Ir a la página web de la empresa
driver.get('https://system.netsuite.com/pages/customerlogin.jsp')

# Iniciar sesión
usuario = driver.find_element(By.NAME, 'email')  # Ajusta el selector según el campo de usuario
contrasena = driver.find_element(By.NAME, 'password')  # Ajusta el selector según el campo de contraseña

usuario.send_keys(args.selected_email)  # Ingresa tu email
contrasena.send_keys(args.selected_password)  # Ingresa tu contraseña
contrasena.send_keys(Keys.RETURN)  # Presiona Enter para enviar el formulario


# Esperar a que cargue la página de "centro de empleados"
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.LINK_TEXT, 'Introducir informes de gastos'))  # Cambia este selector según la página
)

# Dar click en el botón de introducir informe de gastos
informe = driver.find_element(By.LINK_TEXT, 'Introducir informes de gastos')
informe.click()

# Esperar a que cargue la página de "Informe de gastos"
WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.ID, 'expense_addedit'))
)
time.sleep(2)
# Llenamos el campo de departamento

departamento = driver.find_element(By.NAME, 'inpt_department')
departamento.send_keys(args.option1)

time.sleep(t)
f_inicio = driver.find_element(By.NAME, 'custbody_pslad_er_fecha_inicio_viaje')
f_inicio.send_keys(fecha_inicio)

time.sleep(t)
f_fin = driver.find_element(By.NAME, 'custbody_pslad_er_fecha_fin_viaje')
f_fin.send_keys(fecha_fin)



 # Paso 1: Haz clic en el elemento <td> para activar el campo de entrada
campo_ref = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "td[data-ns-tooltip='Ref. n.º']"))
)
campo_ref.click()

def ordenar_archivos_por_numero(lista_archivos):
    def extraer_numero(nombre):
        partes = nombre.split(' ')
        for parte in partes:
            if parte.isdigit():
                return int(parte)
        return float('inf')  # Si no se encuentra un número, ordenar al final
    return sorted(lista_archivos, key=extraer_numero)

# Recorrer todos los archivos XML en la carpeta
archivos_xml = [archivo for archivo in os.listdir(carpeta) if archivo.endswith(".xml")]
archivos_ordenados = ordenar_archivos_por_numero(archivos_xml)

action = ActionChains(driver)


  
# Recorrer todos los archivos XML en la carpeta
for archivo in archivos_ordenados:
    if archivo.endswith(".xml"):  # Procesar solo los archivos XML
        ruta_archivo = os.path.join(carpeta, archivo)
        datos = procesar_xml(ruta_archivo)
        print(datos)
        print(f"Procesado archivo XML: {datos['archivo_xml']}")
        print(f"Subiendo archivo PDF: {datos['archivo_pdf']}")
        print(f"Subtotal: {datos['subtotal']}, UUID: {datos['uuid']}, Fecha de emisión: {datos['fecha_emision']}, Nombre del emisor: {datos['nombre_emisor']}")
        print(f"Procesado ish: {datos['ish']}")
        print(f"fecha: {datos['fecha']}")
        print(f"IVA: {datos['iva']}")
        print('-' * 40)
        procesar_linea_factura(driver, datos, t)
        if datos['ish']:
            datos['subtotal']=datos['ish']
            datos['iva']=0
            procesar_linea_factura(driver, datos, t)


manejar_reembolso(driver, t)

print("Guardar")
guardar = driver.find_element(By.ID, 'tr_completelater')
guardar2 = driver.find_element(By.ID, 'tdbody_completelater')
guardar3 = driver.find_element(By.ID, 'completelater')
guardar.click()
guardar2.click()
guardar3.click()
time.sleep(50)
print("Cuenta completada")
#-------------------------Esperar para ver-----------------------
driver.quit()