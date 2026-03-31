import streamlit as st
import os
import re
import json
import requests
import pandas as pd
from pathlib import Path


CARPETA_TXT  = os.environ.get("CARPETA_TXT", r"C:\Users\kians\Desktop\sentencias individuales txt")
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
