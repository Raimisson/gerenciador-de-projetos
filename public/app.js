'use strict';

const STATUS_LABEL = {
  pendente: 'A Fazer',
  fazendo: 'Fazendo',
  concluida: 'Feito',
};

const LIMIAR_ARRASTE = 8; // px de movimento antes de considerar que é um arraste

// Endereço base da API.
// - Página servida por HTTP (Express local, janela do Electron, dev server):
//   usa a mesma origem — caminhos relativos, sem CORS.
// - Página aberta de outra origem sem servidor próprio (ex.: file://, WebView
//   de app empacotado): cai no endereço absoluto do servidor na rede local.
const API_BASE =
  location.protocol === 'http:' || location.protocol === 'https:'
    ? ''
    : 'http://192.168.0.15:3000';

let projetoAtual = null;

// --- Elementos ---
const listaProjetosEl = document.getElementById('lista-projetos');
const formProjetoEl = document.getElementById('form-projeto');
const projetoNomeEl = document.getElementById('projeto-nome');
const projetoDescricaoEl = document.getElementById('projeto-descricao');

const semSelecaoEl = document.getElementById('sem-selecao');
const painelProjetoEl = document.getElementById('painel-projeto');
const projetoTituloEl = document.getElementById('projeto-titulo');
const projetoDescEl = document.getElementById('projeto-desc');

const formTarefaEl = document.getElementById('form-tarefa');
const tarefaTituloEl = document.getElementById('tarefa-titulo');
const tarefaPrazoEl = document.getElementById('tarefa-prazo');
const tarefaStatusEl = document.getElementById('tarefa-status');
const kanbanEl = document.getElementById('kanban');
const dropzones = {};
for (const dz of kanbanEl.querySelectorAll('[data-dropzone]')) {
  dropzones[dz.dataset.dropzone] = dz;
}

// --- Helper de fetch ---
// `caminho` é sempre algo como '/api/...'; o endereço completo é montado com API_BASE.
async function api(caminho, options = {}) {
  const resp = await fetch(API_BASE + caminho, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!resp.ok) {
    let msg = `Erro ${resp.status}`;
    try {
      const corpo = await resp.json();
      if (corpo && corpo.erro) msg = corpo.erro;
    } catch (_) {
      /* resposta sem JSON */
    }
    throw new Error(msg);
  }

  if (resp.status === 204) return null;
  return resp.json();
}

// --- Projetos ---

async function carregarProjetos() {
  const projetos = await api('/api/projetos');
  listaProjetosEl.innerHTML = '';

  if (projetos.length === 0) {
    const li = document.createElement('li');
    li.className = 'vazio';
    li.textContent = 'Nenhum projeto ainda.';
    listaProjetosEl.appendChild(li);
    return;
  }

  for (const projeto of projetos) {
    const li = document.createElement('li');
    li.textContent = projeto.nome;
    li.dataset.id = projeto.id;
    if (projetoAtual && projeto.id === projetoAtual.id) {
      li.classList.add('ativo');
    }
    li.addEventListener('click', () => selecionarProjeto(projeto));
    listaProjetosEl.appendChild(li);
  }
}

function selecionarProjeto(projeto) {
  projetoAtual = projeto;

  for (const li of listaProjetosEl.querySelectorAll('li')) {
    li.classList.toggle('ativo', Number(li.dataset.id) === projeto.id);
  }

  semSelecaoEl.classList.add('oculto');
  painelProjetoEl.classList.remove('oculto');
  projetoTituloEl.textContent = projeto.nome;
  projetoDescEl.textContent = projeto.descricao || '';

  carregarTarefas();
}

formProjetoEl.addEventListener('submit', async (e) => {
  e.preventDefault();
  const nome = projetoNomeEl.value.trim();
  if (!nome) return;

  try {
    const novo = await api('/api/projetos', {
      method: 'POST',
      body: JSON.stringify({
        nome,
        descricao: projetoDescricaoEl.value.trim(),
      }),
    });
    formProjetoEl.reset();
    await carregarProjetos();
    selecionarProjeto(novo);
  } catch (err) {
    alert(err.message);
  }
});

// --- Tarefas (quadro kanban) ---

async function carregarTarefas() {
  if (!projetoAtual) return;

  const tarefas = await api(`/api/projetos/${projetoAtual.id}/tarefas`);
  renderKanban(tarefas);
}

