'use strict';

const path = require('path');
const { app, BrowserWindow, shell } = require('electron');

// O banco vai para uma pasta gravável do usuário — dentro do pacote (asar) o
// diretório do app é somente leitura. `db.js` lê esta variável.
process.env.BANCO_DB = path.join(app.getPath('userData'), 'banco.db');

const { iniciar } = require('../server');

let janela = null;
let servidor = null;

async function criarJanela() {
  // Porta 0: o SO escolhe uma livre, evitando colisão com outro serviço na 3000.
  const { server, port } = await iniciar(0);
  servidor = server;

  janela = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    title: 'Gerenciador de Projetos',
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  janela.removeMenu();

  // Links externos abrem no navegador do sistema, não numa janela do app.
  janela.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  await janela.loadURL(`http://localhost:${port}`);

  janela.on('closed', () => {
    janela = null;
  });
}

app.whenReady().then(criarJanela);

app.on('window-all-closed', () => {
  if (servidor) servidor.close();
  app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) criarJanela();
});
