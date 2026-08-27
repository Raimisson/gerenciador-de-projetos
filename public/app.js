'use strict';

const STATUS_LABEL = {
  pendente: 'Pendente',
  fazendo: 'Fazendo',
  concluida: 'Concluída',
};

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
async function api(url, options = {}) {
  const resp = await fetch(url, {
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
  card.draggable = true;
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

  card.addEventListener('dragstart', (e) => {
    e.dataTransfer.setData('text/plain', String(tarefa.id));
    e.dataTransfer.effectAllowed = 'move';
    card.classList.add('arrastando');
  });
  card.addEventListener('dragend', () => card.classList.remove('arrastando'));

  return card;
}

// Listeners de drop nas colunas (fixas — registrados uma vez)
for (const status of Object.keys(dropzones)) {
  const zona = dropzones[status];
  const coluna = zona.closest('.coluna');

  zona.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    coluna.classList.add('drag-over');
  });
  zona.addEventListener('dragleave', (e) => {
    if (!zona.contains(e.relatedTarget)) coluna.classList.remove('drag-over');
  });
  zona.addEventListener('drop', (e) => {
    e.preventDefault();
    coluna.classList.remove('drag-over');
    const id = e.dataTransfer.getData('text/plain');
    if (!id) return;
    const card = kanbanEl.querySelector(`.card[data-id="${id}"]`);
    if (card && card.dataset.status === status) return; // mesma coluna
    mudarStatus(id, status);
  });
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
