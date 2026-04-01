import streamlit as st
import os
import re
import json
import html
import hashlib
import requests
import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

CARPETA_TXT  = os.environ.get("CARPETA_TXT", r"C:\Users\kians\Desktop\sentencias individuales txt")
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_HAIKU = "claude-haiku-4-5-20251001"   # para detección IA: 20× más rápido y barato
CLAUDE_URL   = "https://api.anthropic.com/v1/messages"
IA_WORKERS   = 8                              # llamadas paralelas a la API

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

with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input("API Key de Claude", type="password", key="api_key")

    st.markdown("---")

    # NUEVO: descripción del corpus que calibra a Claude
    st.header("📋 Tipo de corpus")
    descripcion_corpus = st.text_area(
        "Describe brevemente tus documentos:",
        placeholder=(
            "Ej: sentencias de amparo indirecto en materia administrativa "
            "emitidas por juzgados federales en México\n\n"
            "Ej: contratos de arrendamiento comercial\n\n"
            "Ej: laudos arbitrales en materia mercantil"
        ),
        height=110,
        key="descripcion_corpus",
        help=(
            "Esta descripción le indica a Claude qué tipo de documentos "
            "está analizando, para que genere términos de búsqueda "
            "calibrados al lenguaje específico de tu corpus."
        )
    )
    if not descripcion_corpus.strip():
        st.caption("⚠️ Describe tu corpus para obtener mejores términos de búsqueda.")

    st.markdown("---")
    st.header("📂 Corpus")
    archivos_subidos = st.file_uploader(
        "Sube tus archivos TXT",
        type=["txt"],
        accept_multiple_files=True,
        help="Selecciona uno o varios archivos .txt para cargar tu corpus."
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
        st.info(f"📄 {len(st.session_state.corpus)} documentos en memoria")
        if st.button("🗑️ Limpiar corpus", use_container_width=True):
            st.session_state.corpus = {}
            st.rerun()
    st.markdown("---")
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

CAMPOS_BOOLEANOS = [
    ("omite_transcripcion_conceptos",        "Omite transcripción de conceptos/agravios"),
    ("silencio_administrativo",              "Acto reclamado: silencio/omisión de autoridad"),
    ("clausula_precariedad",                 "Cláusula de precariedad (tóner/papel)"),
    ("rechazo_documento_digital",            "Rechazo de documento digital/QR"),
    ("sesgo_negativa_autoridad",             "Sesgo: negativa de autoridad como verdad base"),
    ("sobreseimiento",                       "Sentencia: sobreseimiento"),
    ("delegacion_pericial_acritica",         "Delegación acrítica en perito"),
    ("hecho_notorio_digital_sin_protocolo",  "Hecho notorio digital sin protocolo"),
]

_ESQUEMA_PROMPT = """{
  "omite_transcripcion_conceptos": bool,
  "justificacion_omision": "cita breve o ''",
  "silencio_administrativo": bool,
  "tipo_acto_reclamado": "descripción breve",
  "clausula_precariedad": bool,
  "texto_precariedad": "cita o ''",
  "rechazo_documento_digital": bool,
  "razon_rechazo_digital": "razón o ''",
  "sesgo_negativa_autoridad": bool,
  "sobreseimiento": bool,
  "delegacion_pericial_acritica": bool,
  "hecho_notorio_digital_sin_protocolo": bool,
  "resolucion": "concede | niega | sobresee | otro",
  "resumen": "máximo 2 oraciones del caso"
}"""


def indexar_documento(nombre, texto, ak):
    """
    Extrae el JSON estructurado de una sentencia con Haiku.
    Solo usa los primeros 6 000 caracteres (~1 500 tokens) para minimizar costo.
    Retorna el dict JSON más _hash y _documento.
    """
    h       = hashlib.md5(texto.encode("utf-8")).hexdigest()
    extracto = texto[:6000]
    prompt  = (
        "Eres un asistente de análisis jurídico mexicano.\n"
        "Analiza esta sentencia de amparo y extrae información estructurada.\n"
        "Responde ÚNICAMENTE con un objeto JSON que tenga exactamente estas claves:\n\n"
        f"{_ESQUEMA_PROMPT}\n\n"
        "Reglas: bool → true/false en minúsculas; texto vacío → \"\"; "
        "sin texto antes ni después del JSON.\n\n"
        f"Sentencia (primeros 6 000 caracteres):\n\"\"\"\n{extracto}\n\"\"\""
    )
    headers = {"Content-Type": "application/json",
               "x-api-key": ak, "anthropic-version": "2023-06-01"}
    body    = {"model": CLAUDE_HAIKU, "max_tokens": 600,
               "messages": [{"role": "user", "content": prompt}]}
    try:
        r    = requests.post(CLAUDE_URL, headers=headers, json=body, timeout=30)
        r.raise_for_status()
        raw  = r.json()["content"][0]["text"].strip().strip("```json").strip("```").strip()
        datos = json.loads(raw)
    except Exception as e:
        datos = {"_error": str(e)}
    datos["_hash"]      = h
    datos["_documento"] = nombre
    return datos


def indexar_corpus_paralelo(corpus, ak, cb_progreso=None):
    """Indexa todo el corpus en paralelo con ThreadPoolExecutor (IA_WORKERS hilos)."""
    resultado   = {}
    total       = len(corpus)
    completados = 0
    with ThreadPoolExecutor(max_workers=IA_WORKERS) as ex:
        futures = {ex.submit(indexar_documento, n, t, ak): n
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


tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Estadísticas", "🔗 Referencias", "📋 Historial", "📑 Índice IA"]
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

# ── TAB 5: ÍNDICE IA ─────────────────────────────────────────────────────────
with tab5:
    st.subheader("📑 Índice semántico IA")
    st.caption(
        "Indexa el corpus una sola vez (Haiku, ~$2-4). "
        "Luego consulta cualquier patrón en lenguaje natural en segundos, "
        "sin gastar tokens adicionales."
    )

    if not st.session_state.corpus:
        st.warning("⬅️ Primero carga los TXT desde el panel izquierdo.")
    elif not api_key:
        st.warning("⬅️ Ingresa tu API Key en el panel izquierdo.")
    else:
        # ── Sección 1: Indexar ────────────────────────────────────────────────
        st.markdown("### 1 · Indexar corpus")
        n_corp  = len(st.session_state.corpus)
        n_idx   = len(st.session_state.indice)
        pendientes = n_corp - n_idx

        col_idx1, col_idx2, col_idx3 = st.columns(3)
        col_idx1.metric("Documentos en corpus",   n_corp)
        col_idx2.metric("Documentos indexados",   n_idx)
        col_idx3.metric("Pendientes",             pendientes)

        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            btn_indexar = st.button(
                "⚡ Indexar corpus" if pendientes == n_corp else "⚡ Indexar pendientes",
                type="primary", use_container_width=True, key="btn_indexar"
            )
        with col_b2:
            # Cargar índice guardado
            idx_file = st.file_uploader(
                "Cargar índice (JSON)", type=["json"], key="carga_indice",
                help="Sube un índice guardado previamente para no re-indexar."
            )
            if idx_file:
                try:
                    cargado = json.loads(idx_file.read().decode("utf-8"))
                    st.session_state.indice = cargado
                    st.success(f"✅ Índice cargado: {len(cargado)} documentos.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al cargar: {e}")
        with col_b3:
            if st.session_state.indice:
                json_bytes = json.dumps(
                    st.session_state.indice, ensure_ascii=False, indent=2
                ).encode("utf-8")
                st.download_button(
                    "💾 Guardar índice (JSON)",
                    data=json_bytes,
                    file_name="indice_corpus.json",
                    mime="application/json",
                    use_container_width=True
                )

        if btn_indexar:
            # Solo indexar los documentos que aún no están en el índice
            pendientes_dict = {
                n: t for n, t in st.session_state.corpus.items()
                if n not in st.session_state.indice
            }
            if not pendientes_dict:
                st.info("Todos los documentos ya están indexados.")
            else:
                barra   = st.progress(0, text="Iniciando indexación...")
                counter = {"n": 0}

                def _cb(completados, total, nombre):
                    counter["n"] = completados
                    barra.progress(
                        completados / total,
                        text=f"Indexando {completados}/{total}: {nombre[:55]}"
                    )

                nuevos = indexar_corpus_paralelo(pendientes_dict, api_key, _cb)
                st.session_state.indice.update(nuevos)
                barra.empty()
                errores = sum(1 for v in nuevos.values() if "_error" in v)
                st.success(
                    f"✅ Indexación completa. "
                    f"{len(nuevos) - errores} documentos procesados"
                    + (f", {errores} con error." if errores else ".")
                )

        # ── Estadísticas del índice ───────────────────────────────────────────
        if st.session_state.indice:
            st.markdown("---")
            st.markdown("### 2 · Frecuencias de patrones detectados")
            st.caption(
                "Porcentaje de sentencias donde Haiku detectó cada patrón. "
                "Base: documentos indexados sin error."
            )
            validos = [v for v in st.session_state.indice.values() if "_error" not in v]
            n_val   = len(validos)
            if n_val:
                filas_freq = []
                for campo, etiqueta in CAMPOS_BOOLEANOS:
                    cuenta = sum(1 for v in validos if v.get(campo) is True)
                    filas_freq.append({
                        "Patrón"          : etiqueta,
                        "Documentos"      : cuenta,
                        "% del corpus"    : f"{cuenta/n_val*100:.1f}%",
                    })
                st.dataframe(
                    pd.DataFrame(filas_freq).sort_values("Documentos", ascending=False),
                    use_container_width=True, hide_index=True
                )

                # Distribución de resoluciones
                resoluciones = {}
                for v in validos:
                    r = v.get("resolucion", "otro")
                    resoluciones[r] = resoluciones.get(r, 0) + 1
                cols_res = st.columns(len(resoluciones))
                for i, (res, cnt) in enumerate(
                    sorted(resoluciones.items(), key=lambda x: -x[1])
                ):
                    cols_res[i].metric(res.capitalize(), cnt)

            # ── Sección 3: Consultar ──────────────────────────────────────────
            st.markdown("---")
            st.markdown("### 3 · Consultar índice en lenguaje natural")
            st.caption(
                "Describe el patrón que buscas. Claude compara tu descripción "
                "con las fichas del índice. Sin keywords, sin límites de patrón."
            )

            consulta_ia = st.text_area(
                "¿Qué buscas?",
                placeholder=(
                    "Ej: sentencias donde el juez otorga valor pleno al perito sin cuestionarlo\n"
                    "Ej: casos de sobreseimiento basados solo en el informe de la autoridad\n"
                    "Ej: resoluciones que validan documentos de internet sin verificar"
                ),
                height=100,
                key="consulta_ia"
            )

            col_q1, col_q2 = st.columns(2)
            with col_q1:
                btn_consultar = st.button(
                    "🔍 Consultar", type="primary",
                    use_container_width=True, key="btn_consultar_ia"
                )
            with col_q2:
                if st.button("🗑️ Limpiar resultados", use_container_width=True, key="btn_limpiar_ia"):
                    st.session_state.ia_resultados_consulta = []
                    st.rerun()

            if btn_consultar:
                if not consulta_ia.strip():
                    st.error("Escribe una consulta.")
                else:
                    with st.spinner("Consultando índice..."):
                        matches = consultar_indice(
                            st.session_state.indice, consulta_ia, api_key
                        )
                    st.session_state.ia_resultados_consulta = matches
                    st.success(
                        f"✅ {len(matches)} documento(s) coinciden con la búsqueda."
                    )

            # ── Resultados de consulta ────────────────────────────────────────
            if st.session_state.ia_resultados_consulta:
                matches = st.session_state.ia_resultados_consulta
                st.markdown(f"#### {len(matches)} resultados")

                filas_res = []
                for m in matches:
                    doc    = m.get("doc", "")
                    razon  = m.get("razon", "")
                    ficha  = st.session_state.indice.get(doc, {})
                    filas_res.append({
                        "Documento" : doc,
                        "Razón IA"  : razon,
                        "Resolución": ficha.get("resolucion", ""),
                        "Resumen"   : ficha.get("resumen", ""),
                        "Revisado"  : "Sí" if doc in st.session_state.ia_revisados else "No",
                    })
                st.dataframe(
                    pd.DataFrame(filas_res),
                    use_container_width=True, height=380
                )

                # Visor de texto original + botón marcar
                st.markdown("---")
                st.markdown("#### 📖 Ver texto original")
                opciones = ["— Elige un documento —"] + [m.get("doc","") for m in matches]
                doc_sel  = st.selectbox("Documento:", opciones, key="ia_visor_sel")

                if doc_sel != "— Elige un documento —":
                    texto_orig = st.session_state.corpus.get(doc_sel, "")
                    st.markdown(
                        f'<div style="height:480px;overflow-y:scroll;border:1px solid #2A3D52;'
                        f'padding:16px 20px;font-family:monospace;font-size:0.83rem;'
                        f'white-space:pre-wrap;background:#172030;color:#F0EBE3;'
                        f'border-radius:8px;line-height:1.65;">'
                        f'{html.escape(texto_orig)}</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown("")
                    if doc_sel in st.session_state.ia_revisados:
                        st.success("✅ Ya marcado como revisado.")
                    else:
                        if st.button("✅ Marcar como revisado", type="primary",
                                     key="ia_marcar_visor"):
                            st.session_state.ia_revisados.add(doc_sel)
                            st.rerun()

                # Exportar CSV
                st.markdown("")
                csv_ia = pd.DataFrame(filas_res).to_csv(
                    index=False, encoding="utf-8-sig"
                ).encode("utf-8-sig")
                st.download_button(
                    "⬇️ Exportar resultados (CSV)",
                    data=csv_ia,
                    file_name="consulta_ia.csv",
                    mime="text/csv",
                    use_container_width=True
                )
