# Gerenciador de Projetos e Tarefas

Aplicação full-stack simples para organizar projetos e as tarefas de cada um.
Backend e frontend rodam no **mesmo processo, na mesma porta** — não há CORS para
tratar, e um único comando (`node server.js`) sobe tudo.

---

## Arquitetura

```
┌───────────────────────────────────────────────┐
│  Navegador                                     │
│  public/index.html + style.css + app.js       │
│  (HTML/CSS/JS puro, chamadas via fetch())      │
└───────────────┬───────────────────────────────┘
                │ HTTP (mesma origem, porta 3000)
                ▼
┌───────────────────────────────────────────────┐
│  server.js  —  Node.js + Express              │
│  • express.static('public')  → serve o front   │
│  • rotas /api/*              → API REST JSON    │
└───────────────┬───────────────────────────────┘
                │ chamadas de função (síncronas)
                ▼
┌───────────────────────────────────────────────┐
│  db.js  —  better-sqlite3                     │
│  • abre/cria banco.db                          │
│  • cria as tabelas se não existirem            │
│  • statements preparados + funções de acesso   │
└───────────────┬───────────────────────────────┘
                ▼
            banco.db  (arquivo SQLite no disco)
```

**Camadas:**

- **Frontend (`public/`)** — servido como arquivos estáticos pelo próprio Express.
  Nenhum framework: `app.js` manipula o DOM e conversa com a API por `fetch()`.
  Como o front vem do mesmo servidor da API, as requisições são de mesma origem
  (sem CORS).
- **Backend (`server.js`)** — Express com `express.json()` para ler o corpo das
  requisições, `express.static()` para entregar `public/`, e as rotas REST sob
  `/api/`. Cada rota valida a entrada e delega a persistência para `db.js`.
- **Acesso a dados (`db.js`)** — usa `better-sqlite3` (API **síncrona**, sem
  callbacks/promises). Na primeira carga do módulo, ativa `PRAGMA foreign_keys`,
  roda os `CREATE TABLE IF NOT EXISTS` e prepara os statements. Exporta funções
  de alto nível (`listarProjetos`, `criarTarefa`, `atualizarTarefa`, ...).
- **Banco (`banco.db`)** — arquivo SQLite criado automaticamente no primeiro
  start, na raiz do projeto. Está no `.gitignore`.

### Quadro kanban

As tarefas do projeto selecionado aparecem em três colunas lado a lado —
**A Fazer** (`status = pendente`), **Fazendo** (`fazendo`) e **Feito**
(`concluida`) — cada tarefa como um cartão dentro da coluna do seu `status`.

Para mover um cartão entre colunas há **arrastar-e-soltar** implementado à mão
em `public/app.js`, sem os eventos de drag do HTML5:

- **Toque**: `touchstart` / `touchmove` (não passivo, com `preventDefault` para
  travar a rolagem) / `touchend` / `touchcancel`.
- **Mouse**: `mousedown` / `mousemove` / `mouseup`, reaproveitando a mesma
  lógica.

O arraste só começa após ~8 px de movimento; um clone flutuante segue o
dedo/cursor e `document.elementFromPoint` identifica a coluna sob o ponteiro.
Ao soltar numa coluna diferente, chama-se `PUT /api/tarefas/:id` apenas com o
novo `status` e o quadro é recarregado da API; soltar na mesma coluna não faz
nada. O `<select>` de cada cartão continua como alternativa acessível.

Não há mudança de backend nem de schema: o kanban é apenas uma visão sobre o
campo `status` que já existia.

### Estrutura de arquivos

| Arquivo | Papel |
|---|---|
| `server.js` | Servidor Express: estáticos de `public/` + API REST em `/api/`. Exporta `iniciar(porta)`; só escuta sozinho com `node server.js` |
| `db.js` | Conexão SQLite (caminho via `BANCO_DB`), criação das tabelas e funções de acesso a dados |
| `electron/main.js` | Processo Electron (versão desktop): sobe o Express numa porta livre e abre a janela em `http://localhost:<porta>` |
| `public/index.html` | Layout: barra lateral de projetos + quadro kanban de tarefas |
| `public/style.css` | Estilo (flexbox; colunas do kanban; borda colorida por status; prazo atrasado em vermelho) |
| `public/app.js` | Lógica do cliente: carrega/cria projetos e tarefas, renderiza o kanban, arrastar-e-soltar por toque e mouse (`touch*` / `mouse*`, sem drag HTML5), `<select>` de status, exclusão — tudo via `fetch()` |
| `package.json` | Dependências e scripts (`start`, `electron`, `dist:win`, `postinstall`); config `build` do electron-builder |
| `banco.db` | Banco SQLite (gerado em runtime; ignorado pelo git) |
| `dist/` | Instaladores gerados pelo electron-builder (ignorado pelo git) |

---

## Estrutura das tabelas

Definidas em `db.js` e criadas com `CREATE TABLE IF NOT EXISTS` no start.

### `projetos`

| Coluna | Tipo | Restrições |
|---|---|---|
| `id` | INTEGER | `PRIMARY KEY AUTOINCREMENT` |
| `nome` | TEXT | `NOT NULL` |
| `descricao` | TEXT | opcional (`NULL` permitido) |

### `tarefas`

