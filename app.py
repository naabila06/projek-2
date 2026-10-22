
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
# 1. DATASET DAN PEMILIHAN 20 ANGGOTA
# ==================================================

@st.cache_resource
def load_original_network():
    return nx.karate_club_graph()


def select_members(graph, jumlah=20):
    urutan = sorted(
        graph.nodes(),
        key=lambda n: (-graph.degree(n), n)
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

if "edge_animasi" not in st.session_state:
    st.session_state.edge_animasi = None

G = st.session_state.G

# Posisi anggota dibuat tetap agar grafik tidak berpindah-pindah
pos = nx.spring_layout(
    st.session_state.G_awal,
    seed=7
)


# ==================================================
# 2. FUNGSI ANALISIS
# ==================================================

def jumlah_kelompok(graph):
    return nx.number_connected_components(graph)


def format_anggota(n):
    return f"Anggota {n + 1}"


# ==================================================
# 3. FUNGSI MEMBUAT GRAFIK
# ==================================================

def buat_graf(graph, posisi, edge_baru=None, edge_hapus=None):
    fig = go.Figure()

    # Garis hubungan yang masih aktif
    edge_x = []
    edge_y = []

    for u, v in graph.edges():
        edge_x.extend([
            posisi[u][0],
            posisi[v][0],
            None
        ])
        edge_y.extend([
            posisi[u][1],
            posisi[v][1],
            None
        ])

    fig.add_trace(go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(
            color="#94A3B8",
            width=1.8
        ),
        hoverinfo="none",
        name="Hubungan"
    ))

    # Garis hubungan yang dihapus
    if edge_hapus is not None:
        u, v = edge_hapus

        fig.add_trace(go.Scatter(
            x=[posisi[u][0], posisi[v][0]],
            y=[posisi[u][1], posisi[v][1]],
            mode="lines",
            line=dict(
                color="#DC2626",
                width=4,
                dash="dash"
            ),
            hovertemplate="Hubungan terputus<extra></extra>",
            name="Hubungan terputus"
        ))

    # Garis hubungan yang baru ditambahkan
    if edge_baru is not None:
        u, v = edge_baru

        fig.add_trace(go.Scatter(
            x=[posisi[u][0], posisi[v][0]],
            y=[posisi[u][1], posisi[v][1]],
            mode="lines",
            line=dict(
                color="#16A34A",
                width=4
            ),
            hovertemplate="Hubungan dipulihkan<extra></extra>",
            name="Hubungan dipulihkan"
        ))

    # Warna anggota berdasarkan kelompok terhubung
    komponen = list(nx.connected_components(graph))

    warna_node = []
    for n in graph.nodes():
        nomor_kelompok = next(
            i for i, kelompok in enumerate(komponen)
            if n in kelompok
        )
        warna_node.append(nomor_kelompok)

    derajat = dict(graph.degree())

    fig.add_trace(go.Scatter(
        x=[posisi[n][0] for n in graph.nodes()],
        y=[posisi[n][1] for n in graph.nodes()],
        mode="markers+text",
        text=[str(n + 1) for n in graph.nodes()],
        textposition="top center",
        marker=dict(
            size=[
                14 + 2 * derajat[n]
                for n in graph.nodes()
            ],
            color=warna_node,
            colorscale="Viridis",
            showscale=False,
            line=dict(
                width=1,
                color="white"
            )
        ),
        customdata=[
            derajat[n] for n in graph.nodes()
        ],
        hovertemplate=(
            "Anggota %{text}<br>"
            "Jumlah hubungan: %{customdata}"
            "<extra></extra>"
        ),
        name="Anggota"
    ))

    fig.update_layout(
        height=580,
        margin=dict(l=10, r=10, t=35, b=10),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    return fig


# ==================================================
# 4. RINGKASAN JARINGAN
# ==================================================

st.subheader("📊 Kondisi Jaringan")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Jumlah anggota",
    G.number_of_nodes()
)

c2.metric(
    "Jumlah hubungan",
    G.number_of_edges()
)

c3.metric(
    "Kelompok terhubung",
    jumlah_kelompok(G)
)

st.caption(
    "Grafik menampilkan 20 anggota yang dipilih berdasarkan "
    "derajat tertinggi pada jaringan asli. Nomor pada grafik "
    "mengikuti nomor anggota dari dataset."
)




