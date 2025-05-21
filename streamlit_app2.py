import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Diccionarios
column_names = {
    "Total": "Ingresos Totales",
    "Date": "Tiempo",
    "Member": "Miembro",
    "gross income": "Ingreso Bruto",
    "cogs": "Costo Bienes Vendidos",
    "Payment": "Método de Pago",
    "Rating": "Calificaciones",
    "Product line": "Línea de Producto"
}

product_translation = {
    "Electronic accessories": "Accesorios Electrónicos",
    "Fashion accessories": "Accesorios de Moda",
    "Food and beverages": "Alimentos y Bebidas",
    "Health and beauty": "Salud y Belleza",
    "Home and lifestyle": "Hogar y Estilo de Vida",
    "Sports and travel": "Deportes y Viajes"
}

payment_translation = {
    "Cash": "Efectivo",
    "Credit card": "Tarjeta de Crédito",
    "Ewallet": "Billetera Electrónica"
}

customer_type_translation = {
    "Member": "Miembro",
    "Normal": "Normal"
}

# Carga de datos
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# Aplicar traducción
df["Product line"] = df["Product line"].replace(product_translation)
df["Payment"] = df["Payment"].replace(payment_translation)
df["Customer type"] = df["Customer type"].replace(customer_type_translation)

# Definir rango de fechas disponibles
min_date = df["Date"].min()
max_date = df["Date"].max()

# Barra lateral de filtros
st.sidebar.header("Filtros")
branches = ["Todas"] + sorted(df["Branch"].unique().tolist())
selected_branch = st.sidebar.selectbox("Seleccionar sucursal", branches)

