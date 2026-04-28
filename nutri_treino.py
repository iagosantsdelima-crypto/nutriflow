import streamlit as st
import json
import os
import hashlib
import random
from datetime import date, timedelta
from pathlib import Path
import pandas as pd

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="NutriFlow · Diário Pessoal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Pastas e arquivos ───────────────────────────────────────────────────────
DATA_FILE  = "nutriflow_users.json"
PHOTOS_DIR = Path("nutriflow_fotos")
PHOTOS_DIR.mkdir(exist_ok=True)

# ── Dicas de alimentação ─────────────────────────────────────────────────────
DICAS = [
    ("💧 Hidratação", "Beba pelo menos 35ml de água por kg de peso corporal por dia. A hidratação adequada melhora o metabolismo e reduz a fome."),
    ("🥦 Vegetais no prato", "Encha metade do prato com vegetais coloridos. Eles são ricos em fibras, vitaminas e têm baixa densidade calórica."),
    ("🍗 Proteína em cada refeição", "Inclua proteína magra (frango, peixe, ovo, leguminosas) em todas as refeições para manter a saciedade e preservar a massa muscular."),
    ("🕐 Timing das refeições", "Tente comer a cada 3-4 horas para manter o metabolismo estável e evitar picos de fome que levam a excessos."),
    ("🍚 Carboidratos complexos", "Prefira arroz integral, batata-doce, aveia e quinoa. Eles fornecem energia sustentada e evitam picos de insulina."),
    ("🛌 Sono e peso", "Dormir menos de 7h por noite aumenta os hormônios da fome (grelina) em até 15%. Priorize o descanso!"),
    ("🥑 Gorduras boas", "Abacate, azeite, oleaginosas e peixes gordos contêm gorduras essenciais que regulam hormônios e reduzem inflamação."),
    ("🍽️ Mastigar devagar", "Mastigar bem e comer devagar permite que os sinais de saciedade cheguem ao cérebro, evitando comer em excesso."),
    ("📅 Planejamento semanal", "Planejar as refeições da semana reduz decisões impulsivas e aumenta a aderência à dieta em até 40%."),
    ("🥗 Pré-treino ideal", "Consuma carboidratos de fácil digestão + proteína 1-2h antes do treino para energia e síntese muscular."),
    ("🍌 Pós-treino", "Após o treino, consuma proteína + carboidrato em até 1 hora para maximizar a recuperação e o crescimento muscular."),
    ("🚫 Calorias líquidas", "Sucos, refrigerantes e bebidas alcoólicas têm muitas calorias sem saciedade. Prefira água, chás e café sem açúcar."),
    ("🌾 Fibras diárias", "Consuma 25-35g de fibras por dia. Elas melhoram a digestão, reduzem o colesterol e aumentam a saciedade."),
    ("🧂 Sódio e inchaço", "Excesso de sódio retém água e causa inchaço. Reduza sal e alimentos ultraprocessados para resultados mais visíveis."),
    ("📊 Déficit calórico", "Um déficit de 500 kcal/dia resulta em ~0,5kg de perda de gordura por semana — ritmo saudável e sustentável."),
]

# ── Carregar / salvar dados ─────────────────────────────────────────────────
def load_all_data() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"usuarios": {}}

