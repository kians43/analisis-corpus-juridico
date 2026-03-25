import streamlit as st
import os
import re
import json
import requests
import pandas as pd
from pathlib import Path

CARPETA_TXT  = r"D:\sentencias individuales txt"
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_URL   = "https://api.anthropic.com/v1/messages"

st.set_page_config(page_title="Análisis de Corpus Jurídico", layout="wide")
st.title("⚖️ Análisis de Corpus Jurídico")

if "corpus" not in st.session_state:
    st.session_state.corpus = {}
if "sets" not in st.session_state:
    st.session_state.sets = {}
if "set_counter" not in st.session_state:
    st.session_state.set_counter = 1
if "historial" not in st.session_state:
    st.session_state.historial = []

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
    if st.button("📥 Cargar TXT", use_container_width=True):
        carpeta = Path(CARPETA_TXT)
        if not carpeta.exists():
            st.error(f"No se encuentra la carpeta:\n{CARPETA_TXT}")
        else:
            archivos = list(carpeta.glob("*.txt"))
            if not archivos:
                st.error("No se encontraron archivos .txt en esa carpeta.")
            else:
                corpus_temp = {}
                barra = st.progress(0, text="Cargando archivos...")
                total = len(archivos)
                for i, archivo in enumerate(archivos):
                    try:
                        texto = archivo.read_text(encoding="utf-8", errors="ignore")
                        corpus_temp[archivo.name] = texto
                    except Exception:
                        pass
                    barra.progress((i + 1) / total, text=f"Cargando {i+1}/{total}...")
                st.session_state.corpus = corpus_temp
                st.success(f"✅ {len(corpus_temp)} documentos cargados")
    if st.session_state.corpus:
        st.info(f"📄 {len(st.session_state.corpus)} documentos en memoria")
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
        })
    df = pd.DataFrame(filas)
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")


tab1, tab2, tab3, tab4 = st.tabs(
    ["🔍 Búsqueda", "📊 Estadísticas", "🔗 Referencias", "📋 Historial"]
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
                    filas_display = []
                    for nombre in resultados[:50]:
                        texto    = subcorpus.get(nombre, "")
                        extracto = obtener_extracto(texto, todos_terminos, 250)
                        filas_display.append({"Documento": nombre, "Extracto": extracto})
                    st.dataframe(pd.DataFrame(filas_display), use_container_width=True, height=400)
                    if len(resultados) > 50:
                        st.caption(f"_(Mostrando 50 de {len(resultados)}. Exporta CSV para ver todos.)_")
                    csv_bytes = exportar_csv(resultados, subcorpus, todos_terminos)
                    st.download_button(
                        "⬇️ Exportar documentos (CSV)",
                        data=csv_bytes,
                        file_name=f"{nombre_set}_documentos.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.warning(
                        "0 resultados. Abre 'Escribir términos manualmente' "
                        "e intenta con palabras más simples y cortas."
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
