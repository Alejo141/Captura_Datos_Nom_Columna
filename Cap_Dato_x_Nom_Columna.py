import streamlit as st
import pandas as pd
from io import BytesIO

def procesar_archivo(file):
    df = pd.read_excel(file)
    
    # Normalizar nombres de columnas (eliminar espacios extra, convertir a minúsculas)
    df.columns = df.columns.str.strip().str.lower()
    
    # Definir columnas que queremos extraer (también normalizadas)
    columnas_deseadas = ["Identificación", "Factura", "PROYECTO", "Saldo Factura", "Mes de Cobro"]  # Modifica según necesidad
    
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

st.markdown("Sube un archivo Excel, extrae columnas específicas y descarga el CSV resultante.")

archivo = st.file_uploader("Cargar archivo Excel", type=["xlsx"])

if archivo is not None:
    df_filtrado = procesar_archivo(archivo)
    st.success("Archivo procesado correctamente.")
    st.dataframe(df_filtrado)  # Muestra la tabla con las columnas seleccionadas
    
    csv = generar_csv(df_filtrado)
    st.download_button(label="📥 Descargar CSV", data=csv, file_name="archivo_filtrado.csv", mime="text/csv")