def save_all_data(all_data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()

def save_photo(uploaded_file, categoria: str, usuario: str, dia_str: str) -> str:
    filename = f"{usuario}_{categoria}_{dia_str}_{uploaded_file.name}"
    filepath = PHOTOS_DIR / filename
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(filepath)

# ── Cálculo de calorias (Mifflin-St Jeor) ───────────────────────────────────
def calcular_tmb(peso, altura, idade, sexo) -> float:
    if sexo == "Masculino":
        return 10 * peso + 6.25 * altura - 5 * idade + 5
    else:
        return 10 * peso + 6.25 * altura - 5 * idade - 161

NIVEL_ATIVIDADE = {
    "Sedentário (sem exercício)":         1.2,
    "Levemente ativo (1-3x/semana)":      1.375,
    "Moderadamente ativo (3-5x/semana)":  1.55,
    "Muito ativo (6-7x/semana)":          1.725,
    "Extremamente ativo (2x/dia)":        1.9,
}

def calcular_meta(perfil: dict, objetivo: str) -> float:
    tmb = calcular_tmb(
        perfil["peso"], perfil["altura"],
        perfil["idade"], perfil["sexo"]
    )
    fator = NIVEL_ATIVIDADE.get(perfil["atividade"], 1.55)
    tdee  = tmb * fator
    if objetivo == "Manutenção":
        return round(tdee)
    elif objetivo == "Perda saudável (-0,5kg/sem)":
        return round(tdee - 500)
    elif objetivo == "Perda agressiva (-1kg/sem)":
        return round(tdee - 1000)
    elif objetivo == "Ganho muscular":
        return round(tdee + 300)
    return round(tdee)

# ── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d0f14 !important;
    color: #e8eaf0 !important;
  }
  header[data-testid="stHeader"] { background: transparent !important; }
  .block-container { padding-top: 2rem !important; max-width: 1140px; }

  .hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem; font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #00e5a0 0%, #00b4d8 60%, #7b5ea7 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; line-height: 1.1; margin-bottom: 0;
  }
  .hero-sub {
    font-size: 0.9rem; color: #6b7280;
    letter-spacing: 0.08em; text-transform: uppercase; margin-top: 0.2rem;
  }
  .card {
    background: #161923; border: 1px solid #1f2535;
    border-radius: 16px; padding: 1.5rem 1.6rem;
    margin-bottom: 1rem; box-shadow: 0 4px 30px rgba(0,0,0,0.4);
  }
  .card-title {
    font-family: 'Syne', sans-serif; font-size: 1.05rem;
    font-weight: 700; color: #e8eaf0; margin-bottom: 1rem;
  }
  .metric-box {
    background: #1a1f2e; border: 1px solid #252d42;
    border-radius: 12px; padding: 1rem 1.2rem; text-align: center;
  }
  .metric-value {
    font-family: 'Syne', sans-serif; font-size: 2rem;
    font-weight: 800; color: #00e5a0; line-height: 1;
  }
  .metric-label {
    font-size: 0.75rem; color: #6b7280;
    text-transform: uppercase; letter-spacing: 0.07em; margin-top: 0.3rem;
  }
  .metric-value.accent-blue   { color: #00b4d8; }
  .metric-value.accent-purple { color: #a78bfa; }

  .food-item {
    display: flex; justify-content: space-between; align-items: center;
    background: #1a1f2e; border-radius: 10px;
    padding: 0.65rem 1rem; margin-bottom: 0.45rem;
    border-left: 3px solid #00e5a0; font-size: 0.88rem;
  }
  .food-name  { font-weight: 500; color: #d1d5db; }
  .food-qty   { color: #6b7280; font-size: 0.78rem; margin-top: 2px; }
  .food-tipo  { font-size: 0.75rem; color: #00b4d8; font-weight: 500; margin-top: 1px; }
  .food-kcal  { font-family: 'Syne', sans-serif; font-weight: 700; color: #00e5a0; font-size: 0.95rem; }

  .treino-item {
    background: #1a1f2e; border-radius: 10px;
    padding: 0.7rem 1rem; margin-bottom: 0.45rem;
    border-left: 3px solid #7b5ea7; font-size: 0.88rem;
    display: flex; justify-content: space-between; align-items: center;
  }
  .treino-hoje  { border-left: 3px solid #00e5a0 !important; background: #1a2e24 !important; }
  .treino-ok    { color: #00e5a0; font-weight: 600; }
  .treino-miss  { color: #6b7280; font-weight: 500; }

  .progress-bar-bg {
    background: #1a1f2e; border-radius: 999px; height: 8px;
    margin-top: 0.4rem; overflow: hidden;
  }
  .progress-bar-fill {
    height: 100%; border-radius: 999px;
    background: linear-gradient(90deg, #00e5a0, #00b4d8);
    transition: width 0.5s ease;
  }

  .dica-popup {
    background: linear-gradient(135deg, #1a2e24 0%, #1a1f2e 100%);
    border: 1px solid #00e5a0; border-radius: 16px;
    padding: 1.2rem 1.5rem; margin-bottom: 1rem;
    box-shadow: 0 0 25px rgba(0,229,160,0.1);
    position: relative;
  }
  .dica-title {
    font-family: 'Syne', sans-serif; font-size: 0.95rem;
    font-weight: 700; color: #00e5a0; margin-bottom: 0.4rem;
  }
  .dica-text { font-size: 0.85rem; color: #9ca3af; line-height: 1.5; }

  .perfil-badge {
    background: #1a1f2e; border: 1px solid #252d42; border-radius: 12px;
    padding: 0.6rem 1.2rem; display: inline-flex; align-items: center;
    gap: 0.5rem; font-size: 0.85rem; color: #9ca3af;
  }
  .objetivo-badge {
    font-family: 'Syne', sans-serif; font-size: 0.75rem; font-weight: 700;
    padding: 0.2rem 0.7rem; border-radius: 999px; margin-left: 0.5rem;
  }
  .obj-manutencao  { background: #1a3a4a; color: #00b4d8; }
  .obj-saudavel    { background: #1a2e1a; color: #00e5a0; }
  .obj-agressiva   { background: #3a1a1a; color: #f87171; }
  .obj-ganho       { background: #2a1a3a; color: #a78bfa; }

  .stTextInput > div > div > input,
  .stNumberInput > div > div > input,
  .stTextArea > div > div > textarea {
    background: #1a1f2e !important; border: 1px solid #252d42 !important;
    border-radius: 10px !important; color: #e8eaf0 !important;
  }
  div[data-baseweb="select"] > div {
    background: #1a1f2e !important; border-color: #252d42 !important; color: #e8eaf0 !important;
  }
  [data-testid="stFileUploader"] {
    background: #1a1f2e !important; border: 1px dashed #252d42 !important;
    border-radius: 12px !important; padding: 0.3rem !important;
  }
  .stButton > button {
    background: linear-gradient(135deg, #00e5a0, #00b4d8) !important;
    color: #0d0f14 !important; font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; border: none !important;
    border-radius: 10px !important; padding: 0.55rem 1.4rem !important;
    font-size: 0.9rem !important; box-shadow: 0 0 20px rgba(0,229,160,0.15) !important;
    transition: opacity 0.2s !important;
  }
  .stButton > button:hover { opacity: 0.85 !important; }
  .btn-danger > button {
    background: linear-gradient(135deg, #7f1d1d, #b91c1c) !important;
    color: #fff !important; box-shadow: 0 0 20px rgba(239,68,68,0.15) !important;
  }
  .btn-secondary > button {
    background: #1a1f2e !important; color: #9ca3af !important;
    border: 1px solid #252d42 !important; box-shadow: none !important;
  }
  .stTabs [data-baseweb="tab-list"] {
    background: #161923 !important; border-radius: 12px !important;
    padding: 4px !important; gap: 4px !important; border: 1px solid #1f2535 !important;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #6b7280 !important;
    font-family: 'Syne', sans-serif !important; font-weight: 600 !important;
    border-radius: 9px !important; border: none !important;
  }
  .stTabs [aria-selected="true"] { background: #1a1f2e !important; color: #00e5a0 !important; }
  hr { border-color: #1f2535 !important; }
  ::-webkit-scrollbar { width: 5px; }
  ::-webkit-scrollbar-track { background: #0d0f14; }
  ::-webkit-scrollbar-thumb { background: #252d42; border-radius: 4px; }

  /* Login page */
  .login-container {
    max-width: 420px; margin: 4rem auto; padding: 2.5rem;
    background: #161923; border: 1px solid #1f2535;
    border-radius: 20px; box-shadow: 0 8px 50px rgba(0,0,0,0.5);
  }
  .login-title {
    font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800;
    text-align: center; margin-bottom: 0.3rem;
    background: linear-gradient(135deg, #00e5a0, #00b4d8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .login-sub { text-align: center; color: #4b5563; font-size: 0.85rem; margin-bottom: 2rem; }

  .objetivo-card {
    background: #1a1f2e; border: 2px solid #252d42;
    border-radius: 12px; padding: 1rem; cursor: pointer;
    transition: border-color 0.2s, background 0.2s; text-align: center;
  }
  .objetivo-card:hover { border-color: #00e5a0; }
  .objetivo-card.selected { border-color: #00e5a0; background: #1a2e24; }
</style>
""", unsafe_allow_html=True)

# ── Estado global ───────────────────────────────────────────────────────────
if "all_data"         not in st.session_state: st.session_state.all_data = load_all_data()
if "usuario_logado"   not in st.session_state: st.session_state.usuario_logado = None
if "pagina_auth"      not in st.session_state: st.session_state.pagina_auth = "login"
if "dica_idx"         not in st.session_state: st.session_state.dica_idx = random.randint(0, len(DICAS)-1)
if "editar_treino"    not in st.session_state: st.session_state.editar_treino = None
if "mostrar_dica"     not in st.session_state: st.session_state.mostrar_dica = True

all_data = st.session_state.all_data

def get_user_data(username: str) -> dict:
    return all_data["usuarios"][username]

def save():
    save_all_data(all_data)

# ════════════════════════════════════════════════════════════════════════════
# TELA DE LOGIN / CADASTRO
# ════════════════════════════════════════════════════════════════════════════
if not st.session_state.usuario_logado:

    st.markdown('<div class="login-title">⚡ NutriFlow</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">Diário pessoal de nutrição & treinos</div>', unsafe_allow_html=True)

    if st.session_state.pagina_auth == "login":
        st.markdown("<br>", unsafe_allow_html=True)
        col_c, col_l, col_r = st.columns([1, 2, 1])
        with col_l:
            st.markdown("### Entrar na conta")
            username = st.text_input("Usuário", key="login_user")
            senha    = st.text_input("Senha", type="password", key="login_pass")

            if st.button("Entrar →", use_container_width=True):
                users = all_data["usuarios"]
                if username in users and users[username]["senha"] == hash_senha(senha):
                    st.session_state.usuario_logado = username
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div style="text-align:center;color:#4b5563;font-size:0.85rem;">Não tem conta?</div>', unsafe_allow_html=True)
            if st.button("Criar conta gratuita", use_container_width=True):
                st.session_state.pagina_auth = "cadastro"
                st.rerun()

    elif st.session_state.pagina_auth == "cadastro":
        col_c, col_l, col_r = st.columns([1, 2.5, 1])
        with col_l:
            st.markdown("### Criar nova conta")
            st.markdown("**Dados de acesso**")
            novo_user = st.text_input("Nome de usuário (sem espaços)", key="cad_user")
            novo_nome = st.text_input("Nome completo", key="cad_nome")
            nova_senha = st.text_input("Senha", type="password", key="cad_pass")
            conf_senha = st.text_input("Confirmar senha", type="password", key="cad_conf")

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("**Dados para cálculo calórico**")

            col_a, col_b = st.columns(2)
            with col_a:
                sexo  = st.selectbox("Sexo biológico", ["Masculino", "Feminino"])
                idade = st.number_input("Idade (anos)", min_value=10, max_value=99, value=25)
            with col_b:
                peso   = st.number_input("Peso (kg)", min_value=30.0, max_value=300.0, value=70.0, step=0.5)
                altura = st.number_input("Altura (cm)", min_value=100, max_value=250, value=170)

            atividade = st.selectbox("Nível de atividade física", list(NIVEL_ATIVIDADE.keys()))

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**Objetivo**")
            objetivo = st.radio(
                "Selecione seu objetivo",
                ["Manutenção", "Perda saudável (-0,5kg/sem)", "Perda agressiva (-1kg/sem)", "Ganho muscular"],
                horizontal=True
            )

            # Preview da meta
            if peso and altura and idade:
                perfil_preview = {"peso": peso, "altura": altura, "idade": idade, "sexo": sexo, "atividade": atividade}
                meta_preview   = calcular_meta(perfil_preview, objetivo)
                cor_obj = {"Manutenção": "#00b4d8", "Perda saudável (-0,5kg/sem)": "#00e5a0",
                           "Perda agressiva (-1kg/sem)": "#f87171", "Ganho muscular": "#a78bfa"}
                st.markdown(f"""
                <div style="background:#1a1f2e;border-radius:12px;padding:1rem;text-align:center;margin:0.8rem 0;border:1px solid #252d42">
                  <div style="font-size:0.75rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.07em">Meta calórica estimada</div>
                  <div style="font-family:Syne,sans-serif;font-size:2.2rem;font-weight:800;color:{cor_obj.get(objetivo,'#00e5a0')}">{meta_preview} kcal</div>
                  <div style="font-size:0.78rem;color:#6b7280">{objetivo}</div>
                </div>""", unsafe_allow_html=True)

            if st.button("Criar conta →", use_container_width=True):
                if not novo_user or not novo_nome or not nova_senha:
                    st.error("Preencha todos os campos obrigatórios.")
                elif " " in novo_user:
                    st.error("O nome de usuário não pode conter espaços.")
                elif nova_senha != conf_senha:
                    st.error("As senhas não coincidem.")
                elif novo_user in all_data["usuarios"]:
                    st.error("Este nome de usuário já existe.")
                else:
                    perfil = {"peso": peso, "altura": altura, "idade": idade,
                              "sexo": sexo, "atividade": atividade}
                    meta   = calcular_meta(perfil, objetivo)
                    all_data["usuarios"][novo_user] = {
                        "senha":        hash_senha(nova_senha),
                        "nome":         novo_nome,
                        "perfil":       perfil,
                        "objetivo":     objetivo,
                        "meta_calorias": meta,
                        "alimentacao":  {},
                        "treinos":      {},
                    }
                    save()
                    st.success(f"Conta criada! Sua meta é {meta} kcal/dia.")
                    st.session_state.pagina_auth = "login"
                    st.rerun()

            if st.button("← Voltar ao login", use_container_width=True):
                st.session_state.pagina_auth = "login"
                st.rerun()

    st.stop()

# ════════════════════════════════════════════════════════════════════════════
# APP PRINCIPAL (usuário logado)
# ════════════════════════════════════════════════════════════════════════════
uname     = st.session_state.usuario_logado
udata     = get_user_data(uname)
today_str = str(date.today())

META_CALORIAS = udata.get("meta_calorias", 2000)

udata["alimentacao"].setdefault(today_str, [])
udata["treinos"].setdefault(today_str, {"descricao": "", "concluido": False, "notas": "", "foto": ""})

def total_kcal_dia(dia_str: str) -> float:
    return sum(r["calorias"] for r in udata["alimentacao"].get(dia_str, []))

def media_semanal() -> float:
    hoje   = date.today()
    dias   = [(hoje - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
    totais = [total_kcal_dia(d) for d in dias if d in udata["alimentacao"]]
    return round(sum(totais) / len(totais), 1) if totais else 0.0

# ── Cabeçalho ──────────────────────────────────────────────────────────────
col_h1, col_h2, col_h3 = st.columns([3, 1, 1])
with col_h1:
    st.markdown('<div class="hero-title">⚡ NutriFlow</div>', unsafe_allow_html=True)
    objetivo_atual = udata.get("objetivo", "Manutenção")
    cor_obj_map = {
        "Manutenção":                   ("obj-manutencao",  "💎"),
        "Perda saudável (-0,5kg/sem)":  ("obj-saudavel",   "🎯"),
        "Perda agressiva (-1kg/sem)":   ("obj-agressiva",  "🔥"),
        "Ganho muscular":               ("obj-ganho",      "💪"),
    }
    cls_obj, ico_obj = cor_obj_map.get(objetivo_atual, ("obj-manutencao", "⚡"))
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.5rem;margin-top:0.3rem;">
      <span style="color:#6b7280;font-size:0.82rem;">Olá, <strong style="color:#d1d5db">{udata['nome']}</strong></span>
      <span class="objetivo-badge {cls_obj}">{ico_obj} {objetivo_atual}</span>
    </div>""", unsafe_allow_html=True)

with col_h2:
    selected_date = st.date_input("Data", value=date.today(), label_visibility="collapsed")
    selected_str  = str(selected_date)

with col_h3:
    if st.button("Sair →"):
        st.session_state.usuario_logado = None
        st.rerun()

udata["alimentacao"].setdefault(selected_str, [])
udata["treinos"].setdefault(selected_str, {"descricao": "", "concluido": False, "notas": "", "foto": ""})

st.markdown("<br>", unsafe_allow_html=True)

# ── Dica do dia (popup) ─────────────────────────────────────────────────────
if st.session_state.mostrar_dica:
    dica_titulo, dica_texto = DICAS[st.session_state.dica_idx]
    col_dica, col_btn_dica = st.columns([8, 1])
    with col_dica:
        st.markdown(f"""
        <div class="dica-popup">
          <div class="dica-title">💡 Dica do dia · {dica_titulo}</div>
          <div class="dica-text">{dica_texto}</div>
        </div>""", unsafe_allow_html=True)
    with col_btn_dica:
        st.markdown("<br>", unsafe_allow_html=True)
        col_f, col_n = st.columns(2)
        with col_f:
            if st.button("✕", help="Fechar dica"):
                st.session_state.mostrar_dica = False
                st.rerun()
        with col_n:
            if st.button("▶", help="Próxima dica"):
                st.session_state.dica_idx = (st.session_state.dica_idx + 1) % len(DICAS)
                st.rerun()
else:
    if st.button("💡 Ver dica de alimentação"):
        st.session_state.mostrar_dica = True
        st.session_state.dica_idx = random.randint(0, len(DICAS)-1)
        st.rerun()

# ── Métricas ────────────────────────────────────────────────────────────────
kcal_hoje = total_kcal_dia(selected_str)
kcal_med  = media_semanal()
pct_meta  = min(kcal_hoje / META_CALORIAS * 100, 100) if META_CALORIAS > 0 else 0
treinos_7d = sum(
    1 for i in range(7)
    if udata["treinos"].get((date.today() - timedelta(days=i)).isoformat(), {}).get("concluido")
)
cor = "#00e5a0" if pct_meta < 90 else ("#f59e0b" if pct_meta < 110 else "#f87171")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-box"><div class="metric-value">{kcal_hoje:.0f}</div><div class="metric-label">kcal hoje</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-box"><div class="metric-value accent-blue">{kcal_med}</div><div class="metric-label">média kcal / semana</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-box"><div class="metric-value accent-purple">{treinos_7d}/7</div><div class="metric-label">treinos na semana</div></div>', unsafe_allow_html=True)
with c4:
    restante = max(0, META_CALORIAS - kcal_hoje)
    st.markdown(f'<div class="metric-box"><div class="metric-value" style="color:{cor}">{pct_meta:.0f}%</div><div class="metric-label">meta · {restante:.0f} kcal restam</div></div>', unsafe_allow_html=True)

st.markdown(f"""
<div style="margin:1rem 0 0.3rem;">
  <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:#6b7280;margin-bottom:0.3rem;">
    <span>Progresso calórico — {kcal_hoje:.0f} / {META_CALORIAS} kcal</span>
    <span>{objetivo_atual}</span>
  </div>
  <div class="progress-bar-bg">
    <div class="progress-bar-fill" style="width:{pct_meta}%;background:{cor};"></div>
  </div>
</div>
<br>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs(["🥗  Alimentação", "🏋️  Treino", "📊  Histórico", "⚙️  Perfil"])

# ── TAB 1 — ALIMENTAÇÃO ─────────────────────────────────────────────────────
with tab1:
    col_form, col_lista = st.columns([1, 1.3], gap="large")

    with col_form:
        st.markdown('<div class="card"><div class="card-title">➕ Registrar refeição</div>', unsafe_allow_html=True)

        tipo_refeicao = st.selectbox(
            "Tipo de refeição",
            ["☀️ Café da manhã", "🍎 Lanche da manhã", "🍽️ Almoço",
             "🍪 Lanche da tarde", "🌙 Jantar", "🌛 Ceia"]
        )
        alimento   = st.text_input("Alimento / prato", placeholder="Ex: Arroz integral cozido")
        col_q, col_u = st.columns([2, 1])
        with col_q:
            quantidade = st.number_input("Quantidade", min_value=0.0, step=10.0, value=100.0)
        with col_u:
            unidade = st.selectbox("Unidade", ["g", "ml", "unid", "colher", "xícara"])
        calorias = st.number_input("Calorias (kcal)", min_value=0.0, step=1.0, value=0.0)

        st.markdown('<div style="font-size:0.82rem;color:#6b7280;margin:0.6rem 0 0.2rem;">📷 Foto da refeição (opcional)</div>', unsafe_allow_html=True)
        foto_refeicao = st.file_uploader(
            "foto_ref", type=["jpg","jpeg","png","webp"],
            label_visibility="collapsed", key="upload_refeicao"
        )
        if foto_refeicao:
            st.image(foto_refeicao, use_container_width=True)

        if st.button("Adicionar ✓", use_container_width=True):
            if alimento.strip():
                foto_path = ""
                if foto_refeicao:
                    foto_path = save_photo(foto_refeicao, "refeicao", uname, selected_str)
                udata["alimentacao"][selected_str].append({
                    "alimento": alimento.strip(), "tipo": tipo_refeicao,
                    "quantidade": quantidade, "unidade": unidade,
                    "calorias": calorias, "foto": foto_path,
                })
                save()
                st.success("Refeição registrada!", icon="✅")
                st.rerun()
            else:
                st.warning("Informe o nome do alimento.")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-title">📖 Referência rápida</div>', unsafe_allow_html=True)
        for nome, kcal in {
            "Arroz branco cozido (100g)": 130,
            "Frango grelhado (100g)":     165,
            "Ovo inteiro (1 unid)":        78,
            "Batata-doce cozida (100g)":   86,
            "Aveia (40g)":                148,
            "Whey protein (30g)":         120,
        }.items():
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:0.3rem 0;
                        border-bottom:1px solid #1f2535;font-size:0.82rem;">
              <span style="color:#9ca3af">{nome}</span>
              <span style="color:#00e5a0;font-weight:600">{kcal} kcal</span>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_lista:
        refeicoes = udata["alimentacao"].get(selected_str, [])
        st.markdown(
            f'<div class="card-title">🗓️ {selected_date.strftime("%d/%m/%Y")} — '
            f'{len(refeicoes)} item(ns) · {total_kcal_dia(selected_str):.0f} kcal</div>',
            unsafe_allow_html=True
        )

        if not refeicoes:
            st.markdown('<div style="color:#4b5563;text-align:center;padding:3rem 0;font-size:0.9rem;">Nenhum registro para este dia.</div>', unsafe_allow_html=True)
        else:
            for i, r in enumerate(refeicoes):
                col_item, col_del = st.columns([7, 1])
                with col_item:
                    st.markdown(f"""
                    <div class="food-item">
                      <div>
                        <div class="food-tipo">{r.get('tipo','')}</div>
                        <div class="food-name">{r['alimento']}</div>
                        <div class="food-qty">{r['quantidade']} {r['unidade']}</div>
                      </div>
                      <div class="food-kcal">{r['calorias']:.0f} kcal</div>
                    </div>""", unsafe_allow_html=True)
                    foto_p = r.get("foto","")
                    if foto_p and os.path.exists(foto_p):
                        with st.expander("📷 Ver foto"):
                            st.image(foto_p, use_container_width=True)
                with col_del:
                    if st.button("🗑️", key=f"del_food_{i}_{selected_str}_{uname}"):
                        udata["alimentacao"][selected_str].pop(i)
                        save()
                        st.rerun()

            st.markdown("<hr>", unsafe_allow_html=True)
            restante_kcal = META_CALORIAS - total_kcal_dia(selected_str)
            cor_r = "#00e5a0" if restante_kcal >= 0 else "#f87171"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;padding:0.5rem 0;">
              <span style="color:#6b7280;font-size:0.85rem">Total do dia</span>
              <span style="font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800;color:#00e5a0">
                {total_kcal_dia(selected_str):.0f} kcal
              </span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding:0.2rem 0;">
              <span style="color:#6b7280;font-size:0.82rem">Saldo em relação à meta</span>
              <span style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:{cor_r}">
                {"+" if restante_kcal < 0 else ""}{-restante_kcal:.0f} {"acima" if restante_kcal < 0 else "abaixo"} da meta
              </span>
            </div>""", unsafe_allow_html=True)

# ── TAB 2 — TREINO ──────────────────────────────────────────────────────────
with tab2:
    col_tf, col_tl = st.columns([1, 1.2], gap="large")
    treino_dia = udata["treinos"][selected_str]

    # ── Modal de edição de treino ──────────────────────────────────────────
    if st.session_state.editar_treino is not None:
        d_edit     = st.session_state.editar_treino
        t_edit     = udata["treinos"].get(d_edit, {"descricao":"","concluido":False,"notas":"","foto":""})
        grupos_ed  = ["— Selecione —","Peito e Tríceps","Costas e Bíceps","Ombros",
                      "Pernas (Quadríceps)","Pernas (Posterior/Glúteos)","Full Body",
                      "HIIT / Cardio","Funcional","Mobilidade / Alongamento","Descanso","Outro"]

        st.markdown(f"""
        <div style="background:#161923;border:1px solid #00e5a0;border-radius:16px;padding:1.5rem;margin-bottom:1.5rem;">
          <div style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:#00e5a0;margin-bottom:1rem;">
            ✏️ Editando treino de {d_edit}
          </div>
        </div>""", unsafe_allow_html=True)

        idx_ed = grupos_ed.index(t_edit.get("descricao","")) if t_edit.get("descricao","") in grupos_ed else 0
        desc_ed  = st.selectbox("Grupo muscular / tipo", grupos_ed, index=idx_ed, key="edit_desc")
        notas_ed = st.text_area("Observações / exercícios", value=t_edit.get("notas",""), height=100, key="edit_notas")
        conc_ed  = st.checkbox("✅ Treino concluído", value=t_edit.get("concluido", False), key="edit_conc")

        col_sv, col_cn = st.columns(2)
        with col_sv:
            if st.button("💾 Salvar edição", use_container_width=True):
                udata["treinos"][d_edit] = {
                    "descricao": desc_ed if desc_ed != "— Selecione —" else "",
                    "notas":     notas_ed,
                    "concluido": conc_ed,
                    "foto":      t_edit.get("foto",""),
                }
                save()
                st.session_state.editar_treino = None
                st.success("Treino atualizado!")
                st.rerun()
        with col_cn:
            if st.button("✕ Cancelar", use_container_width=True):
                st.session_state.editar_treino = None
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

    with col_tf:
        st.markdown('<div class="card"><div class="card-title">🏋️ Registrar treino</div>', unsafe_allow_html=True)

        grupos = ["— Selecione —","Peito e Tríceps","Costas e Bíceps","Ombros",
                  "Pernas (Quadríceps)","Pernas (Posterior/Glúteos)","Full Body",
                  "HIIT / Cardio","Funcional","Mobilidade / Alongamento","Descanso","Outro"]
        idx       = grupos.index(treino_dia["descricao"]) if treino_dia.get("descricao") in grupos else 0
        descricao = st.selectbox("Grupo muscular / tipo", grupos, index=idx)
        notas     = st.text_area(
            "Observações / exercícios realizados",
            value=treino_dia.get("notas",""),
            placeholder="Ex: Supino 4x10 80kg, Crucifixo 3x12…",
            height=130
        )
        concluido = st.checkbox("✅ Treino concluído", value=treino_dia.get("concluido", False))

        st.markdown('<div style="font-size:0.82rem;color:#6b7280;margin:0.6rem 0 0.2rem;">📷 Foto do treino (opcional)</div>', unsafe_allow_html=True)
        foto_treino = st.file_uploader(
            "foto_tr", type=["jpg","jpeg","png","webp"],
            label_visibility="collapsed", key="upload_treino"
        )
        if foto_treino:
            st.image(foto_treino, use_container_width=True)
        elif treino_dia.get("foto") and os.path.exists(treino_dia.get("foto","")):
            st.markdown('<div style="font-size:0.78rem;color:#6b7280;margin-bottom:0.3rem;">Foto salva:</div>', unsafe_allow_html=True)
            st.image(treino_dia["foto"], use_container_width=True)

        if st.button("Salvar treino", use_container_width=True):
            foto_path = treino_dia.get("foto","")
            if foto_treino:
                foto_path = save_photo(foto_treino, "treino", uname, selected_str)
            udata["treinos"][selected_str] = {
                "descricao": descricao if descricao != "— Selecione —" else "",
                "notas":     notas,
                "concluido": concluido,
                "foto":      foto_path,
            }
            save()
            st.success("Treino salvo!", icon="💪")
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with col_tl:
        st.markdown('<div class="card-title">📅 Próximos 30 dias — planejamento</div>', unsafe_allow_html=True)

        hoje = date.today()
        semanas_pt = ["Seg","Ter","Qua","Qui","Sex","Sáb","Dom"]

        for i in range(30):
            d     = hoje + timedelta(days=i)
            d_str = d.isoformat()
            udata["treinos"].setdefault(d_str, {"descricao":"","concluido":False,"notas":"","foto":""})

            t        = udata["treinos"][d_str]
            desc     = t.get("descricao") or "—"
            ok       = t.get("concluido", False)
            tem_foto = t.get("foto") and os.path.exists(t.get("foto",""))
            semana   = semanas_pt[d.weekday()]

            if i == 0:   dia_l = "Hoje";  cls_card = "treino-hoje"
            elif i == 1: dia_l = "Amanhã"; cls_card = ""
            else:        dia_l = d.strftime("%d/%m"); cls_card = ""

            if ok:               label = "✓ Concluído"; cls_label = "treino-ok"
            elif t.get("descricao"): label = "· Planejado"; cls_label = "treino-miss"
            else:                label = "· Vazio";      cls_label = "treino-miss"

            foto_icon = " 📷" if tem_foto else ""

            col_card, col_edit_btn = st.columns([5, 1])
            with col_card:
                st.markdown(f"""
                <div class="treino-item {cls_card}">
                  <div>
                    <div style="font-size:0.78rem;color:#6b7280">{dia_l} · {semana}</div>
                    <div style="color:#d1d5db;font-weight:500;font-size:0.88rem">{desc}{foto_icon}</div>
                  </div>
                  <span class="{cls_label}">{label}</span>
                </div>""", unsafe_allow_html=True)
            with col_edit_btn:
                if st.button("✏️", key=f"edit_btn_{d_str}", help=f"Editar treino de {d_str}"):
                    st.session_state.editar_treino = d_str
                    st.rerun()

# ── TAB 3 — HISTÓRICO ───────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="card-title">📊 Histórico calórico — últimos 30 dias</div>', unsafe_allow_html=True)

    hoje    = date.today()
    dias_30 = [(hoje - timedelta(days=i)).isoformat() for i in range(29,-1,-1)]
    labels  = [(hoje - timedelta(days=i)).strftime("%d/%m") for i in range(29,-1,-1)]
    kcal_30 = [total_kcal_dia(d) for d in dias_30]
    meta_line = [META_CALORIAS] * 30

    df_chart = pd.DataFrame({"Kcal consumidas": kcal_30, "Meta": meta_line}, index=labels)
    st.line_chart(df_chart, height=260, color=["#00e5a0","#f87171"])

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="card-title">📋 Resumo diário detalhado</div>', unsafe_allow_html=True)

    rows = []
    for d_str in reversed(dias_30):
        kcal = total_kcal_dia(d_str)
        t    = udata["treinos"].get(d_str, {})
        if kcal == 0 and not t.get("descricao"):
            continue
        saldo = kcal - META_CALORIAS
        rows.append({
            "Data":      d_str,
            "Kcal":      f"{kcal:.0f}",
            "Meta":      str(META_CALORIAS),
            "Saldo":     f"{'+'if saldo>0 else ''}{saldo:.0f}",
            "Refeições": len(udata["alimentacao"].get(d_str,[])),
            "Treino":    t.get("descricao") or "—",
            "Concluído": "✓" if t.get("concluido") else "✗",
        })

    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.markdown('<div style="color:#4b5563;text-align:center;padding:2rem;">Sem dados nos últimos 30 dias.</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="card-title">🖼️ Galeria de fotos</div>', unsafe_allow_html=True)

    fotos = sorted([f for f in PHOTOS_DIR.glob(f"{uname}_*.*")], reverse=True)
    if fotos:
        cols_g = st.columns(4)
        for idx, fp in enumerate(fotos):
            with cols_g[idx % 4]:
                st.image(str(fp), use_container_width=True, caption=fp.stem[:22])
    else:
        st.markdown('<div style="color:#4b5563;text-align:center;padding:1.5rem;font-size:0.88rem;">Nenhuma foto registrada ainda.</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    export_data = {"alimentacao": udata["alimentacao"], "treinos": udata["treinos"]}
    st.download_button(
        label="⬇️ Exportar meus dados (JSON)",
        data=json.dumps(export_data, ensure_ascii=False, indent=2),
        file_name=f"nutriflow_{uname}_backup.json",
        mime="application/json",
    )

# ── TAB 4 — PERFIL ──────────────────────────────────────────────────────────
with tab4:
    col_p1, col_p2 = st.columns([1, 1], gap="large")

    with col_p1:
        st.markdown('<div class="card"><div class="card-title">👤 Dados pessoais & meta</div>', unsafe_allow_html=True)

        perfil = udata.get("perfil", {})
        nome_ed    = st.text_input("Nome completo", value=udata.get("nome",""))
        col_pa, col_pb = st.columns(2)
        with col_pa:
            sexo_ed  = st.selectbox("Sexo biológico", ["Masculino","Feminino"],
                                     index=0 if perfil.get("sexo","Masculino")=="Masculino" else 1)
            idade_ed = st.number_input("Idade (anos)", min_value=10, max_value=99,
                                        value=int(perfil.get("idade",25)))
        with col_pb:
            peso_ed   = st.number_input("Peso (kg)", min_value=30.0, max_value=300.0,
                                         value=float(perfil.get("peso",70.0)), step=0.5)
            altura_ed = st.number_input("Altura (cm)", min_value=100, max_value=250,
                                         value=int(perfil.get("altura",170)))

        ativ_idx = list(NIVEL_ATIVIDADE.keys()).index(perfil.get("atividade", list(NIVEL_ATIVIDADE.keys())[0]))
        ativ_ed  = st.selectbox("Nível de atividade", list(NIVEL_ATIVIDADE.keys()), index=ativ_idx)

        obj_opcoes = ["Manutenção","Perda saudável (-0,5kg/sem)","Perda agressiva (-1kg/sem)","Ganho muscular"]
        obj_idx    = obj_opcoes.index(udata.get("objetivo","Manutenção")) if udata.get("objetivo") in obj_opcoes else 0
        obj_ed     = st.radio("Objetivo", obj_opcoes, index=obj_idx, horizontal=True)

        # Preview da nova meta
        perfil_prev = {"peso": peso_ed, "altura": altura_ed, "idade": idade_ed, "sexo": sexo_ed, "atividade": ativ_ed}
        nova_meta   = calcular_meta(perfil_prev, obj_ed)
        tmb_calc    = calcular_tmb(peso_ed, altura_ed, idade_ed, sexo_ed)
        tdee_calc   = tmb_calc * NIVEL_ATIVIDADE[ativ_ed]

        st.markdown(f"""
        <div style="background:#1a1f2e;border-radius:12px;padding:1rem;margin:0.8rem 0;border:1px solid #252d42;">
          <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;">
            <div style="text-align:center;flex:1;">
              <div style="font-size:0.7rem;color:#6b7280;text-transform:uppercase">TMB</div>
              <div style="font-family:Syne,sans-serif;font-size:1.2rem;font-weight:700;color:#a78bfa">{tmb_calc:.0f}</div>
            </div>
            <div style="text-align:center;flex:1;">
              <div style="font-size:0.7rem;color:#6b7280;text-transform:uppercase">TDEE</div>
              <div style="font-family:Syne,sans-serif;font-size:1.2rem;font-weight:700;color:#00b4d8">{tdee_calc:.0f}</div>
            </div>
            <div style="text-align:center;flex:1;">
              <div style="font-size:0.7rem;color:#6b7280;text-transform:uppercase">Nova meta</div>
              <div style="font-family:Syne,sans-serif;font-size:1.2rem;font-weight:700;color:#00e5a0">{nova_meta}</div>
            </div>
          </div>
          <div style="font-size:0.72rem;color:#4b5563;text-align:center">
            TMB = metabolismo basal · TDEE = gasto total com atividade
          </div>
        </div>""", unsafe_allow_html=True)

        if st.button("💾 Salvar alterações", use_container_width=True):
            udata["nome"]         = nome_ed
            udata["objetivo"]     = obj_ed
            udata["meta_calorias"] = nova_meta
            udata["perfil"]       = {"peso": peso_ed, "altura": altura_ed,
                                      "idade": idade_ed, "sexo": sexo_ed, "atividade": ativ_ed}
            save()
            st.success(f"Perfil atualizado! Nova meta: {nova_meta} kcal/dia", icon="✅")
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with col_p2:
        st.markdown('<div class="card"><div class="card-title">🔑 Alterar senha</div>', unsafe_allow_html=True)
        senha_atual  = st.text_input("Senha atual", type="password", key="s_atual")
        senha_nova   = st.text_input("Nova senha", type="password", key="s_nova")
        senha_conf   = st.text_input("Confirmar nova senha", type="password", key="s_conf")

        if st.button("Alterar senha", use_container_width=True):
            if udata["senha"] != hash_senha(senha_atual):
                st.error("Senha atual incorreta.")
            elif senha_nova != senha_conf:
                st.error("As senhas não coincidem.")
            elif len(senha_nova) < 4:
                st.error("A nova senha deve ter pelo menos 4 caracteres.")
            else:
                udata["senha"] = hash_senha(senha_nova)
                save()
                st.success("Senha alterada com sucesso!")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-title">📊 Resumo do perfil atual</div>', unsafe_allow_html=True)
        p = udata.get("perfil",{})
        imc = p.get("peso",70) / ((p.get("altura",170)/100)**2)
        if imc < 18.5:    class_imc, cor_imc = "Abaixo do peso", "#00b4d8"
        elif imc < 25:    class_imc, cor_imc = "Peso normal", "#00e5a0"
        elif imc < 30:    class_imc, cor_imc = "Sobrepeso", "#f59e0b"
        else:             class_imc, cor_imc = "Obesidade", "#f87171"

        for label, val in [
            ("Usuário",    f"@{uname}"),
            ("IMC",        f"{imc:.1f} — {class_imc}"),
            ("Meta atual", f"{udata.get('meta_calorias','—')} kcal/dia"),
            ("Objetivo",   udata.get("objetivo","—")),
            ("Atividade",  p.get("atividade","—")),
        ]:
            cor_v = cor_imc if label == "IMC" else "#d1d5db"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:0.4rem 0;
                        border-bottom:1px solid #1f2535;font-size:0.84rem;">
              <span style="color:#6b7280">{label}</span>
              <span style="color:{cor_v};font-weight:500">{val}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ── Rodapé ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;color:#374151;font-size:0.75rem;
            margin-top:3rem;padding:1rem 0;border-top:1px solid #1f2535;">
  ⚡ NutriFlow · Logado como <code style="color:#4b5563">@{uname}</code>
  · Dados em <code style="color:#4b5563">{DATA_FILE}</code>
</div>
""", unsafe_allow_html=True)