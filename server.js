'use strict';

const path = require('path');
const express = require('express');
const projetosDB = require('./db');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// Serve o frontend (public/index.html em "/") na mesma porta da API -> sem CORS.
app.use(express.static(path.join(__dirname, 'public')));

// ------------------------------------------------------------------
// /api/projetos
// ------------------------------------------------------------------

app.get('/api/projetos', (req, res) => {
  res.json(projetosDB.listarProjetos());
});

app.post('/api/projetos', (req, res) => {
  const { nome, descricao } = req.body || {};

  if (typeof nome !== 'string' || nome.trim() === '') {
    return res.status(400).json({ erro: 'O campo "nome" é obrigatório.' });
  }

  const projeto = projetosDB.criarProjeto({
    nome: nome.trim(),
    descricao: typeof descricao === 'string' ? descricao.trim() : null,
  });
  res.status(201).json(projeto);
});

// ------------------------------------------------------------------
// /api/projetos/:id/tarefas
// ------------------------------------------------------------------

app.get('/api/projetos/:id/tarefas', (req, res) => {
  const projetoId = Number(req.params.id);
  if (!Number.isInteger(projetoId)) {
    return res.status(400).json({ erro: 'ID de projeto inválido.' });
  }

  if (!projetosDB.buscarProjeto(projetoId)) {
    return res.status(404).json({ erro: 'Projeto não encontrado.' });
  }

  res.json(projetosDB.listarTarefas(projetoId));
});

app.post('/api/projetos/:id/tarefas', (req, res) => {
  const projetoId = Number(req.params.id);
  if (!Number.isInteger(projetoId)) {
    return res.status(400).json({ erro: 'ID de projeto inválido.' });
  }

  if (!projetosDB.buscarProjeto(projetoId)) {
    return res.status(404).json({ erro: 'Projeto não encontrado.' });
  }

  const { titulo, status, prazo } = req.body || {};

  if (typeof titulo !== 'string' || titulo.trim() === '') {
    return res.status(400).json({ erro: 'O campo "titulo" é obrigatório.' });
  }

  if (status !== undefined && !projetosDB.STATUS_VALIDOS.includes(status)) {
    return res.status(400).json({
      erro: `Status inválido. Use um de: ${projetosDB.STATUS_VALIDOS.join(', ')}.`,
    });
  }

  const tarefa = projetosDB.criarTarefa(projetoId, {
    titulo: titulo.trim(),
    status,
    prazo: typeof prazo === 'string' ? prazo.trim() : null,
  });
  res.status(201).json(tarefa);
});

// ------------------------------------------------------------------
// /api/tarefas/:id
// ------------------------------------------------------------------

app.put('/api/tarefas/:id', (req, res) => {
  const tarefaId = Number(req.params.id);
  if (!Number.isInteger(tarefaId)) {
    return res.status(400).json({ erro: 'ID de tarefa inválido.' });
  }

  const { titulo, status, prazo } = req.body || {};
  const campos = {};

  if (titulo !== undefined) {
    if (typeof titulo !== 'string' || titulo.trim() === '') {
      return res.status(400).json({ erro: 'O campo "titulo" não pode ser vazio.' });
    }
    campos.titulo = titulo.trim();
  }

  if (status !== undefined) {
    if (!projetosDB.STATUS_VALIDOS.includes(status)) {
      return res.status(400).json({
        erro: `Status inválido. Use um de: ${projetosDB.STATUS_VALIDOS.join(', ')}.`,
      });
    }
    campos.status = status;
  }

  if (prazo !== undefined) {
    campos.prazo = typeof prazo === 'string' ? prazo.trim() : null;
  }

  if (Object.keys(campos).length === 0) {
    return res.status(400).json({ erro: 'Nenhum campo para atualizar.' });
  }

  const tarefa = projetosDB.atualizarTarefa(tarefaId, campos);
  if (!tarefa) {
    return res.status(404).json({ erro: 'Tarefa não encontrada.' });
  }
  res.json(tarefa);
});

app.delete('/api/tarefas/:id', (req, res) => {
  const tarefaId = Number(req.params.id);
  if (!Number.isInteger(tarefaId)) {
    return res.status(400).json({ erro: 'ID de tarefa inválido.' });
  }

  const ok = projetosDB.deletarTarefa(tarefaId);
  if (!ok) {
    return res.status(404).json({ erro: 'Tarefa não encontrada.' });
  }
  res.status(204).end();
});

// ------------------------------------------------------------------

app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});
