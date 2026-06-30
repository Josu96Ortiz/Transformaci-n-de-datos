import mysql.connector
import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io

# =========================================================
# CONFIGURACIÓN DE LA PÁGINA
# =========================================================
st.set_page_config(page_title="Dashboard Big Data", layout="wide")

st.title("📊 Dashboard Estilo Power BI - Big Data")

# =========================================================
# 💾 PERSISTENCIA DE DATOS (Mantiene los cambios entre menús)
# =========================================================
if "df" not in st.session_state:
    # Primera vez que se carga la app, leemos el archivo original
    df_base = pd.read_csv("datos_practica.csv")
    st.session_state.df = df_base.copy()

# Usamos la variable 'df' apuntando al estado de la sesión para comodidad
df = st.session_state.df

# =========================================================
# MENÚ LATERAL (POWER BI STYLE)
# =========================================================
menu = st.sidebar.selectbox(
    "📌 Menú de Navegación",
    [
        "📂 Exploración de Datos",
        "🧹 Limpieza de Datos",
        "🔄 Transformación de Datos",
        "📊 Visualización",
        "📦 Dataset Final",
        "⬇️ Exportar Datos"
    ]
)

# =========================================================
# 📂 EXPLORACIÓN DE DATOS
# =========================================================
if menu == "📂 Exploración de Datos":
    st.header("Exploración de Datos")
    st.dataframe(df)

    st.subheader("Primeras filas")
    st.dataframe(df.head())

    st.subheader("Últimas filas")
    st.dataframe(df.tail())

    st.subheader("Info del DataFrame")
    buffer = io.StringIO()
    df.info(buf=buffer)
    st.text(buffer.getvalue())

    st.subheader("Estadísticas")
    st.dataframe(df.describe())

    st.subheader("Valores nulos")
    st.write(df.isnull().sum())

    st.subheader("Duplicados")
    st.write(df.duplicated().sum())

    st.subheader("Tipos de datos")
    st.dataframe(df.dtypes)

# =========================================================
# 🧹 LIMPIEZA DE DATOS (Requerimiento del Profesor)
# =========================================================
elif menu == "🧹 Limpieza de Datos":
    st.header("Limpieza de Datos")

    st.subheader("Reemplazar nulos con 'Desconocido'")
    # Se modifican los datos directamente en la sesión global
    st.session_state.df["Edad"] = st.session_state.df["Edad"].fillna("Desconocido")
    st.session_state.df["Salario"] = st.session_state.df["Salario"].fillna("Desconocido")
    st.session_state.df["Ciudad"] = st.session_state.df["Ciudad"].fillna("Desconocido")
    
    st.success("¡Valores nulos reemplazados por 'Desconocido' exitosamente!")
    st.dataframe(st.session_state.df)

    st.subheader("Eliminar duplicados")
    st.session_state.df = st.session_state.df.drop_duplicates()
    st.dataframe(st.session_state.df)

# =========================================================
# 🔄 TRANSFORMACIÓN DE DATOS
# =========================================================
elif menu == "🔄 Transformación de Datos":
    st.header("Transformación de Datos")

    # Variable simulada ventas
    np.random.seed(42)
    st.session_state.df["ventas"] = np.random.randint(100, 1000, len(st.session_state.df))

    # Normalización
    st.session_state.df["ventas_norm"] = (
        (st.session_state.df["ventas"] - st.session_state.df["ventas"].min()) /
        (st.session_state.df["ventas"].max() - st.session_state.df["ventas"].min())
    )

    # Z-score
    st.session_state.df["ventas_z"] = (
        (st.session_state.df["ventas"] - st.session_state.df["ventas"].mean()) / st.session_state.df["ventas"].std()
    )

    # Logarítmica
    st.session_state.df["ventas_log"] = np.log1p(st.session_state.df["ventas"])

    # Binning Ventas
    st.session_state.df["categoria"] = pd.cut(
        st.session_state.df["ventas"],
        bins=[0, 300, 600, 1000],
        labels=["Bajo", "Medio", "Alto"]
    )

    # Binning por EDAD
    # 'errors=coerce' convierte el texto 'Desconocido' en NaN temporalmente 
    # para que pd.cut no falle con textos, manteniendo la coherencia.
    edad_numerica = pd.to_numeric(st.session_state.df["Edad"], errors='coerce')
    
    st.session_state.df["grupo_edad"] = pd.cut(
        edad_numerica,
        bins=[0, 6, 12, 20, 25, 60, 120],
        labels=["Infancia", "Niñez", "Adolescencia", "Juventud", "Adultez", "Ancianidad"],
        right=True
    )

    st.success("¡Transformaciones aplicadas y guardadas en el sistema!")
    st.dataframe(st.session_state.df)

# =========================================================
# 📊 VISUALIZACIÓN
# =========================================================
elif menu == "📊 Visualización":
    st.header("Visualización de Datos")

    # Validación por seguridad si el usuario salta directo a esta pestaña
    if "ventas" in df.columns:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Distribución de Ventas")
            fig, ax = plt.subplots()
            ax.hist(df["ventas"], bins=10, color="skyblue", ec="black")
            st.pyplot(fig)

        with col2:
            st.subheader("Outliers de Ventas")
            fig, ax = plt.subplots()
            sns.boxplot(x=df["ventas"], ax=ax, color="lightgreen")
            st.pyplot(fig)

        st.subheader("Relación de datos (Muestra)")
        st.dataframe(df[["ventas"]])
    else:
        st.warning("⚠️ Para ver las gráficas de ventas, primero debes pasar por la pestaña '🔄 Transformación de Datos'.")

# =========================================================
# 📦 DATASET FINAL
# =========================================================
elif menu == "📦 Dataset Final":
    st.header("Dataset Final Procesado")
    
    # Muestra el estado actual del DataFrame con todos los cambios acumulados
    st.dataframe(df)

    st.subheader("Estadísticas finales")
    st.dataframe(df.describe())

# =========================================================
# ⬇️ EXPORTAR DATOS
# =========================================================
elif menu == "⬇️ Exportar Datos":
    st.header("Descarga de Datos Limpios")

    # Muestra el avance antes de descargar
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Descargar CSV",
        data=csv,
        file_name="datos_transformados.csv",
        mime="text/csv"
    )