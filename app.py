import streamlit as st
import os
import re
import json
import html
import hashlib
import requests
import pandas as pd
from pathlib import Path

CARPETA_TXT  = os.environ.get("CARPETA_TXT", r"C:\Users\kians\Desktop\sentencias individuales txt")
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_URL   = "https://api.anthropic.com/v1/messages"

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
if "ia_cache" not in st.session_state:
    st.session_state.ia_cache = {}
if "ia_resultados" not in st.session_state:
    st.session_state.ia_resultados = []
if "ia_revisados" not in st.session_state:
    st.session_state.ia_revisados = set()

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


# ── Funciones de detección IA ────────────────────────────────────────────────

def dividir_texto(texto, tamaño=1200):
    """Divide el texto en fragmentos de tamaño fijo para enviar a Claude."""
    return [texto[i:i+tamaño] for i in range(0, len(texto), tamaño)]


def filtrar_documentos(corpus, palabras_clave):
    """Pre-filtro por palabras clave antes de llamar a la IA (sin costo de API)."""
    if not palabras_clave:
        return list(corpus.keys())
    palabras_lower = [p.lower().strip() for p in palabras_clave if p.strip()]
    return [nombre for nombre, texto in corpus.items()
            if any(p in texto.lower() for p in palabras_lower)]


def evaluar_chunk_con_ia(chunk, ak):
    """Envía un fragmento a Claude y pregunta si contiene la omisión buscada."""
    prompt = f"""Eres un asistente de análisis jurídico.
Responde SOLO en JSON válido, sin texto adicional.

¿Este texto contiene un caso donde el juez NO transcribe los conceptos de violación o agravios?

Criterios de inclusión:
* El juez declara que es innecesario transcribir los conceptos de violación o agravios
* El juez omite la transcripción sin justificación expresa

Criterios de exclusión:
* El juez sí transcribe los conceptos de violación o agravios
* Solo se menciona el término sin aplicarlo al caso concreto

Formato de respuesta (JSON puro):
{{"match": true/false, "fragmento": "cita textual breve del pasaje relevante, o cadena vacía si no hay match"}}

Texto a analizar:
\"\"\"{chunk}\"\"\""""
    headers = {
        "Content-Type": "application/json",
        "x-api-key": ak,
        "anthropic-version": "2023-06-01"
    }
    body = {
        "model": CLAUDE_MODEL,
        "max_tokens": 256,
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        r = requests.post(CLAUDE_URL, headers=headers, json=body, timeout=30)
        r.raise_for_status()
        raw = r.json()["content"][0]["text"].strip()
        limpia = raw.strip("```json").strip("```").strip()
        return json.loads(limpia)
    except Exception:
        return {"match": False, "fragmento": ""}


def procesar_documento(nombre, texto, ak, cache):
    """Procesa un documento completo con early-stop y caché por hash."""
    h = hashlib.md5(texto.encode("utf-8")).hexdigest()
    if h in cache:
        return cache[h]
    for chunk in dividir_texto(texto):
        resultado = evaluar_chunk_con_ia(chunk, ak)
        if resultado.get("match"):
            res = {"match": True, "fragmento": resultado.get("fragmento", "")}
            cache[h] = res
            return res
    res = {"match": False, "fragmento": ""}
    cache[h] = res
    return res


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


tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["🔍 Búsqueda", "📊 Estadísticas", "🔗 Referencias", "📋 Historial", "🤖 Detección IA"]
)

