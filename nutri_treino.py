import streamlit as st
import json, os, hashlib, random, re
from datetime import date, timedelta, datetime
from pathlib import Path
import pandas as pd

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="NutriFlow", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

DATA_FILE  = "nutriflow_users.json"
PHOTOS_DIR = Path("nutriflow_fotos")
PHOTOS_DIR.mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# HTML HELPER
# ══════════════════════════════════════════════════════════════════════════════
def H(html: str):
    st.markdown(html, unsafe_allow_html=True)

def card(inner: str, extra_style: str = "") -> str:
    return f'<div style="background:var(--card);border:1px solid var(--border);border-radius:20px;padding:1.4rem 1.6rem;margin-bottom:1rem;box-shadow:var(--shadow);{extra_style}">{inner}</div>'

def row_between(left: str, right: str, extra: str = "") -> str:
    return f'<div style="display:flex;justify-content:space-between;align-items:center;{extra}">{left}{right}</div>'

def syne(txt: str, size="1rem", color="var(--text-primary)", weight=700) -> str:
    return f'<span style="font-family:Syne,sans-serif;font-size:{size};font-weight:{weight};color:{color}">{txt}</span>'

def label(txt: str, color="var(--text-muted)") -> str:
    return f'<span style="font-size:0.72rem;color:{color};text-transform:uppercase;letter-spacing:0.08em">{txt}</span>'

def spacer(rem=0.8):
    H(f'<div style="margin-top:{rem}rem"></div>')

# ══════════════════════════════════════════════════════════════════════════════
# BANCO DE ALIMENTOS
# ══════════════════════════════════════════════════════════════════════════════
BANCO_ALIMENTOS = {
    "Arroz branco cozido":    {"kcal_100g": 130,  "unidade": "g",    "emoji": "🍚", "proteina": 2.7,  "carbo": 28.0, "gordura": 0.3},
    "Arroz integral cozido":  {"kcal_100g": 124,  "unidade": "g",    "emoji": "🍚", "proteina": 2.6,  "carbo": 26.0, "gordura": 1.0},
    "Macarrao cozido":        {"kcal_100g": 158,  "unidade": "g",    "emoji": "🍝", "proteina": 5.8,  "carbo": 30.9, "gordura": 0.9},
    "Batata-doce cozida":     {"kcal_100g": 86,   "unidade": "g",    "emoji": "🍠", "proteina": 1.6,  "carbo": 20.1, "gordura": 0.1},
    "Batata inglesa cozida":  {"kcal_100g": 77,   "unidade": "g",    "emoji": "🥔", "proteina": 2.0,  "carbo": 17.0, "gordura": 0.1},
    "Pao integral":           {"kcal_100g": 247,  "unidade": "g",    "emoji": "🍞", "proteina": 9.0,  "carbo": 44.0, "gordura": 3.4},
    "Aveia em flocos":        {"kcal_100g": 370,  "unidade": "g",    "emoji": "🥣", "proteina": 13.9, "carbo": 66.6, "gordura": 7.0},
    "Tapioca":                {"kcal_100g": 323,  "unidade": "g",    "emoji": "🫓", "proteina": 0.2,  "carbo": 80.0, "gordura": 0.2},
    "Mandioca cozida":        {"kcal_100g": 125,  "unidade": "g",    "emoji": "🌿", "proteina": 1.0,  "carbo": 30.1, "gordura": 0.3},
    "Frango grelhado peito":  {"kcal_100g": 165,  "unidade": "g",    "emoji": "🍗", "proteina": 31.0, "carbo": 0.0,  "gordura": 3.6},
    "Carne bovina grelhada":  {"kcal_100g": 215,  "unidade": "g",    "emoji": "🥩", "proteina": 26.0, "carbo": 0.0,  "gordura": 12.0},
    "Ovo inteiro":            {"kcal_100g": 155,  "unidade": "unid", "emoji": "🥚", "kcal_unid": 78,  "proteina": 6.3,  "carbo": 0.6, "gordura": 5.3},
    "Clara de ovo":           {"kcal_100g": 52,   "unidade": "unid", "emoji": "🥚", "kcal_unid": 17,  "proteina": 3.6,  "carbo": 0.2, "gordura": 0.0},
    "Atum em lata":           {"kcal_100g": 116,  "unidade": "g",    "emoji": "🐟", "proteina": 25.5, "carbo": 0.0,  "gordura": 1.0},
    "Salmao grelhado":        {"kcal_100g": 208,  "unidade": "g",    "emoji": "🐟", "proteina": 20.0, "carbo": 0.0,  "gordura": 13.0},
    "Tilapia grelhada":       {"kcal_100g": 128,  "unidade": "g",    "emoji": "🐟", "proteina": 26.0, "carbo": 0.0,  "gordura": 2.7},
    "Whey protein":           {"kcal_100g": 400,  "unidade": "g",    "emoji": "💪", "proteina": 80.0, "carbo": 6.0,  "gordura": 3.0},
    "Feijao cozido":          {"kcal_100g": 76,   "unidade": "g",    "emoji": "🫘", "proteina": 4.8,  "carbo": 13.6, "gordura": 0.5},
    "Lentilha cozida":        {"kcal_100g": 116,  "unidade": "g",    "emoji": "🫘", "proteina": 9.0,  "carbo": 20.0, "gordura": 0.4},
    "Grao-de-bico cozido":    {"kcal_100g": 164,  "unidade": "g",    "emoji": "🫘", "proteina": 8.9,  "carbo": 27.0, "gordura": 2.6},
    "Iogurte grego zero":     {"kcal_100g": 57,   "unidade": "g",    "emoji": "🥛", "proteina": 10.0, "carbo": 3.6,  "gordura": 0.4},
    "Queijo cottage":         {"kcal_100g": 98,   "unidade": "g",    "emoji": "🧀", "proteina": 11.1, "carbo": 3.4,  "gordura": 4.3},
    "Leite desnatado":        {"kcal_100g": 35,   "unidade": "ml",   "emoji": "🥛", "proteina": 3.4,  "carbo": 4.8,  "gordura": 0.1},
    "Azeite de oliva":        {"kcal_100g": 884,  "unidade": "ml",   "emoji": "🫒", "proteina": 0.0,  "carbo": 0.0,  "gordura": 100.0},
    "Abacate":                {"kcal_100g": 160,  "unidade": "g",    "emoji": "🥑", "proteina": 2.0,  "carbo": 9.0,  "gordura": 14.7},
    "Amendoim torrado":       {"kcal_100g": 567,  "unidade": "g",    "emoji": "🥜", "proteina": 25.8, "carbo": 16.1, "gordura": 49.2},
    "Pasta de amendoim":      {"kcal_100g": 588,  "unidade": "g",    "emoji": "🥜", "proteina": 25.0, "carbo": 20.0, "gordura": 50.0},
    "Banana":                 {"kcal_100g": 89,   "unidade": "unid", "emoji": "🍌", "kcal_unid": 105, "proteina": 1.1, "carbo": 23.0, "gordura": 0.3},
    "Maca":                   {"kcal_100g": 52,   "unidade": "unid", "emoji": "🍎", "kcal_unid": 95,  "proteina": 0.3, "carbo": 14.0, "gordura": 0.2},
    "Mamao papaia":           {"kcal_100g": 43,   "unidade": "g",    "emoji": "🍈", "proteina": 0.5,  "carbo": 10.8, "gordura": 0.3},
    "Laranja":                {"kcal_100g": 47,   "unidade": "unid", "emoji": "🍊", "kcal_unid": 62,  "proteina": 0.9, "carbo": 11.8, "gordura": 0.1},
    "Morango":                {"kcal_100g": 32,   "unidade": "g",    "emoji": "🍓", "proteina": 0.7,  "carbo": 7.7,  "gordura": 0.3},
    "Brocolis cozido":        {"kcal_100g": 35,   "unidade": "g",    "emoji": "🥦", "proteina": 2.4,  "carbo": 6.6,  "gordura": 0.4},
    "Espinafre cozido":       {"kcal_100g": 23,   "unidade": "g",    "emoji": "🥬", "proteina": 3.0,  "carbo": 3.6,  "gordura": 0.3},
    "Cenoura cozida":         {"kcal_100g": 41,   "unidade": "g",    "emoji": "🥕", "proteina": 0.9,  "carbo": 9.6,  "gordura": 0.2},
    "Tomate":                 {"kcal_100g": 18,   "unidade": "g",    "emoji": "🍅", "proteina": 0.9,  "carbo": 3.9,  "gordura": 0.2},
    "Granola":                {"kcal_100g": 471,  "unidade": "g",    "emoji": "🥣", "proteina": 10.0, "carbo": 64.0, "gordura": 20.0},
    "Barra de proteina":      {"kcal_100g": 370,  "unidade": "unid", "emoji": "🍫", "kcal_unid": 200, "proteina": 20.0, "carbo": 25.0, "gordura": 7.0},
    "Alcatra s/ gordura grelhada": {"kcal_100g": 134, "unidade": "g", "emoji": "🥩", "proteina": 23.5, "carbo": 0.0, "gordura": 4.5},
    "Miolo de Alcatra grelhado":   {"kcal_100g": 243, "unidade": "g", "emoji": "🥩", "proteina": 30.4, "carbo": 0.0, "gordura": 12.5},
    "Contrafilé s/ gordura":       {"kcal_100g": 160, "unidade": "g", "emoji": "🥩", "proteina": 25.0, "carbo": 0.0, "gordura": 6.0},
    "Capa de Contrafilé":          {"kcal_100g": 300, "unidade": "g", "emoji": "🥩", "proteina": 29.2, "carbo": 0.0, "gordura": 20.0},
    "Coxão Duro":                  {"kcal_100g": 210, "unidade": "g", "emoji": "🥩", "proteina": 28.0, "carbo": 0.0, "gordura": 10.0},
    "Coxão Mole":                  {"kcal_100g": 170, "unidade": "g", "emoji": "🥩", "proteina": 29.0, "carbo": 0.0, "gordura": 6.0},
    "Fraldinha grelhada":          {"kcal_100g": 185, "unidade": "g", "emoji": "🥩", "proteina": 24.0, "carbo": 0.0, "gordura": 9.8},
    "Músculo cozido":              {"kcal_100g": 190, "unidade": "g", "emoji": "🥩", "proteina": 31.0, "carbo": 0.0, "gordura": 7.0},
    "Paleta cozida":               {"kcal_100g": 195, "unidade": "g", "emoji": "🥩", "proteina": 27.0, "carbo": 0.0, "gordura": 9.5},
    "Patinho (Corte Magro)":       {"kcal_100g": 133, "unidade": "g", "emoji": "🥩", "proteina": 35.9, "carbo": 0.0, "gordura": 4.5},
    "Ponta de Agulha":             {"kcal_100g": 250, "unidade": "g", "emoji": "🥩", "proteina": 21.0, "carbo": 0.0, "gordura": 18.0},
    "Vazio (Fraldinha)":           {"kcal_100g": 190, "unidade": "g", "emoji": "🥩", "proteina": 26.0, "carbo": 0.0, "gordura": 9.0},
    "Rabo de boi (ensopado)":      {"kcal_100g": 310, "unidade": "g", "emoji": "🥩", "proteina": 18.0, "carbo": 0.0, "gordura": 26.0},
    "Língua de boi":               {"kcal_100g": 215, "unidade": "g", "emoji": "👅", "proteina": 15.0, "carbo": 3.7, "gordura": 16.0},
    "Fígado de boi grelhado":      {"kcal_100g": 140, "unidade": "g", "emoji": "🥩", "proteina": 21.0, "carbo": 4.0, "gordura": 4.5},
    # --- CORTES SUÍNOS (PORCO) ---
    "Lombo suíno assado":          {"kcal_100g": 210, "unidade": "g", "emoji": "🍖", "proteina": 31.0, "carbo": 0.0, "gordura": 8.5},
    "Filé Mignon suíno":           {"kcal_100g": 145, "unidade": "g", "emoji": "🥩", "proteina": 26.0, "carbo": 0.0, "gordura": 4.0},
    "Pernil assado":               {"kcal_100g": 260, "unidade": "g", "emoji": "🍖", "proteina": 28.0, "carbo": 0.0, "gordura": 16.0},
    "Bisteca de porco grelhada":   {"kcal_100g": 230, "unidade": "g", "emoji": "🥩", "proteina": 24.0, "carbo": 0.0, "gordura": 14.0},
    "Costelinha de porco assada":  {"kcal_100g": 310, "unidade": "g", "emoji": "🍖", "proteina": 18.0, "carbo": 0.0, "gordura": 26.0},
    "Alcatra suína":               {"kcal_100g": 160, "unidade": "g", "emoji": "🥩", "proteina": 26.0, "carbo": 0.0, "gordura": 6.0},
    "Paleta suína assada":         {"kcal_100g": 240, "unidade": "g", "emoji": "🥩", "proteina": 22.0, "carbo": 0.0, "gordura": 17.0},
    "Copa Lombo":                  {"kcal_100g": 180, "unidade": "g", "emoji": "🥩", "proteina": 20.0, "carbo": 0.0, "gordura": 11.0},
    "Leitão assado":               {"kcal_100g": 311, "unidade": "g", "emoji": "🐖", "proteina": 24.0, "carbo": 0.0, "gordura": 23.0},
    "Joelho de porco (Eisbein)":   {"kcal_100g": 280, "unidade": "g", "emoji": "🍖", "proteina": 22.0, "carbo": 0.0, "gordura": 21.0},
    "Tripa de porco frita":        {"kcal_100g": 450, "unidade": "g", "emoji": "🥓", "proteina": 15.0, "carbo": 0.0, "gordura": 44.0},
    "Orelha de porco (cozida)":    {"kcal_100g": 165, "unidade": "g", "emoji": "👂", "proteina": 20.0, "carbo": 0.0, "gordura": 9.0},
    "Pé de porco (cozido)":        {"kcal_100g": 195, "unidade": "g", "emoji": "🦶", "proteina": 19.0, "carbo": 0.0, "gordura": 13.0},
    # --- MIÚDOS E VÍSCERAS ---
    "Coração de boi":              {"kcal_100g": 160, "unidade": "g", "emoji": "❤️", "proteina": 20.0, "carbo": 0.0, "gordura": 8.5},
    "Moela de frango cozida":      {"kcal_100g": 150, "unidade": "g", "emoji": "🍗", "proteina": 30.0, "carbo": 0.0, "gordura": 2.5},
    "Bucho bovino (dobradinha)":   {"kcal_100g": 130, "unidade": "g", "emoji": "🍲", "proteina": 15.0, "carbo": 0.0, "gordura": 7.5},
    "Rins de boi":                 {"kcal_100g": 110, "unidade": "g", "emoji": "🥩", "proteina": 17.0, "carbo": 0.8, "gordura": 4.0},
    # --- CORTES BOVINOS MAGROS (Excelentes para dieta) ---
    "Patinho grelhado/moído": {"kcal_100g": 219, "unidade": "g", "emoji": "🥩", "proteina": 35.9, "carbo": 0.0, "gordura": 7.3},
    "Maminha grelhada":       {"kcal_100g": 153, "unidade": "g", "emoji": "🥩", "proteina": 24.0, "carbo": 0.0, "gordura": 6.0},
    "Lagarto cozido":         {"kcal_100g": 170, "unidade": "g", "emoji": "🥩", "proteina": 28.0, "carbo": 0.0, "gordura": 6.0},
    "Filé Mignon grelhado":   {"kcal_100g": 220, "unidade": "g", "emoji": "🥩", "proteina": 26.0, "carbo": 0.0, "gordura": 12.0},
    "Coxão mole grelhado":    {"kcal_100g": 219, "unidade": "g", "emoji": "🥩", "proteina": 32.0, "carbo": 0.0, "gordura": 8.9},
    # --- CORTES BOVINOS GORDOS (Cuidado com a porção) ---
    "Picanha (com gordura)":  {"kcal_100g": 310, "unidade": "g", "emoji": "🥩", "proteina": 23.8, "carbo": 0.0, "gordura": 23.5},
    "Cupim cozido":           {"kcal_100g": 330, "unidade": "g", "emoji": "🥩", "proteina": 19.0, "carbo": 0.0, "gordura": 28.0},
    "Costela bovina assada":  {"kcal_100g": 350, "unidade": "g", "emoji": "🥩", "proteina": 18.0, "carbo": 0.0, "gordura": 31.0},
    "Contrafilé grelhado":    {"kcal_100g": 250, "unidade": "g", "emoji": "🥩", "proteina": 28.0, "carbo": 0.0, "gordura": 15.0},
    "Acém moído/cozido":      {"kcal_100g": 215, "unidade": "g", "emoji": "🥩", "proteina": 25.0, "carbo": 0.0, "gordura": 12.0},
    # --- AVES (Frango e Peru) ---
    "Coração de frango":      {"kcal_100g": 170, "unidade": "g", "emoji": "🍢", "proteina": 15.0, "carbo": 1.0,  "gordura": 12.0},
    "Asinha de frango (frita)":{"kcal_100g": 300, "unidade": "unid", "emoji": "🍗", "kcal_unid": 110, "proteina": 18.0, "carbo": 0.0, "gordura": 25.0},
    "Coxa de frango (c/ pele)":{"kcal_100g": 215, "unidade": "g", "emoji": "🍗", "proteina": 20.0, "carbo": 0.0, "gordura": 15.0},
    "Frango desfiado":        {"kcal_100g": 160, "unidade": "g", "emoji": "🍗", "proteina": 30.0, "carbo": 0.0, "gordura": 3.5},
    # --- CARNE SUÍNA (Porco) ---
    "Bacon frito":            {"kcal_100g": 540, "unidade": "fatia", "emoji": "🥓", "kcal_unid": 45, "proteina": 37.0, "carbo": 1.5, "gordura": 42.0},
    "Panceta/Torresmo":       {"kcal_100g": 520, "unidade": "g", "emoji": "🥓", "proteina": 15.0, "carbo": 0.0, "gordura": 50.0},
    "Presunto de Parma":      {"kcal_100g": 230, "unidade": "g", "emoji": "🍖", "proteina": 25.0, "carbo": 0.0, "gordura": 15.0},
    "Salame":                 {"kcal_100g": 400, "unidade": "fatia", "emoji": "🍕", "kcal_unid": 25, "proteina": 20.0, "carbo": 1.0, "gordura": 35.0},
    # --- PEIXES E FRUTOS DO MAR ---
    "Bacalhau cozido":        {"kcal_100g": 90,  "unidade": "g", "emoji": "🐟", "proteina": 20.0, "carbo": 0.0,  "gordura": 1.0},
    "Camarão grelhado":       {"kcal_100g": 110, "unidade": "g", "emoji": "🍤", "proteina": 22.0, "carbo": 0.0,  "gordura": 2.0},
    "Caranguejo/Siri":        {"kcal_100g": 85,  "unidade": "g", "emoji": "🦀", "proteina": 18.0, "carbo": 0.0,  "gordura": 1.0},
    "Mexilhão cozido":        {"kcal_100g": 80,  "unidade": "g", "emoji": "🦪", "proteina": 12.0, "carbo": 3.0,  "gordura": 2.0},
    # --- CARNES EXÓTICAS E OUTRAS ---
    "Carne de Cordeiro":      {"kcal_100g": 250, "unidade": "g", "emoji": "🍖", "proteina": 20.0, "carbo": 0.0,  "gordura": 18.0},
    "Carne de Coelho":        {"kcal_100g": 130, "unidade": "g", "emoji": "🐇", "proteina": 22.0, "carbo": 0.0,  "gordura": 4.0},
    "Carne de Pato":          {"kcal_100g": 330, "unidade": "g", "emoji": "🦆", "proteina": 18.0, "carbo": 0.0,  "gordura": 28.0},
    # --- PADARIA E CAFÉ DA MANHÃ ---
    "Pão de sal (Francês)":   {"kcal_100g": 300,  "unidade": "unid", "emoji": "🥖", "kcal_unid": 150, "proteina": 4.5,  "carbo": 29.0, "gordura": 1.5},
    "Pão de queijo":          {"kcal_100g": 350,  "unidade": "unid", "emoji": "🧀", "kcal_unid": 90,  "proteina": 2.5,  "carbo": 12.0, "gordura": 4.5},
    "Biscoito de sal (Cream cracker)": {"kcal_100g": 440, "unidade": "g", "emoji": "🍪", "proteina": 8.0,  "carbo": 65.0, "gordura": 16.0},
    "Bolo simples (caseiro)": {"kcal_100g": 320,  "unidade": "g",    "emoji": "🍰", "proteina": 4.8,  "carbo": 52.0, "gordura": 10.0},
    "Cuscuz de milho":        {"kcal_100g": 113,  "unidade": "g",    "emoji": "🌽", "proteina": 2.2,  "carbo": 25.0, "gordura": 0.6},
    "Requeijão cremoso":      {"kcal_100g": 257,  "unidade": "g",    "emoji": "🥄", "proteina": 9.5,  "carbo": 3.5,  "gordura": 23.0},
    "Margarina":              {"kcal_100g": 717,  "unidade": "g",    "emoji": "🧈", "proteina": 0.0,  "carbo": 0.0,  "gordura": 80.0},
    # --- PROTEÍNAS (MAIS CORTES E OPÇÕES) ---
    "Carne de Porco (Costela)": {"kcal_100g": 310, "unidade": "g",    "emoji": "🥩", "proteina": 20.0, "carbo": 0.0,  "gordura": 25.0},
    "Bife de Fígado":         {"kcal_100g": 140,  "unidade": "g",    "emoji": "🥩", "proteina": 21.0, "carbo": 4.0,  "gordura": 4.5},
    "Linguiça de churrasco":  {"kcal_100g": 300,  "unidade": "g",    "emoji": "🌭", "proteina": 15.0, "carbo": 2.0,  "gordura": 26.0},
    "Salsicha":               {"kcal_100g": 230,  "unidade": "unid", "emoji": "🌭", "kcal_unid": 115, "proteina": 12.0, "carbo": 2.5,  "gordura": 20.0},
    "Omelete simples (2 ovos)": {"kcal_100g": 170, "unidade": "unid", "emoji": "🍳", "kcal_unid": 154, "proteina": 13.0, "carbo": 1.2,  "gordura": 11.0},
    "Nuggets de frango":      {"kcal_100g": 290,  "unidade": "unid", "emoji": "🍗", "kcal_unid": 45,  "proteina": 13.0, "carbo": 18.0, "gordura": 18.0},
    # --- SELF-SERVICE E PRATOS TÍPICOS ---
    "Farofa de ovos":         {"kcal_100g": 350,  "unidade": "g",    "emoji": "🥘", "proteina": 6.0,  "carbo": 45.0, "gordura": 16.0},
    "Lasanha à Bolonhesa":    {"kcal_100g": 180,  "unidade": "g",    "emoji": "🥘", "proteina": 10.0, "carbo": 18.0, "gordura": 8.0},
    "Strogonoff de Frango":   {"kcal_100g": 160,  "unidade": "g",    "emoji": "🥘", "proteina": 14.0, "carbo": 6.0,  "gordura": 9.0},
    "Empadão de frango":      {"kcal_100g": 280,  "unidade": "g",    "emoji": "🥧", "proteina": 9.0,  "carbo": 30.0, "gordura": 14.0},
    "Yakisoba":               {"kcal_100g": 120,  "unidade": "g",    "emoji": "🥢", "proteina": 6.0,  "carbo": 16.0, "gordura": 4.0},
    "Sushi (Uramaki médio)":  {"kcal_100g": 150,  "unidade": "unid", "emoji": "🍣", "kcal_unid": 35,  "proteina": 4.0,  "carbo": 25.0, "gordura": 3.0},
    # --- FRUTAS EXTRA ---
    "Açaí (polpa pura)":      {"kcal_100g": 60,   "unidade": "g",    "emoji": "🍧", "proteina": 1.0,  "carbo": 4.0,  "gordura": 5.0},
    "Abacaxi (fatia)":        {"kcal_100g": 50,   "unidade": "unid", "emoji": "🍍", "kcal_unid": 40,  "proteina": 0.5,  "carbo": 12.0, "gordura": 0.1},
    "Goiaba vermelha":        {"kcal_100g": 68,   "unidade": "unid", "emoji": "🍈", "kcal_unid": 60,  "proteina": 2.5,  "carbo": 14.0, "gordura": 0.9},
    "Limão (suco)":           {"kcal_100g": 22,   "unidade": "ml",   "emoji": "🍋", "proteina": 0.4,  "carbo": 7.0,  "gordura": 0.1},
    "Melão":                  {"kcal_100g": 34,   "unidade": "g",    "emoji": "🍈", "proteina": 0.8,  "carbo": 8.0,  "gordura": 0.2},
    # --- VEGETAIS E FOLHAS ---
    "Abóbora Cabotiá":        {"kcal_100g": 48,   "unidade": "g",    "emoji": "🎃", "proteina": 1.5,  "carbo": 10.0, "gordura": 0.5},
    "Rúcula":                 {"kcal_100g": 25,   "unidade": "g",    "emoji": "🥗", "proteina": 2.6,  "carbo": 3.7,  "gordura": 0.7},
    "Palmito em conserva":    {"kcal_100g": 30,   "unidade": "g",    "emoji": "🥗", "proteina": 2.0,  "carbo": 5.0,  "gordura": 0.2},
    "Milho de pipoca (grão)": {"kcal_100g": 350,  "unidade": "g",    "emoji": "🍿", "proteina": 10.0, "carbo": 70.0, "gordura": 4.0},
    "Ervilha em conserva":    {"kcal_100g": 81,   "unidade": "g",    "emoji": "🟢", "proteina": 5.0,  "carbo": 14.0, "gordura": 0.4},
    # --- PETISCOS E SOBREMESAS ---
    "Pudim de leite":         {"kcal_100g": 300,  "unidade": "g",    "emoji": "🍮", "proteina": 6.0,  "carbo": 50.0, "gordura": 8.0},
    "Doce de leite":          {"kcal_100g": 315,  "unidade": "g",    "emoji": "🍯", "proteina": 6.0,  "carbo": 55.0, "gordura": 7.0},
    "Gelatina (preparada)":   {"kcal_100g": 60,   "unidade": "g",    "emoji": "🍮", "proteina": 1.5,  "carbo": 14.0, "gordura": 0.0},
    "Paçoca":                 {"kcal_100g": 490,  "unidade": "unid", "emoji": "🥜", "kcal_unid": 110, "proteina": 12.0, "carbo": 50.0, "gordura": 28.0},
    "Chocolate amargo 70%":   {"kcal_100g": 550,  "unidade": "g",    "emoji": "🍫", "proteina": 8.0,  "carbo": 35.0, "gordura": 42.0},
    "Castanha de Caju":       {"kcal_100g": 580,  "unidade": "g",    "emoji": "🥜", "proteina": 18.0, "carbo": 30.0, "gordura": 46.0},
    # --- SUPLEMENTOS E OUTROS ---
    "Creatina":               {"kcal_100g": 0,    "unidade": "g",    "emoji": "⚡", "proteina": 0.0,  "carbo": 0.0,  "gordura": 0.0},
    "BCAA":                   {"kcal_100g": 0,    "unidade": "g",    "emoji": "💊", "proteina": 0.0,  "carbo": 0.0,  "gordura": 0.0},
    "Azeite (colher sopa)":   {"kcal_100g": 884,  "unidade": "unid", "emoji": "🫒", "kcal_unid": 120, "proteina": 0.0, "carbo": 0.0,  "gordura": 14.0},
    "Suco de Laranja natural": {"kcal_100g": 45,   "unidade": "ml",   "emoji": "🥤", "proteina": 0.7,  "carbo": 10.4, "gordura": 0.2},
    "Cerveja (Pilsen)":       {"kcal_100g": 43,   "unidade": "ml",   "emoji": "🍺", "proteina": 0.5,  "carbo": 3.3,  "gordura": 0.0},
    "Vinho tinto":            {"kcal_100g": 85,   "unidade": "ml",   "emoji": "🍷", "proteina": 0.1,  "carbo": 2.6,  "gordura": 0.0},
    "Refrigerante Cola":      {"kcal_100g": 42,   "unidade": "ml",   "emoji": "🥤", "proteina": 0.0,  "carbo": 10.5, "gordura": 0.0},
    "Refrigerante Zero":      {"kcal_100g": 0,    "unidade": "ml",   "emoji": "🥤", "proteina": 0.0,  "carbo": 0.0,  "gordura": 0.0},
}

