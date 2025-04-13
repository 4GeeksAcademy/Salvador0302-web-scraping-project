import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

url = "https://es.wikipedia.org/wiki/Anexo:Pa%C3%ADses_y_territorios_dependientes_por_poblaci%C3%B3n"
response = requests.get(url)
html_content = response.text

response.status_code

tables = pd.read_html(html_content)
print(f"Número de tablas encontradas: {len(tables)}")

df_raw = tables[0]
df_raw.head()

print("Columnas originales:")
print(df_raw.columns)

df_raw.columns = [
    "Nro", "País", "Población", "Porcentaje", "Crecimiento anual (%)",
    "Crecimiento absoluto", "Crecimiento medio (%)",
    "Años duplicación", "Fuente del dato",
    "Fecha del dato", "Tipo", "Enlace"
]

df = df_raw[["País", "Población", "Porcentaje", "Fecha del dato"]].dropna()

df["Población"] = df["Población"].astype(str)
df["Porcentaje"] = df["Porcentaje"].astype(str)

df["Población"] = df["Población"].str.replace(r"[^\d]", "", regex=True)
df["Porcentaje"] = (
    df["Porcentaje"]
    .str.replace(",", ".", regex=False)
    .str.replace(r"[^\d\.]", "", regex=True)
)

df.replace({"": pd.NA}, inplace=True)
df.dropna(subset=["Población", "Porcentaje"], inplace=True)

df["Población"] = df["Población"].astype(int)
df["Porcentaje"] = df["Porcentaje"].astype(float)

df.head()

conn = sqlite3.connect("poblacion_mundial.db")

df.to_sql("paises", conn, if_exists="replace", index=False)

conn.commit()
conn.close()

print("Datos almacenados exitosamente en la base de datos.")

df_filtrado = df[~df["País"].str.contains("Mundo|Total", case=False, na=False)]
df_top10 = df_filtrado.sort_values("Población", ascending=False).head(10)

plt.figure(figsize=(10, 6))
plt.bar(df_top10["País"], df_top10["Población"])
plt.xticks(rotation=45, ha="right")
plt.title("Top 10 países más poblados del mundo")
plt.xlabel("País")
plt.ylabel("Población (habitantes)")
plt.tight_layout()
plt.show()

df_top5 = df.sort_values("Población", ascending=False).head(5)

plt.figure(figsize=(8, 8))
plt.pie(df_top5["Población"], labels=df_top5["País"], autopct="%1.1f%%", startangle=140)
plt.title("Distribución porcentual de población (Top 5 países)")
plt.show()

plt.figure(figsize=(10, 6))
plt.scatter(df_filtrado["Población"], df_filtrado["Porcentaje"])
plt.title("Relación entre población total y su porcentaje del mundo")
plt.xlabel("Población (habitantes)")
plt.ylabel("Porcentaje del total mundial (%)")
plt.grid(True)
plt.show()