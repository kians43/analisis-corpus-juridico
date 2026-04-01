import streamlit as st
import os
import re
import json
import html
import hashlib
import requests
import pandas as pd
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

CARPETA_TXT  = os.environ.get("CARPETA_TXT", r"C:\Users\kians\Desktop\sentencias individuales txt")
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_HAIKU = CLAUDE_MODEL   # usa el mismo modelo verificado del resto de la app
CLAUDE_URL   = "https://api.anthropic.com/v1/messages"
IA_WORKERS   = 1             # secuencial para respetar rate limits de la API

st.set_page_config(page_title="Análisis de Corpus Jurídico", layout="wide")

st.markdown("""
<style>
/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   PALETA  —  Fondo oscuro + acento naranja tabique
   --bg-deep:    #0F1923   fondo principal
   --bg-card:    #172030   tarjetas / paneles
   --bg-mid:     #1E2D40   inputs, hovers
   --accent:     #C8622A   naranja tabique principal
   --accent-lit: #E07840   naranja claro (hover)
   --accent-dim: #7A3A18   naranja oscuro (bordes)
   --text-hi:    #F0EBE3   texto principal
   --text-mid:   #A89A8E   texto secundario
   --border:     #2A3D52   bordes sutiles
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Base ─────────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', system-ui, sans-serif !important;
    color: #F0EBE3 !important;
}
.stApp {
    background-color: #0F1923 !important;
}

/* ── Contenedor principal ─────────────────────────────────────────────── */
.main .block-container {
    padding: 2rem 2.5rem !important;
    max-width: 1200px;
    background-color: #0F1923 !important;
}

/* ── Título principal ─────────────────────────────────────────────────── */
.stApp h1 {
    font-size: 1.85rem !important;
    font-weight: 700 !important;
    color: #F0EBE3 !important;
    letter-spacing: -0.5px;
    padding-bottom: 0.3rem;
    border-bottom: 3px solid #C8622A;
    margin-bottom: 1.5rem !important;
    display: inline-block;
}

/* ── Subtítulos ───────────────────────────────────────────────────────── */
h2, h3, h4 {
    color: #F0EBE3 !important;
    font-weight: 600 !important;
}
p, li, label, span {
    color: #D4C9BF !important;
}

/* ── Sidebar ──────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #0A1219 !important;
    border-right: 1px solid #1E2D40 !important;
}
[data-testid="stSidebar"] * {
    color: #A89A8E !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] strong {
    color: #F0EBE3 !important;
}
[data-testid="stSidebar"] hr {
    border-color: #1E2D40 !important;
    opacity: 1 !important;
}
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea {
    background: #172030 !important;
    border: 1px solid #2A3D52 !important;
    color: #F0EBE3 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: #C8622A !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #E07840 !important;
}

/* ── Tabs ─────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #172030 !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid #2A3D52 !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    color: #A89A8E !important;
    padding: 0.5rem 1.1rem !important;
    border: none !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: #C8622A !important;
    color: #ffffff !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background: transparent !important;
}

/* ── Botones primarios ────────────────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #C8622A 0%, #A64E20 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.4rem !important;
    box-shadow: 0 4px 16px rgba(200,98,42,0.4) !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #E07840 0%, #C8622A 100%) !important;
    box-shadow: 0 6px 22px rgba(200,98,42,0.55) !important;
    transform: translateY(-1px);
}

/* ── Botones secundarios ──────────────────────────────────────────────── */
.stButton > button:not([kind="primary"]) {
    background: #172030 !important;
    color: #F0EBE3 !important;
    border: 1.5px solid #2A3D52 !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
.stButton > button:not([kind="primary"]):hover {
    border-color: #C8622A !important;
    color: #E07840 !important;
}

/* ── Botón de descarga ────────────────────────────────────────────────── */
[data-testid="stDownloadButton"] > button {
    background: #172030 !important;
    color: #C8622A !important;
    border: 1.5px solid #C8622A !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #1E2D40 !important;
    color: #E07840 !important;
    border-color: #E07840 !important;
}

/* ── Inputs y textareas ───────────────────────────────────────────────── */
.stTextInput input,
.stTextArea textarea {
    background: #172030 !important;
    border: 1.5px solid #2A3D52 !important;
    color: #F0EBE3 !important;
    border-radius: 10px !important;
    font-size: 0.9rem !important;
    transition: border-color 0.2s !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #C8622A !important;
    box-shadow: 0 0 0 3px rgba(200,98,42,0.18) !important;
}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #4E5D6E !important;
}

/* ── Selectbox ────────────────────────────────────────────────────────── */
[data-baseweb="select"] > div {
    background: #172030 !important;
    border: 1.5px solid #2A3D52 !important;
    border-radius: 10px !important;
    color: #F0EBE3 !important;
}
[data-baseweb="select"] svg { fill: #A89A8E !important; }
[data-baseweb="popover"] {
    background: #172030 !important;
    border: 1px solid #2A3D52 !important;
    border-radius: 10px !important;
}
[data-baseweb="menu"] {
    background: #172030 !important;
}
[role="option"] {
    background: #172030 !important;
    color: #F0EBE3 !important;
}
[role="option"]:hover {
    background: #1E2D40 !important;
}
[aria-selected="true"][role="option"] {
    background: #7A3A18 !important;
    color: #F0EBE3 !important;
}

/* ── Dataframe ────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid #2A3D52 !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
}

/* ── Alerts ───────────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border-left-width: 4px !important;
    font-size: 0.9rem !important;
    background: #172030 !important;
}
[data-testid="stAlert"][data-baseweb="notification"] {
    background: #172030 !important;
}

/* ── Expander ─────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: #172030 !important;
    border: 1.5px solid #2A3D52 !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary {
    color: #F0EBE3 !important;
}

/* ── Métricas ─────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #172030 !important;
    border-radius: 12px !important;
    padding: 1rem 1.2rem !important;
    border: 1px solid #2A3D52 !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3) !important;
}
[data-testid="stMetricLabel"] p {
    color: #A89A8E !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
[data-testid="stMetricValue"] {
    color: #C8622A !important;
    font-weight: 700 !important;
}

/* ── Slider ───────────────────────────────────────────────────────────── */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background: #C8622A !important;
    border-color: #C8622A !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] div[class*="sliderTrackFill"] {
    background: #C8622A !important;
}

/* ── Progress bar ─────────────────────────────────────────────────────── */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #C8622A, #E07840) !important;
    border-radius: 999px !important;
}

/* ── Caption y texto secundario ──────────────────────────────────────── */
.stCaption, [data-testid="stCaptionContainer"] p {
    color: #6B7E92 !important;
    font-size: 0.8rem !important;
}

/* ── Divider ──────────────────────────────────────────────────────────── */
hr {
    border-color: #2A3D52 !important;
    opacity: 1 !important;
}

/* ── Header / toolbar de Streamlit ───────────────────────────────────── */
header[data-testid="stHeader"] {
    background-color: #0F1923 !important;
    border-bottom: 1px solid #1E2D40 !important;
}
[data-testid="stHeader"] * {
    color: #A89A8E !important;
}
[data-testid="stToolbar"] {
    background-color: #0F1923 !important;
}
[data-testid="stDecoration"] {
    background: #0F1923 !important;
    display: none !important;
}

/* ── Scrollbar ────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #172030; border-radius: 999px; }
::-webkit-scrollbar-thumb { background: #2A3D52; border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: #C8622A; }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ Análisis de Corpus Jurídico")

if "corpus" not in st.session_state:
    st.session_state.corpus = {}
if "sets" not in st.session_state:
    st.session_state.sets = {}
if "set_counter" not in st.session_state:
    st.session_state.set_counter = 1
if "historial" not in st.session_state:
    st.session_state.historial = []
if "revisados" not in st.session_state:
    st.session_state.revisados = set()
if "ultimo_resultado" not in st.session_state:
    st.session_state.ultimo_resultado = None
if "indice" not in st.session_state:
    st.session_state.indice = {}
if "ia_revisados" not in st.session_state:
    st.session_state.ia_revisados = set()
if "ia_resultados_consulta" not in st.session_state:
    st.session_state.ia_resultados_consulta = []
if "esquema_guardado" not in st.session_state:
    st.session_state.esquema_guardado = {}
if "confirmados" not in st.session_state:
    st.session_state.confirmados = {}   # {patron_desc: set(nombres_doc)}
if "busquedas" not in st.session_state:
    st.session_state.busquedas = {}     # {patron_desc: {nombre_doc: bool}}

with st.sidebar:
    # ── Paso 1 ───────────────────────────────────────────────────────────────
    st.markdown("### Paso 1 · API Key")
    api_key = st.text_input("API Key de Claude", type="password", key="api_key")
    if api_key:
        st.caption("✅ API Key ingresada")

    st.markdown("---")

    # ── Paso 1b ──────────────────────────────────────────────────────────────
    st.markdown("### Tipo de corpus")
    descripcion_corpus = st.text_area(
        "¿Qué tipo de documentos vas a analizar?",
        placeholder=(
            "Ej: sentencias de amparo indirecto en materia administrativa\n"
            "Ej: contratos de arrendamiento comercial\n"
            "Ej: laudos arbitrales en materia mercantil\n"
            "Ej: resoluciones de órganos regulatorios"
        ),
        height=100,
        key="descripcion_corpus",
        help="Esta descripción le ayuda a Claude a entender el contexto de tus documentos."
    )

    st.markdown("---")

    # ── Paso 2 ───────────────────────────────────────────────────────────────
    st.markdown("### Paso 2 · Carga tu corpus")
    archivos_subidos = st.file_uploader(
        "Archivos TXT",
        type=["txt"],
        accept_multiple_files=True,
        help="Selecciona uno o varios archivos .txt."
    )
    if archivos_subidos:
        corpus_temp = {}
        for archivo in archivos_subidos:
            try:
                texto = archivo.read().decode("utf-8", errors="ignore")
                corpus_temp[archivo.name] = texto
            except Exception:
                pass
        if corpus_temp:
            st.session_state.corpus = corpus_temp
            st.success(f"✅ {len(corpus_temp)} documentos cargados")
    if st.session_state.corpus:
        st.info(f"📄 {len(st.session_state.corpus)} docs en memoria")
        if st.button("🗑️ Limpiar corpus", use_container_width=True):
            st.session_state.corpus = {}
            st.rerun()

    st.markdown("---")
    st.markdown("### Herramientas avanzadas")
    st.header("🗂️ Sets guardados")
    if st.session_state.sets:
        for nombre_set, lista in st.session_state.sets.items():
            st.write(f"**{nombre_set}**: {len(lista)} documentos")
        if st.button("🗑️ Borrar todos los sets", use_container_width=True):
            st.session_state.sets = {}
            st.session_state.set_counter = 1
            st.rerun()
    else:
        st.write("_(vacío)_")


def llamar_claude(prompt):
    if not api_key:
        return "ERROR: Ingresa tu API Key."
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    body = {
        "model": CLAUDE_MODEL,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        r = requests.post(CLAUDE_URL, headers=headers, json=body, timeout=30)
        r.raise_for_status()
        return r.json()["content"][0]["text"]
    except Exception as e:
        return f"ERROR API: {e}"


def extraer_terminos_claude(consulta, descripcion, maximo_sinonimos=3):
    # MODIFICADO: usa la descripción del corpus en lugar de hardcodear "amparo"
    desc = descripcion.strip() if descripcion.strip() else "documentos jurídicos en español"
    prompt = f"""Eres un asistente de investigación jurídica especializado en análisis de corpus documentales.

El investigador está trabajando con el siguiente tipo de documentos:
"{desc}"

El investigador quiere buscar LITERALMENTE (como Ctrl+F) dentro de esos documentos.

Consulta del investigador: "{consulta}"

Tu tarea:
1. Extrae entre 3 y 6 FRAGMENTOS MUY CORTOS (2 a 4 palabras) que aparezcan EXACTAMENTE en ese tipo de documentos.
2. Piensa en el lenguaje técnico y las fórmulas que los autores de ese tipo de documentos realmente usan.
3. Agrega máximo {maximo_sinonimos} variantes cortas adicionales que expresen lo mismo con otras palabras.
4. NUNCA uses frases de más de 5 palabras.

Responde ÚNICAMENTE con JSON válido, sin markdown:
{{"terminos_principales": ["frase 1", "frase 2"], "sinonimos": ["variante 1"]}}"""

    respuesta = llamar_claude(prompt)
    try:
        limpia = respuesta.strip().strip("```json").strip("```").strip()
        return json.loads(limpia)
    except Exception:
        return {"terminos_principales": [], "sinonimos": [], "raw": respuesta}


def buscar_en_corpus(terminos, corpus, modo="AND"):
    resultados = []
    terminos_lower = [t.lower() for t in terminos if t.strip()]
    for nombre, texto in corpus.items():
        texto_lower = texto.lower()
        if modo == "AND":
            if all(t in texto_lower for t in terminos_lower):
                resultados.append(nombre)
        else:
            if any(t in texto_lower for t in terminos_lower):
                resultados.append(nombre)
    return resultados


def buscar_con_fallback(principales, sinonimos, corpus):
    todos = principales + sinonimos
    res = buscar_en_corpus(principales, corpus, "AND")
    if len(res) >= 5:
        return res, "AND (términos principales)"
    res = buscar_en_corpus(principales, corpus, "OR")
    if len(res) >= 5:
        return res, "OR (términos principales)"
    res = buscar_en_corpus(todos, corpus, "OR")
    return res, "OR (todos los términos)"


def obtener_extracto(texto, terminos, chars=300):
    texto_lower = texto.lower()
    for t in terminos:
        idx = texto_lower.find(t.lower())
        if idx != -1:
            inicio = max(0, idx - 100)
            fin = min(len(texto), idx + chars)
            return "..." + texto[inicio:fin].replace("\n", " ") + "..."
    return texto[:chars].replace("\n", " ")


def resaltar_terminos(texto, terminos):
    """Devuelve el texto con cada ocurrencia de los términos envuelta en <mark> amarillo."""
    texto_esc = html.escape(texto)
    for t in sorted(terminos, key=len, reverse=True):   # más largos primero → evita solapamientos
        if not t.strip():
            continue
        patron = re.compile(re.escape(html.escape(t)), re.IGNORECASE)
        texto_esc = patron.sub(
            lambda m: (
                f'<mark style="background-color:#FFE066;padding:0 2px;'
                f'border-radius:2px;font-weight:bold;">{m.group()}</mark>'
            ),
            texto_esc
        )
    return texto_esc


def identificar_referencias(texto, patrones_custom):
    """
    Busca patrones definidos por el investigador.
    Acepta texto literal o expresiones regulares básicas.
    """
    encontrados = set()
    for patron in patrones_custom:
        try:
            matches = re.findall(patron, texto)
            encontrados.update(matches)
        except re.error:
            pass
    return sorted(list(encontrados))


# ── Índice semántico estructurado ────────────────────────────────────────────
# Esquema de extracción: cubre los 7 patrones identificados en la investigación.
# Haiku llena este JSON por cada sentencia (una sola llamada por documento).



def indexar_documento(nombre, texto, ak, tipo_corpus="documentos"):
    """
    Lee el documento UNA SOLA VEZ y genera un resumen rico independiente de patrones.
    Este resumen se reutiliza para todas las búsquedas de patrones posteriores.
    Usa los primeros 6 000 caracteres para minimizar costo.
    """
    h        = hashlib.md5(texto.encode("utf-8")).hexdigest()
    extracto = texto[:6000]
    ctx      = tipo_corpus.strip() if tipo_corpus.strip() else "documentos"

    prompt = (
        f"Eres un asistente experto en análisis de documentos jurídicos.\n"
        f"El investigador está trabajando con: {ctx}.\n\n"
        "Analiza el siguiente documento y genera un resumen estructurado lo más rico posible.\n"
        "Responde ÚNICAMENTE con un objeto JSON con exactamente estas claves:\n"
        "{\n"
        '  "tipo_documento": "tipo de documento jurídico (sentencia, contrato, laudo, resolución, dictamen, etc.)",\n'
        '  "conclusion_principal": "decisión, fallo o conclusión principal del documento en máximo 8 palabras",\n'
        '  "resolucion": "mismo que conclusion_principal, para compatibilidad",\n'
        '  "resumen": "3-4 oraciones que describan: qué tipo de documento es, cuál es su objeto o materia, cuáles son los argumentos o fundamentos centrales, y cuál es el resultado o posición adoptada",\n'
        '  "actores": "partes, autoridades, instituciones, personas o entidades principales mencionadas en el documento",\n'
        '  "referencias_normativas": "leyes, artículos, normas, criterios jurisprudenciales o instrumentos citados en el documento",\n'
        '  "temas_juridicos": "temas, figuras jurídicas, derechos o conceptos legales centrales del documento",\n'
        '  "argumentacion": "descripción detallada del razonamiento jurídico empleado: cómo se justifican las decisiones, qué lógica argumentativa se sigue, qué evidencias o pruebas se consideran, qué omisiones o irregularidades destacan (3-4 oraciones)"\n'
        "}\n\n"
        "Reglas: adapta el análisis al tipo de documento; cadenas vacías → \"\"; "
        "sin texto antes ni después del JSON.\n\n"
        f"Documento (primeros 6 000 caracteres):\n\"\"\"\n{extracto}\n\"\"\""
    )
    headers = {"Content-Type": "application/json",
               "x-api-key": ak, "anthropic-version": "2023-06-01"}
    body    = {"model": CLAUDE_HAIKU, "max_tokens": 900,
               "messages": [{"role": "user", "content": prompt}]}
    datos = {}
    for intento in range(4):
        try:
            r = requests.post(CLAUDE_URL, headers=headers, json=body, timeout=45)
            if r.status_code == 429:
                time.sleep(30 * (intento + 1))
                continue
            r.raise_for_status()
            raw   = r.json()["content"][0]["text"].strip().strip("```json").strip("```").strip()
            datos = json.loads(raw)
            break
        except Exception as e:
            if intento == 3:
                datos = {"_error": str(e)}
            else:
                time.sleep(10)
    datos["_hash"]      = h
    datos["_documento"] = nombre
    return datos


def indexar_corpus_paralelo(corpus, ak, tipo_corpus="documentos", cb_progreso=None):
    """Indexa todo el corpus con ThreadPoolExecutor (IA_WORKERS hilos)."""
    resultado   = {}
    total       = len(corpus)
    completados = 0
    with ThreadPoolExecutor(max_workers=IA_WORKERS) as ex:
        futures = {ex.submit(indexar_documento, n, t, ak, tipo_corpus): n
                   for n, t in corpus.items()}
        for f in as_completed(futures):
            nombre       = futures[f]
            completados += 1
            if cb_progreso:
                cb_progreso(completados, total, nombre)
            try:
                resultado[nombre] = f.result()
            except Exception as e:
                resultado[nombre] = {"_documento": nombre, "_error": str(e)}
    return resultado


def buscar_patron_en_indice(indice, patron, ak, tipo_corpus="documentos"):
    """
    Busca un patrón en el índice ya construido SIN releer los documentos originales.
    Envía los resúmenes en lotes de 25 a Claude y pregunta cuáles coinciden.
    Devuelve dict {nombre_doc: True/False}.
    """
    if not indice:
        return {}

    ctx = tipo_corpus.strip() if tipo_corpus.strip() else "documentos"
    validos = [(n, d) for n, d in indice.items() if "_error" not in d]
    LOTE = 25
    resultados = {}

    for i in range(0, len(validos), LOTE):
        lote = validos[i:i + LOTE]
        fichas = []
        for nombre, datos in lote:
            fichas.append({
                "doc"                  : nombre,
                "tipo_documento"       : datos.get("tipo_documento", ""),
                "conclusion_principal" : datos.get("conclusion_principal", datos.get("resolucion", "")),
                "resumen"              : datos.get("resumen", ""),
                "actores"              : datos.get("actores", ""),
                "referencias_normativas": datos.get("referencias_normativas", ""),
                "temas_juridicos"      : datos.get("temas_juridicos", datos.get("temas", "")),
                "argumentacion"        : datos.get("argumentacion", datos.get("patrones_razonamiento", "")),
            })
        fichas_str = json.dumps(fichas, ensure_ascii=False)
        prompt = (
            f"Eres un asistente de investigación experto en {ctx}.\n\n"
            f"El investigador busca documentos que muestren el siguiente patrón:\n"
            f"\"{patron}\"\n\n"
            "A continuación hay fichas con el resumen de cada documento. "
            "Determina cuáles muestran ese patrón basándote en los resúmenes.\n\n"
            f"Fichas:\n{fichas_str}\n\n"
            "Responde ÚNICAMENTE con JSON:\n"
            "{\"resultados\": [{\"doc\": \"nombre\", \"coincide\": true}, ...]}\n"
            "Incluye TODOS los documentos del lote con true o false. "
            "Sin texto antes ni después del JSON."
        )
        headers = {"Content-Type": "application/json",
                   "x-api-key": ak, "anthropic-version": "2023-06-01"}
        body = {"model": CLAUDE_HAIKU, "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]}
        for intento in range(3):
            try:
                r = requests.post(CLAUDE_URL, headers=headers, json=body, timeout=45)
                if r.status_code == 429:
                    time.sleep(30 * (intento + 1))
                    continue
                r.raise_for_status()
                raw = r.json()["content"][0]["text"].strip().strip("```json").strip("```").strip()
                parsed = json.loads(raw)
                for entry in parsed.get("resultados", []):
                    resultados[entry["doc"]] = bool(entry.get("coincide", False))
                break
            except Exception:
                if intento == 2:
                    # Si falla el lote, marcar todos como False
                    for nombre, _ in lote:
                        resultados[nombre] = False
                else:
                    time.sleep(10)
    return resultados


def consultar_indice(indice, consulta, ak):
    """
    Manda el índice completo a Haiku en lotes de 30 fichas.
    Devuelve lista de {doc, razon} para los que coinciden con la consulta.
    """
    if not indice:
        return []
    entradas = []
    for nombre, datos in indice.items():
        ficha = {k: v for k, v in datos.items() if not k.startswith("_")}
        ficha["_doc"] = nombre
        entradas.append(ficha)

    LOTE   = 30
    matches = []
    for i in range(0, len(entradas), LOTE):
        lote_str = json.dumps(entradas[i:i+LOTE], ensure_ascii=False)
        prompt   = (
            f"Investigador busca: \"{consulta}\"\n\n"
            f"Fichas de sentencias (JSON):\n{lote_str}\n\n"
            "¿Cuáles fichas coinciden con la búsqueda? "
            "Responde SOLO con JSON:\n"
            "{\"matches\": [{\"doc\": \"nombre\", \"razon\": \"explicación breve\"}]}\n"
            "Si ninguna coincide: {\"matches\": []}"
        )
        headers = {"Content-Type": "application/json",
                   "x-api-key": ak, "anthropic-version": "2023-06-01"}
        body    = {"model": CLAUDE_HAIKU, "max_tokens": 1200,
                   "messages": [{"role": "user", "content": prompt}]}
        try:
            r   = requests.post(CLAUDE_URL, headers=headers, json=body, timeout=30)
            r.raise_for_status()
            raw = r.json()["content"][0]["text"].strip().strip("```json").strip("```").strip()
            matches.extend(json.loads(raw).get("matches", []))
        except Exception:
            pass
    return matches


def guardar_set(resultados):
    nombre = f"SET_{st.session_state.set_counter}"
    st.session_state.sets[nombre] = resultados
    st.session_state.set_counter += 1
    return nombre


def exportar_csv(nombres, corpus, terminos):
    filas = []
    for nombre in nombres:
        texto    = corpus.get(nombre, "")
        extracto = obtener_extracto(texto, terminos)
        filas.append({
            "documento"                    : nombre,
            "extracto"                     : extracto,
            "pertinente_validacion_humana" : "",
            "observacion_investigador"     : "",
            "revisado_manualmente"         : "Sí" if nombre in st.session_state.revisados else "No",
        })
    df = pd.DataFrame(filas)
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")


tab1, tab2, tab3, tab4 = st.tabs(
    ["🔬 Análisis IA", "📊 Estadísticas", "🔗 Referencias", "📋 Historial"]
)

# ── TAB 2: ESTADÍSTICAS ─────────────────────────────────────────────────────
with tab2:
    st.subheader("📊 Estadísticas")
    if not st.session_state.corpus:
        st.info("Carga el corpus primero.")
    else:
        st.metric("Total documentos", len(st.session_state.corpus))
        if st.session_state.sets:
            filas_stats = []
            for nombre_set, lista in st.session_state.sets.items():
                pct = len(lista) / len(st.session_state.corpus) * 100
                filas_stats.append({
                    "Set"         : nombre_set,
                    "Documentos"  : len(lista),
                    "% del corpus": f"{pct:.1f}%"
                })
            st.dataframe(pd.DataFrame(filas_stats), use_container_width=True)
            st.markdown("---")
            nombres_sets = list(st.session_state.sets.keys())
            if len(nombres_sets) >= 2:
                st.subheader("Comparar dos sets")
                col1, col2 = st.columns(2)
                with col1:
                    set_a = st.selectbox("Set A", nombres_sets, key="cmp_a")
                with col2:
                    set_b = st.selectbox("Set B", nombres_sets, index=1, key="cmp_b")
                if st.button("Comparar"):
                    a = set(st.session_state.sets[set_a])
                    b = set(st.session_state.sets[set_b])
                    interseccion = a & b
                    col1, col2, col3 = st.columns(3)
                    col1.metric(f"Solo en {set_a}", len(a - b))
                    col2.metric("En ambos",         len(interseccion))
                    col3.metric(f"Solo en {set_b}", len(b - a))
                    if interseccion:
                        st.success(f"Intersección guardada como **{guardar_set(list(interseccion))}**")

# ── TAB 3: REFERENCIAS — genérico y configurable ─────────────────────────────
with tab3:
    st.subheader("🔗 Búsqueda de referencias")
    st.caption(
        "Identifica y cuenta referencias específicas en el corpus: "
        "artículos, normas, criterios, cláusulas o cualquier patrón recurrente."
    )
    if not st.session_state.corpus:
        st.info("Carga el corpus primero.")
    else:
        set_para_ref = st.selectbox(
            "Analizar en:",
            ["Todo el corpus"] + list(st.session_state.sets.keys()),
            key="sel_ref"
        )
        st.markdown("**Define los patrones que quieres identificar:**")
        st.caption(
            "Un patrón por línea. Puedes escribir texto literal "
            "o expresiones regulares básicas."
        )
        patrones_txt = st.text_area(
            "Patrones:",
            placeholder=(
                "artículo 16\n"
                "fracción [IVX]+\n"
                "cláusula \\w+\n"
                "registro[:\\s]+\\d{6,7}"
            ),
            height=140,
            key="patrones_ref"
        )

        if st.button("🔎 Identificar referencias", type="primary"):
            patrones_lista = [p.strip() for p in patrones_txt.splitlines() if p.strip()]
            if not patrones_lista:
                st.error("Escribe al menos un patrón.")
            else:
                if set_para_ref == "Todo el corpus":
                    subcorpus = st.session_state.corpus
                else:
                    nombres = st.session_state.sets[set_para_ref]
                    subcorpus = {
                        n: st.session_state.corpus[n]
                        for n in nombres if n in st.session_state.corpus
                    }
                with st.spinner(f"Analizando {len(subcorpus)} documentos..."):
                    conteo_ref = {}
                    for nombre, texto in subcorpus.items():
                        for ref in identificar_referencias(texto, patrones_lista):
                            conteo_ref[ref] = conteo_ref.get(ref, 0) + 1
                if conteo_ref:
                    df_ref = pd.DataFrame(
                        sorted(conteo_ref.items(), key=lambda x: -x[1]),
                        columns=["Referencia encontrada", "Frecuencia"]
                    )
                    st.dataframe(df_ref, use_container_width=True, height=400)
                    csv_r = df_ref.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
                    st.download_button("⬇️ Exportar CSV", csv_r, "referencias.csv", "text/csv")
                else:
                    st.warning("No se encontraron referencias con los patrones indicados.")

# ── TAB 4: HISTORIAL — sin cambios ──────────────────────────────────────────
with tab4:
    st.subheader("📋 Historial")
    if not st.session_state.historial:
        st.info("Sin consultas registradas.")
    else:
        for h in reversed(st.session_state.historial):
            with st.expander(f"[{h['set']}] {h['consulta'][:80]}"):
                st.write(
                    f"**Base:** {h['base']} | "
                    f"**Resultados:** {h['resultados']} | "
                    f"**Estrategia:** {h['estrategia']}"
                )
                st.write(f"**Términos:** {', '.join(h['terminos'])}")
        if st.button("🗑️ Limpiar historial"):
            st.session_state.historial = []
            st.rerun()

# ── TAB 1: ANÁLISIS IA ───────────────────────────────────────────────────────
with tab1:
    st.subheader("🔬 Análisis semántico de corpus")

    # ── Guía de inicio ────────────────────────────────────────────────────────
    if not api_key or not st.session_state.corpus:
        st.markdown("#### Para comenzar, completa los pasos en el panel izquierdo:")
        c1, c2 = st.columns(2)
        c1.markdown(f"{'✅' if api_key else '⬜'} **Paso 1**  \nIngresa tu API Key")
        c2.markdown(f"{'✅' if st.session_state.corpus else '⬜'} **Paso 2**  \nCarga tu corpus")
    else:
        # ── Sección 1: Indexar ────────────────────────────────────────────────
        st.markdown("### 1 · Indexar corpus")
        st.caption(
            "Claude lee cada documento **una sola vez** y genera un resumen estructurado. "
            "Ese resumen se reutiliza para todas las búsquedas de patrones posteriores — "
            "sin costo adicional por documento. "
            "Guarda el índice como JSON para reutilizarlo en sesiones futuras."
        )

        n_corp     = len(st.session_state.corpus)
        n_idx      = len(st.session_state.indice)
        pendientes = n_corp - n_idx

        col_idx1, col_idx2, col_idx3 = st.columns(3)
        col_idx1.metric("Docs en corpus",   n_corp)
        col_idx2.metric("Docs indexados",   n_idx)
        col_idx3.metric("Pendientes",       pendientes)

        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            btn_indexar = st.button(
                "⚡ Indexar corpus" if pendientes == n_corp else "⚡ Indexar pendientes",
                type="primary", use_container_width=True, key="btn_indexar",
                disabled=(pendientes == 0)
            )
        with col_b2:
            idx_file = st.file_uploader(
                "Cargar índice (JSON)", type=["json"], key="carga_indice",
                help="Sube un índice guardado para continuar sin re-indexar."
            )
            if idx_file:
                try:
                    cargado = json.loads(idx_file.read().decode("utf-8"))
                    if "_busquedas" in cargado:
                        saved_busq = cargado.pop("_busquedas")
                        st.session_state.busquedas.update(saved_busq)
                    # compatibilidad con índices viejos
                    cargado.pop("_esquema", None)
                    st.session_state.indice = cargado
                    st.success(f"✅ Índice cargado: {len(cargado)} documentos.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al cargar: {e}")
        with col_b3:
            if st.session_state.indice:
                exportable = dict(st.session_state.indice)
                exportable["_busquedas"] = {
                    p: dict(r) for p, r in st.session_state.busquedas.items()
                }
                json_bytes = json.dumps(exportable, ensure_ascii=False, indent=2).encode("utf-8")
                st.download_button(
                    "💾 Guardar índice (JSON)",
                    data=json_bytes,
                    file_name="indice_corpus.json",
                    mime="application/json",
                    use_container_width=True
                )

        if btn_indexar:
            pendientes_dict = {
                n: t for n, t in st.session_state.corpus.items()
                if n not in st.session_state.indice
            }
            if not pendientes_dict:
                st.info("Todos los documentos ya están indexados.")
            else:
                barra = st.progress(0, text="Iniciando indexación...")

                def _cb(completados, total, nombre):
                    barra.progress(
                        completados / total,
                        text=f"Indexando {completados}/{total}: {nombre[:55]}"
                    )

                tipo_c = st.session_state.get("descripcion_corpus", "documentos")
                nuevos = indexar_corpus_paralelo(pendientes_dict, api_key, tipo_c, _cb)
                st.session_state.indice.update(nuevos)
                barra.empty()
                errores = sum(1 for v in nuevos.values() if "_error" in v)
                st.success(
                    f"✅ {len(nuevos) - errores} documentos indexados"
                    + (f" ({errores} con error)." if errores else ".")
                )
                if errores:
                    muestra = [
                        f"{v['_documento']}: {v['_error']}"
                        for v in nuevos.values() if "_error" in v
                    ][:5]
                    with st.expander(f"Ver errores ({min(5, errores)} de {errores})"):
                        for e in muestra:
                            st.code(e)

        # ── A partir de aquí solo si hay índice ──────────────────────────────
        if st.session_state.indice:
            validos = [v for v in st.session_state.indice.values() if "_error" not in v]
            n_val   = len(validos)

            # ── Sección 2: Buscar patrón ──────────────────────────────────────
            st.markdown("---")
            st.markdown("### 2 · Buscar un patrón en el corpus")
            st.caption(
                "Describe el fenómeno que quieres detectar. "
                "Claude comparará tu descripción contra los resúmenes ya guardados en el índice — "
                "sin releer los documentos originales. "
                "Puedes hacer tantas búsquedas como necesites sobre el mismo índice."
            )

            col_pat1, col_pat2, col_pat3 = st.columns([5, 1, 1])
            with col_pat1:
                nuevo_patron = st.text_input(
                    "Patrón a buscar:",
                    placeholder="Ej: Casos donde la autoridad no respondió el escrito del particular",
                    key="nuevo_patron_input"
                )
            with col_pat2:
                st.markdown("<br>", unsafe_allow_html=True)
                btn_buscar = st.button(
                    "🔍 Buscar", type="primary",
                    use_container_width=True, key="btn_buscar_patron"
                )
            with col_pat3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️ Limpiar", use_container_width=True, key="btn_limpiar_busquedas",
                             help="Borra todos los resultados de búsqueda anteriores. El índice se conserva."):
                    st.session_state.busquedas = {}
                    st.session_state.confirmados = {}
                    st.rerun()

            if btn_buscar:
                if not nuevo_patron.strip():
                    st.error("Escribe un patrón para buscar.")
                elif nuevo_patron.strip() in st.session_state.busquedas:
                    st.info("Este patrón ya fue buscado. Puedes verlo en la tabla de abajo.")
                else:
                    with st.spinner(f"Buscando patrón en {n_val} documentos del índice..."):
                        tipo_c = st.session_state.get("descripcion_corpus", "documentos")
                        resultados_patron = buscar_patron_en_indice(
                            st.session_state.indice, nuevo_patron.strip(), api_key, tipo_c
                        )
                    st.session_state.busquedas[nuevo_patron.strip()] = resultados_patron
                    n_enc = sum(1 for v in resultados_patron.values() if v)
                    st.success(
                        f"✅ Patrón encontrado en {n_enc} de {len(resultados_patron)} documentos."
                    )
                    st.rerun()

            # ── Sección 3: Frecuencias ────────────────────────────────────────
            if st.session_state.busquedas:
                st.markdown("---")
                st.markdown("### 3 · Frecuencias de patrones buscados")

                # Tabla con botón de eliminar por fila
                for pat_desc, pat_res in list(st.session_state.busquedas.items()):
                    cuenta  = sum(1 for v in pat_res.values() if v)
                    total_b = len(pat_res)
                    pct     = f"{cuenta/total_b*100:.1f}%" if total_b else "—"
                    col_desc, col_docs, col_pct, col_del = st.columns([6, 1, 1, 1])
                    col_desc.markdown(
                        f'<div style="padding:6px 0;font-size:0.88rem;color:#F0EBE3;">{pat_desc}</div>',
                        unsafe_allow_html=True
                    )
                    col_docs.markdown(
                        f'<div style="padding:6px 0;text-align:center;font-weight:700;color:#C8622A;">{cuenta}</div>',
                        unsafe_allow_html=True
                    )
                    col_pct.markdown(
                        f'<div style="padding:6px 0;text-align:center;color:#A89A8E;">{pct}</div>',
                        unsafe_allow_html=True
                    )
                    with col_del:
                        if st.button("✕", key=f"del_pat_{hash(pat_desc)}",
                                     help="Eliminar esta búsqueda (el índice se conserva)"):
                            del st.session_state.busquedas[pat_desc]
                            st.session_state.confirmados.pop(pat_desc, None)
                            st.rerun()
                st.divider()
                resoluciones = {}
                for v in validos:
                    r = str(v.get("resolucion", "otro"))[:30]
                    resoluciones[r] = resoluciones.get(r, 0) + 1
                top_res = sorted(resoluciones.items(), key=lambda x: -x[1])[:5]
                if top_res:
                    cols_res = st.columns(len(top_res))
                    for i, (res, cnt) in enumerate(top_res):
                        cols_res[i].metric(res.capitalize(), cnt)

            # ── Sección 4: Validar hallazgos ──────────────────────────────────
            if st.session_state.busquedas:
                st.markdown("---")
                st.markdown("### 4 · Validar hallazgos por patrón")
                st.caption(
                    "Selecciona un patrón, revisa los documentos donde la IA lo detectó "
                    "y palomea los que confirmas. El total validado es tu cifra definitiva."
                )

                patron_sel_desc = st.selectbox(
                    "Patrón a validar:",
                    list(st.session_state.busquedas.keys()),
                    key="sel_patron_validar"
                )
                resultados_sel       = st.session_state.busquedas[patron_sel_desc]
                docs_det_nombres     = [n for n, v in resultados_sel.items() if v]
                docs_detectados      = [
                    st.session_state.indice[n]
                    for n in docs_det_nombres
                    if n in st.session_state.indice and "_error" not in st.session_state.indice[n]
                ]

                if patron_sel_desc not in st.session_state.confirmados:
                    st.session_state.confirmados[patron_sel_desc] = set()
                confirmados_set = st.session_state.confirmados[patron_sel_desc]

                n_det  = len(docs_detectados)
                n_conf = len(confirmados_set)
                mc1, mc2, mc3, mc4 = st.columns([2, 2, 2, 2])
                mc1.metric("Detectados por IA", n_det)
                mc2.metric("Confirmados",       n_conf)
                mc3.metric("Precisión", f"{n_conf/n_det*100:.0f}%" if n_det else "—")
                with mc4:
                    if st.button("🔄 Limpiar validación", use_container_width=True,
                                 key="btn_limpiar_validacion",
                                 help="Limpia las palomitas. El índice y las búsquedas se conservan."):
                        st.session_state.confirmados[patron_sel_desc] = set()
                        st.rerun()

                if not docs_detectados:
                    st.info("La IA no detectó este patrón en ningún documento del índice.")
                else:
                    st.markdown(f"**{n_det} documento(s) detectados** — palomea los que confirmas:")
                    st.markdown("")
                    for doc_ficha in docs_detectados:
                        nombre_doc   = doc_ficha.get("_documento", "")
                        resumen      = doc_ficha.get("resumen", "")
                        argumentacion = doc_ficha.get("argumentacion", doc_ficha.get("patrones_razonamiento", ""))
                        conclusion   = doc_ficha.get("conclusion_principal", doc_ficha.get("resolucion", ""))
                        tipo_doc     = doc_ficha.get("tipo_documento", "")
                        confirmado   = nombre_doc in confirmados_set
                        col_chk, col_info = st.columns([1, 8])
                        with col_chk:
                            checked = st.checkbox(
                                "✓", value=confirmado,
                                key=f"chk_{hash(patron_sel_desc)}_{nombre_doc}"
                            )
                            if checked and nombre_doc not in confirmados_set:
                                st.session_state.confirmados[patron_sel_desc].add(nombre_doc)
                                st.rerun()
                            elif not checked and nombre_doc in confirmados_set:
                                st.session_state.confirmados[patron_sel_desc].discard(nombre_doc)
                                st.rerun()
                        with col_info:
                            tipo_tag = f'<span style="color:#6B7E92;font-size:0.72rem;text-transform:uppercase;letter-spacing:.05em;">{html.escape(tipo_doc)}</span>  ' if tipo_doc else ""
                            st.markdown(
                                f'<div style="background:{"#1a3a1a" if confirmado else "#1E2D40"};'
                                f'border-left:4px solid {"#4CAF50" if confirmado else "#C8622A"};'
                                f'padding:10px 14px;border-radius:6px;margin-bottom:6px;">'
                                f'<span style="color:#A89A8E;font-size:0.78rem;">{nombre_doc}</span>  {tipo_tag}<br>'
                                f'<span style="color:#F0EBE3;font-size:0.88rem;">{html.escape(resumen)}</span><br>'
                                + (f'<span style="color:#A89A8E;font-size:0.82rem;font-style:italic;">{html.escape(argumentacion)}</span><br>' if argumentacion else "")
                                + f'<span style="color:#C8622A;font-size:0.78rem;">→ {html.escape(conclusion)}</span>'
                                f'</div>',
                                unsafe_allow_html=True
                            )

                    st.markdown("")
                    filas_val = []
                    for doc_ficha in docs_detectados:
                        nd = doc_ficha.get("_documento", "")
                        filas_val.append({
                            "documento"              : nd,
                            "resumen"                : doc_ficha.get("resumen", ""),
                            "resolucion"             : doc_ficha.get("resolucion", ""),
                            "detectado_ia"           : "Sí",
                            "confirmado_investigador": "Sí" if nd in confirmados_set else "No",
                        })
                    csv_val = pd.DataFrame(filas_val).to_csv(
                        index=False, encoding="utf-8-sig"
                    ).encode("utf-8-sig")
                    st.download_button(
                        f"⬇️ Exportar validación — {patron_sel_desc[:50]} (CSV)",
                        data=csv_val,
                        file_name="validacion_patron.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

            # ── Sección 5: Leer documento completo ────────────────────────────
            st.markdown("---")
            st.markdown("### 5 · Leer documento completo")
            st.caption("Selecciona cualquier documento indexado para leer su texto completo y corroborar los hallazgos.")

            todos_indexados = sorted(st.session_state.indice.keys())
            doc_leer = st.selectbox(
                "Documento:", ["— elige —"] + todos_indexados, key="sel_doc_leer"
            )
            if doc_leer != "— elige —":
                texto_orig = st.session_state.corpus.get(doc_leer, "")
                if texto_orig:
                    st.markdown(
                        f'<div style="height:520px;overflow-y:scroll;border:1px solid #2A3D52;'
                        f'padding:16px 20px;font-family:monospace;font-size:0.83rem;'
                        f'white-space:pre-wrap;background:#172030;color:#F0EBE3;'
                        f'border-radius:8px;line-height:1.65;">'
                        f'{html.escape(texto_orig)}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.warning("El documento no está en memoria. Súbelo en el panel izquierdo.")