UNIDADES_ALIAS = {"g":"g","kg":"g","ml":"ml","l":"ml","unid":"unid","unidade":"unid",
                  "un":"unid","und":"unid","colher":"colher","col":"colher","xicara":"xicara","xic":"xicara",
                  "fatia":"fatia","fat":"fatia","porcao":"g","porção":"g"}

TIPOS_REFEICAO = ["☀️ Cafe da manha","🍎 Lanche da manha","🍽️ Almoco","🍪 Lanche da tarde","🌙 Jantar","🌛 Ceia"]
GRUPOS_TREINO  = ["Selecione","Peito e Triceps","Costas e Biceps","Ombros","Pernas Quadriceps",
                  "Pernas Posterior/Gluteos","Full Body","HIIT / Cardio","Funcional",
                  "Mobilidade / Alongamento","Descanso","Outro"]
NIVEL_ATIVIDADE = {"Sedentario (sem exercicio)":1.2,"Levemente ativo (1-3x/semana)":1.375,
                   "Moderadamente ativo (3-5x/semana)":1.55,"Muito ativo (6-7x/semana)":1.725,
                   "Extremamente ativo (2x/dia)":1.9}

NIVEIS = [
    {"nome":"Iniciante",     "emoji":"🌱","min_pts":0},
    {"nome":"Consistente",   "emoji":"📒","min_pts":50},
    {"nome":"Focado",        "emoji":"🎯","min_pts":150},
    {"nome":"Dedicado",      "emoji":"💪","min_pts":350},
    {"nome":"Atleta",        "emoji":"🏃","min_pts":750},
    {"nome":"Monstro",       "emoji":"🔥","min_pts":1500},
    {"nome":"Lenda",         "emoji":"👑","min_pts":3000},
]

CONQUISTAS = [
    {"id":"primeiro_registro","emoji":"🌟","nome":"Primeira Refeicao",   "desc":"Registrou sua primeira refeicao",           "pts":10},
    {"id":"meta_dia",         "emoji":"🎯","nome":"Meta Batida",          "desc":"Atingiu a meta calorica",                   "pts":25},
    {"id":"streak_3",         "emoji":"🔥","nome":"Em Chamas",            "desc":"3 dias seguidos de treino",                 "pts":30},
    {"id":"streak_7",         "emoji":"💥","nome":"Semana Perfeita",      "desc":"7 dias seguidos de treino",                 "pts":75},
    {"id":"streak_30",        "emoji":"🏆","nome":"Maquina",              "desc":"30 dias seguidos de treino",                "pts":300},
    {"id":"treino_10",        "emoji":"💪","nome":"10 Treinos",           "desc":"10 treinos concluidos",                     "pts":50},
    {"id":"treino_50",        "emoji":"🦾","nome":"Atleta",               "desc":"50 treinos concluidos",                    "pts":200},
    {"id":"log_7",            "emoji":"📒","nome":"Habito em Formacao",   "desc":"7 dias com alimentacao registrada",        "pts":50},
    {"id":"log_30",           "emoji":"📅","nome":"Habito Formado",       "desc":"30 dias com alimentacao registrada",       "pts":200},
    {"id":"modo_rapido",      "emoji":"⚡","nome":"Modo Rapido",          "desc":"Usou o modo rapido pela primeira vez",     "pts":15},
    {"id":"kcal_1000",        "emoji":"🍽️","nome":"Primeiro Dia Cheio",  "desc":"Registrou 1000+ kcal em um dia",           "pts":15},
    {"id":"social_share",     "emoji":"📣","nome":"Social",               "desc":"Compartilhou conquista no feed",            "pts":20},
]

