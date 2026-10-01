// Zero-dependency static server for local development: `npm run dev`.
// Serves this folder at http://localhost:5173 (or the next free port).
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { extname, join, normalize, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(fileURLToPath(new URL('.', import.meta.url)));
const START_PORT = Number(process.env.PORT) || 5173;

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.woff2': 'font/woff2',
};

const server = createServer(async (req, res) => {
  try {
    let path = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    if (path.endsWith('/')) path += 'index.html';

    const file = normalize(join(ROOT, path));
    if (file !== ROOT && !file.startsWith(ROOT + sep)) return send(res, 403, 'Forbidden');

    const info = await stat(file).catch(() => null);
    if (!info || !info.isFile()) return send(res, 404, 'Not found: ' + path);

    res.writeHead(200, {
      'Content-Type': TYPES[extname(file).toLowerCase()] || 'application/octet-stream',
      'Cache-Control': 'no-store',
    });
    res.end(await readFile(file));
  } catch (err) {
    send(res, 500, 'Server error');
    console.error(err);
  }
});

function send(res, status, text) {
  res.writeHead(status, { 'Content-Type': 'text/plain; charset=utf-8' });
  res.end(text);
}

function listen(port) {
  server.once('error', (err) => {
    if (err.code === 'EADDRINUSE' && port < START_PORT + 20) {
      console.log(`Port ${port} is busy, trying ${port + 1}…`);
      listen(port + 1);
    } else {
      throw err;
    }
  });
  server.listen(port, () => {
    console.log(`\n  Opulence dev server running at http://localhost:${port}/\n  Press Ctrl+C to stop.\n`);
  });
}

listen(START_PORT);
