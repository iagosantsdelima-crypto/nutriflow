import streamlit as st
import json, os, hashlib, random
from datetime import date, timedelta
from pathlib import Path
import pandas as pd

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="NutriFlow",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_FILE  = "nutriflow_users.json"
PHOTOS_DIR = Path("nutriflow_fotos")
PHOTOS_DIR.mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# BANCO DE ALIMENTOS
# ══════════════════════════════════════════════════════════════════════════════
BANCO_ALIMENTOS = {
    "Arroz branco cozido":    {"kcal_100g": 130,  "unidade": "g",    "emoji": "🍚", "proteina": 2.7, "carbo": 28.0, "gordura": 0.3},
    "Arroz integral cozido":  {"kcal_100g": 124,  "unidade": "g",    "emoji": "🍚", "proteina": 2.6, "carbo": 26.0, "gordura": 1.0},
    "Macarrao cozido":        {"kcal_100g": 158,  "unidade": "g",    "emoji": "🍝", "proteina": 5.8, "carbo": 30.9, "gordura": 0.9},
    "Batata-doce cozida":     {"kcal_100g": 86,   "unidade": "g",    "emoji": "🍠", "proteina": 1.6, "carbo": 20.1, "gordura": 0.1},
    "Batata inglesa cozida":  {"kcal_100g": 77,   "unidade": "g",    "emoji": "🥔", "proteina": 2.0, "carbo": 17.0, "gordura": 0.1},
    "Pao integral":           {"kcal_100g": 247,  "unidade": "g",    "emoji": "🍞", "proteina": 9.0, "carbo": 44.0, "gordura": 3.4},
    "Aveia em flocos":        {"kcal_100g": 370,  "unidade": "g",    "emoji": "🥣", "proteina": 13.9,"carbo": 66.6, "gordura": 7.0},
    "Tapioca":                {"kcal_100g": 323,  "unidade": "g",    "emoji": "🫓", "proteina": 0.2, "carbo": 80.0, "gordura": 0.2},
    "Mandioca cozida":        {"kcal_100g": 125,  "unidade": "g",    "emoji": "🌿", "proteina": 1.0, "carbo": 30.1, "gordura": 0.3},
    "Frango grelhado peito":  {"kcal_100g": 165,  "unidade": "g",    "emoji": "🍗", "proteina": 31.0,"carbo": 0.0,  "gordura": 3.6},
    "Carne bovina grelhada":  {"kcal_100g": 215,  "unidade": "g",    "emoji": "🥩", "proteina": 26.0,"carbo": 0.0,  "gordura": 12.0},
    "Ovo inteiro":            {"kcal_100g": 155,  "unidade": "unid", "emoji": "🥚", "kcal_unid": 78, "proteina": 6.3, "carbo": 0.6, "gordura": 5.3},
    "Clara de ovo":           {"kcal_100g": 52,   "unidade": "unid", "emoji": "🥚", "kcal_unid": 17, "proteina": 3.6, "carbo": 0.2, "gordura": 0.0},
    "Atum em lata":           {"kcal_100g": 116,  "unidade": "g",    "emoji": "🐟", "proteina": 25.5,"carbo": 0.0,  "gordura": 1.0},
    "Salmao grelhado":        {"kcal_100g": 208,  "unidade": "g",    "emoji": "🐟", "proteina": 20.0,"carbo": 0.0,  "gordura": 13.0},
    "Tilapia grelhada":       {"kcal_100g": 128,  "unidade": "g",    "emoji": "🐟", "proteina": 26.0,"carbo": 0.0,  "gordura": 2.7},
    "Whey protein":           {"kcal_100g": 400,  "unidade": "g",    "emoji": "💪", "proteina": 80.0,"carbo": 6.0,  "gordura": 3.0},
    "Feijao cozido":          {"kcal_100g": 76,   "unidade": "g",    "emoji": "🫘", "proteina": 4.8, "carbo": 13.6, "gordura": 0.5},
    "Lentilha cozida":        {"kcal_100g": 116,  "unidade": "g",    "emoji": "🫘", "proteina": 9.0, "carbo": 20.0, "gordura": 0.4},
    "Grao-de-bico cozido":    {"kcal_100g": 164,  "unidade": "g",    "emoji": "🫘", "proteina": 8.9, "carbo": 27.0, "gordura": 2.6},
    "Iogurte grego zero":     {"kcal_100g": 57,   "unidade": "g",    "emoji": "🥛", "proteina": 10.0,"carbo": 3.6,  "gordura": 0.4},
    "Queijo cottage":         {"kcal_100g": 98,   "unidade": "g",    "emoji": "🧀", "proteina": 11.1,"carbo": 3.4,  "gordura": 4.3},
    "Leite desnatado":        {"kcal_100g": 35,   "unidade": "ml",   "emoji": "🥛", "proteina": 3.4, "carbo": 4.8,  "gordura": 0.1},
    "Azeite de oliva":        {"kcal_100g": 884,  "unidade": "ml",   "emoji": "🫒", "proteina": 0.0, "carbo": 0.0,  "gordura": 100.0},
    "Abacate":                {"kcal_100g": 160,  "unidade": "g",    "emoji": "🥑", "proteina": 2.0, "carbo": 9.0,  "gordura": 14.7},
    "Amendoim torrado":       {"kcal_100g": 567,  "unidade": "g",    "emoji": "🥜", "proteina": 25.8,"carbo": 16.1, "gordura": 49.2},
    "Pasta de amendoim":      {"kcal_100g": 588,  "unidade": "g",    "emoji": "🥜", "proteina": 25.0,"carbo": 20.0, "gordura": 50.0},
    "Banana":                 {"kcal_100g": 89,   "unidade": "unid", "emoji": "🍌", "kcal_unid": 105,"proteina": 1.1,"carbo": 23.0, "gordura": 0.3},
    "Maca":                   {"kcal_100g": 52,   "unidade": "unid", "emoji": "🍎", "kcal_unid": 95, "proteina": 0.3,"carbo": 14.0, "gordura": 0.2},
    "Mamao papaia":           {"kcal_100g": 43,   "unidade": "g",    "emoji": "🍈", "proteina": 0.5, "carbo": 10.8, "gordura": 0.3},
    "Laranja":                {"kcal_100g": 47,   "unidade": "unid", "emoji": "🍊", "kcal_unid": 62, "proteina": 0.9,"carbo": 11.8, "gordura": 0.1},
    "Morango":                {"kcal_100g": 32,   "unidade": "g",    "emoji": "🍓", "proteina": 0.7, "carbo": 7.7,  "gordura": 0.3},
    "Brocolis cozido":        {"kcal_100g": 35,   "unidade": "g",    "emoji": "🥦", "proteina": 2.4, "carbo": 6.6,  "gordura": 0.4},
    "Espinafre cozido":       {"kcal_100g": 23,   "unidade": "g",    "emoji": "🥬", "proteina": 3.0, "carbo": 3.6,  "gordura": 0.3},
    "Cenoura cozida":         {"kcal_100g": 41,   "unidade": "g",    "emoji": "🥕", "proteina": 0.9, "carbo": 9.6,  "gordura": 0.2},
    "Tomate":                 {"kcal_100g": 18,   "unidade": "g",    "emoji": "🍅", "proteina": 0.9, "carbo": 3.9,  "gordura": 0.2},
    "Granola":                {"kcal_100g": 471,  "unidade": "g",    "emoji": "🥣", "proteina": 10.0,"carbo": 64.0, "gordura": 20.0},
    "Barra de proteina":      {"kcal_100g": 370,  "unidade": "unid", "emoji": "🍫", "kcal_unid": 200,"proteina": 20.0,"carbo": 25.0,"gordura": 7.0},
}

DICAS = [
    ("💧 Hidratacao", "Beba pelo menos 35ml de agua por kg de peso corporal por dia. A hidratacao adequada melhora o metabolismo e reduz a fome."),
    ("🥦 Vegetais no prato", "Encha metade do prato com vegetais coloridos. Eles sao ricos em fibras, vitaminas e tem baixa densidade calorica."),
    ("🍗 Proteina em cada refeicao", "Inclua proteina magra em todas as refeicoes para manter a saciedade e preservar a massa muscular."),
    ("🕐 Timing das refeicoes", "Tente comer a cada 3-4 horas para manter o metabolismo estavel e evitar picos de fome."),
    ("🍚 Carboidratos complexos", "Prefira arroz integral, batata-doce, aveia e quinoa para energia sustentada."),
    ("🛌 Sono e peso", "Dormir menos de 7h por noite aumenta os hormonios da fome em ate 15%. Priorize o descanso!"),
    ("🥑 Gorduras boas", "Abacate, azeite e oleaginosas contem gorduras essenciais que regulam hormonios."),
    ("📊 Deficit calorico", "Um deficit de 500 kcal/dia resulta em ~0,5kg de perda de gordura por semana."),
    ("🏋️ Treino e metabolismo", "Musculacao aumenta o metabolismo basal permanentemente, mesmo em repouso."),
    ("🍌 Pos-treino", "Apos o treino, proteina + carboidrato em ate 1h maximiza a recuperacao muscular."),
]

TIPOS_REFEICAO = ["☀️ Cafe da manha", "🍎 Lanche da manha", "🍽️ Almoco", "🍪 Lanche da tarde", "🌙 Jantar", "🌛 Ceia"]
GRUPOS_TREINO = ["Selecione", "Peito e Triceps", "Costas e Biceps", "Ombros", "Pernas Quadriceps", "Pernas Posterior/Gluteos", "Full Body", "HIIT / Cardio", "Funcional", "Mobilidade / Alongamento", "Descanso", "Outro"]
NIVEL_ATIVIDADE = {"Sedentario (sem exercicio)":1.2,"Levemente ativo (1-3x/semana)":1.375,"Moderadamente ativo (3-5x/semana)":1.55,"Muito ativo (6-7x/semana)":1.725,"Extremamente ativo (2x/dia)":1.9}

