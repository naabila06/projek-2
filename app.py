
import streamlit as st
import networkx as nx
import plotly.graph_objects as go

st.set_page_config(
    page_title="Community Connection Lab",
    page_icon="🌐",
    layout="wide"
)

st.title("Community Connection Lab")
st.write(
    "Ubah hubungan pertemanan dan amati bagaimana "
    "kelompok jaringan bergabung atau terpisah."
)

# Memuat dataset sosial asli
@st.cache_resource
def load_original_network():
    return nx.karate_club_graph()

# Memilih 20 anggota berdasarkan derajat tertinggi.
# Jika derajat sama, nomor anggota terkecil diprioritaskan.
def select_members(G, jumlah=20):
    urutan = sorted(
        G.nodes(),
        key=lambda n: (-G.degree(n), n)
    )
    return urutan[:jumlah]

if "G" not in st.session_state:
    G_asli = load_original_network()
    anggota_pilihan = select_members(G_asli, 20)
    st.session_state.G = G_asli.subgraph(
        anggota_pilihan
    ).copy()

if "G_awal" not in st.session_state:
    st.session_state.G_awal = st.session_state.G.copy()

G = st.session_state.G

# Statistik jaringan
st.subheader("Kondisi Jaringan")

c1, c2, c3 = st.columns(3)
c1.metric("Jumlah anggota", G.number_of_nodes())
c2.metric("Jumlah hubungan", G.number_of_edges())
c3.metric(
    "Kelompok terhubung",
    nx.number_connected_components(G)
)

# Kontrol hubungan
st.subheader("Ubah Hubungan Pertemanan")

anggota = sorted(G.nodes())
kol1, kol2 = st.columns(2)

with kol1:
    a = st.selectbox("Anggota A", anggota)

with kol2:
    b = st.selectbox(
        "Anggota B",
        anggota,
        index=1 if len(anggota) > 1 else 0
    )

kol3, kol4, kol5 = st.columns(3)

with kol3:
    if st.button("Tambah hubungan"):
        if a == b:
            st.warning("Pilih dua anggota berbeda.")
        elif G.has_edge(a, b):
            st.warning("Hubungan tersebut sudah ada.")
        else:
            G.add_edge(a, b)
            st.session_state.G = G
            st.rerun()

with kol4:
    if st.button("Hapus hubungan"):
        if G.has_edge(a, b):
            G.remove_edge(a, b)
            st.session_state.G = G
            st.rerun()
        else:
            st.warning("Kedua anggota belum terhubung.")

with kol5:
    if st.button("Reset jaringan"):
        st.session_state.G = (
            st.session_state.G_awal.copy()
        )
        st.rerun()

# Visualisasi jaringan
st.subheader("Visualisasi Jaringan")

pos = nx.spring_layout(G, seed=7)
edge_x, edge_y = [], []

for u, v in G.edges():
    edge_x.extend([pos[u][0], pos[v][0], None])
    edge_y.extend([pos[u][1], pos[v][1], None])

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=edge_x,
    y=edge_y,
    mode="lines",
    line=dict(width=1.5, color="#A0AEC0"),
    hoverinfo="none"
))

derajat = dict(G.degree())

fig.add_trace(go.Scatter(
    x=[pos[n][0] for n in G.nodes()],
    y=[pos[n][1] for n in G.nodes()],
    mode="markers+text",
    text=[str(n) for n in G.nodes()],
    textposition="top center",
    marker=dict(
        size=[14 + 2 * derajat[n] for n in G.nodes()],
        color=[derajat[n] for n in G.nodes()],
        colorscale="Viridis",
        showscale=True,
        colorbar=dict(title="Jumlah hubungan"),
        line=dict(width=1, color="white")
    ),
    hovertemplate=(
        "Anggota %{text}<br>"
        "Jumlah hubungan: %{marker.color}<extra></extra>"
    )
))

fig.update_layout(
    height=650,
    showlegend=False,
    margin=dict(l=10, r=10, t=20, b=10),
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    plot_bgcolor="white"
)

st.plotly_chart(fig, use_container_width=True)

# Analisis perubahan
st.subheader("Analisis Kelompok")

komponen = list(nx.connected_components(G))

if len(komponen) == 1:
    st.success(
        "Semua anggota masih berada dalam satu kelompok terhubung."
    )
else:
    st.warning(
        f"Jaringan terpisah menjadi {len(komponen)} kelompok."
    )

for i, kelompok in enumerate(
    sorted(komponen, key=len, reverse=True), start=1
):
    st.write(
        f"Kelompok {i}: {len(kelompok)} anggota — "
        f"{', '.join(map(str, sorted(kelompok)))}"
    )

st.caption(
    "Sumber: Zachary's Karate Club Network melalui NetworkX. "
    "Subgraf dibatasi menjadi 20 anggota berdasarkan derajat "
    "dalam jaringan asli. Hubungan antarangggota tetap mengikuti "
    "data asli."
)
