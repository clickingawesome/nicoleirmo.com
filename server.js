// Minimal static server for nicoleirmo.com (no dependencies).
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = __dirname, PORT = process.env.PORT || 3000;
const TYPES = {'.html':'text/html; charset=utf-8','.css':'text/css','.js':'application/javascript','.json':'application/json','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml','.mp4':'video/mp4','.webm':'video/webm','.xml':'application/xml','.txt':'text/plain; charset=utf-8','.ico':'image/x-icon'};
const REDIRECTS = {'/cv':'/resume/','/resume':'/resume/','/results':'/#/results','/contact':'/#/contact'};
http.createServer((req, res) => {
  let url = decodeURIComponent(req.url.split('?')[0]);
  if (REDIRECTS[url]) { res.writeHead(301, {Location: REDIRECTS[url]}); return res.end(); }
  if (url.endsWith('/')) url += 'index.html';
  let file = path.normalize(path.join(ROOT, url));
  if (!file.startsWith(ROOT)) { res.writeHead(403); return res.end(); }
  fs.stat(file, (err, st) => {
    if (!err && st.isDirectory()) { res.writeHead(301, {Location: url + '/'}); return res.end(); }
    if (err) { file = path.join(ROOT, 'index.html'); }
    const ext = path.extname(file).toLowerCase();
    const headers = {'Content-Type': TYPES[ext] || 'application/octet-stream', 'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'SAMEORIGIN'};
    headers['Cache-Control'] = ext === '.html' ? 'public, max-age=0, must-revalidate' : 'public, max-age=31536000, immutable';
    res.writeHead(err ? 404 : 200, headers);
    fs.createReadStream(file).pipe(res);
  });
}).listen(PORT, () => console.log('nicoleirmo.com on :' + PORT));
