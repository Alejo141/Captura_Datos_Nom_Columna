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
    columnas_deseadas = ["identificación", "factura", "proyecto", "saldo factura", "mes de cobro"]

    # Filtrar solo columnas que existen en el archivo
    columnas_presentes = [col for col in columnas_deseadas if col in df.columns]
    
    if not columnas_presentes:
        raise ValueError("Ninguna de las columnas esperadas está en el archivo.")

    df_filtrado = df[columnas_presentes]
    return df_filtrado

def generar_csv(df):
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    return output

# Configuración de la página
st.set_page_config(page_title="Filtro de Columnas", page_icon="📂", layout="centered")
st.title("📂 Filtro de Columnas en Excel")

st.markdown("Sube un archivo Excel, extrae columnas específicas de las hojas 'Cartera' y 'Cartera Escuelas' y descarga el CSV resultante.")

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
