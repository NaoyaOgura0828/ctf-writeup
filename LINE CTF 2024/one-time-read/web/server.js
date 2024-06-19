const express = require('express');
const morgan = require('morgan');
const fs = require('fs');
const uuid = require('uuid');
const md5 = require('md5');
const session = require('express-session');
const crypto = require('crypto');

const PORT = 80;
const HOST = '0.0.0.0';
const REGEX = /^[a-zA-Z0-9-]*$/;
const BUSINESS_NAME = process.env.BUSINESS_NAME || '';
const DOMAIN_SUFFIX = process.env.DOMAIN_SUFFIX || '';
const DOMAIN = BUSINESS_NAME + DOMAIN_SUFFIX;

const app = express();
app.use(session({
  secret: crypto.randomBytes(20).toString("hex"),
  cookie: {}
}));
app.set('view engine', 'ejs');
app.use(express.urlencoded({extended: false}));
app.use(morgan('combined'));

app.use('/public', function (req, res, next) { 
  res.sendFile(__dirname + '/public' + decodeURIComponent(req.path), { root: '/' });
});

app.get('/', (req, res) => { return res.redirect('/write'); });

app.get('/content', (req, res) => { return res.render('content.ejs'); });

app.get('/write', (req, res) => { 
  req.session.csrfToken = crypto.randomBytes(20).toString("hex");
  return res.render('write.ejs', { csrfToken: req.session.csrfToken }); 
});

app.post('/write', (req, res) => {
  let { passCode, content, csrfToken } = req.body;
  if (!req.session.csrfToken || !csrfToken || req.session.csrfToken !== csrfToken) {
    req.session.csrfToken = crypto.randomBytes(20).toString("hex");
    return res.redirect('/');
  }
  req.session.csrfToken = crypto.randomBytes(20).toString("hex");
  if (typeof passCode === 'string' && typeof content === 'string') {
    let noteId = uuid.v4();
    let noteDir = 'notes/' + noteId;
    try {
      if (!fs.existsSync(noteDir)) fs.mkdirSync(noteDir);
      fs.writeFileSync(noteDir + '/' + md5(passCode).substring(10), content);
      res.cookie('noteId', noteId, {
        domain: DOMAIN,
        httpOnly: false
      });
      return res.render('success.ejs');
    } catch {
      return res.send('<script>alert("Write note failed")</script>');
    }
  }
  return res.redirect('/');
});

app.get('/read/:noteId', (req, res) => {
  let noteId = req.params.noteId;
  if (typeof noteId === 'string' && REGEX.test(noteId)) return res.render('read.ejs', { noteId: noteId });
  return res.redirect('/');
});

app.get('/read', (req, res) => {
  if (!req.headers['x-ctf-from']) return res.redirect('/');
  let { passCode, noteId, next } = req.query;
  if (typeof passCode === 'string' && typeof noteId === 'string' && REGEX.test(noteId)) {
    if (!next) next = '/content';
    try {
      let noteDir = 'notes/' + noteId;
      let notePath = noteDir + '/' + md5(passCode).substring(10);
      if (fs.existsSync(notePath)) {
        let content = fs.readFileSync(notePath);
        fs.rmSync(noteDir + '/', { recursive: true, force: true });
        return res.redirect(next + `?content=` + encodeURIComponent(content));
      } else {
        if (fs.existsSync(noteDir)) fs.rmSync(noteDir + '/', { recursive: true, force: true });
        return res.send('<script>alert("Read note failed")</script>');
      }
    } catch {
      return res.send('<script>alert("Read note failed")</script>');
    }
  }
  return res.redirect('/');
});

app.listen(PORT, HOST, async () => {
  if (fs.existsSync('notes/')) fs.rmSync('notes/', { recursive: true, force: true });
  fs.mkdirSync('notes/');
  console.log(`Running on http://${HOST}:${PORT}`);
});