DICAS = [
    ("💧 Hidratacao","Beba 35ml de agua por kg de peso/dia. Hidratacao adequada melhora o metabolismo e reduz a fome."),
    ("🥦 Vegetais no prato","Encha metade do prato com vegetais coloridos — ricos em fibras e baixa densidade calorica."),
    ("🍗 Proteina em cada refeicao","Inclua proteina magra em todas as refeicoes para saciedade e preservar massa muscular."),
    ("🍚 Carboidratos complexos","Prefira arroz integral, batata-doce e aveia para energia sustentada ao longo do dia."),
    ("🛌 Sono e peso","Dormir menos de 7h aumenta os hormonios da fome em ate 15%. Priorize o descanso!"),
    ("🥑 Gorduras boas","Abacate, azeite e oleaginosas contem gorduras essenciais que regulam hormonios."),
    ("📊 Deficit calorico","Um deficit de 500 kcal/dia resulta em ~0,5kg de perda de gordura por semana."),
    ("🏋️ Musculacao","Musculacao aumenta o metabolismo basal permanentemente, mesmo em repouso."),
    ("🍌 Pos-treino","Proteina + carboidrato em ate 1h apos o treino maximiza a recuperacao muscular."),
    ("⚡ Modo Rapido","Use o Modo Rapido! Digite 'frango 150g arroz 100g' e adicione tudo de uma vez."),
]

# ══════════════════════════════════════════════════════════════════════════════
# UTILITÁRIOS
# ══════════════════════════════════════════════════════════════════════════════
def load_all_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE,"r",encoding="utf-8") as f: return json.load(f)
    return {"usuarios":{}}

def save_all_data(d):
    with open(DATA_FILE,"w",encoding="utf-8") as f: json.dump(d,f,ensure_ascii=False,indent=2)

def hash_senha(s): return hashlib.sha256(s.encode()).hexdigest()

def save_photo(uf, cat, user, dia):
    fp = PHOTOS_DIR / f"{user}_{cat}_{dia}_{uf.name}"
    with open(fp,"wb") as f: f.write(uf.getbuffer())
    return str(fp)

def calcular_tmb(peso,altura,idade,sexo):
    return (10*peso+6.25*altura-5*idade+5) if sexo=="Masculino" else (10*peso+6.25*altura-5*idade-161)

def calcular_meta(perfil,objetivo):
    tmb  = calcular_tmb(perfil["peso"],perfil["altura"],perfil["idade"],perfil["sexo"])
    tdee = tmb * NIVEL_ATIVIDADE.get(perfil["atividade"],1.55)
    delta = {"Manutencao":0,"Perda saudavel (-0,5kg/sem)":-500,"Perda agressiva (-1kg/sem)":-1000,"Ganho muscular":300}
    return round(tdee + delta.get(objetivo,0))

def buscar_alimentos(query):
    if not query or len(query)<2: return []
    q = query.lower()
    return [k for k in BANCO_ALIMENTOS if q in k.lower()][:8]

def kcal_item(nome, qtd, un):
    info = BANCO_ALIMENTOS.get(nome)
    if not info: return 0.0
    if un=="unid" and "kcal_unid" in info: return round(info["kcal_unid"]*qtd,1)
    return round(info["kcal_100g"]*qtd/100,1)

def macros_item(nome, qtd, un):
    info = BANCO_ALIMENTOS.get(nome)
    if not info: return {"p":0,"c":0,"g":0}
    fator = qtd/100 if un!="unid" else (qtd if "kcal_unid" not in info else 1)
    return {k: round(info.get(k,0)*fator,1) for k in ["proteina","carbo","gordura"]}

def _macros_normalized(macro_dict):
    """Normalize macro dict to p/c/g keys"""
    return {
        "p": macro_dict.get("p", macro_dict.get("proteina", 0)),
        "c": macro_dict.get("c", macro_dict.get("carbo", 0)),
        "g": macro_dict.get("g", macro_dict.get("gordura", 0)),
    }

def total_kcal(udata, dia): 
    return sum(r.get("kcal", r.get("calorias", 0)) for r in udata["alimentacao"].get(dia,[]))

def total_macros(udata, dia):
    t={"p":0.0,"c":0.0,"g":0.0}
    for r in udata["alimentacao"].get(dia,[]):
        t["p"] += r.get("p", r.get("proteina", 0))
        t["c"] += r.get("c", r.get("carbo", 0))
        t["g"] += r.get("g", r.get("gordura", 0))
    return {k:round(v,1) for k,v in t.items()}

def _streak(ud):
    hoje=date.today(); s=0
    for i in range(365):
        d=(hoje-timedelta(days=i)).isoformat()
        if ud["treinos"].get(d,{}).get("concluido"): s+=1
        elif i>0: break
    return s

def calcular_pontos(ud):
    return sum(c["pts"] for c in CONQUISTAS if c["id"] in ud.get("conquistas",[]))

def calcular_nivel(pts):
    nivel=NIVEIS[0]; prox=None
    for i,n in enumerate(NIVEIS):
        if pts>=n["min_pts"]:
            nivel=n; prox=NIVEIS[i+1] if i+1<len(NIVEIS) else None
    return nivel,prox

def dias_usando_app(ud):
    return len([d for d,v in ud["alimentacao"].items() if v])

def verificar_conquistas(ud):
    ul=ud.get("conquistas",[]); novas=[]
    checks={
        "primeiro_registro": lambda: any(ud["alimentacao"].values()),
        "meta_dia":    lambda: any(sum(r.get("kcal",r.get("calorias",0)) for r in v)>=ud.get("meta_calorias",2000)*0.95 for v in ud["alimentacao"].values() if v),
        "streak_3":    lambda: _streak(ud)>=3,
        "streak_7":    lambda: _streak(ud)>=7,
        "streak_30":   lambda: _streak(ud)>=30,
        "treino_10":   lambda: sum(1 for t in ud["treinos"].values() if t.get("concluido"))>=10,
        "treino_50":   lambda: sum(1 for t in ud["treinos"].values() if t.get("concluido"))>=50,
        "log_7":       lambda: dias_usando_app(ud)>=7,
        "log_30":      lambda: dias_usando_app(ud)>=30,
        "kcal_1000":   lambda: any(sum(r.get("kcal",r.get("calorias",0)) for r in v)>=1000 for v in ud["alimentacao"].values() if v),
        "modo_rapido": lambda: ud.get("usou_modo_rapido",False),
        "social_share":lambda: ud.get("usou_social_share",False),
    }
    for c in CONQUISTAS:
        if c["id"] not in ul:
            try:
                if checks.get(c["id"],lambda:False)():
                    novas.append(c); ul.append(c["id"])
            except: pass
    if novas: ud["conquistas"]=ul
    return novas

def parse_quick_add(texto):
    if not texto.strip(): return []
    tokens = texto.lower().strip().split()
    results = []
    i = 0
    while i < len(tokens):
        nome_partes = []
        qtd = None
        un  = "g"
        while i < len(tokens) and not re.match(r"^\d+([.,]\d+)?$", tokens[i]):
            nome_partes.append(tokens[i])
            i += 1
        if i < len(tokens) and re.match(r"^\d+([.,]\d+)?$", tokens[i]):
            qtd = float(tokens[i].replace(",","."))
            i += 1
            if i < len(tokens) and tokens[i] in UNIDADES_ALIAS:
                un = UNIDADES_ALIAS[tokens[i]]
                i += 1
        if not nome_partes:
            if qtd and i < len(tokens):
                while i < len(tokens) and tokens[i] not in UNIDADES_ALIAS and not re.match(r"^\d+([.,]\d+)?$",tokens[i]):
                    nome_partes.append(tokens[i])
                    i += 1
        if nome_partes:
            nome_raw = " ".join(nome_partes)
            matches = buscar_alimentos_fuzzy(nome_raw)
            match_nome = matches[0] if matches else None
            qtd_final = qtd if qtd else 100.0
            if match_nome:
                info = BANCO_ALIMENTOS[match_nome]
                un_real = un
                k = kcal_item(match_nome, qtd_final, un_real)
                m = macros_item(match_nome, qtd_final, un_real)
                mn = _macros_normalized(m)
                results.append({"nome":match_nome,"qtd":qtd_final,"un":un_real,"kcal":k,**mn,"encontrado":True,"raw":nome_raw})
            else:
                results.append({"nome":nome_raw,"qtd":qtd_final,"un":un,"kcal":0,"p":0,"c":0,"g":0,"encontrado":False,"raw":nome_raw})
    return [r for r in results if r["qtd"]>0]

def buscar_alimentos_fuzzy(query):
    if not query: return []
    q = query.lower().strip()
    exact = [k for k in BANCO_ALIMENTOS if q in k.lower()]
    if exact: return exact[:3]
    words = q.split()
    scored = {}
    for k in BANCO_ALIMENTOS:
        kl = k.lower()
        score = sum(1 for w in words if w in kl)
        if score > 0: scored[k] = score
    return sorted(scored, key=scored.get, reverse=True)[:3]

def gerar_mensagem_contextual(ud, kcal_hoje, meta, macros, streak, dias_app):
    pct = kcal_hoje/meta*100 if meta>0 else 0
    restante = meta-kcal_hoje
    hora = datetime.now().hour
    prot = macros.get("p",0)
    meta_prot = ud.get("perfil",{}).get("peso",70)*2

    if dias_app == 0 and kcal_hoje == 0:
        return "Bem-vindo! Comece registrando sua primeira refeicao 🚀", "var(--accent-blue)"
    if streak >= 7 and kcal_hoje == 0:
        return f"Sequencia de {streak} dias! Mais um dia para manter o nivel 🏆", "var(--accent-yellow)"
    if kcal_hoje == 0:
        if hora < 10:   return "Bom dia! Cafe da manha registrado melhora o metabolismo ☀️", "var(--accent-blue)"
        elif hora < 14: return "Ja quase meio-dia — registrou o almoco? 🍽️", "var(--accent-blue)"
        elif hora < 19: return f"Boa tarde! Faltam {restante:.0f} kcal para a meta de hoje", "var(--accent-blue)"
        else:           return "Boa noite! Ainda da tempo de registrar o jantar 🌙", "var(--accent-purple)"
    if pct < 25:
        return f"Bom inicio! Faltam {restante:.0f} kcal — ainda tem o dia todo ☀️", "var(--accent-blue)"
    elif pct < 50:
        if prot < meta_prot*0.3: return "Indo bem! Dica: ainda tem pouca proteina hoje 🥩", "var(--accent-blue)"
        return f"Metade do caminho! Faltam {restante:.0f} kcal 🎯", "var(--accent-green)"
    elif pct < 80:
        return f"Excelente ritmo! {pct:.0f}% da meta concluida", "var(--accent-green)"
    elif pct < 95:
        return f"Quase la! Mais {restante:.0f} kcal para completar o dia ✨", "var(--accent-yellow)"
    elif pct <= 108:
        if streak >= 3: return f"Meta batida! {streak} dias seguidos 🔥", "var(--accent-green)"
        return "Meta batida! Dia completo 🎉", "var(--accent-green)"
    else:
        exc = kcal_hoje-meta
        return f"{exc:.0f} kcal acima da meta. Nao esqueça o treino amanha 💪", "var(--accent-red)"

def gerar_insights(ud, meta):
    insights=[]
    hoje=date.today()
    dias_30=[(hoje-timedelta(days=i)).isoformat() for i in range(30)]
    kcals={d:total_kcal(ud,d) for d in dias_30}
    com_dados={d:k for d,k in kcals.items() if k>0}
    if len(com_dados)<2:
        return [{"emoji":"👋","txt":"Registre pelo menos 2 dias para ver seus insights personalizados!"}]
    media=sum(com_dados.values())/len(com_dados)
    insights.append({"emoji":"📊","txt":f"Sua media nos ultimos {len(com_dados)} dias: {media:.0f} kcal/dia"})
    kl=list(com_dados.values())
    if len(kl)>=5:
        rec=sum(kl[:3])/3; ant=sum(kl[-3:])/3
        if rec<ant*0.92:   insights.append({"emoji":"📉","txt":f"Tendencia de queda: ultimos 3 dias estao {ant-rec:.0f} kcal abaixo"})
        elif rec>ant*1.08: insights.append({"emoji":"📈","txt":f"Consumo subindo: ultimos 3 dias em media {rec-ant:.0f} kcal acima"})
    acima=sum(1 for k in com_dados.values() if k>meta*1.05)
    abaixo=sum(1 for k in com_dados.values() if k<meta*0.85)
    if acima>len(com_dados)*0.4:  insights.append({"emoji":"⚠️","txt":f"Voce ultrapassa a meta em {acima}/{len(com_dados)} dias"})
    if abaixo>len(com_dados)*0.4: insights.append({"emoji":"⬇️","txt":f"Voce fica abaixo da meta em {abaixo} dias — risco de deficit excessivo"})
    s=_streak(ud)
    if s>=5:   insights.append({"emoji":"🔥","txt":f"Voce esta em uma sequencia de {s} dias de treino!"})
    elif s==0:
        tot=sum(1 for t in ud["treinos"].values() if t.get("concluido"))
        if tot: insights.append({"emoji":"💪","txt":f"Voce ja fez {tot} treinos. Mantenha a regularidade!"})
    return insights[:5]

def sugerir_frequentes(ud):
    cnt={}
    for refs in ud["alimentacao"].values():
        for r in refs:
            nm=r.get("nome",r.get("alimento",""))
            if nm in BANCO_ALIMENTOS: cnt[nm]=cnt.get(nm,0)+1
    return sorted(cnt,key=cnt.get,reverse=True)[:5] if cnt else []

# ══════════════════════════════════════════════════════════════════════════════
# CSS — DESIGN SYSTEM V7
# Premium dark theme com profundidade, hierarquia e microinterações
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap');

/* ── DESIGN TOKENS ── */
:root {
  /* Backgrounds — progressão de profundidade */
  --bg-base:      #050709;
  --bg-surface:   #090c12;
  --card:         #0d1219;
  --card-hover:   #111722;
  --card-raised:  #131a24;
  
  /* Bordas */
  --border:       #161f2e;
  --border-hover: #1e2d45;
  --border-active:#0e7490;
  
  /* Texto — hierarquia clara */
  --text-primary: #f1f5f9;
  --text-secondary:#94a3b8;
  --text-muted:   #475569;
  --text-faint:   #1e293b;
  
  /* Acentos — com função semântica */
  --accent-blue:  #22d3ee;
  --accent-green: #34d399;
  --accent-yellow:#fbbf24;
  --accent-red:   #fb7185;
  --accent-purple:#a78bfa;
  
  /* Sombras */
  --shadow:       0 4px 24px rgba(0,0,0,.45), 0 1px 3px rgba(0,0,0,.3);
  --shadow-lg:    0 8px 40px rgba(0,0,0,.6);
  --glow-blue:    0 0 20px rgba(34,211,238,.12);
  --glow-green:   0 0 20px rgba(52,211,153,.12);
}

