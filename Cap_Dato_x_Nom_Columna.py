import streamlit as st
import pandas as pd
from io import BytesIO

def procesar_archivo(file):
    # Cargar todas las hojas del archivo Excel
    xls = pd.ExcelFile(file)
    
    # Nombres de las hojas a buscar
    hojas_deseadas = ["Cartera", "Cartera Escuelas"]
    
    # Verificar qué hojas existen en el archivo
    hojas_presentes = [hoja for hoja in hojas_deseadas if hoja in xls.sheet_names]
    
    if not hojas_presentes:
        raise ValueError("El archivo no contiene las hojas 'Cartera' o 'Cartera Escuelas'.")

    # Leer y combinar los datos de las hojas deseadas
    df_list = [pd.read_excel(xls, sheet_name=hoja) for hoja in hojas_presentes]
    df = pd.concat(df_list, ignore_index=True)

    # Normalizar nombres de columnas (eliminar espacios extra, convertir a minúsculas)
    df.columns = df.columns.str.strip().str.lower()

    # Definir columnas a extraer (ajustar nombres en minúsculas)
    columnas_deseadas = ["identificación", "factura", "saldo factura", "mes de cobro"]

    # Filtrar solo columnas que existen en el archivo
    columnas_presentes = [col for col in columnas_deseadas if col in df.columns]
    
    if not columnas_presentes:
        raise ValueError("Ninguna de las columnas esperadas está en el archivo.")

    df_filtrado = df[columnas_presentes]

    # Convertir "Mes de Cobro" en mes (numérico) y año
    if "mes de cobro" in df_filtrado.columns:
        df_filtrado["mes de cobro"] = df_filtrado["mes de cobro"].astype(str)  # Asegurar que es texto
        df_filtrado[["mes", "año"]] = df_filtrado["mes de cobro"].str.split(" ", expand=True)
        
        # Diccionario de meses para conversión a número
        meses_dict = {
            "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
            "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
        }
        
        # Convertir nombre del mes a número
        df_filtrado["mes"] = df_filtrado["mes"].str.lower().map(meses_dict)
        
        # Convertir año a número
        df_filtrado["año"] = pd.to_numeric(df_filtrado["año"], errors='coerce')

        # Eliminar columna original "Mes de Cobro"
        df_filtrado.drop(columns=["mes de cobro"], inplace=True)

    return df_filtrado

def generar_csv(df):
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    return output

# Configuración de la página
st.set_page_config(page_title="Filtro de Columnas", page_icon="📂", layout="centered")
st.title("📂 Filtro de Columnas en Excel")

st.markdown("Sube un archivo Excel, extrae columnas específicas de las hojas 'Cartera' y 'Cartera Escuelas', divide 'Mes de Cobro' en mes y año, y descarga el CSV resultante.")

archivo = st.file_uploader("Cargar archivo Excel", type=["xlsx"])

if archivo is not None:
    try:
        df_filtrado = procesar_archivo(archivo)
        st.success("Archivo procesado correctamente.")
        st.dataframe(df_filtrado)  # Muestra la tabla con las columnas seleccionadas
        
        csv = generar_csv(df_filtrado)
        st.download_button(label="📥 Descargar CSV", data=csv, file_name="archivo_filtrado.csv", mime="text/csv")
    except Exception as e:
        st.error(f"Error: {e}")
