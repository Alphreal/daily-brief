// PURPOSE: Postgres storage (pool + helpers). Tables: race (one row), signups.
// Learning note: same job db.js did for SQLite — now async, because network I/O
// can wait. Every helper returns a promise; callers await it.
import pg from 'pg';
import { readFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = dirname(fileURLToPath(import.meta.url));
if (existsSync(join(dir, '.env'))) {
  for (const line of readFileSync(join(dir, '.env'), 'utf8').split('\n')) {
    const m = line.match(/^\s*([A-Z_]+)=(.*)\s*$/);
    if (m && !process.env[m[1]]) process.env[m[1]] = m[2];
  }
}

export const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL,
  max: 5,
});

export const getRace = async () =>
  (await pool.query('SELECT gp, circuit, lights_out AS "lightsOut" FROM race WHERE id = 1')).rows[0];

export const setRace = (gp, circuit, lightsOut) =>
  pool.query('UPDATE race SET gp = $1, circuit = $2, lights_out = $3 WHERE id = 1', [gp, circuit, lightsOut]);

export const addSignup = async (email) => {
  try {
    const r = await pool.query('INSERT INTO signups (email) VALUES ($1) RETURNING id', [email]);
    return { id: r.rows[0].id };
  } catch (e) {
    if (e.code === '23505') return { taken: true }; // unique violation = dedupe
    throw e;
  }
};

export const listSignups = async () =>
  (await pool.query('SELECT id, email, created_at AS "createdAt" FROM signups ORDER BY id DESC')).rows;
