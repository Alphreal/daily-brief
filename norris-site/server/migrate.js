// One-time migration: creates ln4db + tables + seed. Run: node migrate.js
// Reads connection from .env (DATABASE_URL points at the server, not the db).
import pg from 'pg';
import { readFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = dirname(fileURLToPath(import.meta.url));
if (existsSync(join(dir, '.env'))) {
  for (const line of readFileSync(join(dir, '.env'), 'utf8').split('\n')) {
    const m = line.match(/^\s*([A-Z_]+)=(.*)\s*$/);
    if (m) process.env[m[1]] = m[2];
  }
}
const admin = new pg.Client({ connectionString: process.env.DATABASE_URL.replace(/\/ln4db$/, '/postgres') });
await admin.connect();
await admin.query('CREATE DATABASE ln4db').catch((e) => {
  if (e.code !== '42P04') throw e; // already exists = fine
  console.log('ln4db already exists');
});
await admin.end();

const db = new pg.Client({ connectionString: process.env.DATABASE_URL });
await db.connect();
await db.query(`CREATE TABLE IF NOT EXISTS race (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    gp TEXT NOT NULL,
    circuit TEXT NOT NULL,
    lights_out TEXT NOT NULL
  )`);
await db.query(`CREATE TABLE IF NOT EXISTS signups (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
  )`);
await db.query(`INSERT INTO race (id, gp, circuit, lights_out)
  VALUES (1, 'Azerbaijan GP', 'Baku City Circuit', '2026-09-26T07:00:00Z')
  ON CONFLICT (id) DO NOTHING`);
await db.end();
console.log('migrated: ln4db ready');
