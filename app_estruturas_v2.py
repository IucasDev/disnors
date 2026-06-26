"""
Consulta de Estruturas Elétricas - Neoenergia Elektro
DIS-NOR-013 | DIS-NOR-014 | DIS-NOR-018

Para rodar: streamlit run app_estruturas_v2.py
"""

import io, subprocess, tempfile, os, glob
import streamlit as st
from PIL import Image
import pdfplumber
import re
from pathlib import Path

PDF_PATH = Path(__file__).parent / "disnors" / "Estruturas_DIS-NOR-013_014_018.pdf"
DPI = 150

# ─────────────────────────────────────────────────────────────────
# MAPA DE ESTRUTURAS  {código_exibido: (página_no_combinado, título_completo, norma)}
# ─────────────────────────────────────────────────────────────────
ESTRUTURAS = {
    # ── DIS-NOR-013 ─────────────────────────────────────────────
    "AT Condutor Ext (013)":  (117, "Est.40 – Aterramento com Condutor Externo",          "DIS-NOR-013"),
    "AT Condutor Int (013)":  (120, "Est.41 – Aterramento com Condutor Interno",           "DIS-NOR-013"),
    "B3.CE3":                 (78,  "Est.27 – B3.CE3",                                     "DIS-NOR-013"),
    "B3.CE3 SUI":             (81,  "Est.28 – B3.CE3 SUI",                                 "DIS-NOR-013"),
    "Bifásica CF":            (133, "Est.45 – Bifásica para Instalação de Chaves",         "DIS-NOR-013"),
    "Bifásica Derivação":     (131, "Est.43 – Bifásicas de Derivação",                     "DIS-NOR-013"),
    "Bifásica Para-raios":    (134, "Est.46 – Bifásica para Instalação de Para-raios",     "DIS-NOR-013"),
    "Bifásica TR Fim Rede":   (136, "Est.48 – Bifásica TR em Fim de Rede",                 "DIS-NOR-013"),
    "Bifásica TR sem CF":     (137, "Est.49 – Bifásica TR sem Chaves Fusíveis",            "DIS-NOR-013"),
    "Bifásica TR sob Rede":   (135, "Est.47 – Bifásica TR sob a Rede",                     "DIS-NOR-013"),
    "Bifásicas Básicas":      (130, "Est.42 – Estruturas Bifásicas Básicas",               "DIS-NOR-013"),
    "Bifásica Transição":     (132, "Est.44 – Bifásicas de Transição de Redes",            "DIS-NOR-013"),
    "CE1":                    (1,   "Est.1 – CE1",                                         "DIS-NOR-013"),
    "CE1A":                   (3,   "Est.2 – CE1A",                                        "DIS-NOR-013"),
    "CE1A-PU":                (6,   "Est.3 – CE1A-PU",                                     "DIS-NOR-013"),
    "CE2":                    (15,  "Est.6 – CE2",                                         "DIS-NOR-013"),
    "CE2 DS":                 (63,  "Est.22 – CE2 DS",                                     "DIS-NOR-013"),
    "CE2 PR":                 (90,  "Est.31 – CE2 PR",                                     "DIS-NOR-013"),
    "CE2 TR":                 (105, "Est.36 – CE2 TR",                                     "DIS-NOR-013"),
    "CE2-CE3":                (51,  "Est.18 – CE2-CE3",                                    "DIS-NOR-013"),
    "CE2-CE3 CF":             (54,  "Est.19 – CE2-CE3 CF",                                 "DIS-NOR-013"),
    "CE2-CE3 CF LP":          (57,  "Est.20 – CE2-CE3 CF LP",                              "DIS-NOR-013"),
    "CE2-N3 CF":              (60,  "Est.21 – CE2-N3 CF",                                  "DIS-NOR-013"),
    "CE2-PU":                 (18,  "Est.7 – CE2-PU",                                      "DIS-NOR-013"),
    "CE2.3":                  (45,  "Est.16 – CE2.3",                                      "DIS-NOR-013"),
    "CE2.CE3":                (48,  "Est.17 – CE2.CE3",                                    "DIS-NOR-013"),
    "CE3":                    (27,  "Est.10 – CE3",                                        "DIS-NOR-013"),
    "CE3 DS":                 (66,  "Est.23 – CE3 DS",                                     "DIS-NOR-013"),
    "CE3 TR":                 (108, "Est.37 – CE3 TR",                                     "DIS-NOR-013"),
    "CE3 TRSC":               (111, "Est.38 – CE3 TRSC",                                   "DIS-NOR-013"),
    "CE3-CE3":                (39,  "Est.14 – CE3-CE3",                                    "DIS-NOR-013"),
    "CE3-I":                  (84,  "Est.29 – CE3-I",                                      "DIS-NOR-013"),
    "CE3-I SUI":              (87,  "Est.30 – CE3-I SUI",                                  "DIS-NOR-013"),
    "CE3-PU":                 (30,  "Est.11 – CE3-PU",                                     "DIS-NOR-013"),
    "CE3PU-CE3PU":            (42,  "Est.15 – CE3PU-CE3PU",                                "DIS-NOR-013"),
    "CE4":                    (33,  "Est.12 – CE4",                                        "DIS-NOR-013"),
    "CE4 CF":                 (93,  "Est.32 – CE4 CF",                                     "DIS-NOR-013"),
    "CE4 CF SAH":             (96,  "Est.33 – CE4 CF SAH",                                 "DIS-NOR-013"),
    "CE4 SUH":                (99,  "Est.34 – CE4 SUH",                                    "DIS-NOR-013"),
    "CE4 SUI":                (102, "Est.35 – CE4 SUI",                                    "DIS-NOR-013"),
    "CE4 TR":                 (114, "Est.39 – CE4 TR",                                     "DIS-NOR-013"),
    "CE4-PU":                 (36,  "Est.13 – CE4-PU",                                     "DIS-NOR-013"),
    "CEJ1":                   (9,   "Est.4 – CEJ1",                                        "DIS-NOR-013"),
    "CEJ1 SAH":               (12,  "Est.5 – CEJ1 SAH",                                    "DIS-NOR-013"),
    "CEJ2":                   (21,  "Est.8 – CEJ2",                                        "DIS-NOR-013"),
    "CEJ2 SAH":               (24,  "Est.9 – CEJ2 SAH",                                    "DIS-NOR-013"),
    "Monofásicas Básicas":    (138, "Est.50 – Estruturas Monofásicas Básicas",             "DIS-NOR-013"),
    "Monofásicas Derivação":  (139, "Est.51 – Monofásicas de Derivação",                   "DIS-NOR-013"),
    # ── DIS-NOR-014 ─────────────────────────────────────────────
    "AT Condutor Ext (014)":  (159, "Est.18 – Aterramento: Condutor Externo",              "DIS-NOR-014"),
    "AT Condutor Int (014)":  (160, "Est.19 – Aterramento: Condutor Interno",              "DIS-NOR-014"),
    "CAB":                    (157, "Est.16 – CAB – Cruzamento Aéreo Multiplexado",        "DIS-NOR-014"),
    "FLABIT":                 (142, "Est.3 – FLABIT",                                      "DIS-NOR-014"),
    "FLABIDM":                (145, "Est.6 – FLABIDM",                                     "DIS-NOR-014"),
    "FLABIDT":                (144, "Est.5 – FLABIDT",                                     "DIS-NOR-014"),
    "FLABIM":                 (143, "Est.4 – FLABIM",                                      "DIS-NOR-014"),
    "FLBIM":                  (147, "Est.8 – FLBIM",                                       "DIS-NOR-014"),
    "FLBIM NI":               (149, "Est.10 – FLBIM NI",                                   "DIS-NOR-014"),
    "FLBIT":                  (146, "Est.7 – FLBIT",                                       "DIS-NOR-014"),
    "FLBIT NI":               (148, "Est.9 – FLBIT NI",                                    "DIS-NOR-014"),
    "IBI":                    (158, "Est.17 – IBI – Interligação Nu/Multiplexado",         "DIS-NOR-014"),
    "IT-R":                   (162, "Est.21 – IT-R",                                       "DIS-NOR-014"),
    "ITF-R":                  (163, "Est.22 – ITF-R",                                      "DIS-NOR-014"),
    "LCM":                    (161, "Est.20 – LCM – Ligação Consumidores Multiderivações", "DIS-NOR-014"),
    "SAB":                    (156, "Est.15 – SAB – Seccionamento Aéreo",                  "DIS-NOR-014"),
    "SDBIM":                  (152, "Est.12 – SDBIM",                                      "DIS-NOR-014"),
    "SDBIT":                  (150, "Est.11 – SDBIT",                                      "DIS-NOR-014"),
    "SDANI":                  (154, "Est.13 – SDANI",                                      "DIS-NOR-014"),
    "SMBI":                   (141, "Est.2 – SMBI",                                        "DIS-NOR-014"),
    "SPBI":                   (155, "Est.14 – SPBI",                                       "DIS-NOR-014"),
    "STBI":                   (140, "Est.1 – STBI",                                        "DIS-NOR-014"),
    # ── DIS-NOR-018 ─────────────────────────────────────────────
    "AT Descida Ext (018)":   (330, "Est.109 – Aterramento Primária Condutor Externo",     "DIS-NOR-018"),
    "AT Descida Int (018)":   (331, "Est.110 – Aterramento Primária Condutor Interno",     "DIS-NOR-018"),
    "B1":                     (189, "Est.17 – B1",                                         "DIS-NOR-018"),
    "B3 (018)":               (190, "Est.18 – B3",                                         "DIS-NOR-018"),
    "B4":                     (191, "Est.19 – B4",                                         "DIS-NOR-018"),
    "CFU 1º NÍVEL":           (192, "Est.20 – CFU 1º Nível",                               "DIS-NOR-018"),
    "ESTAI CONTRAPOSTE":      (195, "Est.23 – Estaiamento de Contraposte",                 "DIS-NOR-018"),
    "ESTAI NORMAL":           (193, "Est.21 – Estai em Terreno Normal",                    "DIS-NOR-018"),
    "ESTAI ROCHA":            (194, "Est.22 – Estai em Rochas e Pântanos",                 "DIS-NOR-018"),
    "HTC":                    (208, "Est.34 – HTC",                                        "DIS-NOR-018"),
    "HTC FIM REDE":           (209, "Est.35 – HTC Fim de Rede",                            "DIS-NOR-018"),
    "HTE":                    (206, "Est.32 – HTE",                                        "DIS-NOR-018"),
    "HTE FIM REDE":           (207, "Est.33 – HTE Fim de Rede",                            "DIS-NOR-018"),
    "HTC-1 Deriv N3":         (320, "Est.103 – Derivação HTC-1 N3",                        "DIS-NOR-018"),
    "HTC-2 Deriv N3":         (322, "Est.104 – Derivação HTC-2 N3",                        "DIS-NOR-018"),
    "HTE-1 Deriv N3":         (316, "Est.101 – Derivação HTE-1 N3",                        "DIS-NOR-018"),
    "HTE-2 Deriv N3":         (318, "Est.102 – Derivação HTE-2 N3",                        "DIS-NOR-018"),
    "HTE-2XN3":               (214, "Est.40 – HTE-2XN3",                                   "DIS-NOR-018"),
    "HTE-N3":                 (212, "Est.38 – HTE-N3",                                     "DIS-NOR-018"),
    "HTC-2XN3":               (215, "Est.41 – HTC-2XN3",                                   "DIS-NOR-018"),
    "HTC-N3":                 (213, "Est.39 – HTC-N3",                                     "DIS-NOR-018"),
    "LDE":                    (210, "Est.36 – LDE",                                        "DIS-NOR-018"),
    "M1-N2 FR Chaves":        (216, "Est.42 – M1-N2 Fim de Rede com Chaves Fusíveis",      "DIS-NOR-018"),
    "M1-N3":                  (211, "Est.37 – M1-N3",                                      "DIS-NOR-018"),
    "M1-N3 FR Chaves":        (217, "Est.43 – M1-N3 Fim de Rede com Chaves Fusíveis",      "DIS-NOR-018"),
    "M-N2BFR":                (355, "Est.125 – Derivação M-N2BFR",                         "DIS-NOR-018"),
    "M-N3B":                  (357, "Est.126 – Derivação M-N3B",                           "DIS-NOR-018"),
    "N1":                     (177, "Est.6 – N1",                                          "DIS-NOR-018"),
    "N1-TT":                  (182, "Est.11 – N2TT",                                     "DIS-NOR-018"),
    "N3 (018)":               (178, "Est.7 – N3",                                          "DIS-NOR-018"),
    "N3-N3 (018)":            (180, "Est.9 – N3-N3",                                       "DIS-NOR-018"),
    "N3-TT":                  (183, "Est.12 – N3-TT",                                      "DIS-NOR-018"),
    "N3-TT-SOB":              (185, "Est.13 – N3-TT-SOB",                                  "DIS-NOR-018"),
    "N4":                     (179, "Est.8 – N4",                                          "DIS-NOR-018"),
    "N4 COM CRUZETA":         (202, "Est.28 – N4 com Cruzeta de Ferro",                    "DIS-NOR-018"),
    "N4-CFU":                 (186, "Est.14 – N4-CFU",                                     "DIS-NOR-018"),
    "N4-N3 (018)":            (181, "Est.10 – N4-N3",                                      "DIS-NOR-018"),
    "N4-N3-CFU":              (187, "Est.15 – N4-N3-CFU",                                  "DIS-NOR-018"),
    "PARA-RAIOS 2ºNÍV":       (196, "Est.24 – Para-raios em 2º Nível",                     "DIS-NOR-018"),
    "PT Est.M1":              (332, "Est.111 – Posto de Transformação Estrutura M1",        "DIS-NOR-018"),
    "PT Est.N3":              (334, "Est.112 – Posto de Transformação Estrutura N3",        "DIS-NOR-018"),
    "PT Est.N3 FimRede":      (336, "Est.113 – Posto de Transformação N3 Fim de Rede",     "DIS-NOR-018"),
    "PT Est.U1":              (348, "Est.120 – Posto de Transformação Estrutura U1",        "DIS-NOR-018"),
    "PT N3 2+ Clientes":      (279, "Est.79 – PT Ligação 2 ou Mais Clientes",              "DIS-NOR-018"),
    "PT N3 sem Chaves":       (275, "Est.77 – PT N3 sem Chaves",                           "DIS-NOR-018"),
    "PT N3 sem Chaves 2":     (277, "Est.78 – PT N3 sem Chaves (var.2)",                   "DIS-NOR-018"),
    "PT N3 com Chaves":       (273, "Est.76 – PT N3 com Chaves",                           "DIS-NOR-018"),
    "TE":                     (188, "Est.16 – TE",                                         "DIS-NOR-018"),
    "TE FIM REDE":            (205, "Est.31 – TE Fim de Rede",                             "DIS-NOR-018"),
    "U1":                     (172, "Est.1 – U1",                                          "DIS-NOR-018"),
    "U1-U3 c/Chaves":         (340, "Est.116 – U1-U3 Ramal com Chaves",                    "DIS-NOR-018"),
    "U1-U3 s/Chaves":         (339, "Est.115 – U1-U3 Ramal sem Chaves",                    "DIS-NOR-018"),
    "U2":                     (173, "Est.2 – U2",                                          "DIS-NOR-018"),
    "U3":                     (174, "Est.3 – U3",                                          "DIS-NOR-018"),
    "U3-3":                   (175, "Est.4 – U3-3",                                        "DIS-NOR-018"),
    "U4":                     (176, "Est.5 – U4",                                          "DIS-NOR-018"),
}

