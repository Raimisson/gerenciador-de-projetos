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
const listaTarefasEl = document.getElementById('lista-tarefas');

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

// --- Tarefas ---

async function carregarTarefas() {
  if (!projetoAtual) return;

  const tarefas = await api(`/api/projetos/${projetoAtual.id}/tarefas`);
  listaTarefasEl.innerHTML = '';

  if (tarefas.length === 0) {
    const li = document.createElement('li');
    li.className = 'vazio';
    li.textContent = 'Nenhuma tarefa neste projeto.';
    listaTarefasEl.appendChild(li);
    return;
  }

  for (const tarefa of tarefas) {
    listaTarefasEl.appendChild(criarItemTarefa(tarefa));
  }
}

function criarItemTarefa(tarefa) {
  const li = document.createElement('li');
  li.className = 'tarefa';
  li.dataset.status = tarefa.status;

  const info = document.createElement('div');
  info.className = 'tarefa-info';

  const titulo = document.createElement('div');
  titulo.className = 'tarefa-titulo';
  titulo.textContent = tarefa.titulo;
  info.appendChild(titulo);

  if (tarefa.prazo) {
    const prazo = document.createElement('div');
    prazo.className = 'tarefa-prazo';
    prazo.textContent = `Prazo: ${formatarData(tarefa.prazo)}`;
    const hoje = new Date().toISOString().slice(0, 10);
    if (tarefa.prazo < hoje && tarefa.status !== 'concluida') {
      prazo.classList.add('atrasado');
      prazo.textContent += ' (atrasado)';
    }
    info.appendChild(prazo);
  }

  const select = document.createElement('select');
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

  li.append(info, select, btnApagar);
  return li;
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
