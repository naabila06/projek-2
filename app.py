
import streamlit as st
import networkx as nx
import plotly.graph_objects as go

st.set_page_config(
    page_title="Community Connection Lab",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 Community Connection Lab")
st.write(
    "Ubah hubungan pertemanan dan amati bagaimana "
    "perubahan hubungan memengaruhi kelompok sosial."
)

# ==================================================
# 1. DATASET ASLI DAN PEMILIHAN 20 ANGGOTA
# ==================================================

@st.cache_resource
def load_original_network():
    return nx.karate_club_graph()

def select_members(G, jumlah=20):
    # Aturan: derajat tertinggi, lalu nomor terkecil
    urutan = sorted(
        G.nodes(),
        key=lambda n: (-G.degree(n), n)
    )
    return urutan[:jumlah]

if "G_awal" not in st.session_state:
    G_asli = load_original_network()
    pilihan = select_members(G_asli, 20)
    st.session_state.G_awal = (
        G_asli.subgraph(pilihan).copy()
    )

if "G" not in st.session_state:
    st.session_state.G = st.session_state.G_awal.copy()

G = st.session_state.G

# ==================================================
# 2. FUNGSI STATISTIK DAN VISUALISASI
# ==================================================

def jumlah_kelompok(graph):
    return nx.number_connected_components(graph)

def buat_graf(graph, pos, edge_baru=None, edge_hapus=None):
    edge_x, edge_y = [], []
    warna_garis, tebal_garis = [], []

    for u, v in graph.edges():
        edge_x.extend([pos[u][0], pos[v][0], None])
        edge_y.extend([pos[u][1], pos[v][1], None])

        if edge_baru and set((u, v)) == set(edge_baru):
            warna_garis.append("#16A34A")
            tebal_garis.append(4)
        else:
            warna_garis.append("#94A3B8")
            tebal_garis.append(1.5)

    # Tambahkan garis penghapusan sebagai garis merah putus-putus
    if edge_hapus:
        u, v = edge_hapus
        edge_x.extend([pos[u][0], pos[v][0], None])
        edge_y.extend([pos[u][1], pos[v][1], None])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(width=1.5, color="#94A3B8"),
        hoverinfo="none",
        name="Hubungan"
    ))

    # Garis baru ditampilkan hijau
    if edge_baru:
        u, v = edge_baru
        fig.add_trace(go.Scatter(
            x=[pos[u][0], pos[v][0]],
            y=[pos[u][1], pos[v][1]],
            mode="lines",
            line=dict(width=4, color="#16A34A"),
            hoverinfo="none",
            name="Hubungan baru"
        ))

    # Garis yang dihapus ditandai merah
    if edge_hapus:
        u, v = edge_hapus
        fig.add_trace(go.Scatter(
            x=[pos[u][0], pos[v][0]],
            y=[pos[u][1], pos[v][1]],
            mode="lines",
            line=dict(width=3, color="#DC2626", dash="dash"),
            hoverinfo="none",
            name="Hubungan dihapus"
        ))

    derajat = dict(graph.degree())
    komponen = list(nx.connected_components(graph))

    warna_node = []
    for n in graph.nodes():
        warna_node.append(
            next(i for i, k in enumerate(komponen) if n in k)
        )

    fig.add_trace(go.Scatter(
        x=[pos[n][0] for n in graph.nodes()],
        y=[pos[n][1] for n in graph.nodes()],
        mode="markers+text",
        text=[str(n + 1) for n in graph.nodes()],
        textposition="top center",
        marker=dict(
            size=[14 + 2 * derajat[n] for n in graph.nodes()],
            color=warna_node,
            colorscale="Viridis",
            showscale=False,
            line=dict(width=1, color="white")
        ),
        customdata=[derajat[n] for n in graph.nodes()],
        hovertemplate=(
            "Anggota %{text}<br>"
            "Jumlah hubungan: %{customdata}<extra></extra>"
        ),
        name="Anggota"
    ))

    fig.update_layout(
        height=600,
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="white"
    )

    return fig

# Posisi anggota dibuat tetap agar perubahan garis mudah diamati
pos = nx.spring_layout(st.session_state.G_awal, seed=7)

# ==================================================
# 3. RINGKASAN JARINGAN
# ==================================================

st.subheader("Kondisi Jaringan")

c1, c2, c3 = st.columns(3)
c1.metric("Anggota", G.number_of_nodes())
c2.metric("Hubungan", G.number_of_edges())
c3.metric("Kelompok terhubung", jumlah_kelompok(G))

st.caption(
    "Angka anggota pada grafik dimulai dari 1, sedangkan "
    "label internal dataset NetworkX dimulai dari 0."
)

# ==================================================
# 4. ANIMASI PERUBAHAN HUBUNGAN
# ==================================================

st.subheader("Simulasi Perubahan Jaringan")

