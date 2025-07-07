from pathlib import Path
import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QDateEdit, QPushButton, QFileDialog, QListWidget, QLineEdit, QSizePolicy,QFormLayout
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont,QIcon, QPixmap
import subprocess
from PyQt5.QtGui import QIntValidator

class ModernInterface(QMainWindow):
    SETTINGS_FILE = "settings.json"

    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.setWindowTitle("Contemplación - SMH")

        # Cambiar el ícono de la ventana (asegúrate de tener un archivo 'logo.png')
        self.setWindowIcon(QIcon("img/Logo.jpeg"))

        self.setGeometry(300, 100, 800, 600)

        # Cargar los datos guardados
        self.saved_data = self.load_settings()

        # Llamada al método que crea la interfaz
        self.initUI()

    def initUI(self):
        # Widget principal
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # Fuente moderna
        font_label = QFont("Arial", 10)
        font_input = QFont("Arial", 10)

        # Layout principal
        main_layout = QVBoxLayout(main_widget)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setSpacing(15)

        # Crear un QLabel para mostrar la imagen
        image_label = QLabel()

        # Cargar la imagen con QPixmap
        pixmap = QPixmap("img/smh.png")  # Asegúrate de que la ruta sea correcta

        # Establecer la imagen en el QLabel
        image_label.setPixmap(pixmap)

        # Ajustar la imagen al tamaño del QLabel
        image_label.setAlignment(Qt.AlignLeft)  # Centra la imagen en el QLabel
        image_label.setFixedSize(500, 75)  # Establece un tamaño fijo para el QLabel (ajusta según necesites)

        # Añadir el QLabel al layout principal
        main_layout.addWidget(image_label)

        # Layout para email y password en una sola fila
        email_password_layout = QHBoxLayout()

        # Layout para email y password en una sola fila
        self.text_email = self.create_text_input("", font_label, font_input)
        self.text_email['widget'].setPlaceholderText("Email")
        self.text_email["widget"].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.text_email["widget"].setMaximumWidth(500)
        self.text_email["widget"].setText(self.saved_data.get("email", ""))

        self.text_password = QLineEdit()
        self.text_password.setFont(font_input)
        self.text_password.setPlaceholderText("Contraseña")
        self.text_password.setEchoMode(QLineEdit.Password)
        self.text_password.setText(self.saved_data.get("password", ""))
        self.text_password.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.text_password.setMaximumWidth(330)
        self.text_password.setStyleSheet("""
            QLineEdit {
                border: 1px solid #C0C0C0;
                border-radius: 8px;
                padding: 5px;
                background-color: #162447;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #00FFFF;
            }
        """)

        # Botón para mostrar/ocultar la contraseña
        self.show_password_button = QPushButton("👁")
        self.show_password_button.setFixedSize(30, 30)  # Tamaño fijo para el botón
        self.show_password_button.setStyleSheet("""
            QPushButton {
                border: 1px solid black;  /* Contorno negro */
                border-radius: 5px;      /* Esquinas ligeramente redondeadas */
                background-color: white; /* Color de fondo inicial */
            }
            QPushButton:hover {
                background-color: #ADD8E6;  /* Cambiar color al pasar el ratón (azul claro) */
            }
            QPushButton:pressed {
                background-color: #87CEEB;  /* Cambiar color al presionar (azul cielo) */
            }
        """)
        self.show_password_button.pressed.connect(self.show_password)  # Mostrar contraseña al presionar
        self.show_password_button.released.connect(self.hide_password)  # Ocultar contraseña al soltar

       # Layout horizontal para email, contraseña y botón
        email_password_layout = QHBoxLayout()
        email_password_layout.addWidget(self.text_email["widget"])  # Email
        email_password_layout.addSpacing(20)  # Espaciado entre email y contraseña
        email_password_layout.addWidget(self.text_password)  # Contraseña
        email_password_layout.addWidget(self.show_password_button)  # Botón

        # Añadir el layout principal
        main_layout.addLayout(email_password_layout)


        # Layout para caso y cliente en una sola fila
        self.text_caso = self.create_text_input("Caso", font_label, font_input)
        self.text_caso['widget'].setPlaceholderText("Caso")
        self.text_caso["widget"].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.text_caso["widget"].setMaximumWidth(500)
        self.text_caso["widget"].setText(self.saved_data.get("caso", ""))
        self.text_caso["widget"].setValidator(QIntValidator())

        self.text_cliente = self.create_text_input("Cliente", font_label, font_input)
        self.text_cliente['widget'].setPlaceholderText("Proyecto")
        self.text_cliente["widget"].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.text_cliente["widget"].setMaximumWidth(500)
        self.text_cliente["widget"].setText(self.saved_data.get("cliente", ""))
        self.text_cliente["widget"].setValidator(QIntValidator())

        caso_cliente_layout = self.create_horizontal_pair(self.text_caso["widget"], self.text_cliente["widget"])
        main_layout.addLayout(caso_cliente_layout)

        # Departamento y clase en una sola fila
        self.selector1 = self.create_selector("Departamento", font_label, font_input, ["","ADMINISTRACION Y FINANZAS", "ADMINISTRACION Y FINANZAS : CONTABILIDAD", "ADMINISTRACION Y FINANZAS : CREDITO Y COBRANZA",
         "ADMINISTRACION Y FINANZAS : DIRECCION DE FINANZAS","ADMINISTRACION Y FINANZAS : JURIDICO","ADMINISTRACION Y FINANZAS : SISTEMA Y TELEFONIA",
         "CADENA DE SUMINISTRO", "CADENA DE SUMINISTRO : ALMACEN", "CADENA DE SUMINISTRO : COMPRAS E IMPORTACIONES",
         "CADENA DE SUMINISTRO : CORPORATIVO", "CADENA DE SUMINISTRO : CORPORATIVO : CADENA", "CADENA DE SUMINISTRO : GERENCIA",
         "CADENA DE SUMINISTRO : REGULATORIO", "CALIDAD", "CALIDAD : CALIDAD", 
         "COMERCIAL", "COMERCIAL : DIRECCION DE VENTAS", "COMERCIAL : GERENCIA COMERCIAL",
         "COMERCIAL : VENTAS BAJIO", "COMERCIAL : VENTAS CONSUMIBLES", "COMERCIAL : VENTAS GOBIERNO",
         "COMERCIAL : VENTAS GUADALAJARA", "COMERCIAL : VENTAS MONTERREY", "COMERCIAL : VENTAS PRIVADO MEXICO",
         "DIRECCION GENERAL", "DIRECCION GENERAL : CONTRALORIA", "DIRECCION GENERAL : DIRECCION GENERAL", 
         "DIRECCION GENERAL : PROYECTOS ESPECIALES", "MERCADOTECNIA", "MERCADOTECNIA : ADMIN DE VENTAS",
         "MERCADOTECNIA : APLICACIONES", "MERCADOTECNIA : COORDINACION MERCADOTECNIA", "MERCADOTECNIA : DIAGNOSTICO",
         "MERCADOTECNIA : DIRECCION MERCADOTECNIA", "MERCADOTECNIA : DISENO GRAFICO", "MERCADOTECNIA : INFORMATICA MEDICA",
         "RECURSOS HUMANOS", "RECURSOS HUMANOS : ADMON RH", "RECURSOS HUMANOS : GERENCIA RH",
         "RECURSOS HUMANOS : MANTENIMIENTO E INTENDENCIA", "RECURSOS HUMANOS : MENSAJERIA", "SERVICIO TECNICO",
         "SERVICIO TECNICO : ADMON SERVICIO TECNICO", "SERVICIO TECNICO : GERENCIA NACIONAL", "SERVICIO TECNICO : GERENCIA OPERACIONES",
         "SERVICIO TECNICO : OPERACIONES DIAGNOSTICO", "SERVICIO TECNICO : OPERACIONES GUADALAJARA", "SERVICIO TECNICO : OPERACIONES LABORATORIO",
         "SERVICIO TECNICO : OPERACIONES MASTO/DENSI", "SERVICIO TECNICO : OPERACIONES MONTERREY", "SERVICIO TECNICO : OPERACIONES RAYOS X",
         "SERVICIO TECNICO : OPERACIONES RESONANCIA MAGNETICA", "SERVICIO TECNICO : OPERACIONES SURESTE", "SERVICIO TECNICO : OPERACIONES TOMOGRAFIA",
         "SERVICIO TECNICO : OPERACIONES ULTRASONIDO", "SERVICIO TECNICO : PROYECTOS"
         ])
        self.selector1["widget"].setCurrentText(self.saved_data.get("department", ""))
        self.selector1["widget"].setMaximumWidth(500)

        self.selector2 = self.create_selector("Clase", font_label, font_input, ["", "CONSUMIBLE", "CONSUMIBLE : CONSUMIBLE",
         "CONSUMIBLE : DIRUI REACTIVOS","CONSUMIBLE : MERIDIAN CONSUMIBLES", "CONSUMIBLE : MERIDIAN IMMUNOCARDS",
         "CONSUMIBLE : MERIDIAN REACTIVOS", "CONSUMIBLE : NIHON KOHDEN REACTIVOS", "CONSUMIBLE : PANTHER INSTRUMENTS SYSTEMS",
         "CONSUMIBLE : QUÍMICA CLÍNICA REACTIVOS", "CONSUMIBLE : SNIBE REACTIVOS", "CONSUMIBLE : SPINREACT REACTIVOS",
         "CONSUMIBLE : THINPREP", "CONSUMIBLE : VITASSAY REACTIVOS", "DIAGNOSTICO",
         "DIAGNOSTICO : DIRUI INSTRUMENTS", "DIAGNOSTICO : MERIDIAN INSTRUMENTS", "DIAGNOSTICO : NIHON KOHDEN HEMATOLOGÍA",
         "DIAGNOSTICO : PANTHER INSTRUMENTS SYSTEMS", "DIAGNOSTICO : SNIBE MAGLUMI", "DIAGNOSTICO : THINPREP",
         "EQUIPO", "EQUIPO : ACCESORIOS", "EQUIPO : DENSITOMETRIA",
         "EQUIPO : FLUOROSCOPIA", "EQUIPO : HIT", "EQUIPO : MASTOGRAFIA",
         "EQUIPO : MATERNO INFANTIL", "EQUIPO : MICROSCOPIA", "EQUIPO : MONITOREO",
         "EQUIPO : RADIOTERAPIA", "EQUIPO : RAYOS X", "EQUIPO : RESONANCIA MAGNETICA",
         "EQUIPO : TOMOGRAFIA", "EQUIPO : ULTRASONIDO", "SERVICIO TECNICO",
         "SERVICIO TECNICO : ACCESORIOS", "SERVICIO TECNICO : DENSITOMETRIA", "SERVICIO TECNICO : DIAGNOSTICO",
         "SERVICIO TECNICO : FLUOROSCOPIA", "SERVICIO TECNICO : HIT", "SERVICIO TECNICO : MASTOGRAFIA",
         "SERVICIO TECNICO : MATERNO INFANTIL", "SERVICIO TECNICO : MONITOREO", "SERVICIO TECNICO : RAYOS X",
         "SERVICIO TECNICO : RESONANCIA MAGNETICA", "SERVICIO TECNICO : TOMOGRAFIA", "SERVICIO TECNICO : ULTRASONIDO"
         ])
        self.selector2["widget"].setCurrentText(self.saved_data.get("class", ""))
        self.selector2["widget"].setMaximumWidth(500)

        # Layout horizontal para los selectores
        selectors_layout = QHBoxLayout()
        selectors_layout.addLayout(self.selector1["layout"])
        selectors_layout.addSpacing(100)  # Espaciado entre los dos selectores
        selectors_layout.addLayout(self.selector2["layout"])

        # Añade el layout al layout principal
        main_layout.addLayout(selectors_layout)

        

        # Selector de texto 2
        self.text_input2 = self.create_text_input("Solicitud de viaticos:", font_label, font_input)
        main_layout.addLayout(self.text_input2["layout"])
        #self.text_input2["widget"].setText(self.saved_data.get("request", ""))

       # Layout para fechas en una sola fila
        self.date1_input = self.create_date_input("Inicio del viaje", font_label, font_input)
        self.date2_input = self.create_date_input("Fin del viaje", font_label, font_input)

        date_layout = QHBoxLayout()  # Layout horizontal para ambas fechas
        date_layout.addLayout(self.date1_input["layout"])
        date_layout.addSpacing(100)  # Espaciado entre los dos selectores
        date_layout.addLayout(self.date2_input["layout"])

        main_layout.addLayout(date_layout)

        # Botón para seleccionar carpeta
        folder_button = QPushButton("Select Folder")
        folder_button.setFont(QFont("Arial", 12, QFont.Bold))
        folder_button.clicked.connect(self.select_folder)
        main_layout.addWidget(folder_button, alignment=Qt.AlignCenter)

        # Label para mostrar la carpeta seleccionada
        self.folder_label = QLabel("No folder selected")
        self.folder_label.setFont(QFont("Arial", 10))
        folder_button.setStyleSheet(self.button_style())
        self.folder_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.folder_label)


        # Botón "Start"
        start_button = QPushButton("Start")
        start_button.setFont(QFont("Arial", 12, QFont.Bold))
        start_button.setStyleSheet(self.button_style())
        start_button.clicked.connect(self.on_start_click)
        main_layout.addWidget(start_button, alignment=Qt.AlignCenter)
    
    def create_horizontal_pair(self, widget1, widget2, spacing=20):
        layout = QHBoxLayout()
        layout.addWidget(widget1)
        layout.addSpacing(spacing)
        layout.addWidget(widget2)
        layout.setSpacing(spacing)  # Usa el espaciado proporcionado por parámetro
        layout.setContentsMargins(5, 5, 10, 10)  # Añadir márgenes (ajusta según sea necesario)
        return layout


    def list_style(self):
        return """
            QListWidget {
                background-color: #162447;
                border: 2px solid #1f4068;
                color: #ffffff;
                padding: 5px;
                border-radius: 8px;
            }
        """
    
    def button_style(self):
        return """
            QPushButton {
                color: #ffffff;
                background-color: #1f4068;
                border: 2px solid #162447;
                border-radius: 10px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #162447;
            }
            QPushButton:pressed {
                background-color: #1b1b2f;
            }
        """

    def show_password(self):
    # Cambiar el modo de eco para mostrar la contraseña
        self.text_password.setEchoMode(QLineEdit.Normal)

    def hide_password(self):
    # Cambiar el modo de eco para ocultar la contraseña
        self.text_password.setEchoMode(QLineEdit.Password)

    def create_selector(self, label_text, font_label, font_input, options):
        """Crea un selector con una etiqueta y un QComboBox."""
        layout = QFormLayout()
        layout.setSpacing(0)  # Reduce el espacio entre el label y el selector
        layout.setContentsMargins(0, 0, 0, 0)  # Ajusta los márgenes a cero
        label = QLabel(f"{label_text}:")
        label.setFont(font_label)
        selector = QComboBox()
        selector.setFont(font_input)
        selector.addItems(options)
        layout.addWidget(label)
        layout.addWidget(selector)
        return {"layout": layout, "widget": selector}

    def create_text_input(self, label_text, font_label, font_input):
        """Crea un campo de entrada de texto con etiqueta"""
        layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFont(font_label)
        text_input = QLineEdit()  # Campo de texto
        text_input.setFont(font_input)
        text_input.setPlaceholderText("Enter your text here...")
        text_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #1f4068;
                border-radius: 8px;
                padding: 5px;
                background-color: #162447;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)
        layout.addWidget(label)
        layout.addWidget(text_input)
        return {"layout": layout, "widget": text_input}

    def create_date_input(self, label_text, font_label, font_input):
        """Crea un campo de fecha con una etiqueta y un QDateEdit."""
        layout = QFormLayout()
        layout.setSpacing(0)  # Reduce el espacio entre el label y el selector
        layout.setContentsMargins(0, 0, 0, 0)  # Ajusta los márgenes a cerolayout.setSpacing(2)  # Reduce el espacio entre el label y el selector
        layout.setContentsMargins(0, 0, 0, 0)  # Ajusta los márgenes a cero
        label = QLabel(f"{label_text}:")
        label.setFont(font_label)
        date_input = QDateEdit()
        date_input.setFont(font_input)
        date_input.setCalendarPopup(True)
        date_input.setDate(QDate.currentDate())
        layout.addWidget(label)
        layout.addWidget(date_input)
        return {"layout": layout, "widget": date_input}

    def select_folder(self):
        """Abre un diálogo para seleccionar una carpeta y muestra su contenido."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            # Convertir a ruta absoluta y normalizada usando pathlib
            self.folder_path = str(Path(folder).resolve())
            self.folder_label.setText(f"Selected Folder: {self.folder_path}")
            print(f"Folder selected: {self.folder_path}")
            

  
    
    def save_settings(self, data):
        with open(self.SETTINGS_FILE, "w") as f:
            json.dump(data, f)

    def load_settings(self):
        if os.path.exists(self.SETTINGS_FILE):
            with open(self.SETTINGS_FILE, "r") as f:
                return json.load(f)
        return {}

    def on_start_click(self):
        """Recolecta datos de los inputs y los pasa a Auto.py."""
        selected_email = self.text_email["widget"].text()
        selected_password = self.text_password.text()
        selected_caso = self.text_caso["widget"].text()
        selected_cliente = self.text_cliente["widget"].text()
        selected_option1 = self.selector1["widget"].currentText()
        selected_option2 = self.selector2["widget"].currentText()
        selected_text2 = self.text_input2["widget"].text()
        date1 = self.date1_input["widget"].date().toString("yyyy-MM-dd")
        date2 = self.date2_input["widget"].date().toString("yyyy-MM-dd")
        selected_folder = self.folder_path

        data_to_save = {
            "email": self.text_email["widget"].text(),
            "password": self.text_password.text(),
            "department": self.selector1["widget"].currentText(),
            "class": self.selector2["widget"].currentText(),
            #"request": self.text_input2["widget"].text(),
            "start_date": self.date1_input["widget"].date().toString("yyyy-MM-dd"),
            "end_date": self.date2_input["widget"].date().toString("yyyy-MM-dd"),
            "folder": self.folder_path
        }
        self.save_settings(data_to_save)

        


        print(f"Recolectado: {selected_option1}, {selected_option2}, {selected_text2}, {date1}, {date2}, {selected_caso},{selected_cliente},{selected_folder}")

        try:
            subprocess.run(
                ["python", 
                 "Auto.py",
                selected_option1,
                selected_option2,
                selected_text2,
                date1, 
                date2, 
                selected_caso,
                selected_cliente,
                selected_folder,
                selected_email, 
                selected_password],
                check=True,
            )
            print("Script ejecutado correctamente.")
        except Exception as e:
            print(f"Error al ejecutar el script: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernInterface()
    # Establecer un tamaño fijo para la ventana
    window.setFixedSize(800, 700)  # Ancho: 600px, Alto: 600px
    window.show()
    sys.exit(app.exec_())