# ==================================================
# 5. ANIMASI JARINGAN BERTAHAP
# ==================================================

st.subheader("🎬 Animasi Perubahan Jaringan")

st.write(
    "Amati bagaimana anggota dan hubungan pertemanan berubah "
    "secara bertahap, kemudian lihat dampaknya terhadap "
    "kelompok sosial."
)

G_dasar = st.session_state.G_awal.copy()
daftar_sisi = sorted(
    G_dasar.edges(),
    key=lambda e: (min(e), max(e))
)

if daftar_sisi:
    # Pilih beberapa hubungan untuk dihapus bertahap.
    # Hubungan dipilih berdasarkan urutan tetap agar hasil konsisten.
    jumlah_hapus = min(8, max(1, len(daftar_sisi) // 6))
    sisi_dihapus = daftar_sisi[:jumlah_hapus]

    # Buat kondisi jaringan pada setiap tahap.
    tahap_graf = [G_dasar.copy()]
    G_sementara = G_dasar.copy()

    for sisi in sisi_dihapus:
        if G_sementara.has_edge(*sisi):
            G_sementara.remove_edge(*sisi)
            tahap_graf.append(G_sementara.copy())

    # Pulihkan hubungan satu per satu.
    for sisi in reversed(sisi_dihapus):
        if not G_sementara.has_edge(*sisi):
            G_sementara.add_edge(*sisi)
            tahap_graf.append(G_sementara.copy())

    nama_tahap = [
        "Jaringan awal"
    ]

    nama_tahap += [
        f"Hubungan terhapus {i}"
        for i in range(1, len(tahap_graf) - len(sisi_dihapus))
    ]

    nama_tahap += [
        f"Pemulihan hubungan {i}"
        for i in range(1, len(sisi_dihapus) + 1)
    ]

    # Pastikan jumlah label sama dengan jumlah tahap
    nama_tahap = nama_tahap[:len(tahap_graf)]

    def buat_frame(graph, tahap):
        # Buat grafik pada kondisi tertentu.
        fig_tahap = buat_graf(graph, pos)

        # Gunakan warna kelompok yang dihitung dari kondisi tahap ini.
        return go.Frame(
            name=tahap,
            data=fig_tahap.data
        )

    # Gunakan tampilan awal sebagai dasar animasi.
    fig_awal = buat_graf(tahap_graf[0], pos)

    frames = [
        buat_frame(graph, nama)
        for graph, nama in zip(tahap_graf, nama_tahap)
    ]

    fig_animasi = go.Figure(
        data=fig_awal.data,
        frames=frames
    )

    # Kunci batas grafik agar posisi anggota tetap.
    rentang_x = [pos[n][0] for n in G_dasar.nodes()]
    rentang_y = [pos[n][1] for n in G_dasar.nodes()]

    fig_animasi.update_layout(
        height=620,
        margin=dict(l=10, r=10, t=90, b=90),
        showlegend=False,
        plot_bgcolor="white",
        xaxis=dict(
            visible=False,
            range=[
                min(rentang_x) - 0.15,
                max(rentang_x) + 0.15
            ]
        ),
        yaxis=dict(
            visible=False,
            range=[
                min(rentang_y) - 0.15,
                max(rentang_y) + 0.15
            ]
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                x=0,
                y=1.16,
                showactive=False,
                buttons=[
                    dict(
                        label="▶ Mulai",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {
                                    "duration": 900,
                                    "redraw": True
                                },
                                "transition": {
                                    "duration": 250
                                },
                                "fromcurrent": True,
                                "mode": "immediate"
                            }
                        ]
                    ),
                    dict(
                        label="⏸ Jeda",
                        method="animate",
                        args=[
                            [None],
                            {
                                "frame": {
                                    "duration": 0,
                                    "redraw": False
                                },
                                "transition": {
                                    "duration": 0
                                },
                                "mode": "immediate"
                            }
                        ]
                    ),
                    dict(
                        label="↺ Ulangi",
                        method="animate",
                        args=[
                            [nama_tahap[0]],
                            {
                                "frame": {
                                    "duration": 0,
                                    "redraw": True
                                },
                                "transition": {
                                    "duration": 0
                                },
                                "mode": "immediate"
                            }
                        ]
                    )
                ]
            )
        ],
        sliders=[
            dict(
                active=0,
                x=0,
                y=0,
                len=1,
                currentvalue={
                    "prefix": "Tahap: "
                },
                steps=[
                    dict(
                        label=nama,
                        method="animate",
                        args=[
                            [nama],
                            {
                                "frame": {
                                    "duration": 500,
                                    "redraw": True
                                },
                                "transition": {
                                    "duration": 200
                                },
                                "mode": "immediate"
                            }
                        ]
                    )
                    for nama in nama_tahap
                ]
            )
        ]
    )

    st.plotly_chart(
        fig_animasi,
        use_container_width=True,
        key="animasi_banyak_tahap"
    )

    st.write(
        f"Jumlah tahap animasi: {len(tahap_graf)}."
    )

    for i, graph in enumerate(tahap_graf):
        st.caption(
            f"{nama_tahap[i]}: "
            f"{graph.number_of_nodes()} anggota, "
            f"{graph.number_of_edges()} hubungan, "
            f"{jumlah_kelompok(graph)} kelompok."
        )

