'use strict';

const path = require('path');
const Database = require('better-sqlite3');

const db = new Database(path.join(__dirname, 'banco.db'));

// Necessário para o ON DELETE CASCADE das tarefas funcionar.
db.pragma('foreign_keys = ON');

db.exec(`
  CREATE TABLE IF NOT EXISTS projetos (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nome      TEXT NOT NULL,
    descricao TEXT
  );

  CREATE TABLE IF NOT EXISTS tarefas (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    projeto_id INTEGER NOT NULL REFERENCES projetos(id) ON DELETE CASCADE,
    titulo     TEXT NOT NULL,
    status     TEXT NOT NULL DEFAULT 'pendente'
               CHECK (status IN ('pendente', 'fazendo', 'concluida')),
    prazo      TEXT
  );
`);

const STATUS_VALIDOS = ['pendente', 'fazendo', 'concluida'];

// --- Statements preparados ---

const stmts = {
  listarProjetos: db.prepare('SELECT id, nome, descricao FROM projetos ORDER BY id'),
  buscarProjeto: db.prepare('SELECT id, nome, descricao FROM projetos WHERE id = ?'),
  inserirProjeto: db.prepare('INSERT INTO projetos (nome, descricao) VALUES (@nome, @descricao)'),

  listarTarefas: db.prepare(
    'SELECT id, projeto_id, titulo, status, prazo FROM tarefas WHERE projeto_id = ? ORDER BY id'
  ),
  buscarTarefa: db.prepare(
    'SELECT id, projeto_id, titulo, status, prazo FROM tarefas WHERE id = ?'
  ),
  inserirTarefa: db.prepare(
    `INSERT INTO tarefas (projeto_id, titulo, status, prazo)
     VALUES (@projeto_id, @titulo, @status, @prazo)`
  ),
  atualizarTarefa: db.prepare(
    `UPDATE tarefas
        SET titulo = @titulo, status = @status, prazo = @prazo
      WHERE id = @id`
  ),
  deletarTarefa: db.prepare('DELETE FROM tarefas WHERE id = ?'),
};

// --- API de acesso ---

function listarProjetos() {
  return stmts.listarProjetos.all();
}

function buscarProjeto(id) {
  return stmts.buscarProjeto.get(id);
}

function criarProjeto({ nome, descricao }) {
  const info = stmts.inserirProjeto.run({
    nome,
    descricao: descricao ?? null,
  });
  return stmts.buscarProjeto.get(info.lastInsertRowid);
}

function listarTarefas(projetoId) {
  return stmts.listarTarefas.all(projetoId);
}

function buscarTarefa(id) {
  return stmts.buscarTarefa.get(id);
}

function criarTarefa(projetoId, { titulo, status, prazo }) {
  const info = stmts.inserirTarefa.run({
    projeto_id: projetoId,
    titulo,
    status: status || 'pendente',
    prazo: prazo || null,
  });
  return stmts.buscarTarefa.get(info.lastInsertRowid);
}

function atualizarTarefa(id, campos) {
  const atual = stmts.buscarTarefa.get(id);
  if (!atual) return null;

  const atualizada = {
    id,
    titulo: campos.titulo !== undefined ? campos.titulo : atual.titulo,
    status: campos.status !== undefined ? campos.status : atual.status,
    prazo: campos.prazo !== undefined ? (campos.prazo || null) : atual.prazo,
  };

  stmts.atualizarTarefa.run(atualizada);
  return stmts.buscarTarefa.get(id);
}

function deletarTarefa(id) {
  const info = stmts.deletarTarefa.run(id);
  return info.changes > 0;
}

module.exports = {
  db,
  STATUS_VALIDOS,
  listarProjetos,
  buscarProjeto,
  criarProjeto,
  listarTarefas,
  buscarTarefa,
  criarTarefa,
  atualizarTarefa,
  deletarTarefa,
};
