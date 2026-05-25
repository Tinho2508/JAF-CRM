# JAF CRM

Sistema de gestão de seguros completo com CRM, integração WhatsApp e inteligência artificial.

[![GitHub](https://img.shields.io/badge/Reposit%C3%B3rio-GitHub-black?logo=github)](https://github.com/Tinho2508/JAF-CRM)
[![GitHub Pages](https://img.shields.io/badge/Frontend-GitHub%20Pages-blue?logo=github)](https://tinho2508.github.io/JAF-CRM/)
[![Render](https://img.shields.io/badge/Backend-Render-blue?logo=render)](https://jaf-crm-backend.onrender.com)
[![Supabase](https://img.shields.io/badge/Database-Supabase-green?logo=supabase)](https://supabase.com)
[![Gemini](https://img.shields.io/badge/AI-Gemini%202.0%20Flash--Lite-yellow?logo=google)](https://ai.google.dev)
[![Twilio](https://img.shields.io/badge/WhatsApp-Twilio-red?logo=twilio)](https://twilio.com)


---

## Visão Geral

O **JAF CRM** é um sistema completo para corretoras de seguros, desenvolvido para gerenciar clientes, apólices, propostas, leads, produção, comissões, sinistros e agenda — tudo integrado com WhatsApp e inteligência artificial.

```mermaid
graph TB
    A[Usuário] --> B["GitHub Pages - Frontend SPA"]
    B --> C["Supabase - Banco de Dados"]
    B --> D["Cloudflare Worker - Proxy Gemini"]
    E["WhatsApp - Cliente"] --> F[Twilio]
    F --> G["Render - Backend Flask"]
    G --> C
    G --> D
    G --> F
```

### Arquitetura

| Camada | Tecnologia | Função |
|--------|-----------|--------|
| **Frontend** | HTML5 + CSS3 + JavaScript (SPA) | Interface do usuário, offline-first com IndexedDB |
| **Backend** | Flask (Python) | Webhook WhatsApp, API REST, integração Gemini |
| **Banco** | Supabase (PostgreSQL) | Armazenamento cloud, Realtime, autenticação |
| **IA** | Google Gemini 2.0 Flash-Lite | Triagem de mensagens, sugestão de respostas |
| **WhatsApp** | Twilio API | Envio/recebimento de mensagens |
| **Proxy** | Cloudflare Worker | Segurança da chave Gemini |

---

## Funcionalidades

### 📊 Dashboard
- KPIs: total de clientes, apólices ativas, produção do mês, comissões, leads, renovações
- Gráficos por ramo, produto e evolução mensal
- Top clientes por prêmio total
- Alertas de renovações urgentes (7 e 30 dias)
- Filtro por mês/ano

### 👥 Clientes
- Cadastro completo com CPF/CNPJ, telefone, WhatsApp, e-mail, cidade
- Distribuição automática de registros da produção
- Botão WhatsApp direto na listagem
- Visão 360°: apólices, propostas, leads, sinistros, agenda

### 📄 Apólices
- Cadastro com prêmio, comissão (cálculo automático), vigência, vencimento
- Status: Ativa, Cancelada, Suspensa
- Links rápidos para WhatsApp (renovação, cobrança)

### 🎯 Leads
- Pipeline visual em Kanban: Novo → Em Contato → Proposta Enviada → Negociação → Fechado
- Filtro por status, mês, ano
- Automação: leads criados automaticamente via WhatsApp

### 💰 Produção
- Registro de produção com valor, comissão, IOF, parcela
- Deduplicação inteligente (agrupa por nome+data+valor)
- Distribuição para clientes, propostas e apólices
- Filtro por mês/ano

### 💵 Comissões
- Totalização por período
- Detalhamento por produto
- Gráfico de barras mensal

### 📅 Agenda
- Tarefas: ligação, WhatsApp, e-mail, reunião, renovação, visita
- Status: agendado, concluído, cancelado
- Alertas de atraso
- Criação automática via WhatsApp

### ⚠️ Sinistros
- Registro com tipo, valor estimado, status
- Tipos: colisão, roubo/furto, incêndio, alagamento, etc.
- Criação automática via WhatsApp

### 🔄 Renovações
- Pipeline por urgência: 7, 15, 30, 60 dias
- Botão WhatsApp com template automático

### 📈 Relatórios
- Totalizações: premio, comissão, leads, propostas
- Ticket médio, taxa de conversão
- Filtro por mês/ano

### 💬 Mensagens WhatsApp
- Histórico completo de conversas
- Identificação de intenção via IA
- Cores por urgência (alta, média, baixa)
- Simulador de webhook para testes
- Integração com Twilio

### 🤖 Assistente IA (Gemini)
- Comandos de voz e texto
- Localizar clientes, apólices, leads
- Navegar entre páginas
- Contar registros com filtros
- Criar leads e tarefas
- Acessível pelo botão flutuante "AI"

---

## Tecnologias

### Frontend
- **HTML5** + **CSS3** (variáveis, flexbox, grid, animações)
- **JavaScript** (ES6+ assíncrono, IndexedDB)
- **SheetJS (XLSX)** — importação/exportação de planilhas
- **Supabase JS v2** — cliente Supabase no browser
- Design responsivo com **dark mode**

### Backend
- **Flask** — framework web Python
- **Supabase Python** — cliente Supabase server-side
- **Google Generative AI** — cliente Gemini (via proxy)
- **Gunicorn** — servidor WSGI de produção
- **Render** — hospedagem cloud

### Infraestrutura
- **Supabase** — PostgreSQL, autenticação, Realtime
- **GitHub Pages** — deploy contínuo do frontend
- **Render** — deploy do backend Flask
- **Cloudflare Workers** — proxy seguro para Gemini
- **Twilio** — API WhatsApp Business

---

## Estrutura do Projeto

```
JAF-CRM/
├── frontend/
│   └── index.html          # Aplicação SPA completa
├── backend/
│   ├── app.py              # Servidor Flask (webhook + API)
│   ├── auto_crm.py         # Automação CRM via WhatsApp
│   ├── gemini_client.py    # Cliente Gemini via proxy
│   ├── supabase_client.py  # Operações com Supabase
│   ├── wa_adapter.py       # Adaptador de provedores WhatsApp
│   ├── requirements.txt    # Dependências Python
│   ├── render.yaml         # Config Render
│   ├── Procfile            # Comando de start
│   ├── migration_whatsapp_messages.sql  # DDL tabela mensagens
│   └── migration_rls_policies.sql       # Políticas RLS
├── worker/
│   └── worker.js           # Cloudflare Worker (proxy Gemini)
├── .github/workflows/
│   └── deploy-pages.yml    # GitHub Actions (deploy frontend)
└── README.md
```

---

## Fluxo de Mensagens WhatsApp

```mermaid
sequenceDiagram
    participant C as Cliente
    participant W as Twilio
    participant B as Backend Flask
    participant G as Gemini
    participant S as Supabase

    C->>W: Envia mensagem
    W->>B: POST /webhook/whatsapp
    B->>G: Triagem (intenção, urgência)
    G-->>B: JSON com análise
    B->>B: Auto-CRM (cria leads/sinistros/agenda)
    B->>S: Salva mensagem + metadados
    B-->>W: Resposta 200 OK
    W-->>C: (resposta sugerida, se configurado)
```

---

## Sincronização

O sistema opera **offline-first**: os dados ficam no IndexedDB do navegador e sincronizam com o Supabase em segundo plano.

- ✅ **Auto-sync** ao abrir o app
- ✅ **Forçar Download** — substitui dados locais pelo servidor
- ✅ **Enviar ao Supabase** — upload local → cloud
- ✅ **Sincronizar** — merge bidirecional com deduplicação
- ✅ **Backup/restore** via JSON
- ✅ **Importação** de planilhas Excel (.xlsx)

---

## Lógica do Sistema e Algoritmos

### 1. Fluxo de Inicialização (initApp)

```mermaid
sequenceDiagram
    participant U as Usuário
    participant B as Navegador
    participant I as IndexedDB
    participant S as Supabase

    B->>B: DOMContentLoaded
    B->>B: Carrega dark mode
    B->>B: Cria cliente Supabase (anônimo)
    B->>I: init() → abre DB v31
    Note over B,I: Cria object stores se não existirem
    B->>I: seedData() (se primeira vez)
    B->>I: refreshCache() → carrega tudo na RAM
    B->>B: cleanupEmptyRecords()
    B->>B: render() + updateBadges()
    B->>S: setTimeout 500ms → fetchAll() paginado
    S-->>B: Dados completos
    B->>I: deduplicateRecords() + setTable()
    Note over B,I: Colapsa duplicatas por nome/chave
```

### 2. Fluxo de Login (fazerLogin → entrarApp)

```mermaid
sequenceDiagram
    participant U as Usuário
    participant B as Navegador
    participant S as Supabase

    U->>B: Clica "Entrar"
    B->>B: Valida email/senha
    B->>S: signInWithPassword()
    S-->>B: Sessão autenticada
    B->>B: Armazena client autenticado
    B->>B: Oculta tela login, exibe app
    B->>B: refreshCache() (IndexedDB)
    loop Para cada tabela
        B->>S: fetchAll() paginado (1000/request)
        S-->>B: Todos registros
        B->>B: deduplicateRecords()
        B->>I: setTable() — substitui local
    end
    B->>B: render() + toast "Dados carregados!"
    B->>S: iniciarRealtime() — channel postgres_changes
```

### 3. Algoritmo de Sincronização (sincronizar)

O merge bidirecional entre IndexedDB e Supabase:

```mermaid
flowchart TD
    A["Inicio sincronizar"] --> B{"Para cada tabela?"}
    B --> C["fetchAll local + remote"]
    C --> D{"remoteData.length > 0?"}
    D -->|Sim| E["mergeData: mapa por ID"]
    E --> F["deduplicateRecords"]
    F --> G["Filtrar deleted_ids"]
    G --> H["Deletar do Supabase os IDs em deleted_ids"]
    H --> I["Limpar deleted_ids da tabela"]
    I --> J["Upsert dados locais -> Supabase"]
    J --> K["setTable local = merged"]
    D -->|Nao| L{"localData.length > 0?"}
    L -->|Sim| M["Filtrar deleted_ids"]
    M --> N["Deletar do Supabase"]
    N --> O["Upsert locais -> Supabase"]
    O --> P["setTable local"]
    L -->|Nao| Q["setTable []"]
    K --> R{"Ainda ha tabelas?"}
    P --> R
    Q --> R
    R -->|Sim| B
    R -->|Nao| S["Atualizar status + render"]
```

**Algoritmo mergeData:**
```
Entrada: local (Array), remote (Array)
Saída:   Array mesclado

mapa = {}
para cada item em local:
    mapa[item.id] = item
para cada item em remote:
    mapa[item.id] = item
retornar Object.values(mapa)
```
- União por ID: registros locais e remotos com o mesmo ID são mesclados (remoto sobrescreve local)
- Garante que nenhum registro seja perdido

**Algoritmo deduplicateRecords:**
```
Entrada: tabela (string), data (Array)
Saída:   Array sem duplicatas

chaves = {
  clientes: 'nome',
  apolices: 'numero_apolice',
  leads:    'nome_cliente',
  propostas:'numero_proposta'
}
key = chaves[tabela] ou null
se key for null: retornar data

vistos = {}  // mapa: valor_normalizado → registro
unicos = []
para cada item em data:
    val = item[key]
    se val vazio: adicionar a unicos; continuar
    normalizado = val.trim().toLowerCase()
    se não está em vistos:
        vistos[normalizado] = item
        adicionar a unicos
    senão:
        existente = vistos[normalizado]
        se item.criado_em >= existente.criado_em:
            substituir existente por item em unicos
            vistos[normalizado] = item
retornar unicos
```
- Mantém o registro **mais recente** (por `criado_em`) quando encontra o mesmo nome
- Preserva registros sem valor na chave (não os descarta)
- Tabelas sem chave definida (producao, sinistros, agenda) não são deduplicadas

### 4. Algoritmo de Paginação (fetchAll)

```mermaid
flowchart LR
    A["fetchAll(client, table)"] --> B["all = []"]
    B --> C["from = 0"]
    C --> D["pageSize = 1000"]
    D --> E["select * range from..from+pageSize-1"]
    E --> F{"res.data?"}
    F -->|Sim| G["all.concat(res.data)"]
    G --> H{"res.data.length < pageSize?"}
    H -->|Sim| I["return all"]
    H -->|Nao| J["from += pageSize"]
    J --> E
    F -->|Nao| K["return all"]
```

```javascript
async function fetchAll(client, table) {
  var all = [];
  var from = 0;
  var pageSize = 1000;
  while (true) {
    var res = await client
      .from(table)
      .select('*')
      .range(from, from + pageSize - 1);
    if (res.error || !res.data || !res.data.length) break;
    all = all.concat(res.data);
    if (res.data.length < pageSize) break;
    from += pageSize;
  }
  return all;
}
```
- Supabase limita `select('*')` a 1000 linhas por requisição
- `fetchAll` faz requisições sequenciais com `.range()` até obter menos de 1000 linhas
- Usado em: `entrarApp`, `initApp` (auto-sync), `sincronizar`, `forcarDownload`

### 5. Fluxo de Exclusão com Deleção Remota

```mermaid
flowchart TD
    A["Usuario clica"] --> B["confirm2"]
    B -->|Confirma| C["Filtra registro do array local"]
    C --> D["setTable -> IndexedDB"]
    D --> E["addDeletedId na store deleted_ids"]
    E --> F["delete() no Supabase .eq('id', id)"]
    F --> G{"Sucesso?"}
    G -->|Sim| H["toast 'Removido'"]
    G -->|Nao| I["toast 'Erro ao excluir do servidor'"]
    H --> J["render()"]
    I --> J
    J --> K["enviarTabela -> upsert dos restantes"]
```

- `deleted_ids` é uma object store separada no IndexedDB
- Usada pelo `sincronizar()` para deletar registros órfãos do Supabase
- Após delete bem-sucedido no Supabase, `deleted_ids` são limpos na sincronização

### 6. Estratégia de Políticas RLS (Row Level Security)

```sql
-- Para cada tabela CRM (clientes, apolices, etc.):
CREATE POLICY "auth_select" ON public.clientes
  FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "auth_insert" ON public.clientes
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "auth_update" ON public.clientes
  FOR UPDATE USING (auth.role() = 'authenticated')
            WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "auth_delete" ON public.clientes
  FOR DELETE USING (auth.role() = 'authenticated');
```

- **4 políticas independentes** por tabela (vs. `FOR ALL` sem `WITH CHECK` que bloqueava INSERT)
- `USING` → controla quais linhas são visíveis/afetadas (SELECT, UPDATE, DELETE)
- `WITH CHECK` → controla quais novas linhas podem ser inseridas (INSERT, UPDATE)
- Autenticação feita via `supabase.auth.signInWithPassword()` no frontend
- Tabela `whatsapp_messages` usa política `FOR ALL` para anon (webhook público)

### 7. Arquitetura do Auto-CRM (Backend)

```mermaid
flowchart TD
    A["Webhook Twilio - POST /webhook/whatsapp"] --> B[app.py]
    B --> C["Rate limit 3s/telefone?"]
    C -->|Bloqueado| D["return 200 OK (ignora)"]
    C -->|Liberado| E[Salva mensagem raw]
    E --> F[auto_crm.py]
    F --> G["Gemini: triagem (intencao + urgencia)"]
    G --> H["Acao detectada?"]
    H -->|lead_novo| I[Criar lead]
    H -->|sinistro| J[Criar sinistro]
    H -->|agenda| K[Criar agenda]
    H -->|cliente| L["Atualizar/criar cliente"]
    H -->|responder| M[Sugerir resposta]
    I --> N["Salvar no Supabase"]
    J --> N
    K --> N
    L --> N
    M --> N
    N --> O["return 200 OK"]
```

**Fluxo de triagem Gemini:**
```
Mensagem do cliente → POST /worker (proxy)
  → Gemini 2.0 Flash-Lite analisa:
    - intenção (lead_novo, sinistro, agendar, etc.)
    - urgência (alta, media, baixa)
    - dados estruturados extraídos
    - resposta sugerida
  → Backend executa ações no CRM
  → Salva tudo em whatsapp_messages
```

### 8. Diagrama de Componentes (Visão 360°)

```mermaid
graph TB
    subgraph Frontend["Navegador - GitHub Pages"]
        SPA["index.html - SPA Completa"]
        IDB["(IndexedDB) - Offline-first"]
        SPA --> IDB
    end

    subgraph Backend["Render - Flask"]
        API["app.py - API REST"]
        AUTO["auto_crm.py - Automacao"]
        GEM["gemini_client.py - Cliente Gemini"]
        SUP["supabase_client.py - Operacoes BD"]
        WA["wa_adapter.py - Adaptador WhatsApp"]
        API --> AUTO
        API --> WA
        AUTO --> GEM
        AUTO --> SUP
    end

    subgraph Cloud["Infraestrutura"]
        PG["(Supabase PG) - 7 tabelas CRM"]
        REAL["Supabase Realtime - WebSocket"]
        WORKER["Cloudflare Worker - Proxy Gemini"]
        TW["Twilio API - WhatsApp"]
    end

    subgraph IA["Google AI"]
        GEMINI["Gemini 2.0 Flash-Lite"]
    end

    SPA -->|select/upsert| PG
    SPA -->|subscribe| REAL
    REAL -->|notify| SPA
    SPA -->|POST /worker| WORKER
    WORKER -->|API key oculta| GEMINI
    TW -->|POST webhook| API
    API -->|POST| TW
    API -->|POST /worker| WORKER
```

### 9. Diagrama de Estados (Registros)

```mermaid
stateDiagram-v2
    [*] --> Offline: Página carregada
    Offline --> Online: Login / Auto-sync
    Online --> Offline: Logout / Falha de rede
    
    state Online {
        [*] --> Local: Edição do usuário
        Local --> Sincronizado: enviarTabela()
        Sincronizado --> Local: Edição / Exclusão
        Local --> Remoto: Alteração via WhatsApp
        Remoto --> Local: Realtime notification
    }
    
    state Sincronizado {
        [*] --> Merged: sincronizar()
        Merged --> [*]: Deduplicado
    }
```

---

## Direitos Autorais

© 2026 JAF CRM. Todos os direitos reservados.


