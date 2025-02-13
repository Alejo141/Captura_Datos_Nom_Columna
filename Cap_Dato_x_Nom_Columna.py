import streamlit as st
import pandas as pd
from io import BytesIO

def procesar_archivo(file):
    # Obtener el nombre del archivo
    nombre_archivo = file.name
    
    # Cargar todas las hojas del archivo Excel
    xls = pd.ExcelFile(file)
    
    # Nombres de las hojas a buscar
    hojas_deseadas = ["Cartera", "Cartera Escuelas"]
    
    # Verificar qué hojas existen en el archivo
    hojas_presentes = [hoja for hoja in hojas_deseadas if hoja in xls.sheet_names]
    
    if not hojas_presentes:
        raise ValueError("El archivo no contiene las hojas 'Cartera' o 'Cartera Escuelas'.")

    # Leer y combinar los datos de las hojas deseadas
    df_list = []
    for hoja in hojas_presentes:
        df_temp = pd.read_excel(xls, sheet_name=hoja, dtype=str)
        
        # Normalizar nombres de columnas
        df_temp.columns = df_temp.columns.str.strip().str.lower()
        
        # Renombrar columnas duplicadas
        df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
        
        df_list.append(df_temp)
    
    df = pd.concat(df_list, ignore_index=True)

    # Definir columnas a extraer
    columnas_deseadas = ["identificación", "factura", "proyecto", "saldo factura", "mes de cobro"]

    # Filtrar solo columnas que existen en el archivo
    columnas_presentes = [col for col in columnas_deseadas if col in df.columns]
    
    if not columnas_presentes:
        raise ValueError("Ninguna de las columnas esperadas está en el archivo.")

    df_filtrado = df[columnas_presentes]

    # Reemplazar valores vacíos o nulos con "NA" (excepto en "factura")
    df_filtrado.fillna("NA", inplace=True)

    # Eliminar filas donde "factura" esté vacía
    df_filtrado = df_filtrado[df_filtrado["factura"].notna() & (df_filtrado["factura"] != "NA") & (df_filtrado["factura"].str.strip() != "")]

    # Eliminar guiones en la columna "Factura"
    if "factura" in df_filtrado.columns:
        df_filtrado["factura"] = df_filtrado["factura"].str.replace("-", "", regex=True)

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

    # Agregar una nueva columna al inicio con el nombre del archivo
    df_filtrado.insert(0, "nombre_archivo", nombre_archivo)

    return df_filtrado

def generar_csv(df):
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    return output

# Configuración de la página
st.set_page_config(page_title="Filtro de Columnas", page_icon="📂", layout="centered")
st.title("📂 Filtro de Columnas en Excel")

st.markdown("Sube un archivo Excel, extrae columnas específicas de las hojas 'Cartera' y 'Cartera Escuelas', divide 'Mes de Cobro' en mes y año, **excluye filas sin 'Factura'**, elimina guiones en 'Factura' y agrega el nombre del archivo.")

archivo = st.file_uploader("Cargar archivo Excel", type=["xlsx"])

if archivo is not None:
    try:
        df_filtrado = procesar_archivo(archivo)
        st.success("Archivo procesado correctamente.")
        st.dataframe(df_filtrado)  # Muestra la tabla con las columnas seleccionadas
        
        csv = generar_csv(df_filtrado)
        st.download_button(label="📥 Descargar CSV", data=csv, file_name="conso_cartera_xra_db.csv", mime="text/csv")
    except Exception as e:
        st.error(f"Error: {e}")