st.write(
    "Animasi memperlihatkan satu hubungan yang dihapus, "
    "kemudian ditambahkan kembali. Efeknya bergantung pada "
    "struktur jaringan yang dipilih."
)

# Cari sisi jembatan: sisi yang jika dihapus memisahkan jaringan
jembatan = list(nx.bridges(G))

if jembatan:
    edge_demo = jembatan[0]
    G_putus = G.copy()
    G_putus.remove_edge(*edge_demo)

    kelompok_awal = jumlah_kelompok(G)
    kelompok_putus = jumlah_kelompok(G_putus)

    if "langkah_animasi" not in st.session_state:
        st.session_state.langkah_animasi = 0

    langkah = st.session_state.langkah_animasi

    if langkah == 0:
        st.info(
            "Tahap 1: jaringan awal. Semua hubungan yang tercatat "
            "ditampilkan sebagai garis."
        )
        fig_animasi = buat_graf(G, pos)

    elif langkah == 1:
        st.warning(
            f"Tahap 2: hubungan anggota {edge_demo[0] + 1} dan "
            f"{edge_demo[1] + 1} dihapus. Jumlah kelompok berubah "
            f"dari {kelompok_awal} menjadi {kelompok_putus}."
        )
        fig_animasi = buat_graf(
            G_putus, pos, edge_hapus=edge_demo
        )

    else:
        st.success(
            f"Tahap 3: hubungan anggota {edge_demo[0] + 1} dan "
            f"{edge_demo[1] + 1} ditambahkan kembali. Jaringan "
            f"kembali memiliki {kelompok_awal} kelompok."
        )
        fig_animasi = buat_graf(
            G, pos, edge_baru=edge_demo
        )

    st.plotly_chart(fig_animasi, use_container_width=True)

    ca, cb = st.columns(2)

    with ca:
        if st.button("▶ Langkah berikutnya"):
            st.session_state.langkah_animasi = (langkah + 1) % 3
            st.rerun()

    with cb:
        if st.button("🔄 Ulangi simulasi"):
            st.session_state.langkah_animasi = 0
            st.rerun()

else:
    st.warning(
        "Jaringan saat ini tidak memiliki sisi jembatan. "
        "Menghapus satu hubungan saja tidak akan memisahkan "
        "komponen jaringan. Coba pulihkan jaringan awal untuk "
        "menjalankan demonstrasi yang sesuai."
    )
    st.plotly_chart(buat_graf(G, pos), use_container_width=True)

# ==================================================
# 5. KONTROL MANUAL
# ==================================================

st.subheader("Ubah Hubungan Pertemanan")

anggota = sorted(G.nodes())
col_a, col_b = st.columns(2)

with col_a:
    a = st.selectbox(
        "Anggota A",
        anggota,
        format_func=lambda n: f"Anggota {n + 1}"
    )

with col_b:
    b = st.selectbox(
        "Anggota B",
        anggota,
        index=1 if len(anggota) > 1 else 0,
        format_func=lambda n: f"Anggota {n + 1}"
    )

col_tambah, col_hapus, col_reset = st.columns(3)

with col_tambah:
    if st.button("➕ Tambah hubungan"):
        if a == b:
            st.warning("Pilih dua anggota berbeda.")
        elif G.has_edge(a, b):
            st.warning("Hubungan tersebut sudah ada.")
        else:
            G.add_edge(a, b)
            st.session_state.G = G
            st.session_state.langkah_animasi = 0
            st.rerun()

with col_hapus:
    if st.button("➖ Hapus hubungan"):
        if G.has_edge(a, b):
            G.remove_edge(a, b)
            st.session_state.G = G
            st.session_state.langkah_animasi = 0
            st.rerun()
        else:
            st.warning("Kedua anggota belum terhubung.")

with col_reset:
    if st.button("Reset jaringan"):
        st.session_state.G = st.session_state.G_awal.copy()
        st.session_state.langkah_animasi = 0
        st.rerun()

# ==================================================
# 6. ANALISIS KELOMPOK TERKINI
# ==================================================

st.subheader("Analisis Kelompok")

komponen = sorted(
    nx.connected_components(G),
    key=len,
    reverse=True
)

if len(komponen) == 1:
    st.success("Semua anggota berada dalam satu kelompok terhubung.")
else:
    st.warning(
        f"Jaringan terpisah menjadi {len(komponen)} kelompok."
    )

for i, kelompok in enumerate(komponen, start=1):
    label = [n + 1 for n in sorted(kelompok)]
    st.write(
        f"Kelompok {i} ({len(kelompok)} anggota): "
        + ", ".join(map(str, label))
    )

st.caption(
    "Dataset: Zachary's Karate Club Network, tersedia melalui "
    "NetworkX. Pemilihan 20 anggota berdasarkan derajat tertinggi "
    "pada jaringan asli; hubungan subgraf mengikuti data asli."
)
