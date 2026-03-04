import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title="LogisticsGraph Pro", layout="wide")

st.title("🚢 LogisticsGraph Pro - Risk Analysis Simulator")

# =====================================================
# CREACIÓN DEL GRAFO (VERSIÓN PDF EXACTA)
# =====================================================

G = nx.DiGraph()

# -----------------
# NODOS
# -----------------
G.add_node("Fabrica_Shanghai", tipo="Fabrica")

G.add_node("Puerto_Rotterdam", tipo="Puerto")
G.add_node("Puerto_Valencia", tipo="Puerto")

G.add_node("Almacen_Zaragoza", tipo="Almacen")
G.add_node("Almacen_Sevilla", tipo="Almacen")

G.add_node("Tienda_Madrid", tipo="Tienda")
G.add_node("Tienda_Huelva", tipo="Tienda")

# -----------------
# CONEXIONES INICIALES
# IMPORTANTE:
# Rotterdam NO conecta con Zaragoza al inicio
# -----------------

G.add_edge("Fabrica_Shanghai", "Puerto_Rotterdam", tiempo_dias=15)
G.add_edge("Fabrica_Shanghai", "Puerto_Valencia", tiempo_dias=12)

# SOLO Valencia conecta con Zaragoza
G.add_edge("Puerto_Valencia", "Almacen_Zaragoza", tiempo_dias=3)

G.add_edge("Puerto_Valencia", "Almacen_Sevilla", tiempo_dias=2)

G.add_edge("Almacen_Zaragoza", "Tienda_Madrid", tiempo_dias=2)
G.add_edge("Almacen_Sevilla", "Tienda_Huelva", tiempo_dias=1)

# =====================================================
# VISUALIZACIÓN
# =====================================================

st.subheader("📊 Visualización del Grafo")

color_map = []

for node in G.nodes(data=True):
    if node[1]["tipo"] == "Fabrica":
        color_map.append("red")
    elif node[1]["tipo"] == "Puerto":
        color_map.append("blue")
    elif node[1]["tipo"] == "Almacen":
        color_map.append("orange")
    else:
        color_map.append("green")

fig, ax = plt.subplots()
pos = nx.spring_layout(G, seed=42)

nx.draw(G, pos,
        with_labels=True,
        node_color=color_map,
        node_size=2500,
        font_size=8,
        ax=ax)

labels = nx.get_edge_attributes(G, 'tiempo_dias')
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

st.pyplot(fig)

# =====================================================
# STRESS TEST
# =====================================================

st.sidebar.header("⚠️ Stress Test")

nodo_bloqueado = st.sidebar.selectbox(
    "Selecciona un nodo para bloquear",
    list(G.nodes)
)

if st.sidebar.button("Ejecutar Test"):

    G_temp = G.copy()
    G_temp.remove_node(nodo_bloqueado)

    tiendas = [n for n, d in G.nodes(data=True) if d["tipo"] == "Tienda"]
    almacenes = [n for n, d in G.nodes(data=True) if d["tipo"] == "Almacen"]

    ciudades_sin_suministro = []

    # Control tiendas
    for tienda in tiendas:
        if tienda in G_temp.nodes:
            if not nx.has_path(G_temp, "Fabrica_Shanghai", tienda):
                ciudades_sin_suministro.append(tienda)

    # Control almacenes
    for almacen in almacenes:
        if almacen in G_temp.nodes:
            if not nx.has_path(G_temp, "Fabrica_Shanghai", almacen):
                ciudades_sin_suministro.append(almacen)

    if ciudades_sin_suministro:
        st.error("🚨 Ciudades sin suministro:")
        for ciudad in ciudades_sin_suministro:
            st.write(f"- {ciudad}")
    else:
        st.success("✅ La red sigue operativa.")

# =====================================================
# EMERGENCY ROUTE (SEGÚN PDF)
# =====================================================

st.sidebar.header("🚑 Solución de Emergencia")

if st.sidebar.button("Añadir Rotterdam -> Zaragoza (6 días)"):
    G.add_edge("Puerto_Rotterdam", "Almacen_Zaragoza", tiempo_dias=6)
    st.sidebar.success("Ruta de emergencia añadida.")

# =====================================================
# OPTIMIZACIÓN
# =====================================================

st.subheader("🚀 Optimización de Rutas")

tiendas = [n for n, d in G.nodes(data=True) if d["tipo"] == "Tienda"]

tienda_seleccionada = st.selectbox(
    "Selecciona una tienda",
    tiendas
)

if st.button("Calcular ruta más rápida"):

    ruta = nx.shortest_path(
        G,
        source="Fabrica_Shanghai",
        target=tienda_seleccionada,
        weight="tiempo_dias"
    )

    tiempo_total = nx.shortest_path_length(
        G,
        source="Fabrica_Shanghai",
        target=tienda_seleccionada,
        weight="tiempo_dias"
    )

    st.write("Ruta óptima:")
    st.write(" -> ".join(ruta))
    st.write(f"Tiempo total: {tiempo_total} días")