CONQUISTAS = [
    {"id":"primeiro_registro","emoji":"🌟","nome":"Primeira Refeicao","desc":"Registrou sua primeira refeicao","check": lambda ud: any(ud["alimentacao"].values())},
    {"id":"meta_dia","emoji":"🎯","nome":"Meta Batida","desc":"Atingiu a meta calorica pela primeira vez","check": lambda ud: any(sum(r["calorias"] for r in refeicoes) >= ud.get("meta_calorias",2000)*0.95 for refeicoes in ud["alimentacao"].values() if refeicoes)},
    {"id":"streak_3","emoji":"🔥","nome":"Em Chamas","desc":"3 dias seguidos de treino","check": lambda ud: _streak(ud) >= 3},
    {"id":"streak_7","emoji":"💥","nome":"Semana Perfeita","desc":"7 dias seguidos de treino","check": lambda ud: _streak(ud) >= 7},
    {"id":"streak_30","emoji":"🏆","nome":"Maquina","desc":"30 dias seguidos de treino","check": lambda ud: _streak(ud) >= 30},
    {"id":"treino_10","emoji":"💪","nome":"Dedicado","desc":"10 treinos concluidos","check": lambda ud: sum(1 for t in ud["treinos"].values() if t.get("concluido")) >= 10},
    {"id":"treino_50","emoji":"🦾","nome":"Atleta","desc":"50 treinos concluidos","check": lambda ud: sum(1 for t in ud["treinos"].values() if t.get("concluido")) >= 50},
    {"id":"log_7","emoji":"📒","nome":"Consistente","desc":"7 dias com alimentacao registrada","check": lambda ud: len([d for d,v in ud["alimentacao"].items() if v]) >= 7},
]

def _streak(ud):
    hoje = date.today()
    s = 0
    for i in range(365):
        d = (hoje - timedelta(days=i)).isoformat()
        if ud["treinos"].get(d, {}).get("concluido"):
            s += 1
        elif i > 0:
            break
    return s

# ══════════════════════════════════════════════════════════════════════════════
# UTILITÁRIOS
# ══════════════════════════════════════════════════════════════════════════════
def load_all_data() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"usuarios": {}}

def save_all_data(d: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def hash_senha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def save_photo(uf, cat: str, user: str, dia: str) -> str:
    fp = PHOTOS_DIR / f"{user}_{cat}_{dia}_{uf.name}"
    with open(fp, "wb") as f:
        f.write(uf.getbuffer())
    return str(fp)

def calcular_tmb(peso, altura, idade, sexo) -> float:
    if sexo == "Masculino":
        return 10 * peso + 6.25 * altura - 5 * idade + 5
    return 10 * peso + 6.25 * altura - 5 * idade - 161

def calcular_meta(perfil: dict, objetivo: str) -> int:
    tmb  = calcular_tmb(perfil["peso"], perfil["altura"], perfil["idade"], perfil["sexo"])
    tdee = tmb * NIVEL_ATIVIDADE.get(perfil["atividade"], 1.55)
    delta = {"Manutencao": 0, "Perda saudavel (-0,5kg/sem)": -500, "Perda agressiva (-1kg/sem)": -1000, "Ganho muscular": 300}
    return round(tdee + delta.get(objetivo, 0))

def buscar_alimentos(query: str) -> list:
    if not query or len(query) < 2:
        return []
    q = query.lower()
    return [k for k in BANCO_ALIMENTOS if q in k.lower()][:8]

def kcal_estimada(nome: str, qtd: float, unidade: str) -> float:
    info = BANCO_ALIMENTOS.get(nome)
    if not info:
        return 0.0
    if unidade == "unid" and "kcal_unid" in info:
        return round(info["kcal_unid"] * qtd, 1)
    return round(info["kcal_100g"] * qtd / 100, 1)

def macros_estimados(nome: str, qtd: float, unidade: str) -> dict:
    info = BANCO_ALIMENTOS.get(nome)
    if not info:
        return {"proteina": 0, "carbo": 0, "gordura": 0}
    fator = qtd / 100 if unidade != "unid" else (qtd if "kcal_unid" not in info else 1)
    return {
        "proteina": round(info.get("proteina", 0) * fator, 1),
        "carbo":    round(info.get("carbo", 0) * fator, 1),
        "gordura":  round(info.get("gordura", 0) * fator, 1),
    }

def total_kcal_dia(udata, dia_str: str) -> float:
    return sum(r["calorias"] for r in udata["alimentacao"].get(dia_str, []))

def total_macros_dia(udata, dia_str: str) -> dict:
    total = {"proteina": 0.0, "carbo": 0.0, "gordura": 0.0}
    for r in udata["alimentacao"].get(dia_str, []):
        for k in total:
            total[k] += r.get(k, 0.0)
    return {k: round(v, 1) for k, v in total.items()}

def calcular_streak(udata) -> int:
    return _streak(udata)

def gerar_insights(udata, meta: int) -> list:
    """Gera insights automáticos baseados no histórico do usuário"""
    insights = []
    hoje = date.today()

    # Últimos 30 dias de dados
    dias_30 = [(hoje - timedelta(days=i)).isoformat() for i in range(30)]
    kcals_por_dia = {d: total_kcal_dia(udata, d) for d in dias_30}
    dias_com_dados = {d: k for d, k in kcals_por_dia.items() if k > 0}

    if len(dias_com_dados) < 2:
        return [{"emoji": "👋", "txt": "Registre pelo menos 2 dias para ver seus insights personalizados!"}]

    # Média
    media = sum(dias_com_dados.values()) / len(dias_com_dados)
    insights.append({"emoji": "📊", "txt": f"Sua media nos ultimos {len(dias_com_dados)} dias: {media:.0f} kcal/dia"})

    # Tendência
    kcals_list = list(dias_com_dados.values())
    if len(kcals_list) >= 5:
        recente  = sum(kcals_list[:3]) / 3
        anterior = sum(kcals_list[-3:]) / 3
        if recente < anterior * 0.92:
            insights.append({"emoji": "📉", "txt": f"Tendencia de queda: seus ultimos 3 dias estao {anterior - recente:.0f} kcal abaixo da media anterior"})
        elif recente > anterior * 1.08:
            insights.append({"emoji": "📈", "txt": f"Consumo crescendo: ultimos 3 dias em media {recente - anterior:.0f} kcal acima do que antes"})

    # Dias acima/abaixo da meta
    acima = sum(1 for k in dias_com_dados.values() if k > meta * 1.05)
    abaixo = sum(1 for k in dias_com_dados.values() if k < meta * 0.85 and k > 0)
    if acima > len(dias_com_dados) * 0.4:
        insights.append({"emoji": "⚠️", "txt": f"Voce ultrapassa a meta em {acima} dos {len(dias_com_dados)} dias registrados"})
    if abaixo > len(dias_com_dados) * 0.4:
        insights.append({"emoji": "⬇️", "txt": f"Voce fica muito abaixo da meta em {abaixo} dias — risco de deficit excessivo"})

    # Horário favorito de comer
    hora_map = {}
    for refeicoes in udata["alimentacao"].values():
        for r in refeicoes:
            tipo = r.get("tipo", "")
            hora_map[tipo] = hora_map.get(tipo, 0) + r["calorias"]
    if hora_map:
        tipo_top = max(hora_map, key=hora_map.get)
        insights.append({"emoji": "🕐", "txt": f"Sua refeicao mais calórica tende a ser: {tipo_top}"})

    # Projeção de peso
    objetivo = udata.get("objetivo", "")
    if "Perda" in objetivo and len(dias_com_dados) >= 5:
        saldo_medio = media - meta
        # saldo já negativo para perda
        kg_semana = (saldo_medio * 7) / 7700  # 7700 kcal ≈ 1 kg
        if kg_semana < 0:
            insights.append({"emoji": "🎯", "txt": f"Projecao: {abs(kg_semana * 4):.1f} kg em 4 semanas nesse ritmo"})

    # Streak de treinos
    streak = calcular_streak(udata)
    if streak >= 5:
        insights.append({"emoji": "🔥", "txt": f"Incrivel! Voce esta em uma sequencia de {streak} dias de treino!"})
    elif streak == 0:
        treinos_ok = sum(1 for t in udata["treinos"].values() if t.get("concluido"))
        if treinos_ok > 0:
            insights.append({"emoji": "💪", "txt": f"Voce ja fez {treinos_ok} treinos. Mantenha a regularidade para construir uma sequencia!"})

    return insights[:5]

def sugerir_almoco(udata) -> list:
    """Sugere alimentos baseado no histórico"""
    contagem = {}
    for refeicoes in udata["alimentacao"].values():
        for r in refeicoes:
            nm = r.get("alimento", "")
            if nm in BANCO_ALIMENTOS:
                contagem[nm] = contagem.get(nm, 0) + 1
    if not contagem:
        return []
    return sorted(contagem, key=contagem.get, reverse=True)[:5]

def verificar_conquistas(udata) -> list:
    """Retorna conquistas desbloqueadas"""
    unlocked = udata.get("conquistas", [])
    novas = []
    for c in CONQUISTAS:
        if c["id"] not in unlocked:
            try:
                if c["check"](udata):
                    novas.append(c)
                    unlocked.append(c["id"])
            except:
                pass
    if novas:
        udata["conquistas"] = unlocked
    return novas

# ══════════════════════════════════════════════════════════════════════════════
# CSS — CORREÇÃO: Nunca abrir/fechar divs em st.markdown separados
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif;
  background-color: #080b10 !important;
  color: #e2e8f0 !important;
}
header[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding-top: 1.5rem !important; max-width: 1200px; }

