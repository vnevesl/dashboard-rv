# 💼 Painel de Carteiras — Como Rodar

Guia completo para rodar o dashboard no seu computador, mesmo sem experiência com programação.

---

## 📦 Arquivos da pasta

Você precisa ter estes arquivos na mesma pasta:

```
grafico de pizza/
├── .streamlit/
│   └── config.toml       ← tema visual (não apagar)
├── img/
│   ├── logo branca xp (3).png   ← logo para modo escuro
│   └── logo preta xp (2).png    ← logo para modo claro
├── app.py                 ← o dashboard
├── requirements.txt       ← lista de dependências
├── COMO_RODAR.md          ← este guia
└── *.xlsx                 ← seu arquivo de dados
```

> Se tiver outros arquivos como `.claude` ou `claude.md`, pode ignorar ou apagar — não fazem parte do dashboard.

---

## 📋 O que você vai precisar

- Um computador (Mac ou Windows)
- Conexão com a internet (só para instalar, depois roda offline)
- Os arquivos listados acima na mesma pasta

---

## 🚀 Passo a Passo

### Passo 1 — Instalar o Python

O Python é o "motor" que roda o dashboard. Você só precisa instalar uma vez.

#### No Mac:

1. Abra o **Terminal** (pressione `Cmd + Espaço`, digite `Terminal` e aperte Enter)
2. Cole o comando abaixo e aperte Enter:

```
python3 --version
```

3. Se aparecer algo como `Python 3.x.x`, você já tem o Python! Pule para o **Passo 2**
4. Se der erro, acesse [python.org/downloads](https://www.python.org/downloads/), clique no botão amarelo **Download Python** e instale normalmente (Next, Next, Install)

#### No Windows:

1. Acesse [python.org/downloads](https://www.python.org/downloads/)
2. Clique no botão amarelo **Download Python**
3. **IMPORTANTE:** Na tela de instalação, marque a caixinha **"Add Python to PATH"** antes de clicar em Install
4. Clique em **Install Now** e espere terminar

> **Como saber se deu certo?** Abra o Terminal (Mac) ou Prompt de Comando (Windows) e digite:
> ```
> python3 --version
> ```
> Se aparecer `Python 3.x.x` está tudo certo.
>
> No Windows, se `python3` não funcionar, tente apenas `python --version`.

---

### Passo 2 — Abrir o Terminal na pasta certa

Você precisa abrir o Terminal/Prompt de Comando **dentro da pasta** onde estão os arquivos.

#### No Mac:

1. Abra o **Finder** e navegue até a pasta `grafico de pizza`
2. Clique com o **botão direito** na pasta
3. Clique em **"Novo Terminal na Pasta"**

Ou, se preferir, abra o Terminal e cole:

```
cd ~/Desktop/"grafico de pizza"
```

#### No Windows:

1. Abra o **Explorador de Arquivos** e navegue até a pasta `grafico de pizza`
2. Clique na **barra de endereço** no topo (onde mostra o caminho da pasta)
3. Digite `cmd` e aperte Enter

Isso abre o Prompt de Comando já na pasta certa.

---

### Passo 3 — Instalar as dependências

Dependências são as "ferramentas" que o dashboard precisa para funcionar. Você só instala uma vez.

Cole o comando abaixo no Terminal e aperte Enter:

#### No Mac:

```
pip3 install -r requirements.txt
```

#### No Windows:

```
pip install -r requirements.txt
```

Vai aparecer um monte de texto na tela — é normal. Espere até voltar a aparecer o cursor piscando.

> **Deu erro?** Tente:
> ```
> python3 -m pip install -r requirements.txt
> ```
> Ou no Windows:
> ```
> python -m pip install -r requirements.txt
> ```

---

### Passo 4 — Rodar o Dashboard

Agora sim, cole o comando abaixo e aperte Enter:

#### No Mac:

```
python3 -m streamlit run app.py
```

#### No Windows:

```
python -m streamlit run app.py
```

Vai aparecer uma mensagem assim:

```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
```

**O dashboard abriu automaticamente no seu navegador!**

Se não abriu sozinho, copie o endereço `http://localhost:8501` e cole no navegador (Chrome, Firefox, Edge, etc).

---

### Passo 5 — Usar o Dashboard

- **Sidebar esquerda:** use os filtros para selecionar carteiras, status e datas
- **Gráficos:** passe o mouse por cima para ver detalhes de cada dado
- **Dados completos:** clique em "📋 Ver Dados Completos" no final da página

---

## 🔄 Nas próximas vezes

Depois de tudo instalado, para abrir o dashboard de novo você só precisa de **dois passos**:

1. Abrir o Terminal na pasta (Passo 2)
2. Rodar o comando (Passo 4):

```
python3 -m streamlit run app.py
```

---

## 📊 Atualizar os dados do dia

1. Com o dashboard aberto, olhe na **barra lateral esquerda**
2. No final, tem a seção **"🔄 Atualizar Dados"** — ali mostra se o arquivo é de hoje, ontem, ou mais antigo
3. Clique em **"Browse files"** (ou arraste o arquivo) e selecione o novo `.xlsx`
4. O arquivo antigo é substituído automaticamente e o dashboard recarrega com os dados novos

---

## ❌ Parar o Dashboard

Para parar o dashboard, vá no Terminal e aperte:

```
Ctrl + C
```

---

## 🆘 Problemas comuns

| Problema | Solução |
|---|---|
| `python3 não encontrado` | No Windows, tente `python` em vez de `python3` |
| `pip não encontrado` | Tente `python3 -m pip` em vez de `pip3` |
| `Porta já em uso` | O dashboard já está rodando. Acesse `http://localhost:8501` no navegador |
| `Tela em branco` | Aperte `Ctrl + Shift + R` no navegador para forçar o reload |
| `Erro no Excel` | Verifique se o arquivo `.xlsx` está na mesma pasta que o `app.py` |
| `Permissão negada` (Mac) | Adicione `sudo` antes do comando: `sudo pip3 install -r requirements.txt` |
