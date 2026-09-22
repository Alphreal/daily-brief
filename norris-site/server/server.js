// PURPOSE: the backend. Serves the site + 4 JSON endpoints. Run: npm start (port 3000).
import express from 'express';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { getRace, setRace, addSignup, listSignups } from './db.js';

const ADMIN_KEY = process.env.ADMIN_KEY || 'dev-key-change-me';
const PORT = process.env.PORT || 3000;
const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const app = express();

app.use(express.json());
app.use(express.static(root)); // same server hosts frontend + API (no CORS needed)

const isEmail = (s) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(s || ''));
const needAdmin = (req, res, next) =>
  req.headers['x-admin-key'] === ADMIN_KEY ? next() : res.status(401).json({ error: 'admin only' });

// READ: anyone can see the next race (powers the countdown).
app.get('/api/next-race', async (req, res) => {
  res.json(await getRace());
});

// WRITE: only admin can move the calendar (change ADMIN_KEY in production!).
app.put('/api/next-race', needAdmin, async (req, res) => {
  const { gp, circuit, lightsOut } = req.body || {};
  if (!gp || !circuit || !lightsOut || Number.isNaN(Date.parse(lightsOut))) {
    return res.status(400).json({ error: 'need gp, circuit, lightsOut (ISO date)' });
  }
  await setRace(gp, circuit, lightsOut);
  res.json({ ok: true });
});

// CREATE: newsletter signup (validates + dedupes).
app.post('/api/signup', async (req, res) => {
  const email = String(req.body?.email || '').trim().toLowerCase();
  if (!isEmail(email)) return res.status(400).json({ error: 'invalid email' });
  const r = await addSignup(email);
  if (r.taken) return res.status(409).json({ error: 'already signed up' });
  res.status(201).json({ ok: true, id: r.id });
});

// READ: admin lists signups.
app.get('/api/signups', needAdmin, async (req, res) => {
  res.json(await listSignups());
});

app.listen(PORT, () => console.log(`LN4 backend on http://localhost:${PORT}`));