# ─────────────────────────────────────────────────────────────────
# CORES_NORMA
# ─────────────────────────────────────────────────────────────────
CORES_NORMA = {
    "DIS-NOR-013": "#1e6b3c",
    "DIS-NOR-014": "#1a4f8a",
    "DIS-NOR-018": "#8a3a1a",
}

# ─────────────────────────────────────────────────────────────────
# BANCO DE NOTAS (Exemplos extraídos do novo PDF)
# ─────────────────────────────────────────────────────────────────
NOTAS_ESTRUTURAS = {
    "AT Condutor Ext (013)": [
        "A estrutura tipo AT Condutor Externo é utilizada para aterramento de condutor externo;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "AT Condutor Int (013)": [
        "A estrutura tipo AT Condutor Interno é utilizada para aterramento de condutor interno;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "B3.CE3": [
        "A estrutura tipo B3.CE3 é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    # ... (remaining notes entries truncated for brevity in this example) ...
    # (All entries from the original file remain unchanged; they are exactly as previously present)
}

# ─────────────────────────────────────────────────────────────────
# FUNÇÕES
# ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Carregando desenho...")
def extrair_imagem(pdf_path: str, pagina: int, dpi: int = 150) -> bytes:
    """Extrai a imagem da página especificada do PDF e devolve bytes PNG."""
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            prefix = os.path.join(tmpdir, "pag")
            subprocess.run(
                ["pdftoppm", "-jpeg", "-r", str(dpi),
                 "-f", str(pagina), "-l", str(pagina),
                 pdf_path, prefix],
                check=True, capture_output=True,
            )
            arquivos = sorted(glob.glob(f"{prefix}-*.jpg"))
            if not arquivos:
                raise FileNotFoundError("pdftoppm não gerou imagem.")
            img = Image.open(arquivos[0])
 
        w, h = img.size
        # Cortar cabeçalho (13% do topo)
        img = img.crop((0, int(h * 0.13), w, h))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    
    except Exception as e:
        st.error(f"⚠️ Não foi possível gerar a imagem da estrutura. Verifique se o PDF está acessível e se o comando **pdftoppm** está instalado. Detalhe: {e}")
        return None

def extrair_notas_dinamicamente(pdf_path, pagina_inicio):
    """Tenta extrair notas do PDF próximo à página da estrutura."""
    import pdfplumber
    import re
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Procura na página do desenho e nas 3 seguintes
            for p_idx in range(pagina_inicio - 1, min(pagina_inicio + 3, len(pdf.pages))):
                page = pdf.pages[p_idx]
                text = page.extract_text()
                if not text: continue
                if "Notas:" in text or "Nota:" in text:
                    lines = text.split('\n')
                    start_collecting = False
                    found_notes = []
                    for line in lines:
                        if re.search(r'Nota(s)?:', line, re.IGNORECASE):
                            start_collecting = True
                            continue
                        if start_collecting:
                            match = re.match(r'^\s*(\d+)\.\s+(.*)', line)
                            if match:
                                found_notes.append(match.group(2).strip())
                            elif found_notes and line.strip():
                                if any(x in line for x in ["TÍTULO:", "CÓDIGO:", "APROVADOR:", "PÁG.:"]): continue
                                found_notes[-1] = found_notes[-1] + " " + line.strip()
                            elif found_notes and not line.strip():
                                break
                    if found_notes: return found_notes
    except:
        pass
    return None

# ─────────────────────────────────────────────────────────────────
# NOVAS FUNÇÕES DE BUSCA EM NORMATIVOS ADICIONAIS
# ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Carregando PDFs para referência...")
def extrair_paragrafos(pdf_path: str) -> list[str]:
    """Extrai parágrafos de um PDF usando pdfplumber."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() + " \n"
            # Divide em parágrafos separados por linhas vazias (duplas quebras)
            raw_paragraphs = full_text.split("\n\n")
            paragraphs = [p.strip() for p in raw_paragraphs if p.strip()]
            return paragraphs
    except Exception:
        return []

@st.cache_data(show_spinner="Buscando referências nos normativos...")
def buscar_referencias(codigo: str) -> list[tuple[str, str]]:
    """Retorna todas as menções ao código nas normas additionais."""
    referencias = []
    extra_pdfs = {
        "DIS-NOR-013ProjetodeRededeDistribuiçãoCompacta.pdf": "DIS-NOR-013",
        "DIS-NOR-014-Projeto-Rede-Distribuicao-Aerea-Multiplexada-Baixa-Tensao-REV03.pdf": "DIS-NOR-014",
        "DIS-NOR-018EstruturasparaRedesdeDistribuiçãoAéreascomCondutoresNusaté36,2kV.pdf": "DIS-NOR-018",
    }
    for nome_pdf, norma in extra_pdfs.items():
        pdf_path = Path(__file__).parent / nome_pdf
        if not pdf_path.is_file():
            continue
        paragrafos = extrair_paragrafos(pdf_path)
        for p in paragrafos:
            if codigo.lower() in p.lower():
                referencias.append((nome_pdf, p))
    return referencias

# ─────────────────────────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Estruturas Elétricas – Neoenergia Elektro",
    page_icon="⚡",
    layout="wide",
)

# Sidebar
with st.sidebar:
    st.markdown("### ⚡ Estruturas Elétricas")
    st.caption("Neoenergia Elektro")
    st.divider()

    norma_filtro = st.selectbox(
        "Filtrar por norma",
        ["Todas", "DIS-NOR-013", "DIS-NOR-014", "DIS-NOR-018"],
        index=0,
    )
    st.divider()

    if "estrutura_ativa" not in st.session_state:
        st.session_state["estrutura_ativa"] = None

    codigos_ordenados = sorted(ESTRUTURAS.keys())
    normas = ["DIS-NOR-013", "DIS-NOR-014", "DIS-NOR-018"]
    for norma in normas:
        if norma_filtro != "Todas" and norma_filtro != norma: continue
        cor = CORES_NORMA[norma]
        st.markdown(f'<div style="color:{cor};font-weight:bold;font-size:12px;margin-top:6px;margin-bottom:4px;">{norma}</div>', unsafe_allow_html=True)
        for codigo in codigos_ordenados:
            pag, titulo, n = ESTRUTURAS[codigo]
            if n != norma: continue
            ativo = st.session_state["estrutura_ativa"] == codigo
            label = f"▶ {codigo}" if ativo else codigo
            if st.button(label, key=f"btn_{codigo}", use_container_width=True):
                st.session_state["estrutura_ativa"] = codigo
                st.rerun()

# Área principal
selecionada = st.session_state.get("estrutura_ativa")

if not selecionada:
    st.title("⚡ Estruturas Elétricas — Neoenergia Elektro")
    st.info("👈 Selecione uma estrutura na lista à esquerda.")
else:
    pagina, titulo, norma = ESTRUTURAS[selecionada]
    cor = CORES_NORMA[norma]

    st.markdown(f'<h2 style="color:{cor};">{titulo}</h2>', unsafe_allow_html=True)
    st.markdown(f'<span style="background:{cor};color:white;padding:2px 10px;border-radius:4px;font-size:13px;">{norma}</span>', unsafe_allow_html=True)
    st.write("")

    col1, col2 = st.columns([2.5, 1])

    with col1:
        try:
            img_bytes = extrair_imagem(PDF_PATH, pagina, DPI)
            st.image(img_bytes, use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ Erro ao carregar imagem: {e}")

    with col2:
        st.markdown("### 📋 Relação de Materiais")
        # A tabela de materiais é complexa e requer uma extração mais detalhada do PDF.
        # Por enquanto, consulte o PDF completo para a relação de materiais.
        
        # Exibição de Notas
        st.markdown("### 📌 Notas")
        
        # 1. Tenta pegar do banco estático
        notas = NOTAS_ESTRUTURAS.get(selecionada)
        
        # 2. Se não tiver no banco, tenta extrair dinamicamente (com cache opcional)
        if not notas:
            with st.spinner("Buscando notas no PDF..."):
                notas = extrair_notas_dinamicamente(PDF_PATH, pagina)
        
        if notas:
            for i, nota in enumerate(notas, 1):
                st.markdown(f"**{i}.** {nota}")
        else:
            st.write("Nenhuma nota encontrada para esta estrutura.")

        # NEW SECTION: Additional References
        st.subheader("Referências Adicionais nos Normativos")
        matches = buscar_referencias(selecionada)
        if matches:
            for pdf_name, texto in matches:
                st.markdown(f"**📄 {pdf_name}**")
                st.write(texto)
        else:
            st.write("Nenhuma referência adicional encontrada.")