function renderKanban(tarefas) {
  const porStatus = { pendente: [], fazendo: [], concluida: [] };
  for (const tarefa of tarefas) {
    (porStatus[tarefa.status] || porStatus.pendente).push(tarefa);
  }

  for (const status of Object.keys(dropzones)) {
    const zona = dropzones[status];
    zona.innerHTML = '';
    for (const tarefa of porStatus[status]) {
      zona.appendChild(criarCard(tarefa));
    }
    const contador = zona.closest('.coluna').querySelector('[data-count]');
    if (contador) contador.textContent = String(porStatus[status].length);
  }
}

function criarCard(tarefa) {
  const card = document.createElement('div');
  card.className = 'card';
  card.dataset.id = tarefa.id;
  card.dataset.status = tarefa.status;

  const titulo = document.createElement('div');
  titulo.className = 'card-titulo';
  titulo.textContent = tarefa.titulo;
  card.appendChild(titulo);

  if (tarefa.prazo) {
    const prazo = document.createElement('div');
    prazo.className = 'card-prazo';
    prazo.textContent = `Prazo: ${formatarData(tarefa.prazo)}`;
    const hoje = new Date().toISOString().slice(0, 10);
    if (tarefa.prazo < hoje && tarefa.status !== 'concluida') {
      prazo.classList.add('atrasado');
      prazo.textContent += ' (atrasado)';
    }
    card.appendChild(prazo);
  }

  const acoes = document.createElement('div');
  acoes.className = 'card-acoes';

  // <select> como alternativa acessível / para toque, além do arrastar
  const select = document.createElement('select');
  select.title = 'Mover para';
  for (const valor of Object.keys(STATUS_LABEL)) {
    const opt = document.createElement('option');
    opt.value = valor;
    opt.textContent = STATUS_LABEL[valor];
    if (valor === tarefa.status) opt.selected = true;
    select.appendChild(opt);
  }
  select.addEventListener('change', () => mudarStatus(tarefa.id, select.value));

  const btnApagar = document.createElement('button');
  btnApagar.className = 'btn-apagar';
  btnApagar.type = 'button';
  btnApagar.textContent = '\u{1F5D1}';
  btnApagar.title = 'Apagar tarefa';
  btnApagar.addEventListener('click', () => apagarTarefa(tarefa.id));

  acoes.append(select, btnApagar);
  card.appendChild(acoes);

  // Arrastar-e-soltar por toque e por mouse (sem os eventos de drag do HTML5)
  card.addEventListener('touchstart', (e) => arrasteInicio(e, card), { passive: true });
  card.addEventListener('mousedown', (e) => arrasteInicio(e, card));

  return card;
}

// --- Arrastar-e-soltar de cartões (touch* + mouse, lógica compartilhada) ---

let arraste = null;

// Extrai {x, y, id} do evento. `alvoId` = identifier do toque a seguir (null p/ mouse).
function pontoDoEvento(e, alvoId) {
  const toques = e.changedTouches || e.touches;
  if (toques) {
    for (const t of toques) {
      if (alvoId === null || alvoId === undefined || t.identifier === alvoId) {
        return { x: t.clientX, y: t.clientY, id: t.identifier };
      }
    }
    return null;
  }
  return { x: e.clientX, y: e.clientY, id: null };
}

function arrasteInicio(e, card) {
  if (arraste) return;
  // Não iniciar arraste ao tocar no <select> ou no botão de apagar
  if (e.target.closest('select, button')) return;
  if (e.type === 'mousedown' && e.button !== 0) return;

  const p = pontoDoEvento(e, null);
  if (!p) return;

  const toque = e.type === 'touchstart';
  arraste = {
    card,
    id: card.dataset.id,
    statusOrigem: card.dataset.status,
    touchId: toque ? p.id : null,
    x0: p.x,
    y0: p.y,
    ativo: false,
    clone: null,
    offsetX: 0,
    offsetY: 0,
    colunaAlvo: null,
  };

  if (toque) {
    document.addEventListener('touchmove', arrasteMover, { passive: false });
    document.addEventListener('touchend', arrasteFim);
    document.addEventListener('touchcancel', arrasteCancelar);
  } else {
    e.preventDefault(); // evita seleção de texto do cartão
    document.addEventListener('mousemove', arrasteMover);
    document.addEventListener('mouseup', arrasteFim);
  }
}