# ── TAB 1: BÚSQUEDA ─────────────────────────────────────────────────────────
with tab1:
    if not st.session_state.corpus:
        st.warning("⬅️ Primero carga los TXT desde el panel izquierdo.")
    else:
        col1, col2 = st.columns([2, 1])
        with col1:
            consulta = st.text_area(
                "Escribe tu consulta en lenguaje natural:",
                placeholder=(
                    "Ej: documentos donde no se motiva la decisión\n"
                    "Ej: contratos con cláusula de rescisión anticipada\n"
                    "Ej: resoluciones que citan el artículo 16 constitucional"
                ),
                height=100
            )
        with col2:
            set_base = st.selectbox(
                "Buscar dentro de:",
                ["Todo el corpus"] + list(st.session_state.sets.keys())
            )
            max_sin = st.slider("Máx. sinónimos", 0, 6, 3)

        with st.expander("✏️ Escribir términos manualmente (úsalo si los resultados son 0)"):
            st.caption("Un término por línea, 2-4 palabras. Si escribes aquí, se ignoran los términos de Claude.")
            terminos_manuales = st.text_area(
                "Términos:",
                placeholder="término exacto a buscar\notra variante del término",
                height=120,
                key="terminos_manuales"
            )

        if st.button("🔍 Buscar", type="primary", use_container_width=True):
            if not consulta.strip():
                st.error("Escribe una consulta.")
            elif not api_key:
                st.error("Ingresa tu API Key en el panel izquierdo.")
            else:
                manuales_txt = st.session_state.get("terminos_manuales", "").strip()
                if manuales_txt:
                    principales = [l.strip() for l in manuales_txt.splitlines() if l.strip()]
                    sinonimos   = []
                    st.info(f"Usando {len(principales)} términos manuales.")
                else:
                    desc = st.session_state.get("descripcion_corpus", "").strip()
                    with st.spinner("Claude interpretando la consulta..."):
                        datos = extraer_terminos_claude(consulta, desc, max_sin)
                    if "raw" in datos and not datos.get("terminos_principales"):
                        st.error("Claude no pudo interpretar. Respuesta:")
                        st.code(datos.get("raw", ""))
                        st.stop()
                    principales = datos.get("terminos_principales", [])
                    sinonimos   = datos.get("sinonimos", [])

                col_a, col_b = st.columns(2)
                with col_a:
                    st.write("🎯 Principales:", principales)
                with col_b:
                    st.write("🔄 Sinónimos:", sinonimos)

                if set_base == "Todo el corpus":
                    subcorpus = st.session_state.corpus
                else:
                    nombres_set = st.session_state.sets[set_base]
                    subcorpus = {n: st.session_state.corpus[n]
                                 for n in nombres_set if n in st.session_state.corpus}

                with st.spinner(f"Buscando en {len(subcorpus)} documentos..."):
                    resultados, estrategia = buscar_con_fallback(principales, sinonimos, subcorpus)

                total_base = len(subcorpus)
                pct = (len(resultados) / total_base * 100) if total_base > 0 else 0
                st.markdown(f"### Resultados: **{len(resultados)}** documentos ({pct:.1f}% de {total_base})")
                st.caption(f"Estrategia: {estrategia}")

                if resultados:
                    nombre_set     = guardar_set(resultados)
                    todos_terminos = principales + sinonimos
                    st.success(f"✅ Guardado como **{nombre_set}**")
                    st.session_state.historial.append({
                        "set"        : nombre_set,
                        "consulta"   : consulta,
                        "base"       : set_base,
                        "terminos"   : todos_terminos,
                        "resultados" : len(resultados),
                        "estrategia" : estrategia
                    })
                    # Persistir resultados para el visor (sobrevive a reruns del botón "Marcar")
                    st.session_state.ultimo_resultado = {
                        "resultados"    : resultados,
                        "todos_terminos": todos_terminos,
                        "nombre_set"    : nombre_set,
                        "set_base"      : set_base,
                    }
                else:
                    st.session_state.ultimo_resultado = None
                    st.warning(
                        "0 resultados. Abre 'Escribir términos manualmente' "
                        "e intenta con palabras más simples y cortas."
                    )

        # ── Visor de resultados (persiste entre reruns) ─────────────────────
        if st.session_state.ultimo_resultado:
            ur             = st.session_state.ultimo_resultado
            res_nombres    = ur["resultados"]
            res_terminos   = ur["todos_terminos"]
            res_set_name   = ur["nombre_set"]
            res_set_base   = ur["set_base"]

            # Reconstruir subcorpus desde session_state (sin duplicar textos)
            if res_set_base == "Todo el corpus":
                sub = st.session_state.corpus
            else:
                nms = st.session_state.sets.get(res_set_base, [])
                sub = {n: st.session_state.corpus[n]
                       for n in nms if n in st.session_state.corpus}

            # Dataframe de extractos
            filas_display = []
            for nombre in res_nombres[:50]:
                texto    = sub.get(nombre, "")
                extracto = obtener_extracto(texto, res_terminos, 250)
                filas_display.append({"Documento": nombre, "Extracto": extracto})
            st.dataframe(pd.DataFrame(filas_display), use_container_width=True, height=400)
            if len(res_nombres) > 50:
                st.caption(
                    f"_(Mostrando 50 de {len(res_nombres)}. "
                    f"Exporta CSV para ver todos.)_"
                )

            # ── Selector + visor de texto completo ───────────────────────────
            st.markdown("---")
            st.markdown("#### 📖 Leer documento completo")
            opciones_visor = ["— Elige un documento —"] + res_nombres
            doc_sel = st.selectbox(
                "Selecciona un documento para ver su texto completo:",
                opciones_visor,
                key="visor_doc_sel"
            )

            if doc_sel != "— Elige un documento —":
                texto_doc  = sub.get(doc_sel, "")
                texto_html = resaltar_terminos(texto_doc, res_terminos)
                st.markdown(
                    f'<div style="height:540px;overflow-y:scroll;border:1px solid #D0D0D0;'
                    f'padding:18px 20px;font-family:monospace;font-size:0.84rem;'
                    f'white-space:pre-wrap;background:#FAFAFA;border-radius:8px;'
                    f'line-height:1.65;">{texto_html}</div>',
                    unsafe_allow_html=True
                )
                st.markdown("")

                # ── Botón "Marcar como revisado" ─────────────────────────────
                if doc_sel in st.session_state.revisados:
                    st.success(f"✅ **{doc_sel}** ya está marcado como revisado.")
                else:
                    if st.button(
                        "✅ Marcar como revisado",
                        key="btn_marcar_revisado",
                        type="primary"
                    ):
                        st.session_state.revisados.add(doc_sel)
                        st.rerun()

            # ── Exportar CSV (incluye columna "Revisado manualmente") ────────
            st.markdown("")
            csv_bytes = exportar_csv(res_nombres, sub, res_terminos)
            st.download_button(
                "⬇️ Exportar documentos (CSV)",
                data=csv_bytes,
                file_name=f"{res_set_name}_documentos.csv",
                mime="text/csv",
                use_container_width=True
            )

