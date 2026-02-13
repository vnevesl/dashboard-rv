import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import glob
import os
import base64
from datetime import datetime

# ── Configuração da página ───────────────────────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="Painel de Carteiras",
    page_icon="💼",
)

# ── Paleta de cores (funciona em dark e light mode) ─────────────────────────
COLORS = {
    "primary": "#58A6FF",      # azul claro (links/destaque)
    "secondary": "#6DCEAA",    # verde menta
    "positive": "#3FB950",     # verde ganho
    "negative": "#F85149",     # vermelho perda
    "warning": "#D29922",      # dourado alerta
}

# Sequência de cores suaves para gráficos
CHART_PALETTE = [
    "#58A6FF",  # azul claro
    "#6DCEAA",  # verde menta
    "#D2A8FF",  # lilás
    "#F0883E",  # laranja suave
    "#79C0FF",  # azul céu
    "#7EE787",  # verde claro
    "#D29922",  # dourado
    "#F778BA",  # rosa suave
    "#A5D6FF",  # azul pastel
    "#FFA657",  # pêssego
    "#CEE3F8",  # gelo
    "#BBDAFA",  # azul gelo
]

# Template Plotly (bg transparente = adapta ao tema do Streamlit)
# separators=",." → decimal=comma, thousands=dot (padrão BR)
PLOTLY_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    separators=",.",
)

