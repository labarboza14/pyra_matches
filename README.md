# README — Matching de Mentoria (passo a passo para iniciantes)

Este guia te leva do **zero ao resultado** usando o script que cruza **mentores** e **mentorados** com base nos temas (com sinônimos, *fuzzy matching* e similaridade semântica). No final, você terá um arquivo Excel com:

1. `Matches` (pares que deram certo)
2. `Mentores sem mentorados`
3. `Mentorados sem mentores`

---

## 1) O que este script faz

* Lê uma planilha `forms.xlsx` com respostas do formulário (mentores e mentorados juntos).
* Detecta automaticamente as colunas de **nome**, **telefone/WhatsApp**, **o que a pessoa pode oferecer** e **o que a pessoa quer aprender**.
* Normaliza textos (acentos/maiúsculas/minúsculas).
* Usa:

  * **Sinônimos** (ex.: “IA” = “inteligência artificial”)
  * **Fuzzy matching** (parecido com “correção de digitação inteligente”)
  * **Similaridade semântica** (entende quando duas frases têm o mesmo significado)
* Gera um arquivo `correspondencias_mentoria.xlsx` com 3 abas: *Matches*, *Mentores sem mentorados* e *Mentorados sem mentores*.

---

## 2) O que você precisa antes (pré‑requisitos)

* **Windows** (passos abaixo também indicam como fazer em macOS/Linux).
* **Python 3.9+** instalado.
* **Internet** na primeira execução (o modelo semântico é baixado automaticamente).

> Não tem Python?
> Baixe em: [https://www.python.org/downloads/](https://www.python.org/downloads/)
> Na instalação do Windows, marque a opção **“Add Python to PATH”**.

---

## 3) Baixar os arquivos do projeto

Crie uma pasta do projeto e coloque dentro:

* `script.py` (o código que você já tem)
* `forms.xlsx` (sua planilha de entrada)

Estrutura sugerida:

```
mentoria/
├─ script.py
└─ forms.xlsx
```

> Dica: deixe o nome exatamente `forms.xlsx` (ou ajuste a constante `ARQUIVO_ENTRADA` no código).

---

## 4) Criar um ambiente virtual (recomendado)

### Windows (PowerShell ou CMD)

```bash
cd mentoria
python -m venv .venv
.venv\Scripts\activate
```

### macOS/Linux (Terminal)

```bash
cd mentoria
python3 -m venv .venv
source .venv/bin/activate
```

Quando o ambiente estiver ativo, você verá `(.venv)` no começo da linha do terminal.

---

## 5) Instalar as dependências

No terminal **com o venv ativo**:

```bash
pip install -U pip
pip install pandas openpyxl rapidfuzz sentence-transformers scikit-learn torch
```

> Se o `torch` tiver dificuldade de instalar no seu PC, tente:
>
> ```bash
> pip install torch --index-url https://download.pytorch.org/whl/cpu
> ```
>
> (CPU puro, funciona bem para este caso)

---

## 6) Preparar sua planilha `forms.xlsx`

A planilha deve ter **pelo menos** estas informações (os nomes das colunas não precisam ser idênticos, o script acha por palavras‑chave):

* **Nome** → o script procura por “nome”
* **Telefone/WhatsApp** → procura por “whatsapp” ou “telefone”
* **O que pode oferecer** → procura por “oferecer”
* **O que quer aprender** → procura por “aprender”

**Exemplo (pode ser em qualquer ordem):**

| Nome | WhatsApp     | O que posso oferecer (temas) | O que quero aprender (temas) |
| ---- | ------------ | ---------------------------- | ---------------------------- |
| Ana  | 4899999-0000 | Python, Git, Docker          | Cloud, Kubernetes            |
| João | 4891111-2222 | Cloud (AWS), IaC (Terraform) | Python, Data Science         |
| Bia  | 4893333-4444 | Data Science, ML             | Rust                         |

**Regras simples para os temas:**

* Separe **vários temas por vírgula** (`,`) na mesma célula.
* Pode usar acentos ou não; maiúsculas/minúsculas tanto faz.
* Sinônimos comuns já estão mapeados (ex.: “IA” \~ “inteligência artificial”).

---

## 7) Como rodar

Com o venv ativo e dentro da pasta do projeto:

```bash
python script.py
```

O script vai:

* Mostrar as colunas detectadas.
* Baixar o modelo de linguagem na primeira vez (pode demorar um pouco).
* Gerar o arquivo `correspondencias_mentoria.xlsx` na mesma pasta.

---

## 8) Entendendo o resultado

Arquivo: **`correspondencias_mentoria.xlsx`**

### Aba 1 — `Matches`

Pares encontrados. Colunas:

* `Nome mentor`, `Telefone mentor`
* `Nome mentorado`, `Telefone mentorado`
* `Assunto da mentoria` (o tema que bateu)

> Observação: Uma pessoa pode aparecer em **vários** matches se tiver vários temas compatíveis.

### Aba 2 — `Mentores sem mentorados`

Lista de pessoas que **oferecem** temas que **ninguém quer** (segundo a avaliação do script).

### Aba 3 — `Mentorados sem mentores`

Lista de pessoas que **querem aprender** temas que **ninguém oferece**.

---

## 9) Ajustes úteis (sem mexer no “miolo”)

Abra o `script.py` e, no topo, ajuste:

```python
ARQUIVO_ENTRADA = "forms.xlsx"                    # seu Excel de entrada
ARQUIVO_SAIDA = "correspondencias_mentoria.xlsx"  # nome do Excel de saída

LIMIAR_FUZZY = 70             # 0–100 (quanto maior, mais “exigente” o texto)
LIMIAR_SEMANTICA = 0.75       # 0–1 (quanto maior, mais “exigente” o significado)
```

**Recomendações:**

* Se estiver dando **match de menos**, reduza um pouco (ex.: `LIMIAR_FUZZY = 65` ou `LIMIAR_SEMANTICA = 0.70`).
* Se estiver dando **match demais** (muito “genérico”), aumente um pouco.

---

## 10) Personalizar/expandir os sinônimos

No `script.py`, procure por:

```python
SINONIMOS = { ... }
```

* A **chave** é o termo “oficial” (padrão).
* A **lista** são as variações aceitas como sinônimo.

**Exemplo para adicionar “carreira de dados” e variações:**

```python
"carreira de dados": ["trajetória em dados", "profissão em dados", "data career"]
```

**Exemplo para incluir “DevSecOps”:**

```python
"devsecops": ["segurança devops", "security devops", "appsec devops"]
```

> Dica: deixe as chaves **sem acento** e em minúsculas; o script normaliza tudo internamente.

---

## 11) Dicas para qualidade dos dados

* Use **vírgula** para separar múltiplos temas na mesma célula.
* Evite colar **parágrafos longos** com muitas ideias misturadas; prefira **listas curtas** de temas.
* Se muitas pessoas usam **nomes iguais**, considere usar o **telefone** como identificador quando for conferir manualmente.

---

## 12) Problemas comuns (FAQ)

**1) “ModuleNotFoundError: No module named ‘…’”**
→ Você esqueceu de instalar as dependências **no venv ativo**. Rode:

