import streamlit as st
import json
import os
from datetime import date, timedelta
from collections import defaultdict

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="NutriFlow · Diário Pessoal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Arquivo de dados local ──────────────────────────────────────────────────
DATA_FILE = "nutriflow_data.json"

def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"alimentacao": {}, "treinos": {}}

def save_data(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ── CSS personalizado – dark mode premium ──────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

  /* Reset e base */
  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d0f14 !important;
    color: #e8eaf0 !important;
  }

  /* Remove barra branca do topo */
  header[data-testid="stHeader"] { background: transparent !important; }
  .block-container { padding-top: 2rem !important; max-width: 1100px; }

  /* Título principal */
  .hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #00e5a0 0%, #00b4d8 60%, #7b5ea7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0;
    line-height: 1.1;
  }
  .hero-sub {
    font-size: 0.9rem;
    color: #6b7280;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 0.2rem;
  }

  /* Cards */
  .card {
    background: #161923;
    border: 1px solid #1f2535;
    border-radius: 16px;
    padding: 1.5rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 30px rgba(0,0,0,0.4);
  }
  .card-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #e8eaf0;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  /* Métricas customizadas */
  .metric-box {
    background: #1a1f2e;
    border: 1px solid #252d42;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
  }
  .metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #00e5a0;
    line-height: 1;
  }
  .metric-label {
    font-size: 0.75rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-top: 0.3rem;
  }
  .metric-value.accent-blue { color: #00b4d8; }
  .metric-value.accent-purple { color: #a78bfa; }

  /* Badges de refeição */
  .food-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #1a1f2e;
    border-radius: 10px;
    padding: 0.65rem 1rem;
    margin-bottom: 0.45rem;
    border-left: 3px solid #00e5a0;
    font-size: 0.88rem;
  }
  .food-name { font-weight: 500; color: #d1d5db; }
  .food-qty  { color: #6b7280; font-size: 0.8rem; }
  .food-kcal { font-family: 'Syne', sans-serif; font-weight: 700; color: #00e5a0; font-size: 0.95rem; }

  /* Treino badges */
  .treino-item {
    background: #1a1f2e;
    border-radius: 10px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.45rem;
    border-left: 3px solid #7b5ea7;
    font-size: 0.88rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .treino-ok    { color: #00e5a0; font-weight: 600; }
  .treino-miss  { color: #f87171; font-weight: 600; }

  /* Inputs */
  .stTextInput > div > div > input,
  .stNumberInput > div > div > input,
  .stSelectbox > div > div,
  .stTextArea > div > div > textarea {
    background: #1a1f2e !important;
    border: 1px solid #252d42 !important;
    border-radius: 10px !important;
    color: #e8eaf0 !important;
    font-family: 'DM Sans', sans-serif !important;
  }

  /* Botões */
  .stButton > button {
    background: linear-gradient(135deg, #00e5a0, #00b4d8) !important;
    color: #0d0f14 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.55rem 1.4rem !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.02em !important;
    transition: opacity 0.2s !important;
    box-shadow: 0 0 20px rgba(0,229,160,0.2) !important;
  }
  .stButton > button:hover { opacity: 0.85 !important; }

  /* Botão deletar */
  .stButton.delete > button {
    background: linear-gradient(135deg, #f87171, #ef4444) !important;
    box-shadow: 0 0 15px rgba(248,113,113,0.2) !important;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    background: #161923 !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid #1f2535 !important;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #6b7280 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 9px !important;
    padding: 0.5rem 1.2rem !important;
    border: none !important;
  }
  .stTabs [aria-selected="true"] {
    background: #1a1f2e !important;
    color: #00e5a0 !important;
  }

  /* Barra de progresso de calorias */
  .progress-bar-bg {
    background: #1a1f2e;
    border-radius: 999px;
    height: 8px;
    margin-top: 0.4rem;
    overflow: hidden;
  }
  .progress-bar-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #00e5a0, #00b4d8);
    transition: width 0.5s ease;
  }

  /* Date input */
  .stDateInput > div > div > input {
    background: #1a1f2e !important;
    border: 1px solid #252d42 !important;
    color: #e8eaf0 !important;
    border-radius: 10px !important;
  }

  /* Selectbox */
  div[data-baseweb="select"] > div {
    background: #1a1f2e !important;
    border-color: #252d42 !important;
    color: #e8eaf0 !important;
  }

  /* Checkbox */
  .stCheckbox label span { color: #d1d5db !important; }

  /* Divider */
  hr { border-color: #1f2535 !important; }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 5px; }
  ::-webkit-scrollbar-track { background: #0d0f14; }
  ::-webkit-scrollbar-thumb { background: #252d42; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ── Dados ──────────────────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data
today_str = str(date.today())

# Garante entradas de hoje
data["alimentacao"].setdefault(today_str, [])
data["treinos"].setdefault(today_str, {"descricao": "", "concluido": False, "notas": ""})

# ── Cabeçalho ──────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<div class="hero-title">⚡ NutriFlow</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Diário pessoal de nutrição & treinos</div>', unsafe_allow_html=True)
with col_h2:
    selected_date = st.date_input("📅 Data", value=date.today(), label_visibility="collapsed")
    selected_str = str(selected_date)
    data["alimentacao"].setdefault(selected_str, [])
    data["treinos"].setdefault(selected_str, {"descricao": "", "concluido": False, "notas": ""})

st.markdown("<br>", unsafe_allow_html=True)

# ── Cálculos ───────────────────────────────────────────────────────────────
META_CALORIAS = 2100

def total_kcal_dia(dia_str: str) -> float:
    return sum(r["calorias"] for r in data["alimentacao"].get(dia_str, []))

def media_semanal() -> float:
    hoje = date.today()
    dias = [(hoje - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
    totais = [total_kcal_dia(d) for d in dias if d in data["alimentacao"]]
    return round(sum(totais) / len(totais), 1) if totais else 0.0

kcal_hoje    = total_kcal_dia(selected_str)
kcal_semana  = media_semanal()
pct_meta     = min(kcal_hoje / META_CALORIAS * 100, 100)
treinos_7d   = sum(1 for d in [(date.today() - timedelta(days=i)).isoformat() for i in range(7)]
                   if data["treinos"].get(d, {}).get("concluido"))

# ── Métricas do topo ───────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="metric-box">
      <div class="metric-value">{kcal_hoje:.0f}</div>
      <div class="metric-label">kcal hoje</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-box">
      <div class="metric-value accent-blue">{kcal_semana}</div>
      <div class="metric-label">kcal média/semana</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="metric-box">
      <div class="metric-value accent-purple">{treinos_7d}/7</div>
      <div class="metric-label">treinos na semana</div>
    </div>""", unsafe_allow_html=True)
with c4:
    cor_meta = "#00e5a0" if pct_meta < 90 else ("#f59e0b" if pct_meta < 110 else "#f87171")
    st.markdown(f"""
    <div class="metric-box">
      <div class="metric-value" style="color:{cor_meta}">{pct_meta:.0f}%</div>
      <div class="metric-label">da meta ({META_CALORIAS} kcal)</div>
    </div>""", unsafe_allow_html=True)

# Barra de progresso
st.markdown(f"""
<div style="margin:1rem 0 1.5rem;">
  <div style="font-size:0.75rem;color:#6b7280;margin-bottom:0.3rem;">Progresso calórico do dia</div>
  <div class="progress-bar-bg">
    <div class="progress-bar-fill" style="width:{pct_meta}%;background:linear-gradient(90deg,{cor_meta},{cor_meta}aa);"></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs principais ─────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🥗  Alimentação", "🏋️  Treino", "📊  Histórico"])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 – ALIMENTAÇÃO
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    col_form, col_lista = st.columns([1, 1.3], gap="large")

    with col_form:
        st.markdown('<div class="card"><div class="card-title">➕ Registrar refeição</div>', unsafe_allow_html=True)

        alimento   = st.text_input("Alimento / prato", placeholder="Ex: Arroz integral cozido")
        col_q, col_u = st.columns([2, 1])
        with col_q:
            quantidade = st.number_input("Quantidade", min_value=0.0, step=10.0, value=100.0)
        with col_u:
            unidade = st.selectbox("Unidade", ["g", "ml", "unid", "colher", "xícara"])
        calorias = st.number_input("Calorias (kcal)", min_value=0.0, step=1.0, value=0.0)

        if st.button("Adicionar ✓", use_container_width=True):
            if alimento.strip():
                registro = {
                    "alimento": alimento.strip(),
                    "quantidade": quantidade,
                    "unidade": unidade,
                    "calorias": calorias,
                }
                data["alimentacao"][selected_str].append(registro)
                save_data(data)
                st.success("Refeição registrada!", icon="✅")
                st.rerun()
            else:
                st.warning("Informe o nome do alimento.")

        st.markdown('</div>', unsafe_allow_html=True)

        # Macros rápidos (referência)
        st.markdown('<div class="card"><div class="card-title">📖 Referência rápida</div>', unsafe_allow_html=True)
        referencias = {
            "Arroz branco cozido (100g)": 130,
            "Frango grelhado (100g)": 165,
            "Ovo inteiro (1 unid)": 78,
            "Batata-doce cozida (100g)": 86,
            "Aveia (40g)": 148,
            "Whey protein (30g)": 120,
        }
        for nome, kcal in referencias.items():
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:0.3rem 0;
                        border-bottom:1px solid #1f2535;font-size:0.82rem;">
              <span style="color:#9ca3af">{nome}</span>
              <span style="color:#00e5a0;font-weight:600">{kcal} kcal</span>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_lista:
        refeicoes_dia = data["alimentacao"].get(selected_str, [])
        st.markdown(f'<div class="card-title" style="font-family:Syne,sans-serif;font-weight:700;font-size:1.05rem;">🗓️ {selected_date.strftime("%d/%m/%Y")} — {len(refeicoes_dia)} item(ns) · {total_kcal_dia(selected_str):.0f} kcal</div>', unsafe_allow_html=True)

        if not refeicoes_dia:
            st.markdown('<div style="color:#4b5563;text-align:center;padding:3rem 0;font-size:0.9rem;">Nenhum registro para este dia.<br>Adicione sua primeira refeição →</div>', unsafe_allow_html=True)
        else:
            for i, r in enumerate(refeicoes_dia):
                col_item, col_del = st.columns([6, 1])
                with col_item:
                    st.markdown(f"""
                    <div class="food-item">
                      <div>
                        <div class="food-name">{r['alimento']}</div>
                        <div class="food-qty">{r['quantidade']} {r['unidade']}</div>
                      </div>
                      <div class="food-kcal">{r['calorias']:.0f} kcal</div>
                    </div>""", unsafe_allow_html=True)
                with col_del:
                    if st.button("🗑️", key=f"del_food_{i}_{selected_str}", help="Remover"):
                        data["alimentacao"][selected_str].pop(i)
                        save_data(data)
                        st.rerun()

        # Resumo do dia
        if refeicoes_dia:
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;padding:0.5rem 0;">
              <span style="color:#6b7280;font-size:0.85rem">Total do dia</span>
              <span style="font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800;color:#00e5a0">{total_kcal_dia(selected_str):.0f} kcal</span>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 – TREINO
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    col_tf, col_tl = st.columns([1, 1.2], gap="large")

    treino_dia = data["treinos"][selected_str]

    with col_tf:
        st.markdown('<div class="card"><div class="card-title">🏋️ Registrar treino</div>', unsafe_allow_html=True)

        grupos = [
            "— Selecione —",
            "Peito e Tríceps", "Costas e Bíceps", "Ombros",
            "Pernas (Quadríceps)", "Pernas (Posterior/Glúteos)",
            "Full Body", "HIIT / Cardio", "Funcional",
            "Mobilidade / Alongamento", "Descanso", "Outro",
        ]
        idx_atual = 0
        if treino_dia.get("descricao") in grupos:
            idx_atual = grupos.index(treino_dia["descricao"])

        descricao = st.selectbox("Grupo muscular / tipo", grupos, index=idx_atual)
        notas     = st.text_area("Observações / exercícios realizados",
                                  value=treino_dia.get("notas", ""),
                                  placeholder="Ex: Supino 4x10 80kg, Crucifixo 3x12…",
                                  height=120)
        concluido = st.checkbox("✅ Treino concluído", value=treino_dia.get("concluido", False))

        if st.button("Salvar treino", use_container_width=True):
            data["treinos"][selected_str] = {
                "descricao": descricao if descricao != "— Selecione —" else "",
                "notas": notas,
                "concluido": concluido,
            }
            save_data(data)
            st.success("Treino salvo!", icon="💪")
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with col_tl:
        st.markdown('<div class="card-title" style="font-family:Syne,sans-serif;font-weight:700;font-size:1.05rem;">📅 Últimos 14 dias</div>', unsafe_allow_html=True)

        hoje = date.today()
        for i in range(13, -1, -1):
            d = hoje - timedelta(days=i)
            d_str = d.isoformat()
            t = data["treinos"].get(d_str, {})
            desc  = t.get("descricao") or "—"
            ok    = t.get("concluido", False)
            label = "✓ Concluído" if ok else ("· Não registrado" if not t.get("descricao") else "✗ Não concluído")
            cls   = "treino-ok" if ok else "treino-miss"
            dia_label = "Hoje" if i == 0 else ("Ontem" if i == 1 else d.strftime("%d/%m"))
            st.markdown(f"""
            <div class="treino-item">
              <div>
                <div style="font-size:0.8rem;color:#6b7280">{dia_label}</div>
                <div style="color:#d1d5db;font-weight:500;font-size:0.88rem">{desc}</div>
              </div>
              <span class="{cls}">{label}</span>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 – HISTÓRICO / ANALYTICS
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="card-title" style="font-family:Syne,sans-serif;font-weight:700;font-size:1.05rem;">📊 Histórico calórico — últimos 30 dias</div>', unsafe_allow_html=True)

    hoje = date.today()
    dias_30    = [(hoje - timedelta(days=i)).isoformat() for i in range(29, -1, -1)]
    kcal_30    = [total_kcal_dia(d) for d in dias_30]
    labels_30  = [(hoje - timedelta(days=i)).strftime("%d/%m") for i in range(29, -1, -1)]

    # Gráfico de barras nativo do Streamlit (sem dependência extra)
    import pandas as pd
    df_chart = pd.DataFrame({"Data": labels_30, "kcal": kcal_30})
    df_chart = df_chart.set_index("Data")
    st.bar_chart(df_chart, height=260, color="#00e5a0")

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabela resumida
    st.markdown('<div class="card-title" style="font-family:Syne,sans-serif;font-weight:700;font-size:1.05rem;">📋 Resumo diário detalhado</div>', unsafe_allow_html=True)

    rows = []
    for d_str in reversed(dias_30):
        kcal = total_kcal_dia(d_str)
        if kcal == 0 and not data["treinos"].get(d_str, {}).get("descricao"):
            continue
        treino_d = data["treinos"].get(d_str, {})
        rows.append({
            "Data": d_str,
            "Kcal": f"{kcal:.0f}",
            "Refeições": len(data["alimentacao"].get(d_str, [])),
            "Treino": treino_d.get("descricao") or "—",
            "Concluído": "✓" if treino_d.get("concluido") else "✗",
        })

    if rows:
        df_tab = pd.DataFrame(rows)
        st.dataframe(df_tab, use_container_width=True, hide_index=True)
    else:
        st.markdown('<div style="color:#4b5563;text-align:center;padding:2rem;font-size:0.9rem;">Sem dados registrados nos últimos 30 dias.</div>', unsafe_allow_html=True)

    # Exportar dados
    st.markdown("<br>", unsafe_allow_html=True)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw_json = f.read()
    st.download_button(
        label="⬇️ Exportar dados (JSON)",
        data=raw_json,
        file_name="nutriflow_backup.json",
        mime="application/json",
    )

# ── Rodapé ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;color:#374151;font-size:0.75rem;margin-top:3rem;padding:1rem 0;
            border-top:1px solid #1f2535;">
  ⚡ NutriFlow · Todos os dados salvos localmente em <code style="color:#4b5563">nutriflow_data.json</code>
</div>
""", unsafe_allow_html=True)