# ── CSS adaptável (funciona em dark e light mode) ────────────────────────────
st.markdown(
    """
    <style>
    /* Cards de métricas — fundo semi-transparente adapta ao tema */
    div[data-testid="stMetric"] {
        background: rgba(128,128,128,0.06);
        border: 1px solid rgba(128,128,128,0.15);
        border-radius: 0.75rem;
        padding: 1rem 1.2rem;
        border-left: 3px solid #4A90D9;
    }
    div[data-testid="stMetric"] label {
        font-size: 0.82rem !important;
        opacity: 0.7;
    }
    /* Multiselect tags — azul suave */
    span[data-baseweb="tag"] {
        background-color: rgba(74,144,217,0.15) !important;
        border-color: rgba(74,144,217,0.3) !important;
        color: #4A90D9 !important;
    }
    span[data-baseweb="tag"] span[role="presentation"] {
        color: #4A90D9 !important;
    }
    /* Dividers suaves */
    hr {
        border-color: rgba(128,128,128,0.2) !important;
    }
    /* Expander */
    details {
        border-color: rgba(128,128,128,0.2) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Mapa de emojis por tipo de carteira ──────────────────────────────────────
EMOJI_MAP = {
    "fii": "🏢",
    "fiis": "🏢",
    "fundos listados": "🏢",
    "dividendo": "💰",
    "dividend": "💰",
    "ações": "📈",
    "ação": "📈",
    "small cap": "🚀",
    "bdr": "🌎",
    "global": "🌐",
    "etf": "🌐",
    "internacional": "🌍",
    "bunker": "🛡️",
    "multi": "🎯",
    "quant": "🤖",
    "horizonte": "🔭",
    "híbrida": "⚖️",
    "renda": "💵",
    "wisir": "🧠",
    "levante": "🔥",
    "eleven": "⭐",
    "benndorf": "🏛️",
    "gráfica": "📊",
    "mensal": "📅",
    "top": "🏆",
    "mix": "🔀",
}


def get_emoji(name: str) -> str:
    lower = name.lower()
    for keyword, emoji in EMOJI_MAP.items():
        if keyword in lower:
            return emoji
    return "📁"


def add_emojis(name: str) -> str:
    return f"{get_emoji(name)} {name}"


# ── Helpers ──────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner="Carregando dados …")
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, engine="openpyxl")
    df.dropna(how="all", inplace=True)
    for col in df.select_dtypes(include="object").columns:
        try:
            parsed = pd.to_datetime(df[col], dayfirst=True)
            if parsed.notna().sum() > len(df) * 0.5:
                df[col] = parsed
        except (ValueError, TypeError):
            pass
    return df


def detect_columns(df: pd.DataFrame):
    cat_cols = list(df.select_dtypes(include="object").columns)
    num_cols = list(df.select_dtypes(include="number").columns)
    date_cols = list(df.select_dtypes(include="datetime").columns)
    return cat_cols, num_cols, date_cols


def fmt_num_br(value: float, decimals: int = 2) -> str:
    """Formata número no padrão brasileiro: 1.234.567,89"""
    formatted = f"{value:,.{decimals}f}"
    # Swap: comma->@, dot->comma(decimal), @->dot(thousands)
    return formatted.replace(",", "@").replace(".", ",").replace("@", ".")


def fmt_brl(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"R$ {fmt_num_br(value/1_000_000)} M"
    if abs(value) >= 1_000:
        return f"R$ {fmt_num_br(value/1_000, 1)} K"
    return f"R$ {fmt_num_br(value)}"


# ── Detecção do arquivo ──────────────────────────────────────────────────────
app_dir = os.path.dirname(__file__)
xlsx_files = glob.glob(os.path.join(app_dir, "*.xlsx"))

if not xlsx_files:
    st.error("❌ Nenhum arquivo `.xlsx` encontrado na pasta.")
    st.stop()

file_path = max(xlsx_files, key=os.path.getmtime)
file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
df_raw = load_data(file_path)
cat_cols, num_cols, date_cols = detect_columns(df_raw)

# ── Sidebar — Filtros ────────────────────────────────────────────────────────
with st.sidebar:
    # Logo — detecta tema e mostra a versão correta
    logo_dir = os.path.join(app_dir, "img")
    logo_dark = os.path.join(logo_dir, "logo branca xp (3).png")   # branca → dark mode
    logo_light = os.path.join(logo_dir, "logo preta xp (2).png")   # preta → light mode

    theme_base = st.get_option("theme.base")
    is_dark = theme_base != "light"
    logo_file = logo_dark if is_dark else logo_light

    if os.path.exists(logo_file):
        with open(logo_file, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f'<div style="text-align:center; padding: 0.5rem 0 1rem 0;">'
            f'<img src="data:image/png;base64,{b64}" style="max-width:180px; width:100%;" />'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("## 🔍 Filtros")
    st.caption("Ajuste os filtros para explorar os dados")

    filters: dict[str, list] = {}

    FILTER_LABELS = {
        "Carteira": "📂 Carteira",
        "Status": "🔔 Status",
        "Cód. Assessor Cliente": "👤 Assessor",
    }

    for col in cat_cols:
        unique_vals = sorted(df_raw[col].dropna().unique())
        if 2 <= len(unique_vals) <= 60:
            label = FILTER_LABELS.get(col, col)
            chosen = st.multiselect(label, unique_vals, default=unique_vals, key=col)
            filters[col] = chosen

    for col in date_cols:
        min_d = df_raw[col].min()
        max_d = df_raw[col].max()
        if pd.isna(min_d) or pd.isna(max_d):
            continue
        DATE_LABELS = {
            "Entrada": "📅 Período de Entrada",
            "Última execução": "🔄 Última Execução",
            "Próximo execução": "⏭️ Próxima Execução",
        }
        label = DATE_LABELS.get(col, f"📅 {col}")
        st.markdown(f"**{label}**")
        d_range = st.date_input(
            f"Intervalo de {col}",
            value=(min_d.date(), max_d.date()),
            min_value=min_d.date(),
            max_value=max_d.date(),
            key=f"date_{col}",
            label_visibility="collapsed",
        )
        if isinstance(d_range, (list, tuple)) and len(d_range) == 2:
            filters[f"__date__{col}"] = d_range

    st.divider()

    # ── Atualizar dados ──────────────────────────────────────────────────
    st.markdown("### 🔄 Atualizar Dados")

    # Indicador de frescor do arquivo
    file_age = datetime.now() - file_date
    if file_age.days == 0:
        age_text = "📗 Atualizado hoje"
        age_color = COLORS["positive"]
    elif file_age.days == 1:
        age_text = "📙 Atualizado ontem"
        age_color = COLORS["warning"]
    else:
        age_text = f"📕 {file_age.days} dias atrás"
        age_color = COLORS["negative"]

    st.markdown(
        f"<span style='color:{age_color}; font-size:0.85rem;'>"
        f"{age_text}</span>",
        unsafe_allow_html=True,
    )
    st.caption(f"📁 {os.path.basename(file_path)}")

    # Upload — substitui o arquivo antigo
    uploaded = st.file_uploader(
        "Envie o novo arquivo do dia:",
        type=["xlsx"],
        key="upload_novo",
    )
    if uploaded is not None:
        # Remove todos os xlsx antigos
        for old in glob.glob(os.path.join(app_dir, "*.xlsx")):
            os.remove(old)
        # Salva o novo
        dest = os.path.join(app_dir, uploaded.name)
        with open(dest, "wb") as f:
            f.write(uploaded.getbuffer())
        st.cache_data.clear()
        st.rerun()

    st.caption("💼 Painel de Carteiras v1.0")

# Aplicar filtros
df = df_raw.copy()
for key, value in filters.items():
    if key.startswith("__date__"):
        col = key.replace("__date__", "")
        start, end = value
        df = df[(df[col].dt.date >= start) & (df[col].dt.date <= end)]
    else:
        df = df[df[key].isin(value)]

# ── Cabeçalho ────────────────────────────────────────────────────────────────
st.markdown("# 💼 Painel de Carteiras — Renda Variável")
st.caption(
    f"📄 Fonte: **{os.path.basename(file_path)}**  ·  "
    f"🕐 Atualizado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
)

# ── KPIs ─────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)

total_posicao = df["Posição"].sum() if "Posição" in num_cols else 0
total_aportado = df["Valor aportado"].sum() if "Valor aportado" in num_cols else 0
rent_media = df["Rentabilidade"].mean() if "Rentabilidade" in num_cols else 0
resultado = total_posicao - total_aportado

with k1:
    st.metric("📊 Total de Posições", f"{len(df):,}")
with k2:
    st.metric("💰 Patrimônio Atual", fmt_brl(total_posicao))
with k3:
    st.metric("📥 Total Aportado", fmt_brl(total_aportado))
with k4:
    delta_color = "normal" if resultado >= 0 else "inverse"
    st.metric(
        "📈 Rentabilidade Média",
        f"{rent_media:+.2f}%",
        delta=f"Resultado: {fmt_brl(resultado)}",
        delta_color=delta_color,
    )

st.divider()

# ── Gráficos principais ─────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

# Gráfico 1 — Evolução temporal
with col_left:
    st.markdown("### 📅 Evolução Mensal de Aportes")
    main_date = "Entrada" if "Entrada" in date_cols else (date_cols[0] if date_cols else None)

    if main_date and "Valor aportado" in num_cols:
        ts = (
            df.groupby(df[main_date].dt.to_period("M"))
            .agg(
                valor_aportado=("Valor aportado", "sum"),
                posicao=("Posição", "sum"),
                qtd=("Valor aportado", "count"),
            )
        )
        ts.index = ts.index.to_timestamp()
        ts = ts.reset_index().rename(columns={main_date: "Mês"})

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=ts["Mês"], y=ts["valor_aportado"],
            mode="lines+markers",
            name="💰 Aportado",
            line=dict(color=COLORS["primary"], width=2),
            marker=dict(size=5),
            fill="tozeroy",
            fillcolor="rgba(88,166,255,0.05)",
            hovertemplate="<b>%{x|%b/%Y}</b><br>💰 Aportado: R$ %{y:,.2f}<extra></extra>",
        ))
        fig1.add_trace(go.Scatter(
            x=ts["Mês"], y=ts["posicao"],
            mode="lines+markers",
            name="📈 Posição",
            line=dict(color=COLORS["secondary"], width=2),
            marker=dict(size=5),
            fill="tozeroy",
            fillcolor="rgba(109,206,170,0.05)",
            hovertemplate="<b>%{x|%b/%Y}</b><br>📈 Posição: R$ %{y:,.2f}<extra></extra>",
        ))
        fig1.update_layout(
            **PLOTLY_LAYOUT,
            hovermode="x unified",
            margin=dict(l=0, r=0, t=10, b=0),
            height=420,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            xaxis_title="", yaxis_title="Valor (R$)",
            yaxis_tickprefix="R$ ", yaxis_tickformat=",.0f",
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("📅 Nenhuma coluna de data encontrada.")

# Gráfico 2 — Patrimônio por carteira
with col_right:
    st.markdown("### 🏦 Patrimônio por Carteira")
    if "Carteira" in cat_cols and "Posição" in num_cols:
        cat_agg = (
            df.groupby("Carteira", as_index=False)
            .agg(
                posicao=("Posição", "sum"),
                aportado=("Valor aportado", "sum"),
                qtd=("Posição", "count"),
                rent_media=("Rentabilidade", "mean"),
            )
            .sort_values("posicao", ascending=True)
        )
        cat_agg["label"] = cat_agg["Carteira"].apply(add_emojis)
        cat_agg["resultado"] = cat_agg["posicao"] - cat_agg["aportado"]

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            y=cat_agg["label"], x=cat_agg["posicao"],
            orientation="h",
            marker_color="rgba(88,166,255,0.45)",
            marker_line_color="rgba(88,166,255,0.6)",
            marker_line_width=1,
            customdata=cat_agg[["aportado", "qtd", "rent_media", "resultado"]].values,
            hovertemplate=(
                "<b>%{y}</b><br><br>"
                "📈 Posição atual: R$ %{x:,.2f}<br>"
                "📥 Total aportado: R$ %{customdata[0]:,.2f}<br>"
                "👥 Nº de clientes: %{customdata[1]}<br>"
                "📊 Rentabilidade média: %{customdata[2]:+.2f}%<br>"
                "💵 Resultado: R$ %{customdata[3]:,.2f}"
                "<extra></extra>"
            ),
        ))
        fig2.update_layout(
            **PLOTLY_LAYOUT,
            margin=dict(l=0, r=0, t=10, b=0),
            height=420,
            xaxis_title="Posição (R$)",
            xaxis_tickprefix="R$ ", xaxis_tickformat=",.0f",
            yaxis_title="", showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

# ── Segunda linha de gráficos ────────────────────────────────────────────────
col_a, col_b = st.columns(2)

# Gráfico 3 — Composição (donut)
with col_a:
    st.markdown("### 🍕 Composição da Carteira")
    if "Carteira" in cat_cols and "Posição" in num_cols:
        pie_data = (
            df.groupby("Carteira", as_index=False)["Posição"]
            .sum().sort_values("Posição", ascending=False)
        )
        pie_data["label"] = pie_data["Carteira"].apply(add_emojis)

        fig3 = px.pie(
            pie_data, values="Posição", names="label",
            color_discrete_sequence=CHART_PALETTE, hole=0.4,
        )
        fig3.update_traces(
            textposition="inside", textinfo="percent",
            textfont_color="#FFFFFF",
            hovertemplate=(
                "<b>%{label}</b><br><br>"
                "💰 Valor: R$ %{value:,.2f}<br>"
                "📊 Participação: %{percent}"
                "<extra></extra>"
            ),
        )
        fig3.update_layout(
            **PLOTLY_LAYOUT,
            margin=dict(l=0, r=0, t=10, b=10), height=440,
            legend=dict(orientation="v", yanchor="middle", y=0.5,
                        xanchor="left", x=1.02, font=dict(size=10)),
        )
        st.plotly_chart(fig3, use_container_width=True)

# Gráfico 4 — Distribuição de rentabilidade
with col_b:
    st.markdown("### 📊 Distribuição de Rentabilidade")
    if "Rentabilidade" in num_cols:
        fig4 = go.Figure()
        neg = df[df["Rentabilidade"] < 0]["Rentabilidade"]
        pos = df[df["Rentabilidade"] >= 0]["Rentabilidade"]

        fig4.add_trace(go.Histogram(
            x=neg, nbinsx=20,
            marker_color="rgba(248,81,73,0.25)",
            marker_line_color="rgba(248,81,73,0.45)",
            marker_line_width=1,
            name="📉 Negativa",
            hovertemplate="📉 Faixa: %{x:.1f}%<br>Quantidade: %{y} posições<extra></extra>",
        ))
        fig4.add_trace(go.Histogram(
            x=pos, nbinsx=30,
            marker_color="rgba(63,185,80,0.25)",
            marker_line_color="rgba(63,185,80,0.45)",
            marker_line_width=1,
            name="📈 Positiva",
            hovertemplate="📈 Faixa: %{x:.1f}%<br>Quantidade: %{y} posições<extra></extra>",
        ))
        fig4.add_vline(
            x=rent_media, line_dash="dash", line_color=COLORS["primary"],
            annotation_text=f"Média: {rent_media:+.1f}%",
            annotation_position="bottom right",
            annotation_font_size=11, annotation_font_color=COLORS["primary"],
            annotation_yshift=-10,
        )
        fig4.update_layout(
            **PLOTLY_LAYOUT,
            margin=dict(l=0, r=0, t=30, b=0), height=440,
            xaxis_title="Rentabilidade (%)", xaxis_ticksuffix="%",
            yaxis_title="Nº de Posições",
            bargap=0.05, barmode="stack",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig4, use_container_width=True)

# ── Ranking ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown("### 🏆 Ranking por Rentabilidade Média")

if "Carteira" in cat_cols and "Rentabilidade" in num_cols:
    ranking = (
        df.groupby("Carteira", as_index=False)
        .agg(
            rent_media=("Rentabilidade", "mean"),
            posicao_total=("Posição", "sum"),
            aportado_total=("Valor aportado", "sum"),
            clientes=("Cliente", "nunique"),
        )
        .sort_values("rent_media", ascending=False)
    )
    ranking["label"] = ranking["Carteira"].apply(add_emojis)

    colors = [
        "rgba(63,185,80,0.4)" if v >= 0 else "rgba(248,81,73,0.4)"
        for v in ranking["rent_media"]
    ]
    borders = [
        "rgba(63,185,80,0.6)" if v >= 0 else "rgba(248,81,73,0.6)"
        for v in ranking["rent_media"]
    ]

    fig5 = go.Figure()
    fig5.add_trace(go.Bar(
        x=ranking["label"], y=ranking["rent_media"],
        marker_color=colors, marker_line_color=borders, marker_line_width=1,
        customdata=ranking[["posicao_total", "aportado_total", "clientes"]].values,
        hovertemplate=(
            "<b>%{x}</b><br><br>"
            "📊 Rentabilidade média: %{y:+.2f}%<br>"
            "📈 Posição total: R$ %{customdata[0]:,.2f}<br>"
            "📥 Aportado total: R$ %{customdata[1]:,.2f}<br>"
            "👥 Clientes únicos: %{customdata[2]}"
            "<extra></extra>"
        ),
    ))
    fig5.update_layout(
        **PLOTLY_LAYOUT,
        margin=dict(l=0, r=20, t=10, b=0), height=380,
        xaxis_title="", yaxis_title="Rentabilidade Média (%)",
        yaxis_ticksuffix="%", showlegend=False,
    )
    fig5.update_xaxes(tickangle=-45)
    fig5.add_hline(y=0, line_color="rgba(128,128,128,0.3)", line_width=1)
    st.plotly_chart(fig5, use_container_width=True)

# ── Dados brutos ─────────────────────────────────────────────────────────────
st.divider()
with st.expander("📋 Ver Dados Completos"):
    display_df = df.copy()
    for col in ["Valor aportado", "Posição"]:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda v: f"R$ {fmt_num_br(v)}")
    if "Rentabilidade" in display_df.columns:
        display_df["Rentabilidade"] = display_df["Rentabilidade"].apply(lambda v: f"{fmt_num_br(v)}%")
    st.dataframe(
        display_df,
        use_container_width=True, height=400,
    )
    st.caption(
        f"📊 Exibindo **{len(df):,}** de **{len(df_raw):,}** registros após filtros.  ·  "
        f"👥 **{df['Cliente'].nunique():,}** clientes únicos"
    )