/* ── RESET & BASE ── */
html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif !important;
  background: var(--bg-base) !important;
  color: var(--text-secondary) !important;
  line-height: 1.6;
}
header[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding-top: 1.8rem !important; max-width: 1240px; }

/* ── HERO TITLE ── */
.hero-title {
  font-family: 'Syne', sans-serif;
  font-size: 2.4rem;
  font-weight: 800;
  letter-spacing: -.05em;
  background: linear-gradient(135deg, #22d3ee 0%, #06b6d4 35%, #a78bfa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.1;
}

/* ── METRIC CARDS ── */
.metric-box {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 1.3rem 1rem;
  text-align: center;
  box-shadow: var(--shadow);
  transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
  position: relative;
  overflow: hidden;
}
.metric-box::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,.06), transparent);
}
.metric-box:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  border-color: var(--border-hover);
}
.metric-value {
  font-family: 'Syne', sans-serif;
  font-size: 2.2rem;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -.03em;
  /* Animação de contagem — aplicada via JS */
  animation: countUp .8s ease-out;
}
@keyframes countUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
.metric-label {
  font-size: .68rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: .1em;
  margin-top: .5rem;
  font-weight: 600;
}
.metric-sub {
  font-size: .78rem;
  color: var(--text-faint);
  margin-top: .2rem;
}

/* ── PROGRESS BAR ── */
.prog-wrap { margin: .8rem 0 1.6rem; }
.prog-label {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: .6rem;
}
.prog-phrase {
  font-family: 'Syne', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
}
.prog-pct { font-size: .82rem; color: var(--text-muted); }
.prog-bg {
  background: var(--card-raised);
  border-radius: 999px;
  height: 10px;
  overflow: hidden;
  box-shadow: inset 0 1px 3px rgba(0,0,0,.4);
}
.prog-fill {
  height: 100%;
  border-radius: 999px;
  animation: fillBar .9s cubic-bezier(.4,0,.2,1);
  position: relative;
}
.prog-fill::after {
  content: '';
  position: absolute;
  top: 0; right: 0; bottom: 0;
  width: 20px;
  background: rgba(255,255,255,.2);
  border-radius: 999px;
  filter: blur(4px);
}
@keyframes fillBar {
  from { width: 0 !important; opacity: .6; }
  to   { opacity: 1; }
}

/* ── MACRO BARS ── */
.macro-row { margin-bottom: .7rem; }
.macro-label-row {
  display: flex;
  justify-content: space-between;
  font-size: .72rem;
  color: var(--text-muted);
  margin-bottom: .3rem;
  font-weight: 500;
}
.macro-bg {
  background: var(--card-raised);
  border-radius: 999px;
  height: 5px;
  overflow: hidden;
}
.macro-fill {
  height: 100%;
  border-radius: 999px;
  animation: fillBar .8s cubic-bezier(.4,0,.2,1);
}

/* ── CARDS ── */
.nf-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 1.4rem 1.6rem;
  margin-bottom: 1rem;
  box-shadow: var(--shadow);
  transition: transform .2s, box-shadow .2s, border-color .2s;
  position: relative;
  overflow: hidden;
}
.nf-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,.05), transparent);
}
.nf-card:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-lg);
  border-color: var(--border-hover);
}
.nf-card-accent {
  border-left: 3px solid var(--accent-blue);
}

/* ── FOOD ROWS ── */
.food-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: .6rem .85rem;
  border-radius: 12px;
  background: var(--bg-surface);
  margin-bottom: .3rem;
  border: 1px solid var(--border);
  border-left: 3px solid transparent;
  transition: border-color .18s, background .18s, transform .18s;
  cursor: default;
}
.food-row:hover {
  border-left-color: var(--accent-blue);
  background: var(--card);
  transform: translateX(2px);
}
.food-row-name {
  font-size: .84rem;
  font-weight: 500;
  color: var(--text-secondary);
}
.food-row-qty { font-size: .72rem; color: var(--text-muted); margin-top: .1rem; }
.food-row-kcal {
  font-family: 'Syne', sans-serif;
  font-size: .9rem;
  font-weight: 700;
  color: var(--accent-blue);
  white-space: nowrap;
}

/* ── MEAL SECTIONS ── */
.meal-section-label {
  font-family: 'Syne', sans-serif;
  font-size: .72rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: .1em;
  padding: .6rem 0 .3rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: .5rem;
}
.meal-section-kcal {
  font-family: 'Syne', sans-serif;
  font-size: .72rem;
  font-weight: 700;
  color: var(--accent-blue);
}

/* ── BADGES ── */
.streak-badge {
  display: inline-flex;
  align-items: center;
  gap: .25rem;
  background: linear-gradient(135deg,#1c0a03,#3b1006);
  border: 1px solid rgba(251,191,36,.2);
  border-radius: 999px;
  padding: .22rem .65rem;
  font-family: 'Syne', sans-serif;
  font-size: .73rem;
  font-weight: 700;
  color: var(--accent-yellow);
  box-shadow: 0 0 12px rgba(251,191,36,.1);
}
.nivel-badge {
  display: inline-flex;
  align-items: center;
  gap: .3rem;
  background: linear-gradient(135deg,#140c22,#1e1232);
  border: 1px solid rgba(167,139,250,.2);
  border-radius: 999px;
  padding: .22rem .7rem;
  font-family: 'Syne', sans-serif;
  font-size: .73rem;
  font-weight: 700;
  color: var(--accent-purple);
  box-shadow: 0 0 12px rgba(167,139,250,.1);
}
.obj-badge {
  display: inline-block;
  font-family: 'Syne', sans-serif;
  font-size: .68rem;
  font-weight: 700;
  padding: .18rem .6rem;
  border-radius: 999px;
  letter-spacing: .03em;
}
.ob-m { background: rgba(34,211,238,.08);  color: var(--accent-blue);   border: 1px solid rgba(34,211,238,.15); }
.ob-s { background: rgba(52,211,153,.08);  color: var(--accent-green);  border: 1px solid rgba(52,211,153,.15); }
.ob-a { background: rgba(251,113,133,.08); color: var(--accent-red);    border: 1px solid rgba(251,113,133,.15); }
.ob-g { background: rgba(167,139,250,.08); color: var(--accent-purple); border: 1px solid rgba(167,139,250,.15); }

/* ── INSIGHT BOX ── */
.insight-box {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-left: 3px solid rgba(34,211,238,.3);
  border-radius: 14px;
  padding: .75rem 1rem;
  margin-bottom: .5rem;
  display: flex;
  gap: .7rem;
  align-items: center;
  transition: border-color .2s, transform .2s;
  animation: slideIn .35s ease-out both;
}
.insight-box:hover { border-left-color: var(--accent-blue); transform: translateX(2px); }
@keyframes slideIn {
  from { opacity: 0; transform: translateX(-8px); }
  to   { opacity: 1; transform: translateX(0); }
}
.insight-ico { font-size: 1.2rem; flex-shrink: 0; }
.insight-txt { font-size: .81rem; color: var(--text-muted); line-height: 1.55; }

/* ── DICA BOX ── */
.dica-box {
  background: linear-gradient(135deg,rgba(8,30,42,.8),rgba(8,25,38,.9));
  border: 1px solid rgba(14,116,144,.3);
  border-radius: 16px;
  padding: .95rem 1.25rem;
  margin-bottom: 1.4rem;
  display: flex;
  gap: .85rem;
  align-items: flex-start;
  box-shadow: 0 2px 16px rgba(8,145,178,.08);
  animation: fadeIn .4s ease;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; } }
.dica-ico { font-size: 1.4rem; line-height: 1; flex-shrink: 0; margin-top: .1rem; }
.dica-ttl { font-family: 'Syne', sans-serif; font-size: .87rem; font-weight: 700; color: var(--accent-blue); margin-bottom: .2rem; }
.dica-txt { font-size: .79rem; color: var(--text-muted); line-height: 1.6; }

/* ── RANKING ITEMS ── */
.rank-item {
  display: flex;
  align-items: center;
  gap: .8rem;
  padding: .75rem 1rem;
  border-radius: 14px;
  background: var(--card);
  border: 1px solid var(--border);
  margin-bottom: .4rem;
  transition: transform .18s, box-shadow .18s, border-color .18s;
  animation: slideIn .3s ease-out both;
}
.rank-item:hover {
  transform: translateX(3px);
  border-color: var(--border-hover);
  box-shadow: var(--shadow);
}
.rank-item:nth-child(1) { animation-delay: .05s; }
.rank-item:nth-child(2) { animation-delay: .1s; }
.rank-item:nth-child(3) { animation-delay: .15s; }

/* ── FEED ITEMS ── */
.feed-item {
  display: flex;
  gap: .8rem;
  padding: .9rem 1rem;
  background: var(--card);
  border-radius: 14px;
  border: 1px solid var(--border);
  margin-bottom: .5rem;
  align-items: flex-start;
  transition: transform .18s, box-shadow .18s;
  animation: fadeIn .4s ease both;
}
.feed-item:hover { transform: translateY(-1px); box-shadow: var(--shadow); }
.feed-av {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Syne', sans-serif;
  font-weight: 800;
  font-size: .85rem;
  color: var(--bg-base);
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(34,211,238,.2);
}

/* ── QUICK ADD PREVIEW ── */
.quick-preview-item {
  background: rgba(52,211,153,.05);
  border: 1px solid rgba(52,211,153,.15);
  border-left: 3px solid var(--accent-green);
  border-radius: 12px;
  padding: .55rem .85rem;
  margin-bottom: .35rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  animation: slideIn .25s ease;
}
.quick-preview-notfound {
  background: rgba(251,113,133,.05);
  border: 1px solid rgba(251,113,133,.15);
  border-left: 3px solid var(--accent-red);
  border-radius: 12px;
  padding: .55rem .85rem;
  margin-bottom: .35rem;
}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  color: var(--text-primary) !important;
  font-family: 'DM Sans', sans-serif !important;
  transition: border-color .2s, box-shadow .2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--border-active) !important;
  box-shadow: 0 0 0 3px rgba(34,211,238,.08) !important;
}
div[data-baseweb="select"] > div {
  background: var(--card) !important;
  border-color: var(--border) !important;
  color: var(--text-primary) !important;
  border-radius: 12px !important;
}
[data-testid="stFileUploader"] {
  background: var(--card) !important;
  border: 1px dashed var(--border) !important;
  border-radius: 14px !important;
}
label { color: var(--text-muted) !important; font-size: .8rem !important; font-weight: 500 !important; }

/* ── BUTTONS ── */
.stButton > button {
  background: linear-gradient(135deg, #0891b2, #6366f1) !important;
  color: #fff !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important;
  border: none !important;
  border-radius: 12px !important;
  padding: .55rem 1.4rem !important;
  font-size: .85rem !important;
  letter-spacing: .02em !important;
  box-shadow: 0 2px 16px rgba(8,145,178,.25) !important;
  transition: opacity .15s, transform .15s, box-shadow .15s !important;
  position: relative !important;
  overflow: hidden !important;
}
.stButton > button:hover {
  opacity: .88 !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 24px rgba(8,145,178,.35) !important;
}
.stButton > button:active {
  transform: translateY(0px) scale(.98) !important;
  opacity: .95 !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--card) !important;
  border-radius: 14px !important;
  padding: 5px !important;
  gap: 3px !important;
  border: 1px solid var(--border) !important;
  box-shadow: var(--shadow) !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--text-muted) !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 600 !important;
  border-radius: 10px !important;
  border: none !important;
  font-size: .82rem !important;
  transition: color .2s, background .2s !important;
}
.stTabs [aria-selected="true"] {
  background: var(--card-raised) !important;
  color: var(--accent-blue) !important;
  box-shadow: 0 1px 8px rgba(0,0,0,.3) !important;
}

/* ── MISC ── */
hr { border-color: var(--border) !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--border-hover); }
.stAlert { border-radius: 12px !important; }

/* ── CHARTS ── */
[data-testid="stArrowVegaLiteChart"] {
  border-radius: 16px;
  overflow: hidden;
}

/* ── TREINO GRID ── */
.treino-row {
  background: var(--card);
  border-radius: 12px;
  padding: .65rem 1rem;
  margin-bottom: .3rem;
  border-left: 3px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: border-color .2s, background .2s, transform .18s;
  animation: fadeIn .3s ease;
}
.treino-row:hover {
  background: var(--card-hover);
  transform: translateX(2px);
}
.treino-row.hoje { border-left-color: var(--accent-blue); background: rgba(34,211,238,.04); }
.treino-row.concluido { border-left-color: rgba(52,211,153,.4); }