```bash
pip install pandas openpyxl rapidfuzz sentence-transformers scikit-learn torch
```

**2) “SINONIMOS is not defined”**
→ Execute o **arquivo todo**. Em notebooks/células, rode **na ordem** (a célula com `SINONIMOS` precisa ter sido executada antes da função que usa).

**3) O modelo semântico não baixa/erro de rede**
→ Precisa de internet na primeira execução. Depois fica em cache.

**4) Demora para rodar**
→ Normal na primeira execução (download de modelo). Em máquinas mais simples, aumentar os limiares pode reduzir combinações.

**5) “Pandas não grava Excel”**
→ Instale o motor:

```bash
pip install openpyxl
```

**6) “Não encontrou as colunas”**
→ O script busca por palavras‑chave:

* “**nome**”
* “**whatsapp**” ou “**telefone**”
* “**oferecer**”
* “**aprender**”

Adeque os títulos da sua planilha. Exemplos válidos:

* “Seu **Nome** completo”
* “Número de **WhatsApp**”
* “Quais temas você pode **oferecer**?”
* “Quais temas você quer **aprender**?”

---

## 13) Rodar no VS Code (opcional, mas amigável)

1. Abra a pasta `mentoria/` no VS Code.
2. Pressione `Ctrl+Shift+P` → “Python: Select Interpreter” → escolha o **.venv**.
3. Abra o `script.py`.
4. Terminal integrado (\`Ctrl+\`\`) → ative o venv se não estiver ativo.
5. Rode:

   ```bash
   python script.py
   ```

---

## 14) Estrutura final esperada

Após rodar com sucesso:

```
mentoria/
├─ script.py
├─ forms.xlsx
└─ correspondencias_mentoria.xlsx
   ├─ [aba] Matches
   ├─ [aba] Mentores sem mentorados
   └─ [aba] Mentorados sem mentores
```

---

## 15) Próximos passos (ideias)

* Criar uma aba **Resumo** no Excel com contagens totais.
* Permitir **peso por tema** (priorizar certos assuntos).
* Limitar **n matches por pessoa** (ex.: no máximo 3) para facilitar a organização.
* Exportar **listas de contato** já filtradas para facilitar envio de mensagens.

---

