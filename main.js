'use strict';

const path = require('path');
const http = require('http');
const { fork } = require('child_process');
const { app, BrowserWindow, shell } = require('electron');

app.setName('Gerenciador de Projetos');

const URL_APP = 'http://localhost:3000';

let servidor = null;
let janela = null;

// Inicia o server.js como processo filho, com o caminho do banco na pasta de
// dados do usuário (gravável — ao contrário do diretório do app empacotado).
function iniciarServidor() {
  const dbPath = path.join(app.getPath('userData'), 'banco.db');
  servidor = fork(path.join(__dirname, 'server.js'), [], {
    env: { ...process.env, DB_PATH: dbPath },
    stdio: 'inherit',
  });
  servidor.on('exit', (code) => {
    console.log(`[main] server.js encerrou (code ${code})`);
    servidor = null;
  });
}

function pararServidor() {
  if (servidor) {
    servidor.kill();
    servidor = null;
  }
}

// Espera o servidor aceitar conexões, tentando de novo enquanto não estiver pronto.
function esperarServidor(url, { tentativas = 40, intervalo = 250 } = {}) {
  return new Promise((resolve, reject) => {
    let n = 0;

    const tentar = () => {
      const req = http.get(url, (res) => {
        res.resume();
        resolve();
      });
      req.on('error', () => {
        n += 1;
        if (n >= tentativas) {
          reject(new Error(`servidor não respondeu após ${tentativas} tentativas`));
        } else {
          setTimeout(tentar, intervalo);
        }
      });
    };

    tentar();
  });
}

async function criarJanela() {
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

  // Links externos vão para o navegador do sistema.
  janela.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Reforço do retry: se a página falhar ao carregar, tenta de novo.
  janela.webContents.on('did-fail-load', (_e, code, desc, urlQueFalhou) => {
    if (urlQueFalhou && urlQueFalhou.startsWith(URL_APP)) {
      console.log(`[main] did-fail-load (${code} ${desc}); nova tentativa em 500ms`);
      setTimeout(() => janela && janela.loadURL(URL_APP), 500);
    }
  });

  janela.on('closed', () => {
    janela = null;
  });

  try {
    await esperarServidor(URL_APP);
  } catch (err) {
    console.error(`[main] ${err.message} — carregando mesmo assim`);
  }

  await janela.loadURL(URL_APP);
}

app.whenReady().then(() => {
  iniciarServidor();
  criarJanela();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) criarJanela();
  });
});

app.on('window-all-closed', () => {
  pararServidor();
  app.quit();
});

app.on('quit', pararServidor);