# ── TAB 2: ESTADÍSTICAS — sin cambios ───────────────────────────────────────
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

# ── TAB 5: DETECCIÓN IA ──────────────────────────────────────────────────────
with tab5:
    st.subheader("🤖 Detección asistida por IA")
    st.caption(
        "Detecta automáticamente sentencias donde el juez **omite transcribir** "
        "los conceptos de violación o agravios. Claude analiza cada documento "
        "fragmento por fragmento y se detiene en cuanto encuentra el patrón."
    )

    if not st.session_state.corpus:
        st.warning("⬅️ Primero carga los TXT desde el panel izquierdo.")
    elif not api_key:
        st.warning("⬅️ Ingresa tu API Key en el panel izquierdo.")
    else:
        col_ia1, col_ia2 = st.columns([2, 1])
        with col_ia1:
            palabras_prefilter = st.text_area(
                "Palabras clave para pre-filtrar (opcional):",
                placeholder=(
                    "innecesario transcribir\n"
                    "conceptos de violación\n"
                    "agravios\n"
                    "omite transcripción"
                ),
                height=120,
                key="ia_palabras_clave",
                help=(
                    "Solo los documentos que contengan al menos una de estas palabras "
                    "se enviarán a Claude. Reduce costos de API sin perder precisión."
                )
            )
        with col_ia2:
            st.markdown("**ℹ️ Cómo funciona**")
            st.markdown(
                "1. Pre-filtra por palabras clave (gratis)\n"
                "2. Divide cada doc en fragmentos de ~1 200 chars\n"
                "3. Envía fragmento por fragmento a Claude\n"
                "4. Para en cuanto detecta el patrón\n"
                "5. Cachea resultados para no reprocesar"
            )

        col_run1, col_run2 = st.columns(2)
        with col_run1:
            btn_analizar = st.button(
                "🔍 Analizar corpus", type="primary", use_container_width=True,
                key="btn_ia_analizar"
            )
        with col_run2:
            btn_limpiar_cache = st.button(
                "🗑️ Limpiar caché IA", use_container_width=True,
                key="btn_ia_limpiar_cache"
            )

        if btn_limpiar_cache:
            st.session_state.ia_cache = {}
            st.session_state.ia_resultados = []
            st.session_state.ia_revisados = set()
            st.success("Caché limpiada.")
            st.rerun()

        if btn_analizar:
            kw_lista = [
                kw.strip() for kw in palabras_prefilter.splitlines() if kw.strip()
            ]
            docs_candidatos = filtrar_documentos(st.session_state.corpus, kw_lista)

            if not docs_candidatos:
                st.warning("El pre-filtro no encontró documentos candidatos. "
                           "Deja el campo en blanco para analizar todo el corpus.")
            else:
                st.info(
                    f"Pre-filtro: **{len(docs_candidatos)}** documentos candidatos "
                    f"de {len(st.session_state.corpus)} totales."
                )
                progreso = st.progress(0, text="Iniciando análisis...")
                resultados_ia = []
                total = len(docs_candidatos)

                for i, nombre in enumerate(docs_candidatos):
                    progreso.progress(
                        (i + 1) / total,
                        text=f"Analizando {i+1}/{total}: {nombre[:50]}"
                    )
                    texto = st.session_state.corpus[nombre]
                    res = procesar_documento(
                        nombre, texto, api_key, st.session_state.ia_cache
                    )
                    if res["match"]:
                        resultados_ia.append({
                            "documento": nombre,
                            "fragmento": res["fragmento"],
                            "revisado" : nombre in st.session_state.ia_revisados
                        })

                progreso.empty()
                st.session_state.ia_resultados = resultados_ia
                st.success(
                    f"✅ Análisis completo. "
                    f"**{len(resultados_ia)}** documento(s) con el patrón detectado."
                )

        # ── Visor de resultados IA ─────────────────────────────────────────────
        if st.session_state.ia_resultados:
            st.markdown("---")
            st.markdown(
                f"### {len(st.session_state.ia_resultados)} documento(s) detectados"
            )

            for idx, item in enumerate(st.session_state.ia_resultados):
                nombre_doc = item["documento"]
                fragmento  = item["fragmento"]
                revisado   = nombre_doc in st.session_state.ia_revisados

                with st.expander(
                    f"{'✅' if revisado else '🔴'} {nombre_doc}",
                    expanded=not revisado
                ):
                    if fragmento:
                        st.markdown("**Fragmento detectado:**")
                        st.markdown(
                            f'<div style="background:#1E2D40;border-left:4px solid #C8622A;'
                            f'padding:12px 16px;border-radius:6px;font-family:monospace;'
                            f'font-size:0.85rem;color:#F0EBE3;white-space:pre-wrap;">'
                            f'{html.escape(fragmento)}</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.caption("_(Claude detectó el patrón pero no extrajo fragmento)_")

                    st.markdown("")
                    if revisado:
                        st.success("✅ Marcado como revisado")
                    else:
                        if st.button(
                            "✅ Marcar como revisado",
                            key=f"ia_marcar_{idx}",
                            type="primary"
                        ):
                            st.session_state.ia_revisados.add(nombre_doc)
                            st.rerun()

            # ── Exportar CSV de detección IA ──────────────────────────────────
            st.markdown("---")
            filas_ia = []
            for item in st.session_state.ia_resultados:
                filas_ia.append({
                    "documento"                 : item["documento"],
                    "fragmento_detectado"       : item["fragmento"],
                    "match_ia"                  : True,
                    "revisado_manualmente"      : "Sí" if item["documento"] in st.session_state.ia_revisados else "No",
                    "validacion_investigador"   : "",
                    "observaciones"             : "",
                })
            df_ia = pd.DataFrame(filas_ia)
            csv_ia = df_ia.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button(
                "⬇️ Exportar resultados IA (CSV)",
                data=csv_ia,
                file_name="deteccion_ia_omision_conceptos.csv",
                mime="text/csv",
                use_container_width=True
            )
