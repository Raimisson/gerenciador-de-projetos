# Gerenciador de Projetos e Tarefas

App full-stack simples: Express + better-sqlite3 no backend, HTML/CSS/JS puro no frontend.
Backend e frontend rodam no mesmo processo e na mesma porta — sem CORS.

## Rodar

```bash
npm install
node server.js
```

Abrir http://localhost:3000 (porta configurável via variável de ambiente `PORT`).

O arquivo `banco.db` (SQLite) é criado automaticamente no primeiro start.

## Estrutura

| Arquivo | Papel |
|---|---|
| `db.js` | Abre `banco.db`, cria as tabelas `projetos` e `tarefas`, expõe funções de acesso |
| `server.js` | Express: serve `public/` e a API REST em `/api/` |
| `public/index.html` | Layout: sidebar de projetos + painel de tarefas |
| `public/style.css` | Estilo (flexbox, cor por status) |
| `public/app.js` | Consome a API com `fetch()` |

## API

| Método | Rota | Corpo | Resposta |
|---|---|---|---|
| GET | `/api/projetos` | — | lista de projetos |
| POST | `/api/projetos` | `{ nome, descricao? }` | `201` projeto criado |
| GET | `/api/projetos/:id/tarefas` | — | tarefas do projeto |
| POST | `/api/projetos/:id/tarefas` | `{ titulo, status?, prazo? }` | `201` tarefa criada |
| PUT | `/api/tarefas/:id` | `{ titulo?, status?, prazo? }` (parcial) | tarefa atualizada |
| DELETE | `/api/tarefas/:id` | — | `204` |

`status` ∈ `pendente` \| `fazendo` \| `concluida`. `prazo` é texto `YYYY-MM-DD` (opcional).
Apagar um projeto removeria suas tarefas em cascata (`ON DELETE CASCADE`), mas não há
endpoint de exclusão de projeto — só de tarefa, conforme especificado.