| Coluna | Tipo | Restrições |
|---|---|---|
| `id` | INTEGER | `PRIMARY KEY AUTOINCREMENT` |
| `projeto_id` | INTEGER | `NOT NULL`, `REFERENCES projetos(id) ON DELETE CASCADE` |
| `titulo` | TEXT | `NOT NULL` |
| `status` | TEXT | `NOT NULL DEFAULT 'pendente'`, `CHECK (status IN ('pendente','fazendo','concluida'))` |
| `prazo` | TEXT | opcional; formato `YYYY-MM-DD` |

**Notas:**

- `status` só aceita os três valores `pendente`, `fazendo`, `concluida` — o
  `CHECK` garante isso no nível do banco, e a API também valida antes de gravar.
- `prazo` é guardado como texto ISO (`YYYY-MM-DD`), que ordena e compara
  corretamente como string. O frontend exibe no formato `DD/MM/AAAA`.
- `ON DELETE CASCADE` + `PRAGMA foreign_keys = ON`: apagar um projeto apagaria
  automaticamente suas tarefas. (Não há endpoint para excluir projeto — apenas
  tarefas — mas a integridade referencial está garantida.)

---

## Endpoints da API

Todas as respostas são JSON. Erros retornam `{ "erro": "mensagem" }` com o
status HTTP apropriado (`400` entrada inválida, `404` recurso inexistente).

### Projetos

| Método | Rota | Corpo (JSON) | Sucesso | Descrição |
|---|---|---|---|---|
| `GET` | `/api/projetos` | — | `200` `[{id, nome, descricao}]` | Lista todos os projetos |
| `POST` | `/api/projetos` | `{ nome, descricao? }` | `201` projeto criado | Cria um projeto (`nome` obrigatório) |

### Tarefas de um projeto

| Método | Rota | Corpo (JSON) | Sucesso | Descrição |
|---|---|---|---|---|
| `GET` | `/api/projetos/:id/tarefas` | — | `200` `[{id, projeto_id, titulo, status, prazo}]` | Lista as tarefas do projeto `:id` |
| `POST` | `/api/projetos/:id/tarefas` | `{ titulo, status?, prazo? }` | `201` tarefa criada | Cria tarefa no projeto (`titulo` obrigatório; `status` default `pendente`) |

### Tarefa individual

| Método | Rota | Corpo (JSON) | Sucesso | Descrição |
|---|---|---|---|---|
| `PUT` | `/api/tarefas/:id` | `{ titulo?, status?, prazo? }` | `200` tarefa atualizada | Atualização **parcial**: só os campos enviados mudam |
| `DELETE` | `/api/tarefas/:id` | — | `204` (sem corpo) | Remove a tarefa |

### Exemplos (`curl`)

```bash
# criar projeto
curl -X POST http://localhost:3000/api/projetos \
  -H "Content-Type: application/json" \
  -d '{"nome":"Website","descricao":"Refazer o site"}'

# criar tarefa nesse projeto
curl -X POST http://localhost:3000/api/projetos/1/tarefas \
  -H "Content-Type: application/json" \
  -d '{"titulo":"Criar wireframe","prazo":"2026-09-01"}'

# mover a tarefa para "fazendo"
curl -X PUT http://localhost:3000/api/tarefas/1 \
  -H "Content-Type: application/json" \
  -d '{"status":"fazendo"}'

# apagar a tarefa
curl -X DELETE http://localhost:3000/api/tarefas/1
```

---

## Como rodar

Requisito: Node.js instalado.

```bash
npm install
```

```bash
node server.js
```

Depois abra **http://localhost:3000** no navegador.

- A porta pode ser trocada com a variável de ambiente `PORT` (ex.: `PORT=8080 node server.js`).
- `banco.db` é criado sozinho no primeiro start; para "zerar" os dados, pare o
  servidor e apague esse arquivo.

### Sobre o `npm install`

O `better-sqlite3` é um módulo nativo. Ele baixa um binário pré-compilado
compatível com a sua versão do Node; se não houver, tenta compilar do zero (o
que exige ferramentas de build C++). Se o `npm install` falhar na compilação,
atualize para a versão mais recente do `better-sqlite3`, que costuma já ter o
binário pronto para o seu Node.

## Versão desktop (Windows / Electron)

O mesmo backend Express roda dentro de um processo Electron: `electron/main.js`
chama `iniciar(0)` de `server.js` (porta livre escolhida pelo SO), abre uma
janela e carrega `http://localhost:<porta>`. Como a página é servida por HTTP na
mesma origem, o frontend usa caminhos relativos (`API_BASE` vazio) e não há CORS.

O banco fica em `app.getPath('userData')/banco.db` (via `BANCO_DB`), fora do
pacote, que é somente leitura.

### Rodar em desenvolvimento

```bash
npm install
npm run electron
```

### Gerar o instalador

```bash
npm run dist:win
```

Sai um instalador NSIS em `dist/` (config em `build` no `package.json`:
`appId`, `productName`, `asarUnpack` do `better-sqlite3`).

### `postinstall` / `electron-rebuild`

`npm install` roda `electron-rebuild` (script `postinstall`) para recompilar
módulos nativos contra o ABI do Electron. **Isso exige toolchain C++**
(Visual Studio Build Tools com "Desktop development with C++" + Python).

Sem esse toolchain o `electron-rebuild` falha, mas o app ainda funciona: o
`better-sqlite3` 13 usa **Node-API** (ABI estável entre Node e Electron), então
o binário pré-compilado já carrega na janela do Electron sem recompilar.