else:
    st.warning(
        "Jaringan belum memiliki hubungan untuk dianimasikan."
    )


# ==================================================
# 6. KONTROL MANUAL
# ==================================================

st.subheader("👥 Ubah Hubungan Pertemanan")

anggota = sorted(G.nodes())

col_a, col_b = st.columns(2)

with col_a:
    a = st.selectbox(
        "Anggota A",
        anggota,
        format_func=format_anggota,
        key="pilihan_anggota_a"
    )

with col_b:
    b = st.selectbox(
        "Anggota B",
        anggota,
        index=1 if len(anggota) > 1 else 0,
        format_func=format_anggota,
        key="pilihan_anggota_b"
    )

col_tambah, col_hapus, col_reset = st.columns(3)

with col_tambah:
    if st.button(
        "➕ Tambah hubungan",
        use_container_width=True
    ):
        if a == b:
            st.warning(
                "Pilih dua anggota yang berbeda."
            )
        elif G.has_edge(a, b):
            st.warning(
                "Hubungan kedua anggota sudah ada."
            )
        else:
            G.add_edge(a, b)
            st.session_state.G = G
            st.rerun()

with col_hapus:
    if st.button(
        "➖ Hapus hubungan",
        use_container_width=True
    ):
        if a == b:
            st.warning(
                "Pilih dua anggota yang berbeda."
            )
        elif G.has_edge(a, b):
            G.remove_edge(a, b)
            st.session_state.G = G
            st.rerun()
        else:
            st.warning(
                "Kedua anggota belum memiliki hubungan."
            )

with col_reset:
    if st.button(
        "🔄 Reset jaringan",
        use_container_width=True
    ):
        st.session_state.G = (
            st.session_state.G_awal.copy()
        )
        st.rerun()


# ==================================================
# 7. VISUALISASI JARINGAN TERKINI
# ==================================================

st.subheader("🌐 Jaringan Setelah Perubahan")

st.write(
    "Grafik berikut menunjukkan kondisi jaringan yang sedang "
    "aktif setelah kamu menambah atau menghapus hubungan."
)

st.plotly_chart(
    buat_graf(G, pos),
    use_container_width=True,
    key="grafik_jaringan_terkini"
)


# ==================================================
# 8. ANALISIS KELOMPOK
# ==================================================

st.subheader("🔎 Analisis Kelompok")

komponen = sorted(
    nx.connected_components(G),
    key=len,
    reverse=True
)

if len(komponen) == 1:
    st.success(
        "Semua anggota berada dalam satu kelompok terhubung."
    )
else:
    st.warning(
        f"Jaringan terpisah menjadi {len(komponen)} kelompok."
    )

for i, kelompok in enumerate(komponen, start=1):
    label = [
        n + 1 for n in sorted(kelompok)
    ]

    st.write(
        f"**Kelompok {i} ({len(kelompok)} anggota):** "
        + ", ".join(map(str, label))
    )


# ==================================================
# 9. KETERANGAN DATASET
# ==================================================

st.divider()

st.caption(
    "Dataset: Zachary's Karate Club Network melalui NetworkX. "
    "Jaringan dibatasi menjadi 20 anggota berdasarkan derajat "
    "tertinggi pada jaringan asli, dengan nomor terkecil sebagai "
    "pemecah seri. Hubungan pada subgraf mengikuti data asli."
)