.hero-title {
  font-family: 'Syne', sans-serif;
  font-size: 2.2rem; font-weight: 800; letter-spacing: -0.04em;
  background: linear-gradient(135deg, #22d3ee 0%, #06b6d4 40%, #818cf8 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text; line-height: 1.1;
}
.metric-box {
  background: #0f1520; border: 1px solid #1e2a3a;
  border-radius: 16px; padding: 1.1rem 0.8rem; text-align: center;
}
.metric-value { font-family: 'Syne', sans-serif; font-size: 1.9rem; font-weight: 800; line-height: 1; }
.metric-label { font-size: 0.7rem; color: #475569; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.4rem; }
.metric-sub   { font-size: 0.75rem; color: #334155; margin-top: 0.15rem; }

.prog-wrap { margin: 0.8rem 0 1.4rem; }
.prog-label { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 0.5rem; }
.prog-phrase { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; }
.prog-pct { font-size: 0.8rem; color: #475569; }
.prog-bg { background: #1e2a3a; border-radius: 999px; height: 12px; overflow: hidden; }
.prog-fill { height: 100%; border-radius: 999px; transition: width 0.8s ease; }

.food-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.5rem 0.75rem; border-radius: 10px;
  background: #131c2a; margin-bottom: 0.3rem;
  border-left: 3px solid #22d3ee33;
}
.food-row:hover { border-left-color: #22d3ee; }
.food-row-name { font-size: 0.84rem; font-weight: 500; color: #cbd5e1; }
.food-row-qty  { font-size: 0.73rem; color: #334155; }
.food-row-kcal { font-family: 'Syne', sans-serif; font-size: 0.9rem; font-weight: 700; color: #22d3ee; }

.meal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.6rem 0.8rem; border-radius: 10px;
  background: #0f1520; border: 1px solid #1e2a3a;
  margin-bottom: 0.3rem;
}
.meal-title { font-family: 'Syne', sans-serif; font-size: 0.82rem; font-weight: 700; color: #64748b; }
.meal-kcal  { font-family: 'Syne', sans-serif; font-size: 0.82rem; font-weight: 700; color: #22d3ee; }

.treino-item {
  background: #0f1520; border-radius: 11px; padding: 0.7rem 1rem;
  margin-bottom: 0.35rem; border-left: 3px solid #818cf833;
  display: flex; justify-content: space-between; align-items: center;
}

.insight-box {
  background: #0a1428; border: 1px solid #1e3a5f;
  border-radius: 12px; padding: 0.75rem 1rem;
  margin-bottom: 0.5rem; display: flex; gap: 0.6rem; align-items: center;
}
.insight-ico { font-size: 1.2rem; flex-shrink: 0; }
.insight-txt { font-size: 0.82rem; color: #64748b; line-height: 1.5; }

.conquista-box {
  background: linear-gradient(135deg, #1a1000, #2a1a00);
  border: 1px solid #fbbf2444; border-radius: 12px;
  padding: 0.9rem 1rem; display: flex; gap: 0.7rem; align-items: center;
  margin-bottom: 0.5rem;
}
.conquista-emoji { font-size: 1.8rem; flex-shrink: 0; }
.conquista-nome  { font-family: 'Syne', sans-serif; font-size: 0.88rem; font-weight: 700; color: #fbbf24; }
.conquista-desc  { font-size: 0.76rem; color: #78716c; margin-top: 0.1rem; }

.streak-badge {
  display: inline-flex; align-items: center; gap: 0.3rem;
  background: linear-gradient(135deg, #431407, #7c2d12);
  border: 1px solid #9a3412; border-radius: 999px;
  padding: 0.28rem 0.75rem;
  font-family: 'Syne', sans-serif; font-size: 0.78rem; font-weight: 700; color: #fed7aa;
}
.obj-badge {
  display: inline-block; font-family: 'Syne', sans-serif;
  font-size: 0.72rem; font-weight: 700; padding: 0.2rem 0.65rem; border-radius: 999px;
}
.ob-m { background:#0c2a3a; color:#22d3ee; }
.ob-s { background:#0c2a1a; color:#34d399; }
.ob-a { background:#2a0c0c; color:#fb7185; }
.ob-g { background:#1a0c2a; color:#818cf8; }

.dica-box {
  background: #0a1e2a; border: 1px solid #0e7490;
  border-radius: 14px; padding: 0.9rem 1.2rem;
  margin-bottom: 1.2rem; display: flex; gap: 0.8rem; align-items: flex-start;
}
.dica-ico { font-size: 1.5rem; line-height: 1; flex-shrink: 0; }
.dica-ttl { font-family: 'Syne', sans-serif; font-size: 0.87rem; font-weight: 700; color: #22d3ee; margin-bottom: 0.2rem; }
.dica-txt { font-size: 0.8rem; color: #475569; line-height: 1.55; }

.rank-item {
  display: flex; align-items: center; gap: 0.7rem; padding: 0.65rem 0.9rem;
  border-radius: 11px; background: #0f1520; border: 1px solid #1e2a3a; margin-bottom: 0.4rem;
}
.feed-item {
  display: flex; gap: 0.75rem; padding: 0.8rem 0.9rem;
  background: #0f1520; border-radius: 11px; border: 1px solid #1e2a3a; margin-bottom: 0.5rem; align-items: flex-start;
}
.feed-av {
  width: 34px; height: 34px; border-radius: 50%;
  background: linear-gradient(135deg,#22d3ee,#818cf8);
  display: flex; align-items: center; justify-content: center;
  font-family: 'Syne', sans-serif; font-weight: 700; font-size: 0.85rem; color: #080b10; flex-shrink: 0;
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
  background: #0f1520 !important; border: 1px solid #1e2a3a !important;
  border-radius: 10px !important; color: #e2e8f0 !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: #22d3ee !important; box-shadow: 0 0 0 2px rgba(34,211,238,0.1) !important;
}
div[data-baseweb="select"] > div {
  background: #0f1520 !important; border-color: #1e2a3a !important; color: #e2e8f0 !important;
}
[data-testid="stFileUploader"] {
  background: #0f1520 !important; border: 1px dashed #1e2a3a !important; border-radius: 12px !important;
}
label { color: #475569 !important; font-size: 0.82rem !important; }
.stButton > button {
  background: linear-gradient(135deg, #0891b2, #6366f1) !important;
  color: #fff !important; font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important; border: none !important;
  border-radius: 10px !important; padding: 0.52rem 1.3rem !important; font-size: 0.87rem !important;
  box-shadow: 0 2px 15px rgba(8,145,178,0.2) !important; transition: opacity 0.2s, transform 0.1s !important;
}
.stButton > button:hover { opacity: 0.85 !important; transform: translateY(-1px) !important; }
.stTabs [data-baseweb="tab-list"] {
  background: #0f1520 !important; border-radius: 12px !important;
  padding: 4px !important; gap: 3px !important; border: 1px solid #1e2a3a !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important; color: #334155 !important;
  font-family: 'Syne', sans-serif !important; font-weight: 600 !important;
  border-radius: 9px !important; border: none !important; font-size: 0.83rem !important;
}
.stTabs [aria-selected="true"] { background: #131c2a !important; color: #22d3ee !important; }
hr { border-color: #1e2a3a !important; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #080b10; }
::-webkit-scrollbar-thumb { background: #1e2a3a; border-radius: 4px; }
.stAlert { border-radius: 10px !important; }

/* Macro bars */
.macro-bar-wrap { margin: 0.25rem 0; }
.macro-label-row { display:flex; justify-content:space-between; font-size:0.73rem; color:#475569; margin-bottom:0.2rem; }
.macro-bg { background:#1e2a3a; border-radius:999px; height:6px; overflow:hidden; margin-bottom:0.4rem; }
.macro-fill { height:100%; border-radius:999px; }

/* Suggestion chips */
.sug-chip {
  display:inline-block; background:#0f1520; border:1px solid #1e3a5f;
  border-radius:999px; padding:0.3rem 0.75rem; font-size:0.78rem; color:#64748b;
  margin:0.15rem; cursor:pointer; transition:all 0.15s;
}
.sug-chip:hover { border-color:#22d3ee; color:#22d3ee; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
def ss(k, v):
    if k not in st.session_state:
        st.session_state[k] = v

ss("all_data",        load_all_data())
ss("usuario_logado",  None)
ss("pagina_auth",     "login")
ss("dica_idx",        random.randint(0, len(DICAS)-1))
ss("mostrar_dica",    True)
ss("editar_treino",   None)
ss("ac_sel",          None)
ss("ac_q",            "")
ss("nova_conquista",  [])

all_data = st.session_state.all_data

def save():
    save_all_data(all_data)

# ══════════════════════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.usuario_logado:
    st.markdown("""<div style="text-align:center;padding:2.5rem 0 1rem">
      <div style="font-family:Syne,sans-serif;font-size:3rem;font-weight:800;
        background:linear-gradient(135deg,#22d3ee,#818cf8);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">
        ⚡ NutriFlow
      </div>
      <div style="color:#334155;font-size:0.82rem;text-transform:uppercase;letter-spacing:0.12em;margin-top:0.3rem">
        Seu Strava de dieta e treinos
      </div>
    </div>""", unsafe_allow_html=True)

    pg = st.session_state.pagina_auth

    if pg == "login":
        _, col, _ = st.columns([1, 1.3, 1])
        with col:
            with st.container():
                st.markdown("#### Entrar")
                username = st.text_input("Usuario", placeholder="seu usuario")
                senha    = st.text_input("Senha", type="password", placeholder="••••••")
                if st.button("Entrar →", use_container_width=True):
                    users = all_data["usuarios"]
                    if username in users and users[username]["senha"] == hash_senha(senha):
                        st.session_state.usuario_logado = username
                        st.rerun()
                    else:
                        st.error("Usuario ou senha incorretos.")
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div style="text-align:center;color:#334155;font-size:0.82rem">Nao tem conta?</div>', unsafe_allow_html=True)
                if st.button("Criar conta gratuita", use_container_width=True):
                    st.session_state.pagina_auth = "cadastro"
                    st.rerun()
    else:
        _, col, _ = st.columns([0.4, 2.5, 0.4])
        with col:
            st.markdown("#### Criar conta")
            c1, c2 = st.columns(2)
            with c1:
                novo_user  = st.text_input("Usuario (sem espacos)", placeholder="joaosilva")
                nova_senha = st.text_input("Senha", type="password")
            with c2:
                novo_nome  = st.text_input("Nome completo")
                conf_senha = st.text_input("Confirmar senha", type="password")
            st.markdown("---")
            st.markdown("**Dados para calculo calorico**")
            c3, c4 = st.columns(2)
            with c3:
                sexo  = st.selectbox("Sexo biologico", ["Masculino","Feminino"])
                idade = st.number_input("Idade", min_value=10, max_value=99, value=25)
            with c4:
                peso   = st.number_input("Peso (kg)", min_value=30.0, max_value=300.0, value=70.0, step=0.5)
                altura = st.number_input("Altura (cm)", min_value=100, max_value=250, value=170)
            atividade = st.selectbox("Nivel de atividade", list(NIVEL_ATIVIDADE.keys()))
            OBJ_LISTA = ["Manutencao","Perda saudavel (-0,5kg/sem)","Perda agressiva (-1kg/sem)","Ganho muscular"]
            objetivo  = st.radio("Objetivo", OBJ_LISTA, horizontal=True)

            pv = {"peso":peso,"altura":altura,"idade":idade,"sexo":sexo,"atividade":atividade}
            mv = calcular_meta(pv, objetivo)
            cor_obj_map = {"Manutencao":"#22d3ee","Perda saudavel (-0,5kg/sem)":"#34d399","Perda agressiva (-1kg/sem)":"#fb7185","Ganho muscular":"#818cf8"}
            st.markdown(f"""<div style="background:#080b10;border-radius:12px;padding:1rem;text-align:center;margin:0.8rem 0;border:1px solid #1e2a3a">
              <div style="font-size:0.7rem;color:#475569;text-transform:uppercase;letter-spacing:.07em">Meta calorica estimada</div>
              <div style="font-family:Syne,sans-serif;font-size:2rem;font-weight:800;color:{cor_obj_map.get(objetivo,'#22d3ee')}">{mv} kcal</div>
              <div style="font-size:0.75rem;color:#334155">{objetivo}</div>
            </div>""", unsafe_allow_html=True)

            if st.button("Criar conta →", use_container_width=True):
                if not all([novo_user, novo_nome, nova_senha]):
                    st.error("Preencha todos os campos.")
                elif " " in novo_user:
                    st.error("Usuario sem espacos.")
                elif nova_senha != conf_senha:
                    st.error("Senhas nao coincidem.")
                elif novo_user in all_data["usuarios"]:
                    st.error("Usuario ja existe.")
                else:
                    pf = {"peso":peso,"altura":altura,"idade":idade,"sexo":sexo,"atividade":atividade}
                    all_data["usuarios"][novo_user] = {
                        "senha":hash_senha(nova_senha),"nome":novo_nome,
                        "perfil":pf,"objetivo":objetivo,
                        "meta_calorias":calcular_meta(pf, objetivo),
                        "alimentacao":{},"treinos":{},"favoritos":[],"conquistas":[],
                    }
                    save()
                    st.success(f"Conta criada! Meta: {calcular_meta(pf,objetivo)} kcal/dia")
                    st.session_state.pagina_auth = "login"
                    st.rerun()
            if st.button("← Voltar", use_container_width=True):
                st.session_state.pagina_auth = "login"
                st.rerun()
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# APP PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
uname     = st.session_state.usuario_logado
udata     = all_data["usuarios"][uname]
today_str = str(date.today())
META      = udata.get("meta_calorias", 2000)

udata.setdefault("alimentacao", {})
udata.setdefault("treinos", {})
udata.setdefault("favoritos", [])
udata.setdefault("conquistas", [])
udata["alimentacao"].setdefault(today_str, [])
udata["treinos"].setdefault(today_str, {"descricao":"","concluido":False,"notas":"","foto":""})

# Verificar conquistas e notificar
novas_c = verificar_conquistas(udata)
if novas_c:
    save()
    for c in novas_c:
        st.toast(f"{c['emoji']} Conquista desbloqueada: {c['nome']}!", icon="🏆")

# ── CABEÇALHO ────────────────────────────────────────────────────────────────
ch1, ch2, ch3 = st.columns([3, 1, 1])
with ch1:
    st.markdown('<div class="hero-title">⚡ NutriFlow</div>', unsafe_allow_html=True)
    obj_now = udata.get("objetivo","Manutencao")
    obj_cls = {"Manutencao":"ob-m","Perda saudavel (-0,5kg/sem)":"ob-s","Perda agressiva (-1kg/sem)":"ob-a","Ganho muscular":"ob-g"}
    obj_ico = {"Manutencao":"💎","Perda saudavel (-0,5kg/sem)":"🎯","Perda agressiva (-1kg/sem)":"🔥","Ganho muscular":"💪"}
    streak  = calcular_streak(udata)
    str_html = f'<span class="streak-badge">🔥 {streak} dias</span>' if streak >= 2 else ""
    st.markdown(f"""<div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap;margin-top:0.3rem">
      <span style="color:#334155;font-size:0.82rem">Ola, <strong style="color:#64748b">{udata['nome']}</strong></span>
      <span class="obj-badge {obj_cls.get(obj_now,'ob-m')}">{obj_ico.get(obj_now,'⚡')} {obj_now}</span>
      {str_html}
    </div>""", unsafe_allow_html=True)
with ch2:
    selected_date = st.date_input("Data", value=date.today(), label_visibility="collapsed")
    selected_str  = str(selected_date)
with ch3:
    if st.button("Sair"):
        st.session_state.usuario_logado = None
        st.rerun()

udata["alimentacao"].setdefault(selected_str, [])
udata["treinos"].setdefault(selected_str, {"descricao":"","concluido":False,"notas":"","foto":""})

st.markdown("<br>", unsafe_allow_html=True)

# ── DICA DO DIA ──────────────────────────────────────────────────────────────
if st.session_state.mostrar_dica:
    d_raw  = DICAS[st.session_state.dica_idx]
    partes = d_raw[0].split(" ", 1)
    ico_d  = partes[0] if len(partes) > 1 else "💡"
    ttl_d  = partes[1] if len(partes) > 1 else d_raw[0]
    dc1, dc2 = st.columns([9, 1])
    with dc1:
        st.markdown(f"""<div class="dica-box">
          <div class="dica-ico">{ico_d}</div>
          <div><div class="dica-ttl">{ttl_d}</div><div class="dica-txt">{d_raw[1]}</div></div>
        </div>""", unsafe_allow_html=True)
    with dc2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✕", help="Fechar dica"):
            st.session_state.mostrar_dica = False
            st.rerun()
        if st.button("›", help="Proxima dica"):
            st.session_state.dica_idx = (st.session_state.dica_idx + 1) % len(DICAS)
            st.rerun()
else:
    if st.button("💡 Dica do dia"):
        st.session_state.mostrar_dica = True
        st.session_state.dica_idx = random.randint(0, len(DICAS)-1)
        st.rerun()

# ── MÉTRICAS ─────────────────────────────────────────────────────────────────
kcal_hoje = total_kcal_dia(udata, selected_str)
macros_hoje = total_macros_dia(udata, selected_str)
pct_meta  = kcal_hoje / META * 100 if META > 0 else 0
restante  = META - kcal_hoje
treinos_7 = sum(1 for i in range(7) if udata["treinos"].get((date.today()-timedelta(days=i)).isoformat(),{}).get("concluido"))
dias_sem  = [(date.today()-timedelta(days=i)).isoformat() for i in range(6,-1,-1)]
kcals_sem = [total_kcal_dia(udata, d) for d in dias_sem if total_kcal_dia(udata, d) > 0]
media_sem = round(sum(kcals_sem)/len(kcals_sem), 0) if kcals_sem else 0

if pct_meta == 0:
    frase, cor_p = "Vamos comecar! 💪", "#22d3ee"
elif pct_meta < 40:
    frase, cor_p = f"Faltam {restante:.0f} kcal — comece bem o dia", "#22d3ee"
elif pct_meta < 75:
    frase, cor_p = f"Indo bem! Faltam {restante:.0f} kcal 🎯", "#34d399"
elif pct_meta < 95:
    frase, cor_p = f"Quase la! Mais {restante:.0f} kcal ✨", "#fbbf24"
elif pct_meta <= 108:
    frase, cor_p = "Meta batida! Excelente 🎉", "#34d399"
else:
    exc = kcal_hoje - META
    frase, cor_p = f"⚠️ {exc:.0f} kcal acima da meta", "#fb7185"

pct_c = min(pct_meta, 100)
cor_mv_map = {
    "mv-cyan":    "#22d3ee",
    "mv-emerald": "#34d399",
    "mv-amber":   "#fbbf24",
    "mv-rose":    "#fb7185",
}
cor_mv = "#22d3ee" if pct_meta < 95 else ("#34d399" if pct_meta <= 108 else "#fb7185")

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""<div class="metric-box">
      <div class="metric-value" style="color:{cor_mv}">{kcal_hoje:.0f}</div>
      <div class="metric-label">kcal hoje</div>
      <div class="metric-sub">{pct_meta:.0f}% da meta</div>
    </div>""", unsafe_allow_html=True)
with m2:
    st.markdown(f"""<div class="metric-box">
      <div class="metric-value" style="color:#818cf8">{META}</div>
      <div class="metric-label">meta calorica</div>
      <div class="metric-sub">{restante:.0f} restam</div>
    </div>""", unsafe_allow_html=True)
with m3:
    st.markdown(f"""<div class="metric-box">
      <div class="metric-value" style="color:#22d3ee">{media_sem:.0f}</div>
      <div class="metric-label">media semanal</div>
      <div class="metric-sub">ultimos 7 dias</div>
    </div>""", unsafe_allow_html=True)
with m4:
    cor_s = "#fbbf24" if streak >= 3 else "#818cf8"
    st.markdown(f"""<div class="metric-box">
      <div class="metric-value" style="color:{cor_s}">{streak}🔥</div>
      <div class="metric-label">streak treinos</div>
      <div class="metric-sub">{treinos_7}/7 essa semana</div>
    </div>""", unsafe_allow_html=True)

# Barra de progresso
st.markdown(f"""<div class="prog-wrap">
  <div class="prog-label">
    <span class="prog-phrase" style="color:{cor_p}">{frase}</span>
    <span class="prog-pct">{kcal_hoje:.0f} / {META} kcal</span>
  </div>
  <div class="prog-bg">
    <div class="prog-fill" style="width:{pct_c:.1f}%;background:linear-gradient(90deg,{cor_p},{cor_p}99)"></div>
  </div>
</div>""", unsafe_allow_html=True)

# Macro bars
meta_prot = round(udata.get("perfil",{}).get("peso",70) * 2, 0)  # 2g/kg
meta_carbo = round((META * 0.45) / 4, 0)
meta_gord  = round((META * 0.25) / 9, 0)

p_prot = min(macros_hoje["proteina"] / meta_prot * 100, 100) if meta_prot > 0 else 0
p_carb = min(macros_hoje["carbo"] / meta_carbo * 100, 100) if meta_carbo > 0 else 0
p_gord = min(macros_hoje["gordura"] / meta_gord * 100, 100) if meta_gord > 0 else 0

st.markdown(f"""<div style="display:flex;gap:1.5rem;margin-bottom:1.2rem;flex-wrap:wrap">
  <div style="flex:1;min-width:120px">
    <div class="macro-label-row"><span>🥩 Proteina</span><span style="color:#22d3ee">{macros_hoje['proteina']:.0f}g / {meta_prot:.0f}g</span></div>
    <div class="macro-bg"><div class="macro-fill" style="width:{p_prot:.0f}%;background:#22d3ee"></div></div>
  </div>
  <div style="flex:1;min-width:120px">
    <div class="macro-label-row"><span>🍚 Carboidrato</span><span style="color:#fbbf24">{macros_hoje['carbo']:.0f}g / {meta_carbo:.0f}g</span></div>
    <div class="macro-bg"><div class="macro-fill" style="width:{p_carb:.0f}%;background:#fbbf24"></div></div>
  </div>
  <div style="flex:1;min-width:120px">
    <div class="macro-label-row"><span>🥑 Gordura</span><span style="color:#818cf8">{macros_hoje['gordura']:.0f}g / {meta_gord:.0f}g</span></div>
    <div class="macro-bg"><div class="macro-fill" style="width:{p_gord:.0f}%;background:#818cf8"></div></div>
  </div>
</div>""", unsafe_allow_html=True)

# ── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🥗 Alimentacao", "🏋️ Treino", "📊 Historico", "👥 Social", "⚙️ Perfil"])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — ALIMENTAÇÃO
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    col_add, col_view = st.columns([1, 1.45], gap="large")

    with col_add:
        # ── "Repetir ontem" ──────────────────────────────────────────────
        ontem_str = (date.fromisoformat(selected_str) - timedelta(days=1)).isoformat()
        ontem_ref = udata["alimentacao"].get(ontem_str, [])
        if ontem_ref and not udata["alimentacao"].get(selected_str):
            kcal_ont = sum(r["calorias"] for r in ontem_ref)
            st.markdown(f"""<div style="background:#0a1e0a;border:1px solid #166534;border-radius:12px;
              padding:0.75rem 1rem;margin-bottom:0.8rem;display:flex;justify-content:space-between;align-items:center">
              <div>
                <div style="font-family:Syne,sans-serif;font-size:0.85rem;font-weight:700;color:#34d399">📋 Repetir dia anterior?</div>
                <div style="font-size:0.75rem;color:#475569">{len(ontem_ref)} itens · {kcal_ont:.0f} kcal</div>
              </div>
            </div>""", unsafe_allow_html=True)
            if st.button("✓ Repetir ontem", use_container_width=True):
                import copy
                udata["alimentacao"][selected_str] = copy.deepcopy(ontem_ref)
                save()
                st.success("Dia anterior copiado!")
                st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

        # ── Sugestões baseadas no histórico ──────────────────────────────
        sugestoes = sugerir_almoco(udata)
        if sugestoes:
            st.markdown('<div style="font-size:0.78rem;color:#334155;margin-bottom:0.4rem">🧠 Seus mais frequentes:</div>', unsafe_allow_html=True)
            chips_html = " ".join(
                f'<span class="sug-chip">{BANCO_ALIMENTOS[s].get("emoji","🍽️")} {s}</span>'
                for s in sugestoes if s in BANCO_ALIMENTOS
            )
            st.markdown(f'<div style="margin-bottom:0.8rem">{chips_html}</div>', unsafe_allow_html=True)

        # ── Favoritos rápidos ────────────────────────────────────────────
        if udata["favoritos"]:
            st.markdown('<div style="font-size:0.82rem;font-weight:700;color:#64748b;margin-bottom:0.5rem">⭐ Favoritos — 1 clique</div>', unsafe_allow_html=True)
            for fi, fav in enumerate(udata["favoritos"]):
                fa1, fa2 = st.columns([3, 1])
                with fa1:
                    st.markdown(f"""<div style="background:#0f1520;border:1px solid #1e2a3a;border-radius:10px;padding:0.45rem 0.75rem;margin-bottom:0.25rem">
                      <div style="font-size:0.83rem;color:#cbd5e1;font-weight:500">{fav['alimento']}</div>
                      <div style="font-size:0.72rem;color:#334155">{fav.get('tipo','')} · {fav['calorias']:.0f} kcal</div>
                    </div>""", unsafe_allow_html=True)
                with fa2:
                    if st.button("+", key=f"fav_{fi}", help="Adicionar ao dia"):
                        udata["alimentacao"][selected_str].append({
                            "alimento": fav["alimento"], "tipo": fav.get("tipo",""),
                            "quantidade": fav["quantidade"], "unidade": fav["unidade"],
                            "calorias": fav["calorias"], "proteina": 0, "carbo": 0, "gordura": 0,
                            "foto": "", "comentario": "",
                        })
                        save()
                        st.toast(f"✅ {fav['alimento']} adicionado!")
                        st.rerun()
            st.markdown("---")

        # ── Formulário de registro ────────────────────────────────────────
        st.markdown("**➕ Registrar refeicao**")
        tipo_ref = st.selectbox("Tipo", TIPOS_REFEICAO)

        # Autocomplete
        ac_q = st.text_input("🔍 Buscar alimento", placeholder="arroz, frango, ovo... (Enter para buscar)", key="ac_input")
        if ac_q != st.session_state.ac_q:
            st.session_state.ac_q = ac_q
            st.session_state.ac_sel = None

        sugs = buscar_alimentos(ac_q)
        if sugs and not st.session_state.ac_sel:
            st.markdown('<div style="font-size:0.73rem;color:#334155;margin-bottom:0.25rem">Sugestoes:</div>', unsafe_allow_html=True)
            for s in sugs:
                info = BANCO_ALIMENTOS[s]
                label_s = f"{info.get('emoji','🍽️')}  {s}  —  {info['kcal_100g']} kcal/100{info['unidade']}"
                if st.button(label_s, key=f"sug_{s}"):
                    st.session_state.ac_sel = s
                    st.rerun()

        sel   = st.session_state.ac_sel
        UNIDS = ["g","ml","unid","colher","xicara"]
        u_def = BANCO_ALIMENTOS[sel]["unidade"] if sel and BANCO_ALIMENTOS[sel]["unidade"] in UNIDS else "g"
        u_idx = UNIDS.index(u_def)

        alimento    = st.text_input("Nome do alimento", value=sel or "", placeholder="Ex: Frango grelhado peito")
        cq1, cq2   = st.columns([2, 1])
        with cq1:
            unidade  = st.selectbox("Unidade", UNIDS, index=u_idx)
        with cq2:
            quantidade = st.number_input("Qtd", min_value=0.0, step=10.0, value=100.0)

        nm_busca  = alimento.strip() if alimento.strip() else sel
        kcal_auto = kcal_estimada(nm_busca, quantidade, unidade) if nm_busca and nm_busca in BANCO_ALIMENTOS else 0.0
        macros_auto = macros_estimados(nm_busca, quantidade, unidade) if nm_busca and nm_busca in BANCO_ALIMENTOS else {}

        lbl_kcal = "Calorias (kcal)" + (" ✦ auto" if kcal_auto > 0 else "")
        calorias = st.number_input(lbl_kcal, min_value=0.0, step=1.0, value=float(kcal_auto) if kcal_auto > 0 else 0.0)

        if kcal_auto > 0 and macros_auto:
            st.markdown(f"""<div style="background:#080b10;border-radius:8px;padding:0.5rem 0.75rem;margin:0.3rem 0;
              display:flex;gap:1.5rem;font-size:0.75rem;color:#475569;border:1px solid #1e2a3a">
              <span>🥩 P: <b style="color:#22d3ee">{macros_auto.get('proteina',0):.1f}g</b></span>
              <span>🍚 C: <b style="color:#fbbf24">{macros_auto.get('carbo',0):.1f}g</b></span>
              <span>🥑 G: <b style="color:#818cf8">{macros_auto.get('gordura',0):.1f}g</b></span>
            </div>""", unsafe_allow_html=True)

        comentario = st.text_input("💬 Comentario (opcional)", key="ali_com")
        foto_ref   = st.file_uploader("📷 Foto", type=["jpg","jpeg","png","webp"], key="up_ref")
        if foto_ref:
            st.image(foto_ref, use_container_width=True)

        ba1, ba2 = st.columns(2)
        with ba1:
            if st.button("✓ Adicionar", use_container_width=True):
                if alimento.strip():
                    fp = save_photo(foto_ref,"ref",uname,selected_str) if foto_ref else ""
                    ma = macros_auto if macros_auto else {"proteina":0,"carbo":0,"gordura":0}
                    udata["alimentacao"][selected_str].append({
                        "alimento":alimento.strip(),"tipo":tipo_ref,
                        "quantidade":quantidade,"unidade":unidade,
                        "calorias":calorias,
                        "proteina":ma.get("proteina",0),"carbo":ma.get("carbo",0),"gordura":ma.get("gordura",0),
                        "foto":fp,"comentario":comentario,
                    })
                    save()
                    st.toast(f"✅ {alimento.strip()} adicionado! {calorias:.0f} kcal")
                    st.session_state.ac_sel = None
                    st.session_state.ac_q   = ""
                    st.rerun()
                else:
                    st.warning("Informe o alimento.")
        with ba2:
            if st.button("⭐ Favorito", use_container_width=True):
                if alimento.strip():
                    udata["favoritos"].append({
                        "nome":alimento.strip()[:20],"alimento":alimento.strip(),"tipo":tipo_ref,
                        "quantidade":quantidade,"unidade":unidade,"calorias":calorias,
                    })
                    save()
                    st.toast("⭐ Salvo nos favoritos!")
                    st.rerun()

    # ── Visão do dia ─────────────────────────────────────────────────────
    with col_view:
        refeicoes = udata["alimentacao"].get(selected_str, [])
        kcal_dia  = total_kcal_dia(udata, selected_str)

        st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.9rem">
          <div style="font-family:Syne,sans-serif;font-size:0.95rem;font-weight:700;color:#e2e8f0">
            🗓️ {selected_date.strftime('%d/%m/%Y')}
          </div>
          <div style="font-family:Syne,sans-serif;font-size:1.1rem;font-weight:800;color:#22d3ee">
            {kcal_dia:.0f} kcal
          </div>
        </div>""", unsafe_allow_html=True)

        for tipo in TIPOS_REFEICAO:
            itens   = [(i, r) for i, r in enumerate(refeicoes) if r.get("tipo") == tipo]
            tot_t   = sum(r["calorias"] for _, r in itens)
            kcal_s  = f'<span style="font-family:Syne,sans-serif;font-size:0.82rem;font-weight:700;color:#22d3ee">{tot_t:.0f} kcal</span>' if itens else ''

            # Header do tipo de refeição — HTML completo e autônomo
            st.markdown(f"""<div class="meal-header">
              <span class="meal-title">{tipo}</span>
              {kcal_s}
            </div>""", unsafe_allow_html=True)

            if not itens:
                st.markdown('<div style="font-size:0.78rem;color:#1e2a3a;font-style:italic;padding:0.15rem 0.8rem 0.6rem">Nenhum registro</div>', unsafe_allow_html=True)
            else:
                for orig_i, r in itens:
                    fr1, fr2 = st.columns([7, 1])
                    with fr1:
                        com_h = f'<div style="font-size:0.7rem;color:#1e2a3a;font-style:italic">💬 {r["comentario"]}</div>' if r.get("comentario") else ""
                        st.markdown(f"""<div class="food-row">
                          <div>
                            <div class="food-row-name">{r['alimento']}</div>
                            <div class="food-row-qty">{r['quantidade']} {r['unidade']}{" · P:"+str(r.get('proteina',0))+"g" if r.get('proteina',0) else ""}</div>
                            {com_h}
                          </div>
                          <div class="food-row-kcal">{r['calorias']:.0f}</div>
                        </div>""", unsafe_allow_html=True)
                        if r.get("foto") and os.path.exists(r["foto"]):
                            with st.expander("📷 ver foto"):
                                st.image(r["foto"], use_container_width=True)
                    with fr2:
                        if st.button("🗑️", key=f"df_{orig_i}_{selected_str}"):
                            udata["alimentacao"][selected_str].pop(orig_i)
                            save()
                            st.rerun()

            st.markdown('<div style="margin-bottom:0.6rem"></div>', unsafe_allow_html=True)

        if refeicoes:
            saldo = kcal_dia - META
            cor_s = "#fb7185" if saldo > 0 else "#34d399"
            saldo_txt = f"+{saldo:.0f} acima" if saldo > 0 else f"{abs(saldo):.0f} abaixo"
            st.markdown(f"""<div style="display:flex;justify-content:space-between;padding:0.7rem 1rem;
              background:#0f1520;border-radius:11px;border:1px solid #1e2a3a;margin-top:0.4rem">
              <span style="color:#334155;font-size:0.83rem">Saldo do dia</span>
              <span style="font-family:Syne,sans-serif;font-weight:700;color:{cor_s};font-size:0.9rem">{saldo_txt} da meta</span>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — TREINO
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    col_tf, col_tl = st.columns([1, 1.2], gap="large")
    treino_dia = udata["treinos"][selected_str]

    if st.session_state.editar_treino:
        d_ed = st.session_state.editar_treino
        t_ed = udata["treinos"].get(d_ed, {"descricao":"","concluido":False,"notas":"","foto":""})
        st.markdown(f"""<div style="background:#0f1520;border:1.5px solid #22d3ee;border-radius:16px;
          padding:1.2rem;margin-bottom:1.2rem">
          <div style="font-family:Syne,sans-serif;font-size:0.95rem;font-weight:700;color:#22d3ee;margin-bottom:0.5rem">
            ✏️ Editando treino de {d_ed}
          </div>
        </div>""", unsafe_allow_html=True)
        gi  = GRUPOS_TREINO.index(t_ed.get("descricao","")) if t_ed.get("descricao","") in GRUPOS_TREINO else 0
        de  = st.selectbox("Grupo", GRUPOS_TREINO, index=gi, key="ed_d")
        ne  = st.text_area("Observacoes", value=t_ed.get("notas",""), height=90, key="ed_n")
        ce  = st.checkbox("Concluido", value=t_ed.get("concluido",False), key="ed_c")
        es1, es2 = st.columns(2)
        with es1:
            if st.button("💾 Salvar edicao", use_container_width=True):
                udata["treinos"][d_ed] = {"descricao": de if de != "Selecione" else "","notas":ne,"concluido":ce,"foto":t_ed.get("foto","")}
                save()
                st.session_state.editar_treino = None
                st.toast("✅ Treino atualizado!")
                st.rerun()
        with es2:
            if st.button("Cancelar", use_container_width=True):
                st.session_state.editar_treino = None
                st.rerun()
        st.markdown("---")

    with col_tf:
        st.markdown("**🏋️ Registrar treino**")
        gi_d = GRUPOS_TREINO.index(treino_dia["descricao"]) if treino_dia.get("descricao") in GRUPOS_TREINO else 0
        desc = st.selectbox("Grupo muscular", GRUPOS_TREINO, index=gi_d)
        nota = st.text_area("Exercicios realizados", value=treino_dia.get("notas",""), placeholder="Ex: Supino 4x10 80kg\nRosca direta 3x12 20kg", height=130)
        conc = st.checkbox("✅ Treino concluido", value=treino_dia.get("concluido",False))
        ftr  = st.file_uploader("📷 Foto do treino", type=["jpg","jpeg","png","webp"], key="up_tr")
        if ftr:
            st.image(ftr, use_container_width=True)
        elif treino_dia.get("foto") and os.path.exists(treino_dia["foto"]):
            st.image(treino_dia["foto"], use_container_width=True)

        if st.button("💾 Salvar treino", use_container_width=True):
            fp = save_photo(ftr,"tr",uname,selected_str) if ftr else treino_dia.get("foto","")
            udata["treinos"][selected_str] = {"descricao": desc if desc != "Selecione" else "","notas":nota,"concluido":conc,"foto":fp}
            save()
            st.toast("💪 Treino salvo!" if conc else "📝 Treino registrado!")
            st.rerun()

    with col_tl:
        st.markdown("**📅 Proximos 30 dias**")
        hoje_d  = date.today()
        sem_pt  = ["Seg","Ter","Qua","Qui","Sex","Sab","Dom"]
        for i in range(30):
            d  = hoje_d + timedelta(days=i)
            ds = d.isoformat()
            udata["treinos"].setdefault(ds, {"descricao":"","concluido":False,"notas":"","foto":""})
            t     = udata["treinos"][ds]
            desc_t = t.get("descricao") or "—"
            ok    = t.get("concluido", False)
            sem   = sem_pt[d.weekday()]
            dl    = "Hoje" if i==0 else ("Amanha" if i==1 else d.strftime("%d/%m"))
            lbl   = "✓ Concluido" if ok else ("· Planejado" if t.get("descricao") else "· Vazio")
            cor_lbl = "#34d399" if ok else "#334155"
            bord  = "#22d3ee" if i==0 else ("#34d39944" if ok else "#818cf833")
            bg    = "#0a1e1e" if i==0 else "#0f1520"

            tc, te = st.columns([5, 1])
            with tc:
                st.markdown(f"""<div style="background:{bg};border-radius:11px;padding:0.65rem 1rem;
                  margin-bottom:0.3rem;border-left:3px solid {bord};
                  display:flex;justify-content:space-between;align-items:center">
                  <div>
                    <div style="font-size:0.72rem;color:#1e2a3a">{dl} · {sem}</div>
                    <div style="color:#64748b;font-weight:500;font-size:0.84rem">{desc_t}</div>
                  </div>
                  <span style="font-weight:600;font-size:0.83rem;color:{cor_lbl}">{lbl}</span>
                </div>""", unsafe_allow_html=True)
            with te:
                if st.button("✏️", key=f"e_{ds}", help=f"Editar {ds}"):
                    st.session_state.editar_treino = ds
                    st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — HISTÓRICO + INSIGHTS
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    hoje_h  = date.today()
    dias_30 = [(hoje_h-timedelta(days=i)).isoformat() for i in range(29,-1,-1)]
    labs_30 = [(hoje_h-timedelta(days=i)).strftime("%d/%m") for i in range(29,-1,-1)]
    kcal_30 = [total_kcal_dia(udata,d) for d in dias_30]

    # Insights automáticos
    insights = gerar_insights(udata, META)
    if insights:
        st.markdown("**🧠 Seus Insights**")
        for ins in insights:
            st.markdown(f"""<div class="insight-box">
              <div class="insight-ico">{ins['emoji']}</div>
              <div class="insight-txt">{ins['txt']}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("**📊 Calorias — ultimos 30 dias**")
    df_ch = pd.DataFrame({"Consumido":kcal_30,"Meta":[META]*30}, index=labs_30)
    st.line_chart(df_ch, height=240, color=["#22d3ee","#fb7185"])

    st.markdown("<br>")
    st.markdown("**📋 Resumo detalhado**")
    rows = []
    for d_s in reversed(dias_30):
        kc = total_kcal_dia(udata,d_s)
        t  = udata["treinos"].get(d_s,{})
        if kc == 0 and not t.get("descricao"):
            continue
        sl = kc - META
        rows.append({
            "Data":d_s,"Kcal":f"{kc:.0f}","Meta":str(META),
            "Saldo":f"{'+'if sl>0 else ''}{sl:.0f}",
            "Refeicoes":len(udata["alimentacao"].get(d_s,[])),
            "Treino":t.get("descricao") or "—",
            "Concluido":"✓" if t.get("concluido") else "✗",
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.markdown('<div style="color:#1e293b;text-align:center;padding:2rem">Sem dados ainda.</div>', unsafe_allow_html=True)

    # Conquistas
    st.markdown("<br>")
    st.markdown("**🏆 Conquistas**")
    unlocked_ids = udata.get("conquistas", [])
    c_cols = st.columns(2)
    for ci, c in enumerate(CONQUISTAS):
        desbloqueada = c["id"] in unlocked_ids
        bg   = "linear-gradient(135deg,#1a1000,#2a1a00)" if desbloqueada else "#0f1520"
        bord = "#fbbf2444" if desbloqueada else "#1e2a3a"
        cor  = "#fbbf24" if desbloqueada else "#1e2a3a"
        txt  = "#78716c" if desbloqueada else "#1e2a3a"
        emo  = c["emoji"] if desbloqueada else "🔒"
        with c_cols[ci % 2]:
            st.markdown(f"""<div style="background:{bg};border:1px solid {bord};border-radius:12px;
              padding:0.75rem 0.9rem;display:flex;gap:0.6rem;align-items:center;margin-bottom:0.5rem">
              <div style="font-size:1.5rem;flex-shrink:0">{emo}</div>
              <div>
                <div style="font-family:Syne,sans-serif;font-size:0.83rem;font-weight:700;color:{cor}">{c['nome']}</div>
                <div style="font-size:0.74rem;color:{txt};margin-top:0.1rem">{c['desc']}</div>
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>")
    exp_d = {"alimentacao":udata["alimentacao"],"treinos":udata["treinos"]}
    st.download_button("⬇️ Exportar dados (JSON)",
        data=json.dumps(exp_d, ensure_ascii=False, indent=2),
        file_name=f"nutriflow_{uname}.json", mime="application/json")

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — SOCIAL
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    todos = all_data["usuarios"]
    sc1, sc2 = st.columns([1,1], gap="large")

    with sc1:
        st.markdown("**🏆 Ranking — meta de hoje**")
        rank = []
        for u,ud in todos.items():
            m_u = ud.get("meta_calorias",2000)
            k_u = total_kcal_dia(ud, today_str)
            rank.append({"u":u,"nome":ud["nome"],"pct":k_u/m_u*100 if m_u>0 else 0,"kcal":k_u,"meta":m_u,"streak":calcular_streak(ud)})
        rank.sort(key=lambda x:x["pct"], reverse=True)

        for pos, r in enumerate(rank):
            emo  = ["🥇","🥈","🥉"][pos] if pos<3 else f"{pos+1}."
            dest = "border:1.5px solid #0e7490;" if r["u"]==uname else "border:1px solid #1e2a3a;"
            pct2 = min(r["pct"],100)
            st.markdown(f"""<div class="rank-item" style="{dest}">
              <div style="font-family:Syne,sans-serif;font-weight:800;font-size:1rem;width:28px;text-align:center">{emo}</div>
              <div style="width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#22d3ee,#818cf8);
                display:flex;align-items:center;justify-content:center;font-family:Syne,sans-serif;font-weight:700;
                font-size:0.82rem;color:#080b10;flex-shrink:0">{r['nome'][0].upper()}</div>
              <div style="flex:1">
                <div style="font-size:0.87rem;font-weight:600;color:#e2e8f0">{r['nome']} {'👑' if r['u']==uname else ''}</div>
                <div style="font-size:0.73rem;color:#334155">{r['kcal']:.0f}/{r['meta']} kcal · 🔥{r['streak']}d</div>
              </div>
              <div style="text-align:right">
                <div style="font-family:Syne,sans-serif;font-size:0.85rem;font-weight:700;color:#22d3ee">{pct2:.0f}%</div>
                <div style="width:55px;background:#131c2a;border-radius:999px;height:4px;margin-top:3px">
                  <div style="width:{pct2:.0f}%;background:#22d3ee;height:4px;border-radius:999px"></div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>")
        st.markdown("**💪 Desafio semanal de treinos**")
        rank_t = sorted(
            [{"u":u,"nome":ud["nome"],"t7":sum(1 for i in range(7) if ud["treinos"].get((date.today()-timedelta(days=i)).isoformat(),{}).get("concluido"))}
             for u,ud in todos.items()],
            key=lambda x:x["t7"], reverse=True
        )
        for pos,r in enumerate(rank_t):
            emo  = ["🥇","🥈","🥉"][pos] if pos<3 else f"{pos+1}."
            dest = "border:1.5px solid #0e7490;" if r["u"]==uname else "border:1px solid #1e2a3a;"
            b    = int(r["t7"]/7*100)
            st.markdown(f"""<div class="rank-item" style="{dest}">
              <span style="font-family:Syne,sans-serif;font-weight:800;font-size:0.95rem;width:24px">{emo}</span>
              <span style="flex:1;font-size:0.87rem;color:#e2e8f0">{r['nome']}</span>
              <div style="flex:1;margin:0 0.5rem">
                <div style="background:#131c2a;border-radius:999px;height:5px">
                  <div style="width:{b}%;background:#818cf8;height:5px;border-radius:999px"></div>
                </div>
              </div>
              <span style="font-family:Syne,sans-serif;font-size:0.85rem;font-weight:700;color:#818cf8">{r['t7']}/7</span>
            </div>""", unsafe_allow_html=True)

    with sc2:
        st.markdown("**📰 Feed de atividade**")
        feed = []
        for u,ud in todos.items():
            nm = ud["nome"]
            m_ = ud.get("meta_calorias",2000)
            k_ = total_kcal_dia(ud, today_str)
            if k_ >= m_ * 0.95 and k_ > 0:
                feed.append({"nm":nm,"u":u,"h":"hoje","txt":f"🎯 bateu a meta de {m_} kcal! ({k_:.0f} consumidas)"})
            t_h = ud["treinos"].get(today_str,{})
            if t_h.get("concluido") and t_h.get("descricao"):
                feed.append({"nm":nm,"u":u,"h":"hoje","txt":f"💪 concluiu {t_h['descricao']}"})
            s_ = calcular_streak(ud)
            if s_ >= 3:
                feed.append({"nm":nm,"u":u,"h":"hoje","txt":f"🔥 {s_} dias consecutivos de treino!"})
            ont = (date.today()-timedelta(days=1)).isoformat()
            t_o = ud["treinos"].get(ont,{})
            if t_o.get("concluido") and t_o.get("descricao"):
                feed.append({"nm":nm,"u":u,"h":"ontem","txt":f"🏋️ treinou {t_o['descricao']} ontem"})

        if not feed:
            st.markdown('<div style="color:#1e293b;text-align:center;padding:2rem;font-size:0.85rem">Sem atividade ainda. Comece a registrar!</div>', unsafe_allow_html=True)
        else:
            random.shuffle(feed)
            for fi in feed[:12]:
                ini  = fi["nm"][0].upper()
                dest = "border:1.5px solid #0e7490;" if fi["u"]==uname else "border:1px solid #1e2a3a;"
                st.markdown(f"""<div class="feed-item" style="{dest}">
                  <div class="feed-av">{ini}</div>
                  <div>
                    <div style="font-weight:600;font-size:0.85rem;color:#e2e8f0">{fi['nm']} {'(voce)' if fi['u']==uname else ''}</div>
                    <div style="font-size:0.8rem;color:#475569;margin-top:0.1rem">{fi['txt']}</div>
                    <div style="font-size:0.7rem;color:#1e2a3a;margin-top:0.15rem">{fi['h']}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>")
        st.markdown("**🎯 Minhas metas semanais**")
        dias_sw  = [(date.today()-timedelta(days=i)).isoformat() for i in range(6,-1,-1)]
        meta_ok  = sum(1 for d in dias_sw if total_kcal_dia(udata,d) >= META*0.9 and total_kcal_dia(udata,d) > 0)
        trein_ok = sum(1 for d in dias_sw if udata["treinos"].get(d,{}).get("concluido"))

        for lbl,val,cor_m in [("Dias com meta batida 🎯", meta_ok,"#22d3ee"),("Treinos concluidos 💪", trein_ok,"#818cf8")]:
            pm = val/7*100
            st.markdown(f"""<div style="margin-bottom:0.9rem">
              <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#475569;margin-bottom:0.35rem">
                <span>{lbl}</span>
                <span style="color:{cor_m};font-family:Syne,sans-serif;font-weight:700">{val}/7</span>
              </div>
              <div style="background:#1e2a3a;border-radius:999px;height:7px">
                <div style="width:{pm:.0f}%;background:{cor_m};height:7px;border-radius:999px"></div>
              </div>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 5 — PERFIL
# ════════════════════════════════════════════════════════════════════════════
with tab5:
    pp1, pp2 = st.columns([1,1], gap="large")
    with pp1:
        st.markdown("**👤 Dados pessoais**")
        perf = udata.get("perfil",{})
        ne_  = st.text_input("Nome completo", value=udata.get("nome",""))
        pa, pb = st.columns(2)
        with pa:
            sx_ = st.selectbox("Sexo", ["Masculino","Feminino"], index=0 if perf.get("sexo","M")=="Masculino" else 1)
            id_ = st.number_input("Idade", min_value=10, max_value=99, value=int(perf.get("idade",25)))
        with pb:
            pe_ = st.number_input("Peso (kg)", min_value=30.0, max_value=300.0, value=float(perf.get("peso",70.0)), step=0.5)
            al_ = st.number_input("Altura (cm)", min_value=100, max_value=250, value=int(perf.get("altura",170)))
        ai_ = list(NIVEL_ATIVIDADE.keys()).index(perf.get("atividade",list(NIVEL_ATIVIDADE.keys())[0]))
        at_ = st.selectbox("Atividade", list(NIVEL_ATIVIDADE.keys()), index=ai_)
        OBJ2 = ["Manutencao","Perda saudavel (-0,5kg/sem)","Perda agressiva (-1kg/sem)","Ganho muscular"]
        oi_  = OBJ2.index(udata.get("objetivo","Manutencao")) if udata.get("objetivo") in OBJ2 else 0
        ob_  = st.radio("Objetivo", OBJ2, index=oi_, horizontal=True)

        pv_  = {"peso":pe_,"altura":al_,"idade":id_,"sexo":sx_,"atividade":at_}
        nm_  = calcular_meta(pv_, ob_)
        tmb_ = calcular_tmb(pe_,al_,id_,sx_)
        tde_ = tmb_ * NIVEL_ATIVIDADE[at_]

        # Projeção de peso
        proj_html = ""
        if "Perda" in ob_:
            delta = {"Perda saudavel (-0,5kg/sem)": -500, "Perda agressiva (-1kg/sem)": -1000}.get(ob_, -500)
            kg_4s = abs(delta * 28 / 7700)
            proj_html = f'<div style="font-size:0.75rem;color:#34d399;margin-top:0.3rem">📉 Projecao: -{kg_4s:.1f} kg em 4 semanas</div>'
        elif ob_ == "Ganho muscular":
            proj_html = '<div style="font-size:0.75rem;color:#818cf8;margin-top:0.3rem">📈 Superavit de 300 kcal para ganho lean</div>'

        st.markdown(f"""<div style="background:#080b10;border-radius:12px;padding:1rem;text-align:center;margin:0.8rem 0;border:1px solid #1e2a3a">
          <div style="display:flex;justify-content:space-around">
            <div>
              <div style="font-size:0.68rem;color:#334155;text-transform:uppercase">TMB</div>
              <div style="font-family:Syne,sans-serif;font-size:1.3rem;font-weight:800;color:#818cf8">{tmb_:.0f}</div>
            </div>
            <div>
              <div style="font-size:0.68rem;color:#334155;text-transform:uppercase">TDEE</div>
              <div style="font-family:Syne,sans-serif;font-size:1.3rem;font-weight:800;color:#22d3ee">{tde_:.0f}</div>
            </div>
            <div>
              <div style="font-size:0.68rem;color:#334155;text-transform:uppercase">Nova Meta</div>
              <div style="font-family:Syne,sans-serif;font-size:1.3rem;font-weight:800;color:#34d399">{nm_}</div>
            </div>
          </div>
          {proj_html}
        </div>""", unsafe_allow_html=True)

        if st.button("💾 Salvar alteracoes", use_container_width=True):
            udata.update({"nome":ne_,"objetivo":ob_,"meta_calorias":nm_,
                "perfil":{"peso":pe_,"altura":al_,"idade":id_,"sexo":sx_,"atividade":at_}})
            save()
            st.toast(f"✅ Perfil salvo! Meta: {nm_} kcal/dia")
            st.rerun()

    with pp2:
        st.markdown("**🔑 Alterar senha**")
        sa_ = st.text_input("Senha atual", type="password", key="sa_")
        sn_ = st.text_input("Nova senha", type="password", key="sn_")
        sc_ = st.text_input("Confirmar", type="password", key="sc_")
        if st.button("Alterar senha", use_container_width=True):
            if udata["senha"] != hash_senha(sa_): st.error("Senha incorreta.")
            elif sn_ != sc_: st.error("Senhas nao coincidem.")
            elif len(sn_) < 4: st.error("Minimo 4 caracteres.")
            else:
                udata["senha"] = hash_senha(sn_)
                save()
                st.success("Senha alterada!")

        st.markdown("<br>")
        st.markdown("**📊 Resumo do perfil**")
        p_  = udata.get("perfil",{})
        imc_ = p_.get("peso",70) / ((p_.get("altura",170)/100)**2)
        if imc_ < 18.5:   ci_,co_ = "Abaixo do peso","#22d3ee"
        elif imc_ < 25:   ci_,co_ = "Peso normal","#34d399"
        elif imc_ < 30:   ci_,co_ = "Sobrepeso","#fbbf24"
        else:             ci_,co_ = "Obesidade","#fb7185"

        n_conquistas = len(udata.get("conquistas",[]))
        for lbl,val,cv in [
            ("Usuario",    f"@{uname}",               "#64748b"),
            ("IMC",        f"{imc_:.1f} — {ci_}",      co_),
            ("Meta atual", f"{META} kcal/dia",         "#22d3ee"),
            ("Objetivo",   udata.get("objetivo","—"),  "#94a3b8"),
            ("Streak",     f"🔥 {streak} dias",         "#fbbf24"),
            ("Conquistas", f"🏆 {n_conquistas}/{len(CONQUISTAS)}","#fbbf24"),
            ("Favoritos",  f"⭐ {len(udata.get('favoritos',[]))}","#94a3b8"),
        ]:
            st.markdown(f"""<div style="display:flex;justify-content:space-between;padding:0.38rem 0;
              border-bottom:1px solid #1e2a3a;font-size:0.82rem">
              <span style="color:#334155">{lbl}</span>
              <span style="color:{cv};font-weight:500">{val}</span>
            </div>""", unsafe_allow_html=True)

        if udata["favoritos"]:
            st.markdown("<br>")
            st.markdown('<div style="font-size:0.8rem;color:#334155;margin-bottom:0.4rem">Gerenciar favoritos:</div>', unsafe_allow_html=True)
            for fi,fav in enumerate(udata["favoritos"]):
                fg1,fg2 = st.columns([4,1])
                with fg1:
                    st.markdown(f'<div style="font-size:0.8rem;color:#475569;padding:0.15rem 0">{fav["alimento"][:30]}</div>', unsafe_allow_html=True)
                with fg2:
                    if st.button("🗑️", key=f"dfav_{fi}"):
                        udata["favoritos"].pop(fi)
                        save()
                        st.rerun()

# ── RODAPÉ ────────────────────────────────────────────────────────────────────
st.markdown(f"""<div style="text-align:center;color:#1e293b;font-size:0.7rem;margin-top:2.5rem;
  padding:0.8rem 0;border-top:1px solid #1e2a3a">
  ⚡ NutriFlow v4 · @{uname} · <code style="color:#1e293b">{DATA_FILE}</code>
</div>""", unsafe_allow_html=True)