selected_product_lines = st.sidebar.multiselect(
    "Seleccionar líneas de producto",
    df["Product line"].unique(),
    default=df["Product line"].unique()
)
start_date, end_date = st.sidebar.date_input(
    "Seleccionar rango de fechas",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Título del Dashboard
st.title(f"📊 Dashboard de Ventas - {'Todas las Sucursales' if selected_branch == 'Todas' else f'Sucursal {selected_branch}'}")

# Filtrar
if selected_branch == "Todas":
    df_filtered = df[
        (df["Product line"].isin(selected_product_lines)) &
        (df["Date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date)))
    ]
else:
    df_filtered = df[
        (df["Branch"] == selected_branch) &
        (df["Product line"].isin(selected_product_lines)) &
        (df["Date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date)))
    ]

if df_filtered.empty:
    st.warning(f" No hay datos seleccionados para la sucursal {selected_branch}. Por favor, ajuste los filtros para continuar.")
    st.stop()

# ------- MÉTRICAS PRINCIPALES ------
st.header("Metricas Principales")
total_sales = df_filtered["Total"].sum()
total_products = df_filtered["Quantity"].sum()
total_gasto = df_filtered["cogs"].sum()
total_margen = df_filtered["gross income"].sum()
total_tax = df_filtered["Tax 5%"].sum()
total_rating = df_filtered["Rating"]

avg_quantity_period = df_filtered["Quantity"].mean()
avg_tax_period = df_filtered["Tax 5%"].mean()
avg_cogs_period = df_filtered["cogs"].mean()
avg_gross_income_period = df_filtered["gross income"].mean()
avg_gross_margin_percentage = df_filtered["gross margin percentage"].mean()
avg_rating_period = df_filtered["Rating"].mean()
avg_sales_period = df_filtered["Total"].mean()

col1, col2, col3 = st.columns(3)

with col1:
  st.subheader("📊 Valores totales en el Período Seleccionado")
  st.metric("💰 Total Productos", f"{total_products:,.2f}")
  st.metric("📦 Total Ventas", f"${total_sales:,.2f}")
  st.metric("💸 Total Costo Bienes Vendidos", f"${total_gasto:,.2f}")
  st.metric("💸 Total Impuesto Pagado", f"${total_tax:,.2f}")

with col2:
  st.subheader("📊 Promedio Diario en el Período Seleccionado")
  st.metric("📦 Promedio de Productos Vendidos", f"{avg_quantity_period:,.2f}")
  st.metric("💰 Promedio Ingreso por Ventas", f"${avg_sales_period:,.2f}")
  st.metric("💸 Promedio Costo Bienes Vendidos", f"${avg_cogs_period:,.2f}")
  st.metric("💸 Promedio Impuesto 5%", f"${avg_tax_period:,.2f}")  
  st.metric("💰 Promedio Margen Bruto", f"${avg_gross_income_period:,.2f}")

with col3:
  st.subheader("📊 Promedios Performance")
  st.metric("⭐ Promedio Calificaciones", f"{avg_rating_period:.2f}/10")
  st.metric("💰 Total Margen Bruto Periodo", f"${total_margen:,.2f}")

# --- GRÁFICOS FILTRADOS -----------
st.header("Gráficos Filtrados")
col1, col2 = st.columns(2)

# Ventas por fecha
with col1:
    st.subheader("📈 Evolución de las Ventas Totales por Fecha")
    ventas_diarias = df_filtered.groupby("Date")["Total"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(ventas_diarias["Date"], ventas_diarias["Total"], marker="o", color="teal")
    ax.set_title("Evolución de las Ventas Totales por Fecha")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Ventas Totales")
    ax.grid(True)
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

# Ingresos y Cantidad por Línea de Producto
with col2:
    st.subheader(f"📊 {column_names['Total']} y Cantidad por Línea de Producto - Sucursal {selected_branch}")
    # Agrupar datos por PL y sumar total y cantidad
    df_grouped = df_filtered.groupby("Product line").agg({"Total": "sum", "Quantity": "sum"}).reset_index()
    fig, ax1 = plt.subplots(figsize=(6, 3))
    # barra para ingresos totales
    sns.barplot(x="Product line", y="Total", data=df_grouped, ax=ax1, palette="pastel")
    ax1.set_xlabel("Línea de Producto")
    ax1.set_ylabel(column_names["Total"], color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")
    # agregar cantidad en eje 2
    ax2 = ax1.twinx()
    sns.lineplot(x="Product line", y="Quantity", data=df_grouped, ax=ax2, marker="o", color="green")
    ax2.set_ylabel("Cantidad", color="green")
    ax2.tick_params(axis="y", labelcolor="green")
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha="right")
    ax1.set_title(f"Ingresos y Cantidad por Línea de Producto - {selected_branch}")
    st.pyplot(fig)

# columna segunda
col3, col4 = st.columns(2)

# rating de clientes
with col3:
    st.subheader(f"⭐ {column_names['Rating']} - Sucursal {selected_branch}")
    fig, ax = plt.subplots(figsize=(6, 3))
    sns.histplot(df_filtered["Rating"], bins=10, kde=True, ax=ax, color="orange")
    ax.set_xlabel(column_names["Rating"])
    ax.set_ylabel("Frecuencia")
    st.pyplot(fig)

# metodo de pago
with col4:
    st.subheader(f"🏦 {column_names['Payment']} Más Utilizados - Sucursal {selected_branch}")
    df_payment = df_filtered.groupby("Payment", as_index=False).agg(
        Monto_Total=("Total", "sum"),
        Frecuencia=("Total", "count")
    )
    fig, ax1 = plt.subplots(figsize=(6, 3))

    sns.barplot(x="Payment", y="Frecuencia", data=df_payment, ax=ax1, color="lightblue")
    ax1.set_ylabel("Frecuencia", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")

    ax2 = ax1.twinx()
    sns.lineplot(x="Payment", y="Monto_Total", data=df_payment, ax=ax2, marker="o", color="red")
    ax2.set_ylabel("Ingreso ($)", color="red")
    ax2.tick_params(axis="y", labelcolor="red")
    ax1.set_title(f"Frecuencia e Ingreso por {column_names['Payment']} - {selected_branch}")
    ax1.set_xticklabels(df_payment["Payment"], rotation=45)
    st.pyplot(fig)

# columna tercera
col5, col6 = st.columns(2)

# relacion COGS con ingreso bruto
with col5:
    st.subheader(f"🔗 Relación entre {column_names['cogs']} y {column_names['gross income']} - Sucursal {selected_branch}")
    fig, ax = plt.subplots(figsize=(6, 3))
    sns.scatterplot(x=df_filtered["cogs"], y=df_filtered["gross income"], ax=ax, color="red", alpha=0.6)
    ax.set_xlabel(column_names["cogs"])
    ax.set_ylabel(column_names["gross income"])
    st.pyplot(fig)

with col6:
    # Distribución del gasto total por tipo de cliente
    st.subheader("🎻 Distribución del Gasto Total por Tipo de Cliente")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.violinplot(data=df_filtered, x='Customer type', y='Total', palette='Set2', ax=ax)

    # Calcular y agregar etiquetas de media y mediana
    for i, customer_type in enumerate(df_filtered['Customer type'].unique()):
        subset = df_filtered[df_filtered['Customer type'] == customer_type]['Total']
        mean = subset.mean()
        median = subset.median()

        ax.text(i, mean, f'Media:\n{mean:.2f}', color='blue', fontsize=10, ha='center', va='bottom')
        ax.text(i, median, f'Mediana:\n{median:.2f}', color='black', fontsize=10, ha='center', va='top')

    ax.set_title('Distribución del Gasto Total (Total) por Tipo de Cliente con Media y Mediana')
    ax.set_xlabel('Tipo de Cliente')
    ax.set_ylabel('Gasto Total (Total)')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    st.pyplot(fig)
