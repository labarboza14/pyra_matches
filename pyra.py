import pandas as pd
import unicodedata
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ======================
# CONFIGURAÇÕES
# ======================
ARQUIVO_ENTRADA = "forms.xlsx"
ARQUIVO_SAIDA = "correspondencias_mentoria.xlsx"
LIMIAR_FUZZY = 70       # similaridade de texto
LIMIAR_SEMANTICA = 0.75 # similaridade de significado

# ======================
# MAPEAMENTO DE SINÔNIMOS
# ======================
SINONIMOS = {
    "python": ["python programming", "linguagem python", "py"],
    "rust": ["linguagem rust", "programação em rust"],
    "c": ["linguagem c", "programação em c"],
    "pascal": ["linguagem pascal"],
    "golang": ["go", "golang", "linguagem go"],

    # Dados
    "ciência de dados": ["data science", "analise de dados", "análise de dados", "ds"],
    "engenharia de dados": ["data engineering", "engenheiro de dados"],
    "arquitetura de dados": ["data architecture"],
    "carreira em dados": ["trajetória em dados", "profissão em dados", "data career"],
    "machine learning": ["aprendizado de maquina", "aprendizado de máquina", "ml"],
    "inteligência artificial": ["ia", "artificial intelligence", "ai"],
    "treinamento de ia": ["treinamento de modelos", "ia training"],
    "automação": ["automação de processos", "process automation", "rpa"],

    # Banco de dados
    "banco de dados": ["sql", "database", "db", "sistema de banco de dados"],
    "postgresql": ["postgres", "pgsql"],
    "duckdb": ["duck database"],

    # Infra e Cloud
    "cloud": ["nuvem", "cloud computing", "aws", "azure", "gcp", "google cloud", "amazon web services", "microsoft azure"],
    "kubernetes": ["k8s"],
    "docker": ["containers", "docker compose"],
    "terraform": ["infra as code", "iac", "hashicorp terraform"],
    "virtualização": ["vm", "virtual machines", "vmware", "proxmox", "qemu"],

    # Git/GitHub
    "git": ["controle de versão", "versionamento"],
    "github": ["plataforma github", "git hub"],
    "github actions": ["ci/cd github", "automação github"],

    # Sistemas operacionais
    "linux": ["gnu/linux", "sistema linux", "unix-like"],
    "gerenciamento de pacotes": ["package manager", "apt", "dnf", "pacman", "nixos", "gentoo"],
    "redes": ["networking", "ip", "ethernet", "wifi", "reticulum", "i2p"],

    # Desenvolvimento
    "desenvolvimento web": ["web development", "dev web", "fullstack", "frontend", "backend"],
    "devops": ["cultura devops", "engenharia devops"],
    "boas práticas": ["clean code", "práticas de desenvolvimento"],
    "produtividade": ["ferramentas de produtividade", "gestão de tempo", "rotinas de trabalho"],

    # Carreira
    "transição de carreira": ["mudança de carreira", "career change", "migração de carreira"],
    "organização profissional": ["rotinas profissionais", "gestão pessoal", "produtividade no trabalho"],
    "autonomia profissional": ["desenvolvimento profissional", "independência no trabalho"],
    "cv": ["currículo", "resume"],
    "linkedin": ["perfil profissional linkedin", "apresentação profissional"],
    "entrevistas": ["processo seletivo", "job interview"],

    # Outras áreas
    "matemática": ["cálculo", "álgebra", "estatística"],
    "hardware": ["componentes de computador", "informática"],
    "tecnologia": ["tech", "inovação tecnológica"],
    "investimentos": ["finanças", "carreira e finanças"],

    # Interesses diversos
    "meliponicultura": ["criação de abelhas sem ferrão"],
    "confeitaria": ["doces", "confeiteiro", "pâtisserie"],
}