/* ── CONQUISTAS ── */
.conquista-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: .75rem .9rem;
  display: flex;
  gap: .65rem;
  align-items: center;
  margin-bottom: .5rem;
  transition: transform .18s, box-shadow .18s;
}
.conquista-card:hover { transform: translateY(-1px); box-shadow: var(--shadow); }
.conquista-card.desbloqueada {
  background: linear-gradient(135deg, rgba(30,20,0,.6), rgba(42,28,0,.8));
  border-color: rgba(251,191,36,.2);
  box-shadow: 0 2px 16px rgba(251,191,36,.06);
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
def ss(k,v):
    if k not in st.session_state: st.session_state[k]=v

ss("all_data",       load_all_data())
ss("usuario_logado", None)
ss("pagina_auth",    "login")
ss("dica_idx",       random.randint(0,len(DICAS)-1))
ss("mostrar_dica",   True)
ss("editar_treino",  None)
ss("ac_sel",         None)
ss("ac_q",           "")
ss("quick_preview",  [])

all_data = st.session_state.all_data
def save(): save_all_data(all_data)

# ══════════════════════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.usuario_logado:
    # Animação de entrada na tela de login
    H("""
    <style>
    @keyframes heroFloat { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)} }
    .auth-logo { animation: heroFloat 4s ease-in-out infinite; display:inline-block; }
    </style>
    <div style="text-align:center;padding:3rem 0 1.5rem">
      <div class="auth-logo" style="font-family:Syne,sans-serif;font-size:3.2rem;font-weight:800;
        background:linear-gradient(135deg,#22d3ee,#a78bfa);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">
        ⚡ NutriFlow
      </div>
      <div style="color:#1e2a3a;font-size:.78rem;text-transform:uppercase;letter-spacing:.15em;margin-top:.4rem">
        Seu companheiro de dieta e treinos
      </div>
    </div>
    """)
    
    if st.session_state.pagina_auth=="login":
        _,col,_ = st.columns([1,1.2,1])
        with col:
            H('<div class="nf-card" style="animation:fadeIn .4s ease">')
            st.markdown("#### Entrar")
            username = st.text_input("Usuario", placeholder="seu usuario")
            senha    = st.text_input("Senha", type="password", placeholder="••••••")
            if st.button("Entrar →", use_container_width=True):
                u=all_data["usuarios"]
                if username in u and u[username]["senha"]==hash_senha(senha):
                    st.session_state.usuario_logado=username; st.rerun()
                else: st.error("Usuario ou senha incorretos.")
            H('</div>')
            spacer(.5)
            H('<div style="text-align:center;color:#1e293b;font-size:.82rem">Nao tem conta?</div>')
            spacer(.3)
            if st.button("Criar conta gratuita", use_container_width=True):
                st.session_state.pagina_auth="cadastro"; st.rerun()
    else:
        _,col,_ = st.columns([.3,2.8,.3])
        with col:
            H('<div class="nf-card">')
            st.markdown("#### Criar conta")
            c1,c2=st.columns(2)
            with c1:
                novo_user=st.text_input("Usuario (sem espacos)",placeholder="joaosilva")
                nova_senha=st.text_input("Senha",type="password")
            with c2:
                novo_nome=st.text_input("Nome completo")
                conf_senha=st.text_input("Confirmar senha",type="password")
            st.markdown("---")
            st.markdown("**Dados para calculo calorico**")
            c3,c4=st.columns(2)
            with c3:
                sexo=st.selectbox("Sexo",["Masculino","Feminino"])
                idade=st.number_input("Idade",min_value=10,max_value=99,value=25)
            with c4:
                peso=st.number_input("Peso (kg)",min_value=30.0,max_value=300.0,value=70.0,step=.5)
                altura=st.number_input("Altura (cm)",min_value=100,max_value=250,value=170)
            atividade=st.selectbox("Nivel de atividade",list(NIVEL_ATIVIDADE.keys()))
            OBJ_L=["Manutencao","Perda saudavel (-0,5kg/sem)","Perda agressiva (-1kg/sem)","Ganho muscular"]
            objetivo=st.radio("Objetivo",OBJ_L,horizontal=True)
            pv={"peso":peso,"altura":altura,"idade":idade,"sexo":sexo,"atividade":atividade}
            mv=calcular_meta(pv,objetivo)
            cor_obj={"Manutencao":"#22d3ee","Perda saudavel (-0,5kg/sem)":"#34d399","Perda agressiva (-1kg/sem)":"#fb7185","Ganho muscular":"#a78bfa"}
            H(f'<div style="background:var(--bg-base);border-radius:14px;padding:1.1rem;text-align:center;margin:.8rem 0;border:1px solid var(--border)"><div style="font-size:.68rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.1em">Meta calorica estimada</div><div style="font-family:Syne,sans-serif;font-size:2.2rem;font-weight:800;color:{cor_obj.get(objetivo,"#22d3ee")};letter-spacing:-.04em">{mv} kcal</div><div style="font-size:.75rem;color:var(--text-faint)">{objetivo}</div></div>')
            if st.button("Criar conta →", use_container_width=True):
                if not all([novo_user,novo_nome,nova_senha]): st.error("Preencha todos os campos.")
                elif " " in novo_user: st.error("Usuario sem espacos.")
                elif nova_senha!=conf_senha: st.error("Senhas nao coincidem.")
                elif novo_user in all_data["usuarios"]: st.error("Usuario ja existe.")
                else:
                    all_data["usuarios"][novo_user]={"senha":hash_senha(nova_senha),"nome":novo_nome,
                        "perfil":pv,"objetivo":objetivo,"meta_calorias":mv,
                        "alimentacao":{},"treinos":{},"favoritos":[],"conquistas":[],
                        "reacoes":{},"usou_modo_rapido":False,"usou_social_share":False}
                    save(); st.success(f"Conta criada! Meta: {mv} kcal/dia")
                    st.session_state.pagina_auth="login"; st.rerun()
            H('</div>')
            if st.button("← Voltar", use_container_width=True):
                st.session_state.pagina_auth="login"; st.rerun()
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# APP PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
uname     = st.session_state.usuario_logado
udata     = all_data["usuarios"][uname]
today_str = str(date.today())
META      = udata.get("meta_calorias",2000)

for k,v in [("alimentacao",{}),("treinos",{}),("favoritos",[]),("conquistas",[]),
            ("reacoes",{}),("usou_modo_rapido",False),("usou_social_share",False)]:
    udata.setdefault(k,v)
udata["alimentacao"].setdefault(today_str,[])
udata["treinos"].setdefault(today_str,{"descricao":"","concluido":False,"notas":"","foto":""})

novas_c = verificar_conquistas(udata)
if novas_c:
    save()
    for c in novas_c:
        st.toast(f"{c['emoji']} {c['nome']} desbloqueada! +{c['pts']} pts",icon="🏆")

# ── CABEÇALHO ────────────────────────────────────────────────────────────────
ch1,ch2,ch3 = st.columns([3,1,1])
with ch1:
    H('<div class="hero-title">⚡ NutriFlow</div>')
    obj_now = udata.get("objetivo","Manutencao")
    obj_cls = {"Manutencao":"ob-m","Perda saudavel (-0,5kg/sem)":"ob-s","Perda agressiva (-1kg/sem)":"ob-a","Ganho muscular":"ob-g"}
    obj_ico = {"Manutencao":"💎","Perda saudavel (-0,5kg/sem)":"🎯","Perda agressiva (-1kg/sem)":"🔥","Ganho muscular":"💪"}
    streak  = _streak(udata)
    dias_app = dias_usando_app(udata)
    pts_user = calcular_pontos(udata)
    niv,niv_prox = calcular_nivel(pts_user)
    str_html = f'<span class="streak-badge">🔥 {streak} dias</span>' if streak>=2 else ""
    niv_html = f'<span class="nivel-badge">{niv["emoji"]} {niv["nome"]}</span>'
    dia_txt  = f'Dia {dias_app}' if dias_app>0 else "Dia 1"
    H(f'<div style="display:flex;align-items:center;gap:.5rem;flex-wrap:wrap;margin-top:.35rem">'
      f'<span style="color:var(--text-muted);font-size:.82rem">Ola, <strong style="color:var(--text-secondary)">{udata["nome"]}</strong></span>'
      f'<span style="font-size:.7rem;color:var(--text-faint);background:var(--bg-surface);border:1px solid var(--border);border-radius:999px;padding:.12rem .5rem">{dia_txt}</span>'
      f'<span class="obj-badge {obj_cls.get(obj_now,"ob-m")}">{obj_ico.get(obj_now,"⚡")} {obj_now}</span>'
      f'{str_html}{niv_html}'
      f'</div>')
with ch2:
    selected_date = st.date_input("Data",value=date.today(),label_visibility="collapsed")
    selected_str  = str(selected_date)
with ch3:
    if st.button("Sair"): st.session_state.usuario_logado=None; st.rerun()

udata["alimentacao"].setdefault(selected_str,[])
udata["treinos"].setdefault(selected_str,{"descricao":"","concluido":False,"notas":"","foto":""})

st.markdown("<br>", unsafe_allow_html=True)

# ── DICA DO DIA ──────────────────────────────────────────────────────────────
if st.session_state.mostrar_dica:
    d_raw=DICAS[st.session_state.dica_idx]
    partes=d_raw[0].split(" ",1)
    ico_d=partes[0] if len(partes)>1 else "💡"
    ttl_d=partes[1] if len(partes)>1 else d_raw[0]
    dc1,dc2=st.columns([10,1])
    with dc1:
        H(f'<div class="dica-box"><div class="dica-ico">{ico_d}</div><div><div class="dica-ttl">{ttl_d}</div><div class="dica-txt">{d_raw[1]}</div></div></div>')
    with dc2:
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("✕",key="close_dica"): st.session_state.mostrar_dica=False; st.rerun()
        if st.button("›",key="next_dica"):  st.session_state.dica_idx=(st.session_state.dica_idx+1)%len(DICAS); st.rerun()
else:
    if st.button("💡 Dica do dia"):
        st.session_state.mostrar_dica=True; st.session_state.dica_idx=random.randint(0,len(DICAS)-1); st.rerun()

# ── MÉTRICAS ─────────────────────────────────────────────────────────────────
kcal_hoje   = total_kcal(udata,selected_str)
macros_hoje = total_macros(udata,selected_str)
pct_meta    = kcal_hoje/META*100 if META>0 else 0
restante    = META-kcal_hoje
treinos_7   = sum(1 for i in range(7) if udata["treinos"].get((date.today()-timedelta(days=i)).isoformat(),{}).get("concluido"))
kcals_sem   = [total_kcal(udata,(date.today()-timedelta(days=i)).isoformat()) for i in range(7)]
media_sem   = round(sum(k for k in kcals_sem if k>0)/max(len([k for k in kcals_sem if k>0]),1),0)

frase,cor_p = gerar_mensagem_contextual(udata,kcal_hoje,META,macros_hoje,streak,dias_app)
pct_c=min(pct_meta,100)

# Cor semântica da barra principal
if pct_meta < 75:    cor_mv="var(--accent-blue)";   grad_mv="#22d3ee,#0891b2"
elif pct_meta <= 108: cor_mv="var(--accent-green)"; grad_mv="#34d399,#059669"
else:                cor_mv="var(--accent-red)";    grad_mv="#fb7185,#e11d48"

m1,m2,m3,m4=st.columns(4)
with m1: H(f'<div class="metric-box"><div class="metric-value" style="color:{cor_mv}">{kcal_hoje:.0f}</div><div class="metric-label">kcal hoje</div><div class="metric-sub">{pct_meta:.0f}% da meta</div></div>')
with m2: H(f'<div class="metric-box"><div class="metric-value" style="color:var(--accent-purple)">{META}</div><div class="metric-label">meta calorica</div><div class="metric-sub">{restante:.0f} restam</div></div>')
with m3: H(f'<div class="metric-box"><div class="metric-value" style="color:var(--accent-blue)">{media_sem:.0f}</div><div class="metric-label">media semanal</div><div class="metric-sub">ultimos 7 dias</div></div>')
with m4:
    cor_s="var(--accent-yellow)" if streak>=3 else "var(--accent-purple)"
    H(f'<div class="metric-box"><div class="metric-value" style="color:{cor_s}">{streak}🔥</div><div class="metric-label">streak treinos</div><div class="metric-sub">{treinos_7}/7 essa semana</div></div>')

# Progress bar principal
H(f'''<div class="prog-wrap">
  <div class="prog-label">
    <span class="prog-phrase" style="color:{cor_p}">{frase}</span>
    <span class="prog-pct">{kcal_hoje:.0f}/{META} kcal</span>
  </div>
  <div class="prog-bg">
    <div class="prog-fill" style="width:{pct_c:.1f}%;background:linear-gradient(90deg,{grad_mv})"></div>
  </div>
</div>''')

# Macro bars
meta_prot=round(udata.get("perfil",{}).get("peso",70)*2,0)
meta_carbo=round((META*.45)/4,0); meta_gord=round((META*.25)/9,0)
pp=min(macros_hoje["p"]/meta_prot*100,100) if meta_prot>0 else 0
pc=min(macros_hoje["c"]/meta_carbo*100,100) if meta_carbo>0 else 0
pg=min(macros_hoje["g"]/meta_gord*100,100) if meta_gord>0 else 0
H(f'''<div style="display:flex;gap:1.5rem;margin-bottom:1.4rem;flex-wrap:wrap">
  <div style="flex:1;min-width:120px">
    <div class="macro-label-row"><span style="color:var(--text-muted)">🥩 Proteina</span><span style="color:var(--accent-blue);font-family:Syne,sans-serif;font-weight:700">{macros_hoje["p"]:.0f}g <span style="color:var(--text-faint);font-weight:400">/{meta_prot:.0f}g</span></span></div>
    <div class="macro-bg"><div class="macro-fill" style="width:{pp:.0f}%;background:linear-gradient(90deg,#22d3ee,#06b6d4)"></div></div>
  </div>
  <div style="flex:1;min-width:120px">
    <div class="macro-label-row"><span style="color:var(--text-muted)">🍚 Carbo</span><span style="color:var(--accent-yellow);font-family:Syne,sans-serif;font-weight:700">{macros_hoje["c"]:.0f}g <span style="color:var(--text-faint);font-weight:400">/{meta_carbo:.0f}g</span></span></div>
    <div class="macro-bg"><div class="macro-fill" style="width:{pc:.0f}%;background:linear-gradient(90deg,#fbbf24,#f59e0b)"></div></div>
  </div>
  <div style="flex:1;min-width:120px">
    <div class="macro-label-row"><span style="color:var(--text-muted)">🥑 Gordura</span><span style="color:var(--accent-purple);font-family:Syne,sans-serif;font-weight:700">{macros_hoje["g"]:.0f}g <span style="color:var(--text-faint);font-weight:400">/{meta_gord:.0f}g</span></span></div>
    <div class="macro-bg"><div class="macro-fill" style="width:{pg:.0f}%;background:linear-gradient(90deg,#a78bfa,#8b5cf6)"></div></div>
  </div>
</div>''')

# ── TABS ─────────────────────────────────────────────────────────────────────
tab1,tab2,tab3,tab4,tab5=st.tabs(["🥗 Alimentacao","🏋️ Treino","📊 Historico","👥 Social","⚙️ Perfil"])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — ALIMENTAÇÃO
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    col_add,col_view=st.columns([1,1.45],gap="large")
    with col_add:
        add_tab1,add_tab2,add_tab3=st.tabs(["⚡ Rapido","📝 Formulario","⭐ Favoritos"])
        
        # ── MODO RÁPIDO ──
        with add_tab1:
            H('<div style="font-size:.82rem;color:var(--text-muted);margin-bottom:.6rem;line-height:1.6">Digite alimentos em linguagem natural e adicione tudo de uma vez:</div>')
            H('<div style="background:rgba(34,211,238,.04);border:1px solid rgba(34,211,238,.1);border-radius:12px;padding:.65rem 1rem;margin-bottom:.75rem;font-size:.78rem;color:var(--text-muted)">Ex: <span style="color:var(--accent-blue);font-weight:500">frango 150g arroz 100g</span> · <span style="color:var(--accent-blue);font-weight:500">ovo 2 aveia 50g</span> · <span style="color:var(--accent-blue);font-weight:500">banana 1</span></div>')
            
            tipo_rapido_sel = st.selectbox("Refeicao", TIPOS_REFEICAO, key="tipo_rapido")
            texto_rapido = st.text_area("Digite os alimentos", placeholder="frango 150g arroz 100g feijao 80g", height=80, key="texto_rapido")
            
            if st.button("🔍 Analisar", use_container_width=True, key="btn_analisar"):
                if texto_rapido.strip():
                    st.session_state.quick_preview = parse_quick_add(texto_rapido)
                else:
                    st.warning("Digite pelo menos um alimento.")
            
            preview = st.session_state.quick_preview
            if preview:
                total_kcal_prev = sum(r["kcal"] for r in preview)
                H(f'<div style="font-family:Syne,sans-serif;font-size:.82rem;font-weight:700;color:var(--text-primary);margin:.6rem 0 .4rem">Preview — <span style="color:var(--accent-blue)">{total_kcal_prev:.0f} kcal</span></div>')
                for r in preview:
                    if r["encontrado"]:
                        H(f'<div class="quick-preview-item"><div><div style="font-size:.84rem;color:var(--accent-green);font-weight:500">{r["nome"]}</div><div style="font-size:.71rem;color:var(--text-muted)">{r["qtd"]:.0f}{r["un"]} · P:{r["p"]:.0f}g C:{r["c"]:.0f}g G:{r["g"]:.0f}g</div></div><div style="font-family:Syne,sans-serif;font-size:.9rem;font-weight:700;color:var(--accent-blue)">{r["kcal"]:.0f}</div></div>')
                    else:
                        H(f'<div class="quick-preview-notfound"><div style="font-size:.82rem;color:var(--accent-red)">⚠️ "{r["raw"]}" — nao encontrado</div><div style="font-size:.71rem;color:var(--text-muted)">Use o formulario manual</div></div>')
                
                encontrados = [r for r in preview if r["encontrado"]]
                if encontrados:
                    if st.button(f"✓ Adicionar {len(encontrados)} item(ns)", use_container_width=True, key="btn_confirmar_rapido"):
                        for r in encontrados:
                            udata["alimentacao"][selected_str].append({
                                "nome":r["nome"],"alimento":r["nome"],"tipo":tipo_rapido_sel,
                                "quantidade":r["qtd"],"unidade":r["un"],"kcal":r["kcal"],
                                "p":r["p"],"c":r["c"],"g":r["g"],"foto":"","comentario":"",
                            })
                        if not udata.get("usou_modo_rapido",False): udata["usou_modo_rapido"]=True
                        save(); st.toast(f"⚡ {len(encontrados)} itens — {total_kcal_prev:.0f} kcal!")
                        st.session_state.quick_preview=[]; st.rerun()
                    if st.button("✕ Cancelar", use_container_width=True, key="btn_cancelar_rapido"):
                        st.session_state.quick_preview=[]; st.rerun()

        # ── FORMULÁRIO ──
        with add_tab2:
            ontem_str=(date.fromisoformat(selected_str)-timedelta(days=1)).isoformat()
            ontem_ref=udata["alimentacao"].get(ontem_str,[])
            if ontem_ref and not udata["alimentacao"].get(selected_str):
                kcal_ont=sum(r.get("kcal",r.get("calorias",0)) for r in ontem_ref)
                H(f'<div style="background:rgba(52,211,153,.05);border:1px solid rgba(52,211,153,.15);border-radius:14px;padding:.8rem 1rem;margin-bottom:.8rem"><div style="font-family:Syne,sans-serif;font-size:.85rem;font-weight:700;color:var(--accent-green)">📋 Repetir dia anterior?</div><div style="font-size:.75rem;color:var(--text-muted);margin-top:.15rem">{len(ontem_ref)} itens · {kcal_ont:.0f} kcal</div></div>')
                if st.button("✓ Repetir ontem completo", use_container_width=True):
                    import copy
                    udata["alimentacao"][selected_str]=copy.deepcopy(ontem_ref)
                    save(); st.toast("📋 Dia anterior copiado!"); st.rerun()
                st.markdown("---")
            
            freq = sugerir_frequentes(udata)
            if freq:
                H('<div style="font-size:.75rem;color:var(--text-muted);margin-bottom:.4rem;font-weight:500">🧠 Frequentes:</div>')
                for s in freq:
                    info=BANCO_ALIMENTOS.get(s,{})
                    sc1,sc2=st.columns([4,1])
                    with sc1:
                        H(f'<div style="background:var(--card);border:1px solid var(--border);border-radius:10px;padding:.45rem .75rem;margin-bottom:.25rem;transition:border-color .2s"><div style="font-size:.82rem;color:var(--text-secondary)">{info.get("emoji","🍽️")} {s}</div><div style="font-size:.7rem;color:var(--text-muted)">{info.get("kcal_100g",0)} kcal/100{info.get("un","g")}</div></div>')
                    with sc2:
                        if st.button("➕",key=f"freq_{s}"):
                            qtd_d=100.0; un_d=info.get("un","g")
                            hora=datetime.now().hour
                            tipo_d=TIPOS_REFEICAO[0 if hora<10 else (1 if hora<12 else (2 if hora<15 else (3 if hora<18 else (4 if hora<21 else 5))))]
                            k=kcal_item(s,qtd_d,un_d); m=macros_item(s,qtd_d,un_d); mn=_macros_normalized(m)
                            udata["alimentacao"][selected_str].append({"nome":s,"alimento":s,"tipo":tipo_d,"quantidade":qtd_d,"unidade":un_d,"kcal":k,**mn,"foto":"","comentario":""})
                            save(); st.toast(f"✅ {s} adicionado!"); st.rerun()
                st.markdown("---")
            
            st.markdown("**➕ Registrar refeicao**")
            tipo_ref=st.selectbox("Tipo",TIPOS_REFEICAO)
            ac_q=st.text_input("🔍 Buscar alimento",placeholder="arroz, frango, ovo...",key="ac_input")
            if ac_q!=st.session_state.ac_q:
                st.session_state.ac_q=ac_q; st.session_state.ac_sel=None
            
            sugs=buscar_alimentos(ac_q)
            if sugs and not st.session_state.ac_sel:
                H('<div style="font-size:.72rem;color:var(--text-muted);margin-bottom:.3rem">Sugestoes:</div>')
                for s in sugs:
                    info=BANCO_ALIMENTOS[s]
                    if st.button(f"{info.get('emoji','🍽️')}  {s}  —  {info['kcal_100g']} kcal/100{info['un']}",key=f"sug_{s}"):
                        st.session_state.ac_sel=s; st.rerun()
            
            sel=st.session_state.ac_sel
            UNIDS=["g","ml","unid","colher","xicara","fatia"]
            u_def=BANCO_ALIMENTOS[sel]["un"] if sel and BANCO_ALIMENTOS[sel]["un"] in UNIDS else "g"
            u_idx=UNIDS.index(u_def) if u_def in UNIDS else 0
            
            alimento=st.text_input("Nome do alimento",value=sel or "",placeholder="Ex: Frango grelhado peito")
            cq1,cq2=st.columns([2,1])
            with cq1: unidade=st.selectbox("Unidade",UNIDS,index=u_idx)
            with cq2: quantidade=st.number_input("Qtd",min_value=0.0,step=10.0,value=100.0)
            
            nm_b=alimento.strip() if alimento.strip() else sel
            ka=kcal_item(nm_b,quantidade,unidade) if nm_b and nm_b in BANCO_ALIMENTOS else 0.0
            ma=macros_item(nm_b,quantidade,unidade) if nm_b and nm_b in BANCO_ALIMENTOS else {}
            ma_n=_macros_normalized(ma) if ma else {"p":0,"c":0,"g":0}
            
            calorias=st.number_input("Calorias (kcal)"+(" ✦ auto" if ka>0 else ""),min_value=0.0,step=1.0,value=float(ka) if ka>0 else 0.0)
            
            if ka>0 and ma_n:
                H(f'<div style="background:var(--bg-surface);border-radius:10px;padding:.5rem .8rem;margin:.3rem 0;display:flex;gap:1.5rem;font-size:.75rem;color:var(--text-muted);border:1px solid var(--border)"><span>🥩 P: <b style="color:var(--accent-blue)">{ma_n.get("p",0):.1f}g</b></span><span>🍚 C: <b style="color:var(--accent-yellow)">{ma_n.get("c",0):.1f}g</b></span><span>🥑 G: <b style="color:var(--accent-purple)">{ma_n.get("g",0):.1f}g</b></span></div>')
            
            comentario=st.text_input("💬 Comentario (opcional)",key="ali_com")
            foto_ref=st.file_uploader("📷 Foto",type=["jpg","jpeg","png","webp"],key="up_ref")
            if foto_ref: st.image(foto_ref,use_container_width=True)
            
            ba1,ba2=st.columns(2)
            with ba1:
                if st.button("✓ Adicionar",use_container_width=True):
                    if alimento.strip():
                        fp=save_photo(foto_ref,"ref",uname,selected_str) if foto_ref else ""
                        udata["alimentacao"][selected_str].append({"nome":alimento.strip(),"alimento":alimento.strip(),"tipo":tipo_ref,"quantidade":quantidade,"unidade":unidade,"kcal":calorias,**ma_n,"foto":fp,"comentario":comentario})
                        save(); st.toast(f"✅ {alimento.strip()} — {calorias:.0f} kcal")
                        st.session_state.ac_sel=None; st.session_state.ac_q=""; st.rerun()
                    else: st.warning("Informe o alimento.")
            with ba2:
                if st.button("⭐ Favorito",use_container_width=True):
                    if alimento.strip():
                        udata["favoritos"].append({"nome":alimento.strip()[:20],"alimento":alimento.strip(),"tipo":tipo_ref,"quantidade":quantidade,"unidade":unidade,"kcal":calorias,"calorias":calorias})
                        save(); st.toast("⭐ Salvo nos favoritos!"); st.rerun()

        # ── FAVORITOS ──
        with add_tab3:
            if not udata["favoritos"]:
                H('<div style="color:var(--text-faint);text-align:center;padding:2.5rem;font-size:.85rem;line-height:1.7">Sem favoritos ainda.<br>Adicione itens clicando em ⭐</div>')
            else:
                for fi,fav in enumerate(udata["favoritos"]):
                    fa1,fa2,fa3=st.columns([3,1,1])
                    with fa1:
                        H(f'<div style="background:var(--card);border:1px solid var(--border);border-radius:11px;padding:.5rem .8rem;margin-bottom:.25rem"><div style="font-size:.83rem;color:var(--text-secondary);font-weight:500">{fav["alimento"]}</div><div style="font-size:.71rem;color:var(--text-muted)">{fav.get("tipo","")} · {fav.get("kcal",fav.get("calorias",0)):.0f} kcal</div></div>')
                    with fa2:
                        if st.button("➕",key=f"fav_{fi}"):
                            udata["alimentacao"][selected_str].append({"nome":fav["alimento"],"alimento":fav["alimento"],"tipo":fav.get("tipo",""),"quantidade":fav["quantidade"],"unidade":fav["unidade"],"kcal":fav.get("kcal",fav.get("calorias",0)),"p":0,"c":0,"g":0,"foto":"","comentario":""})
                            save(); st.toast(f"✅ {fav['alimento']} adicionado!"); st.rerun()
                    with fa3:
                        if st.button("🗑️",key=f"dfav_{fi}"):
                            udata["favoritos"].pop(fi); save(); st.rerun()

    # ── VISÃO DO DIA ──
    with col_view:
        refeicoes=udata["alimentacao"].get(selected_str,[])
        kcal_dia=total_kcal(udata,selected_str)
        
        cv1,cv2=st.columns([2,1])
        with cv1: H(f'<div style="font-family:Syne,sans-serif;font-size:.95rem;font-weight:700;color:var(--text-primary);padding:.3rem 0">🗓️ {selected_date.strftime("%d/%m/%Y")}</div>')
        with cv2: H(f'<div style="font-family:Syne,sans-serif;font-size:1.2rem;font-weight:800;color:var(--accent-blue);text-align:right;padding:.3rem 0;animation:countUp .6s ease">{kcal_dia:.0f} <span style="font-size:.75rem;font-weight:400;color:var(--text-muted)">kcal</span></div>')
        
        for tipo in TIPOS_REFEICAO:
            itens=[(i,r) for i,r in enumerate(refeicoes) if r.get("tipo")==tipo]
            tot_t=sum(r.get("kcal",r.get("calorias",0)) for _,r in itens)
            
            th1,th2=st.columns([3,1])
            with th1: H(f'<div class="meal-section-label">{tipo}</div>')
            with th2:
                if itens: H(f'<div class="meal-section-kcal" style="text-align:right;padding:.5rem 0 .3rem">{tot_t:.0f} kcal</div>')
            
            if not itens:
                H('<div style="font-size:.77rem;color:var(--text-faint);font-style:italic;padding:.1rem 0 .6rem .2rem">Nenhum registro</div>')
            else:
                for orig_i,r in itens:
                    nm=r.get("nome",r.get("alimento",""))
                    qtd=r.get("quantidade",0); un=r.get("unidade","")
                    prot=r.get("p",r.get("proteina",0)); kcal_r=r.get("kcal",r.get("calorias",0))
                    com=r.get("comentario","")
                    prot_txt=f" · P:{prot:.0f}g" if prot else ""
                    com_html=f'<div style="font-size:.7rem;color:var(--text-muted);font-style:italic;margin-top:.15rem">💬 {com}</div>' if com else ""
                    
                    fr1,fr2=st.columns([8,1])
                    with fr1:
                        H(f'<div class="food-row"><div><div class="food-row-name">{nm}</div><div class="food-row-qty">{qtd:.0f} {un}{prot_txt}</div>{com_html}</div><div class="food-row-kcal">{kcal_r:.0f}</div></div>')
                        if r.get("foto") and os.path.exists(r["foto"]):
                            with st.expander("📷 ver foto"): st.image(r["foto"],use_container_width=True)
                    with fr2:
                        if st.button("🗑️",key=f"df_{orig_i}_{selected_str}_{tipo[:2]}"):
                            udata["alimentacao"][selected_str].pop(orig_i); save(); st.rerun()
            spacer(.2)
        
        if refeicoes:
            saldo=kcal_dia-META; cor_s="var(--accent-red)" if saldo>0 else "var(--accent-green)"
            saldo_txt=f"+{saldo:.0f} acima" if saldo>0 else f"{abs(saldo):.0f} abaixo"
            H(f'<div style="display:flex;justify-content:space-between;padding:.8rem 1.1rem;background:var(--card);border-radius:14px;border:1px solid var(--border);margin-top:.7rem;box-shadow:var(--shadow)"><span style="color:var(--text-muted);font-size:.83rem">Saldo do dia</span><span style="font-family:Syne,sans-serif;font-weight:700;color:{cor_s};font-size:.9rem">{saldo_txt} da meta</span></div>')

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — TREINO
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    col_tf,col_tl=st.columns([1,1.2],gap="large")
    treino_dia=udata["treinos"][selected_str]

    if st.session_state.editar_treino:
        d_ed=st.session_state.editar_treino
        t_ed=udata["treinos"].get(d_ed,{"descricao":"","concluido":False,"notas":"","foto":""})
        H(f'<div class="nf-card nf-card-accent"><div style="font-family:Syne,sans-serif;font-size:.95rem;font-weight:700;color:var(--accent-blue)">✏️ Editando treino de {d_ed}</div></div>')
        gi=GRUPOS_TREINO.index(t_ed.get("descricao","")) if t_ed.get("descricao","") in GRUPOS_TREINO else 0
        de=st.selectbox("Grupo",GRUPOS_TREINO,index=gi,key="ed_d")
        ne=st.text_area("Observacoes",value=t_ed.get("notas",""),height=90,key="ed_n")
        ce=st.checkbox("Concluido",value=t_ed.get("concluido",False),key="ed_c")
        es1,es2=st.columns(2)
        with es1:
            if st.button("💾 Salvar",use_container_width=True):
                udata["treinos"][d_ed]={"descricao":de if de!="Selecione" else "","notas":ne,"concluido":ce,"foto":t_ed.get("foto","")}
                save(); st.session_state.editar_treino=None; st.toast("✅ Treino atualizado!"); st.rerun()
        with es2:
            if st.button("Cancelar",use_container_width=True): st.session_state.editar_treino=None; st.rerun()
        st.markdown("---")

    with col_tf:
        st.markdown("**🏋️ Registrar treino**")
        gi_d=GRUPOS_TREINO.index(treino_dia["descricao"]) if treino_dia.get("descricao") in GRUPOS_TREINO else 0
        desc=st.selectbox("Grupo muscular",GRUPOS_TREINO,index=gi_d)
        nota=st.text_area("Exercicios realizados",value=treino_dia.get("notas",""),placeholder="Ex: Supino 4x10 80kg\nRosca direta 3x12 20kg",height=130)
        conc=st.checkbox("✅ Treino concluido",value=treino_dia.get("concluido",False))
        ftr=st.file_uploader("📷 Foto",type=["jpg","jpeg","png","webp"],key="up_tr")
        if ftr: st.image(ftr,use_container_width=True)
        elif treino_dia.get("foto") and os.path.exists(treino_dia["foto"]): st.image(treino_dia["foto"],use_container_width=True)
        if st.button("💾 Salvar treino",use_container_width=True):
            fp=save_photo(ftr,"tr",uname,selected_str) if ftr else treino_dia.get("foto","")
            udata["treinos"][selected_str]={"descricao":desc if desc!="Selecione" else "","notas":nota,"concluido":conc,"foto":fp}
            save(); st.toast("💪 Treino salvo!" if conc else "📝 Treino registrado!"); st.rerun()

    with col_tl:
        st.markdown("**📅 Proximos 30 dias**")
        hoje_d=date.today(); sem_pt=["Seg","Ter","Qua","Qui","Sex","Sab","Dom"]
        for i in range(30):
            d=hoje_d+timedelta(days=i); ds=d.isoformat()
            udata["treinos"].setdefault(ds,{"descricao":"","concluido":False,"notas":"","foto":""})
            t=udata["treinos"][ds]; desc_t=t.get("descricao") or "—"; ok=t.get("concluido",False)
            sem=sem_pt[d.weekday()]; dl="Hoje" if i==0 else ("Amanha" if i==1 else d.strftime("%d/%m"))
            lbl="✓ Concluido" if ok else ("Planejado" if t.get("descricao") else "Vazio")
            cor_lbl="var(--accent-green)" if ok else "var(--text-muted)"
            cls="hoje" if i==0 else ("concluido" if ok else "")
            
            tc,te=st.columns([5,1])
            with tc:
                H(f'<div class="treino-row {cls}" style="animation-delay:{i*.02}s"><div><div style="font-size:.7rem;color:var(--text-faint);font-weight:500">{dl} · {sem}</div><div style="color:var(--text-secondary);font-weight:500;font-size:.84rem;margin-top:.1rem">{desc_t}</div></div><span style="font-size:.78rem;font-weight:600;color:{cor_lbl};white-space:nowrap">{lbl}</span></div>')
            with te:
                if st.button("✏️",key=f"e_{ds}"): st.session_state.editar_treino=ds; st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — HISTÓRICO
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    hoje_h=date.today()
    dias_30=[(hoje_h-timedelta(days=i)).isoformat() for i in range(29,-1,-1)]
    labs_30=[(hoje_h-timedelta(days=i)).strftime("%d/%m") for i in range(29,-1,-1)]
    kcal_30=[total_kcal(udata,d) for d in dias_30]
    
    pts_h=calcular_pontos(udata); niv_h,niv_prox_h=calcular_nivel(pts_h)
    pts_prox=niv_prox_h["min_pts"] if niv_prox_h else pts_h
    pct_niv=min((pts_h-niv_h["min_pts"])/max(pts_prox-niv_h["min_pts"],1)*100,100)
    proximo_txt=f'Proximo: {niv_prox_h["emoji"]} {niv_prox_h["nome"]} em {pts_prox-pts_h} pts' if niv_prox_h else "Nivel maximo! 👑"
    
    H(f'''<div class="nf-card" style="background:linear-gradient(135deg,var(--card),rgba(20,12,34,.9));border-color:rgba(167,139,250,.2)">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.7rem">
        <div style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:var(--accent-purple)">{niv_h["emoji"]} {niv_h["nome"]}</div>
        <div style="font-family:Syne,sans-serif;font-size:.9rem;font-weight:700;color:var(--accent-purple)">{pts_h} pts</div>
      </div>
      <div class="macro-bg"><div class="macro-fill" style="width:{pct_niv:.0f}%;background:linear-gradient(90deg,#a78bfa,#c4b5fd)"></div></div>
      <div style="font-size:.72rem;color:var(--text-muted);margin-top:.4rem">{proximo_txt}</div>
    </div>''')
    
    insights=gerar_insights(udata,META)
    if insights:
        st.markdown("**🧠 Insights**")
        for ins in insights:
            H(f'<div class="insight-box"><div class="insight-ico">{ins["emoji"]}</div><div class="insight-txt">{ins["txt"]}</div></div>')
        spacer()
    
    st.markdown("**📊 Calorias — 30 dias**")
    df_ch=pd.DataFrame({"Consumido":kcal_30,"Meta":[META]*30},index=labs_30)
    st.line_chart(df_ch,height=240,color=["#22d3ee","#fb7185"])
    
    media_7=round(sum(k for k in kcal_30[-7:] if k>0)/max(len([k for k in kcal_30[-7:] if k>0]),1),0)
    H(f'''<div style="display:flex;gap:1rem;margin:.6rem 0 1.2rem;flex-wrap:wrap">
      <div class="metric-box" style="flex:1"><div class="metric-value" style="font-size:1.4rem;color:var(--accent-blue)">{media_7:.0f}</div><div class="metric-label">media kcal (7d)</div></div>
      <div class="metric-box" style="flex:1"><div class="metric-value" style="font-size:1.4rem;color:var(--accent-yellow)">{sum(1 for k in kcal_30[-7:] if k>0)}</div><div class="metric-label">dias registrados (7d)</div></div>
      <div class="metric-box" style="flex:1"><div class="metric-value" style="font-size:1.4rem;color:var(--accent-purple)">{sum(1 for d in dias_30[-7:] if udata["treinos"].get(d,{}).get("concluido"))}</div><div class="metric-label">treinos (7d)</div></div>
    </div>''')
    
    st.markdown("**📋 Resumo detalhado**")
    rows=[]
    for d_s in reversed(dias_30):
        kc=total_kcal(udata,d_s); t=udata["treinos"].get(d_s,{})
        if kc==0 and not t.get("descricao"): continue
        sl=kc-META
        rows.append({"Data":d_s,"Kcal":f"{kc:.0f}","Meta":str(META),"Saldo":f"{'+'if sl>0 else''}{sl:.0f}","Refeicoes":len(udata["alimentacao"].get(d_s,[])),"Treino":t.get("descricao") or "—","✓":"✓" if t.get("concluido") else "✗"})
    if rows:
        rep1,rep2=st.columns([3,1])
        with rep1: dia_rep=st.selectbox("Repetir dia no diario de hoje:",[r["Data"] for r in rows],key="rep_dia_sel")
        with rep2:
            st.markdown("<br>",unsafe_allow_html=True)
            if st.button("📋 Repetir",key="btn_rep_hist"):
                import copy
                if not udata["alimentacao"].get(today_str):
                    udata["alimentacao"][today_str]=copy.deepcopy(udata["alimentacao"].get(dia_rep,[]))
                    save(); st.success(f"Dia {dia_rep} copiado!"); st.rerun()
                else: st.warning("Hoje ja tem registros.")
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
    else:
        H('<div style="color:var(--text-faint);text-align:center;padding:2.5rem;font-size:.85rem">Sem dados ainda.</div>')
    
    spacer(); st.markdown("**🏆 Conquistas**")
    ul_ids=udata.get("conquistas",[]); c_cols=st.columns(2)
    for ci,c in enumerate(CONQUISTAS):
        ok_c=c["id"] in ul_ids
        emo_c=c["emoji"] if ok_c else "🔒"
        with c_cols[ci%2]:
            if ok_c:
                H(f'<div class="conquista-card desbloqueada"><div style="font-size:1.5rem;flex-shrink:0">{emo_c}</div><div style="flex:1"><div style="font-family:Syne,sans-serif;font-size:.83rem;font-weight:700;color:var(--accent-yellow)">{c["nome"]}</div><div style="font-size:.73rem;color:var(--text-muted);margin-top:.1rem">{c["desc"]}</div></div><div style="font-family:Syne,sans-serif;font-size:.75rem;font-weight:700;color:var(--accent-yellow)">+{c["pts"]}</div></div>')
            else:
                H(f'<div class="conquista-card"><div style="font-size:1.5rem;flex-shrink:0;opacity:.3">{emo_c}</div><div style="flex:1"><div style="font-family:Syne,sans-serif;font-size:.83rem;font-weight:700;color:var(--text-faint)">{c["nome"]}</div><div style="font-size:.73rem;color:var(--text-faint);margin-top:.1rem">{c["desc"]}</div></div><div style="font-family:Syne,sans-serif;font-size:.75rem;font-weight:700;color:var(--text-faint)">+{c["pts"]}</div></div>')
    
    spacer()
    st.download_button("⬇️ Exportar dados JSON",data=json.dumps({"alimentacao":udata["alimentacao"],"treinos":udata["treinos"]},ensure_ascii=False,indent=2),file_name=f"nutriflow_{uname}.json",mime="application/json")

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — SOCIAL (FUNCIONAL DE VERDADE)
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    todos=all_data["usuarios"]
    
    # ── Estatísticas gerais da comunidade ──
    total_users = len(todos)
    total_treinos_hoje = sum(1 for ud in todos.values() if ud["treinos"].get(today_str,{}).get("concluido"))
    total_metas_hoje  = sum(1 for ud in todos.values() if total_kcal(ud,today_str)>=ud.get("meta_calorias",2000)*.9 and total_kcal(ud,today_str)>0)
    
    H(f'''<div style="display:flex;gap:1rem;margin-bottom:1.4rem;flex-wrap:wrap">
      <div class="metric-box" style="flex:1;min-width:90px"><div class="metric-value" style="font-size:1.5rem;color:var(--accent-blue)">{total_users}</div><div class="metric-label">usuarios</div></div>
      <div class="metric-box" style="flex:1;min-width:90px"><div class="metric-value" style="font-size:1.5rem;color:var(--accent-green)">{total_treinos_hoje}</div><div class="metric-label">treinos hoje</div></div>
      <div class="metric-box" style="flex:1;min-width:90px"><div class="metric-value" style="font-size:1.5rem;color:var(--accent-yellow)">{total_metas_hoje}</div><div class="metric-label">metas batidas</div></div>
    </div>''')
    
    sc1,sc2=st.columns([1,1],gap="large")
    
    with sc1:
        # ── Ranking diário ──
        H('<div style="font-family:Syne,sans-serif;font-size:.85rem;font-weight:700;color:var(--text-primary);margin-bottom:.6rem">🏆 Ranking Calorico Hoje</div>')
        rank=sorted([{
            "u":u,"nome":ud["nome"],
            "pct":total_kcal(ud,today_str)/ud.get("meta_calorias",2000)*100 if ud.get("meta_calorias",2000)>0 else 0,
            "kcal":total_kcal(ud,today_str),"meta":ud.get("meta_calorias",2000),
            "streak":_streak(ud),"pts":calcular_pontos(ud)
        } for u,ud in todos.items()],key=lambda x:x["pct"],reverse=True)
        
        for pos,r in enumerate(rank):
            emo_r=["🥇","🥈","🥉"][pos] if pos<3 else f"#{pos+1}"
            is_me = r["u"]==uname
            bord_extra = "border:1.5px solid rgba(34,211,238,.3);background:rgba(34,211,238,.04);" if is_me else ""
            pct2=min(r["pct"],100)
            niv_r,_=calcular_nivel(r["pts"])
            H(f'''<div class="rank-item" style="{bord_extra}animation-delay:{pos*.06}s">
              <div style="font-family:Syne,sans-serif;font-weight:800;font-size:.95rem;width:28px;text-align:center">{emo_r}</div>
              <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,var(--accent-blue),var(--accent-purple));display:flex;align-items:center;justify-content:center;font-family:Syne,sans-serif;font-weight:800;font-size:.82rem;color:var(--bg-base);flex-shrink:0;box-shadow:0 2px 8px rgba(34,211,238,.2)">{r["nome"][0].upper()}</div>
              <div style="flex:1">
                <div style="font-size:.87rem;font-weight:600;color:var(--text-primary)">{r["nome"]} {"👑" if is_me else ""} <span style="font-size:.68rem;color:var(--text-faint)">{niv_r["emoji"]}</span></div>
                <div style="font-size:.72rem;color:var(--text-muted)">{r["kcal"]:.0f}/{r["meta"]} kcal · 🔥{r["streak"]}d</div>
              </div>
              <div style="text-align:right">
                <div style="font-family:Syne,sans-serif;font-size:.88rem;font-weight:700;color:{"var(--accent-green)" if pct2>=95 else "var(--accent-blue)"}">{pct2:.0f}%</div>
                <div style="width:55px;background:var(--card-raised);border-radius:999px;height:4px;margin-top:4px">
                  <div style="width:{pct2:.0f}%;background:{"var(--accent-green)" if pct2>=95 else "var(--accent-blue)"};height:4px;border-radius:999px"></div>
                </div>
              </div>
            </div>''')
        
        spacer(.5)
        # ── Ranking treinos ──
        H('<div style="font-family:Syne,sans-serif;font-size:.85rem;font-weight:700;color:var(--text-primary);margin-bottom:.6rem">💪 Ranking Treinos (7 dias)</div>')
        rank_t=sorted([{
            "u":u,"nome":ud["nome"],
            "t7":sum(1 for i in range(7) if ud["treinos"].get((date.today()-timedelta(days=i)).isoformat(),{}).get("concluido")),
            "streak":_streak(ud)
        } for u,ud in todos.items()],key=lambda x:(x["t7"],x["streak"]),reverse=True)
        
        for pos,r in enumerate(rank_t):
            emo_r=["🥇","🥈","🥉"][pos] if pos<3 else f"#{pos+1}"
            is_me=r["u"]==uname
            bord_extra="border:1.5px solid rgba(167,139,250,.3);background:rgba(167,139,250,.04);" if is_me else ""
            b=int(r["t7"]/7*100)
            H(f'''<div class="rank-item" style="{bord_extra}animation-delay:{pos*.06}s">
              <span style="font-family:Syne,sans-serif;font-weight:800;font-size:.9rem;width:24px">{emo_r}</span>
              <div style="width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,var(--accent-purple),var(--accent-blue));display:flex;align-items:center;justify-content:center;font-family:Syne,sans-serif;font-weight:800;font-size:.8rem;color:var(--bg-base);flex-shrink:0">{r["nome"][0].upper()}</div>
              <div style="flex:1"><div style="font-size:.86rem;color:var(--text-primary);font-weight:500">{r["nome"]} {"(voce)" if is_me else ""}</div><div style="font-size:.7rem;color:var(--text-muted)">🔥 streak: {r["streak"]} dias</div></div>
              <div style="display:flex;flex-direction:column;align-items:flex-end;gap:.2rem">
                <div style="font-family:Syne,sans-serif;font-size:.88rem;font-weight:700;color:var(--accent-purple)">{r["t7"]}/7</div>
                <div style="width:55px;background:var(--card-raised);border-radius:999px;height:4px">
                  <div style="width:{b}%;background:var(--accent-purple);height:4px;border-radius:999px"></div>
                </div>
              </div>
            </div>''')
        
        spacer(.5)
        # ── Comparar com amigo ──
        H('<div style="font-family:Syne,sans-serif;font-size:.85rem;font-weight:700;color:var(--text-primary);margin-bottom:.6rem">⚔️ Duelo</div>')
        outros=[u for u in todos.keys() if u!=uname]
        if outros:
            amigo=st.selectbox("Escolher adversario:",outros,key="cmp_amigo")
            if amigo:
                ud_a=todos[amigo]; k_a=total_kcal(ud_a,today_str); m_a=ud_a.get("meta_calorias",2000)
                k_eu=total_kcal(udata,today_str); pct_eu=min(k_eu/META*100,100); pct_a=min(k_a/m_a*100,100)
                str_eu=_streak(udata); str_a=_streak(ud_a); pts_eu=calcular_pontos(udata); pts_a=calcular_pontos(ud_a)
                eu_ganha = pct_eu > pct_a
                H(f'''<div class="nf-card" style="background:linear-gradient(135deg,rgba(8,14,22,.9),rgba(10,16,26,.95))">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem">
                    <div style="text-align:center;flex:1">
                      <div style="font-family:Syne,sans-serif;font-size:.95rem;font-weight:800;color:var(--accent-blue)">{udata["nome"]}</div>
                      <div style="font-size:.7rem;color:var(--text-muted);margin-top:.2rem">{pts_eu} pts · 🔥{str_eu}d</div>
                    </div>
                    <div style="font-family:Syne,sans-serif;font-size:1.2rem;font-weight:800;color:var(--text-muted);padding:0 .8rem">VS</div>
                    <div style="text-align:center;flex:1">
                      <div style="font-family:Syne,sans-serif;font-size:.95rem;font-weight:800;color:var(--accent-purple)">{ud_a["nome"]}</div>
                      <div style="font-size:.7rem;color:var(--text-muted);margin-top:.2rem">{pts_a} pts · 🔥{str_a}d</div>
                    </div>
                  </div>
                  <div style="font-size:.72rem;color:var(--text-muted);text-align:center;margin-bottom:.5rem">% da meta hoje</div>
                  <div style="display:flex;gap:.5rem;align-items:center">
                    <div style="flex:1;background:var(--card-raised);border-radius:999px;height:9px;overflow:hidden">
                      <div style="width:{pct_eu:.0f}%;background:var(--accent-blue);height:9px;border-radius:999px;float:right"></div>
                    </div>
                    <div style="font-family:Syne,sans-serif;font-size:.75rem;font-weight:700;color:var(--text-muted);padding:0 .3rem;white-space:nowrap">{"🏆" if eu_ganha else "💪"}</div>
                    <div style="flex:1;background:var(--card-raised);border-radius:999px;height:9px;overflow:hidden">
                      <div style="width:{pct_a:.0f}%;background:var(--accent-purple);height:9px;border-radius:999px"></div>
                    </div>
                  </div>
                  <div style="display:flex;justify-content:space-between;margin-top:.4rem;font-size:.72rem;color:var(--text-muted)">
                    <span style="color:var(--accent-blue)">{pct_eu:.0f}%</span>
                    <span style="color:var(--accent-purple)">{pct_a:.0f}%</span>
                  </div>
                </div>''')
        else:
            H('<div style="font-size:.82rem;color:var(--text-faint);padding:.6rem">Nenhum outro usuario ainda. Convide amigos!</div>')

    with sc2:
        # ── Compartilhar meta ──
        kcal_user_hoje=total_kcal(udata,today_str)
        if kcal_user_hoje>=META*0.95 and kcal_user_hoje>0:
            H(f'''<div class="nf-card" style="background:linear-gradient(135deg,rgba(5,40,18,.8),rgba(8,50,25,.9));border-color:rgba(52,211,153,.2);text-align:center;padding:1.5rem">
              <div style="font-size:2rem;margin-bottom:.4rem">🎯</div>
              <div style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:var(--accent-green)">Meta batida hoje!</div>
              <div style="font-size:.8rem;color:var(--text-muted);margin:.3rem 0 .8rem">{kcal_user_hoje:.0f} / {META} kcal</div>
            </div>''')
            if st.button("🔥 Compartilhar no feed!", use_container_width=True):
                chave=f"meta_{uname}_{today_str}"
                udata["reacoes"].setdefault(chave,{"tipo":"meta","reacoes":{},"usuario":uname,"nome":udata["nome"],"data":today_str,"kcal":kcal_user_hoje})
                udata["usou_social_share"]=True
                save(); st.toast("🔥 Compartilhado no feed!"); st.rerun()
        else:
            falt=META-kcal_user_hoje
            H(f'<div class="nf-card" style="text-align:center;padding:1.2rem"><div style="font-size:.82rem;color:var(--text-muted)">Faltam <span style="font-family:Syne,sans-serif;font-size:1.1rem;font-weight:800;color:var(--accent-blue)">{falt:.0f}</span> kcal para compartilhar</div></div>')
        
        spacer(.3)
        # ── Feed ──
        H('<div style="font-family:Syne,sans-serif;font-size:.85rem;font-weight:700;color:var(--text-primary);margin-bottom:.6rem">📰 Feed da Comunidade</div>')
        
        feed=[]
        for u,ud in todos.items():
            nm=ud["nome"]
            # Conquistas recentes
            for ev_key,ev in ud.get("reacoes",{}).items():
                if ev.get("data")==today_str and ev.get("tipo")=="meta":
                    feed.append({"nm":nm,"u":u,"h":"agora","txt":f"🎯 bateu a meta! {ev.get('kcal',0):.0f} kcal","ev_key":ev_key,"reacoes":ev.get("reacoes",{}),"ordem":3})
            # Treino concluido hoje
            t_h=ud["treinos"].get(today_str,{})
            if t_h.get("concluido") and t_h.get("descricao"):
                feed.append({"nm":nm,"u":u,"h":"hoje","txt":f"💪 concluiu {t_h['descricao']}","ev_key":None,"reacoes":{},"ordem":2})
            # Streak alto
            s_=_streak(ud)
            if s_>=5:
                feed.append({"nm":nm,"u":u,"h":"hoje","txt":f"🔥 {s_} dias seguidos — sequencia incrivel!","ev_key":None,"reacoes":{},"ordem":2})
            elif s_>=3:
                feed.append({"nm":nm,"u":u,"h":"hoje","txt":f"🔥 {s_} dias seguidos de treino","ev_key":None,"reacoes":{},"ordem":1})
            # Conquistas novas
            ul_ids_s=ud.get("conquistas",[])
            for cv in CONQUISTAS:
                if cv["id"]=="meta_dia" and cv["id"] in ul_ids_s and total_kcal(ud,today_str)>=ud.get("meta_calorias",2000)*.9:
                    pass  # já coberto acima
            # Treino ontem
            ont=(date.today()-timedelta(days=1)).isoformat()
            t_o=ud["treinos"].get(ont,{})
            if t_o.get("concluido") and t_o.get("descricao"):
                feed.append({"nm":nm,"u":u,"h":"ontem","txt":f"🏋️ treinou {t_o['descricao']}","ev_key":None,"reacoes":{},"ordem":1})
        
        # Ordena: mais recente/importante primeiro, usuário atual em destaque
        feed.sort(key=lambda x:(-x.get("ordem",1), 0 if x["u"]==uname else 1))
        
        if not feed:
            H('<div class="nf-card" style="text-align:center;padding:2.5rem"><div style="font-size:2rem;margin-bottom:.5rem">🌱</div><div style="font-size:.85rem;color:var(--text-muted)">Sem atividade ainda.<br>Comece registrando treinos e refeicoes!</div></div>')
        else:
            for fi_idx,fi in enumerate(feed[:15]):
                ini=fi["nm"][0].upper()
                is_me=fi["u"]==uname
                bord_extra="border:1.5px solid rgba(34,211,238,.2);" if is_me else ""
                H(f'''<div class="feed-item" style="{bord_extra}animation-delay:{fi_idx*.04}s">
                  <div class="feed-av">{ini}</div>
                  <div style="flex:1">
                    <div style="font-weight:600;font-size:.85rem;color:var(--text-primary)">{fi["nm"]} {"<span style='font-size:.7rem;color:var(--accent-blue)'>voce</span>" if is_me else ""}</div>
                    <div style="font-size:.8rem;color:var(--text-secondary);margin-top:.2rem">{fi["txt"]}</div>
                    <div style="font-size:.68rem;color:var(--text-faint);margin-top:.2rem">{fi["h"]}</div>
                  </div>
                </div>''')
                if fi.get("ev_key"):
                    reac=fi.get("reacoes",{}); tot_f=reac.get("🔥",0); tot_l=reac.get("👍",0)
                    r1,r2,_=st.columns([1,1,5])
                    with r1:
                        if st.button(f"🔥 {tot_f}",key=f"rf_{fi_idx}_{fi['u']}"):
                            for u2,ud2 in todos.items():
                                if fi["ev_key"] in ud2.get("reacoes",{}):
                                    ud2["reacoes"][fi["ev_key"]]["reacoes"]["🔥"]=ud2["reacoes"][fi["ev_key"]]["reacoes"].get("🔥",0)+1; break
                            save(); st.rerun()
                    with r2:
                        if st.button(f"👍 {tot_l}",key=f"rl_{fi_idx}_{fi['u']}"):
                            for u2,ud2 in todos.items():
                                if fi["ev_key"] in ud2.get("reacoes",{}):
                                    ud2["reacoes"][fi["ev_key"]]["reacoes"]["👍"]=ud2["reacoes"][fi["ev_key"]]["reacoes"].get("👍",0)+1; break
                            save(); st.rerun()
        
        spacer(.5)
        # ── Minha semana resumo ──
        H('<div style="font-family:Syne,sans-serif;font-size:.85rem;font-weight:700;color:var(--text-primary);margin-bottom:.6rem">🗓️ Minha semana</div>')
        dias_sw=[(date.today()-timedelta(days=i)).isoformat() for i in range(6,-1,-1)]
        sem_pt2=["Seg","Ter","Qua","Qui","Sex","Sab","Dom"]
        
        # Mini calendar view
        sem_html = '<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:.3rem;margin-bottom:.8rem">'
        for i,d in enumerate(dias_sw):
            kd=total_kcal(udata,d); td=udata["treinos"].get(d,{}).get("concluido",False)
            meta_ok=kd>=META*.9 and kd>0
            bg="rgba(52,211,153,.15)" if meta_ok else "var(--card)"
            bord="rgba(52,211,153,.3)" if meta_ok else "var(--border)"
            tr_dot=f'<div style="width:5px;height:5px;border-radius:50%;background:{"var(--accent-purple)" if td else "transparent"};margin:.2rem auto 0"></div>'
            dow=sem_pt2[(date.today()-timedelta(days=6-i)).weekday()]
            sem_html += f'<div style="background:{bg};border:1px solid {bord};border-radius:10px;padding:.4rem .2rem;text-align:center"><div style="font-size:.6rem;color:var(--text-muted)">{dow}</div><div style="font-family:Syne,sans-serif;font-size:.72rem;font-weight:700;color:{"var(--accent-green)" if meta_ok else "var(--text-faint)"}">{kd:.0f}</div>{tr_dot}</div>'
        sem_html += '</div>'
        sem_html += '<div style="display:flex;gap:.8rem;font-size:.72rem;color:var(--text-muted)"><span>🟢 Meta atingida</span><span>🟣 Treino concluido</span></div>'
        H(sem_html)

# ════════════════════════════════════════════════════════════════════════════
# TAB 5 — PERFIL
# ════════════════════════════════════════════════════════════════════════════
with tab5:
    pp1,pp2=st.columns([1,1],gap="large")
    with pp1:
        st.markdown("**👤 Dados pessoais**")
        perf=udata.get("perfil",{})
        ne_=st.text_input("Nome completo",value=udata.get("nome",""))
        pa,pb=st.columns(2)
        with pa:
            sx_=st.selectbox("Sexo",["Masculino","Feminino"],index=0 if perf.get("sexo","M")=="Masculino" else 1)
            id_=st.number_input("Idade",min_value=10,max_value=99,value=int(perf.get("idade",25)))
        with pb:
            pe_=st.number_input("Peso (kg)",min_value=30.0,max_value=300.0,value=float(perf.get("peso",70.0)),step=.5)
            al_=st.number_input("Altura (cm)",min_value=100,max_value=250,value=int(perf.get("altura",170)))
        ai_=list(NIVEL_ATIVIDADE.keys()).index(perf.get("atividade",list(NIVEL_ATIVIDADE.keys())[0]))
        at_=st.selectbox("Atividade",list(NIVEL_ATIVIDADE.keys()),index=ai_)
        OBJ2=["Manutencao","Perda saudavel (-0,5kg/sem)","Perda agressiva (-1kg/sem)","Ganho muscular"]
        oi_=OBJ2.index(udata.get("objetivo","Manutencao")) if udata.get("objetivo") in OBJ2 else 0
        ob_=st.radio("Objetivo",OBJ2,index=oi_,horizontal=True)
        pv_={"peso":pe_,"altura":al_,"idade":id_,"sexo":sx_,"atividade":at_}
        nm_=calcular_meta(pv_,ob_); tmb_=calcular_tmb(pe_,al_,id_,sx_); tde_=tmb_*NIVEL_ATIVIDADE[at_]
        
        cor_obj2={"Manutencao":"var(--accent-blue)","Perda saudavel (-0,5kg/sem)":"var(--accent-green)","Perda agressiva (-1kg/sem)":"var(--accent-red)","Ganho muscular":"var(--accent-purple)"}
        proj=""
        if "Perda" in ob_:
            kg4=abs({"Perda saudavel (-0,5kg/sem)":-500,"Perda agressiva (-1kg/sem)":-1000}.get(ob_,-500)*28/7700)
            proj=f'<div style="font-size:.75rem;color:var(--accent-green);margin-top:.4rem">📉 Projecao: -{kg4:.1f} kg em 4 semanas</div>'
        
        H(f'''<div class="nf-card" style="text-align:center;margin:.8rem 0">
          <div style="display:flex;justify-content:space-around">
            <div><div style="font-size:.66rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.1em">TMB</div><div style="font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800;color:var(--accent-purple)">{tmb_:.0f}</div></div>
            <div><div style="font-size:.66rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.1em">TDEE</div><div style="font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800;color:var(--accent-blue)">{tde_:.0f}</div></div>
            <div><div style="font-size:.66rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.1em">Meta</div><div style="font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800;color:{cor_obj2.get(ob_,"var(--accent-green)")}">{nm_}</div></div>
          </div>
          {proj}
        </div>''')
        
        if st.button("💾 Salvar alteracoes",use_container_width=True):
            udata.update({"nome":ne_,"objetivo":ob_,"meta_calorias":nm_,"perfil":{"peso":pe_,"altura":al_,"idade":id_,"sexo":sx_,"atividade":at_}})
            save(); st.toast(f"✅ Perfil salvo! Meta: {nm_} kcal/dia"); st.rerun()
    
    with pp2:
        st.markdown("**🔑 Alterar senha**")
        sa_=st.text_input("Senha atual",type="password",key="sa_")
        sn_=st.text_input("Nova senha",type="password",key="sn_")
        sc_=st.text_input("Confirmar",type="password",key="sc_")
        if st.button("Alterar senha",use_container_width=True):
            if udata["senha"]!=hash_senha(sa_): st.error("Senha incorreta.")
            elif sn_!=sc_: st.error("Senhas nao coincidem.")
            elif len(sn_)<4: st.error("Minimo 4 caracteres.")
            else: udata["senha"]=hash_senha(sn_); save(); st.success("Senha alterada!")
        
        spacer(); st.markdown("**📊 Resumo**")
        p_=udata.get("perfil",{})
        imc_=p_.get("peso",70)/((p_.get("altura",170)/100)**2)
        ci_,co_=("Abaixo do peso","var(--accent-blue)") if imc_<18.5 else (("Peso normal","var(--accent-green)") if imc_<25 else (("Sobrepeso","var(--accent-yellow)") if imc_<30 else ("Obesidade","var(--accent-red)")))
        pts_p=calcular_pontos(udata); niv_p,_=calcular_nivel(pts_p)
        
        H('<div class="nf-card">')
        for lbl,val,cv in [
            ("Usuario",f"@{uname}","var(--text-secondary)"),
            ("Nivel",f"{niv_p['emoji']} {niv_p['nome']} · {pts_p} pts","var(--accent-purple)"),
            ("IMC",f"{imc_:.1f} — {ci_}",co_),
            ("Meta atual",f"{META} kcal/dia","var(--accent-blue)"),
            ("Objetivo",udata.get("objetivo","—"),"var(--text-secondary)"),
            ("Streak",f"🔥 {streak} dias","var(--accent-yellow)"),
            ("Conquistas",f"🏆 {len(udata.get('conquistas',[]))}/{len(CONQUISTAS)}","var(--accent-yellow)"),
            ("Dias de uso",f"📅 {dias_app} dias","var(--text-muted)")
        ]:
            H(f'<div style="display:flex;justify-content:space-between;padding:.42rem 0;border-bottom:1px solid var(--border);font-size:.82rem"><span style="color:var(--text-muted)">{lbl}</span><span style="color:{cv};font-weight:600">{val}</span></div>')
        H('</div>')

# ── FOOTER ──
H(f'<div style="text-align:center;color:var(--text-faint);font-size:.68rem;margin-top:3rem;padding:1rem 0;border-top:1px solid var(--border)">⚡ NutriFlow v7 · @{uname} · {today_str}</div>')