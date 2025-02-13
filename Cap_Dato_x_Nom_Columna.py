import streamlit as st
import pandas as pd
from io import BytesIO

def procesar_archivo(file):
    df = pd.read_excel(file)
    columnas_deseadas = ["Nombre", "Edad", "Ciudad"]  # Modifica según necesidad
    df_filtrado = df[columnas_deseadas]
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