# ======================
# FUNÇÕES AUXILIARES
# ======================
def normalizar_texto(txt):
    if not isinstance(txt, str):
        return ""
    txt = txt.lower()
    txt = unicodedata.normalize('NFKD', txt).encode('ascii', 'ignore').decode('utf-8')
    return txt.strip()

def aplicar_sinonimos(txt):
    txt_norm = normalizar_texto(txt)
    for chave, lista in SINONIMOS.items():
        if txt_norm in [normalizar_texto(x) for x in lista] or txt_norm == normalizar_texto(chave):
            return chave
    return txt

# ======================
# LEITURA DA PLANILHA
# ======================
df = pd.read_excel(ARQUIVO_ENTRADA)

# Detecta automaticamente as colunas
col_temas_oferece = next(c for c in df.columns if "oferecer" in c.lower())
col_temas_quer = next(c for c in df.columns if "aprender" in c.lower())
col_nome = next(c for c in df.columns if "nome" in c.lower())
col_tel = next(c for c in df.columns if "whatsapp" in c.lower() or "telefone" in c.lower())

# ======================
# MODELO SEMÂNTICO
# ======================
print("\n🔍 Carregando modelo de embeddings...")
modelo = SentenceTransformer("paraphrase-MiniLM-L6-v2")

# ======================
# GERA CORRESPONDÊNCIAS
# ======================
matches = []
mentores_com_match = set()
mentorados_com_match = set()

for idx_mentor, mentor in df.iterrows():
    temas_oferece = [aplicar_sinonimos(t.strip()) for t in str(mentor[col_temas_oferece]).split(",")]
    temas_oferece = [t for t in temas_oferece if t]

    for idx_mentorado, mentorado in df.iterrows():
        if idx_mentor == idx_mentorado:
            continue

        temas_quer = [aplicar_sinonimos(t.strip()) for t in str(mentorado[col_temas_quer]).split(",")]
        temas_quer = [t for t in temas_quer if t]

        for tema_of in temas_oferece:
            for tema_q in temas_quer:
                tema_of_norm = normalizar_texto(tema_of)
                tema_q_norm = normalizar_texto(tema_q)

                score_fuzzy = fuzz.token_sort_ratio(tema_of_norm, tema_q_norm)

                emb = modelo.encode([tema_of_norm, tema_q_norm])
                score_sem = cosine_similarity([emb[0]], [emb[1]])[0][0]

                if score_fuzzy >= LIMIAR_FUZZY or score_sem >= LIMIAR_SEMANTICA:
                    matches.append({
                        "Nome mentor": mentor[col_nome],
                        "Telefone mentor": mentor[col_tel],
                        "Nome mentorado": mentorado[col_nome],
                        "Telefone mentorado": mentorado[col_tel],
                        "Assunto da mentoria": tema_of
                    })
                    mentores_com_match.add(mentor[col_nome])
                    mentorados_com_match.add(mentorado[col_nome])

# ======================
# IDENTIFICAR QUEM FICOU DE FORA
# ======================
mentores_sem_match = df[~df[col_nome].isin(mentores_com_match)][[col_nome, col_tel, col_temas_oferece]]
mentorados_sem_match = df[~df[col_nome].isin(mentorados_com_match)][[col_nome, col_tel, col_temas_quer]]

# ======================
# SALVAR RESULTADOS
# ======================
with pd.ExcelWriter(ARQUIVO_SAIDA) as writer:
    pd.DataFrame(matches).to_excel(writer, sheet_name="Matches", index=False)
    mentores_sem_match.to_excel(writer, sheet_name="Mentores sem mentorados", index=False)
    mentorados_sem_match.to_excel(writer, sheet_name="Mentorados sem mentores", index=False)

print(f"\n✅ Arquivo '{ARQUIVO_SAIDA}' gerado!")
print(f"   → {len(matches)} correspondências")
print(f"   → {len(mentores_sem_match)} mentores ficaram sem mentorados")
print(f"   → {len(mentorados_sem_match)} mentorados ficaram sem mentores")