function arrasteMover(e) {
  if (!arraste) return;
  const p = pontoDoEvento(e, arraste.touchId);
  if (!p) return;

  if (!arraste.ativo) {
    if (Math.hypot(p.x - arraste.x0, p.y - arraste.y0) < LIMIAR_ARRASTE) return;
    arrasteAtivar(p);
  }

  e.preventDefault(); // trava a rolagem durante o arraste por toque
  arraste.clone.style.left = `${p.x - arraste.offsetX}px`;
  arraste.clone.style.top = `${p.y - arraste.offsetY}px`;
  arrasteMarcarColuna(p);
}

function arrasteAtivar(p) {
  const card = arraste.card;
  const r = card.getBoundingClientRect();

  const clone = card.cloneNode(true);
  clone.classList.add('card-clone');
  clone.classList.remove('arrastando');
  clone.style.width = `${r.width}px`;
  clone.style.left = `${r.left}px`;
  clone.style.top = `${r.top}px`;
  document.body.appendChild(clone);

  arraste.clone = clone;
  arraste.offsetX = p.x - r.left;
  arraste.offsetY = p.y - r.top;
  arraste.ativo = true;
  card.classList.add('arrastando');
  document.body.classList.add('arrastando-ativo');
}

function colunaEmPonto(p) {
  const el = document.elementFromPoint(p.x, p.y);
  return el && el.closest ? el.closest('.coluna') : null;
}

function arrasteMarcarColuna(p) {
  const coluna = colunaEmPonto(p);
  if (arraste.colunaAlvo && arraste.colunaAlvo !== coluna) {
    arraste.colunaAlvo.classList.remove('drag-over');
  }
  arraste.colunaAlvo = coluna;
  if (coluna && coluna.dataset.status !== arraste.statusOrigem) {
    coluna.classList.add('drag-over');
  } else if (coluna) {
    coluna.classList.remove('drag-over');
  }
}

function arrasteFim(e) {
  if (!arraste) return;
  const ativo = arraste.ativo;
  const p = pontoDoEvento(e, arraste.touchId) || { x: arraste.x0, y: arraste.y0 };
  const coluna = ativo ? (colunaEmPonto(p) || arraste.colunaAlvo) : null;
  const { id, statusOrigem } = arraste;

  arrasteLimpar();

  if (ativo && coluna) {
    const novoStatus = coluna.dataset.status;
    if (novoStatus && novoStatus !== statusOrigem) {
      mudarStatus(id, novoStatus);
    }
  }
}

function arrasteCancelar() {
  arrasteLimpar();
}

function arrasteLimpar() {
  document.removeEventListener('touchmove', arrasteMover, { passive: false });
  document.removeEventListener('touchend', arrasteFim);
  document.removeEventListener('touchcancel', arrasteCancelar);
  document.removeEventListener('mousemove', arrasteMover);
  document.removeEventListener('mouseup', arrasteFim);

  if (arraste) {
    if (arraste.clone) arraste.clone.remove();
    if (arraste.card) arraste.card.classList.remove('arrastando');
    if (arraste.colunaAlvo) arraste.colunaAlvo.classList.remove('drag-over');
  }
  document.body.classList.remove('arrastando-ativo');
  arraste = null;
}

function formatarData(iso) {
  const [ano, mes, dia] = iso.split('-');
  if (!ano || !mes || !dia) return iso;
  return `${dia}/${mes}/${ano}`;
}

formTarefaEl.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (!projetoAtual) return;

  const titulo = tarefaTituloEl.value.trim();
  if (!titulo) return;

  try {
    await api(`/api/projetos/${projetoAtual.id}/tarefas`, {
      method: 'POST',
      body: JSON.stringify({
        titulo,
        prazo: tarefaPrazoEl.value || null,
        status: tarefaStatusEl.value,
      }),
    });
    formTarefaEl.reset();
    await carregarTarefas();
  } catch (err) {
    alert(err.message);
  }
});

async function mudarStatus(id, status) {
  try {
    await api(`/api/tarefas/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
    await carregarTarefas();
  } catch (err) {
    alert(err.message);
    await carregarTarefas();
  }
}

async function apagarTarefa(id) {
  if (!confirm('Apagar esta tarefa?')) return;
  try {
    await api(`/api/tarefas/${id}`, { method: 'DELETE' });
    await carregarTarefas();
  } catch (err) {
    alert(err.message);
  }
}

// --- Início ---
carregarProjetos().catch((err) => alert(err.message));
