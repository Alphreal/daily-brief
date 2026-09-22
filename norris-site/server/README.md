# LN4 backend — run it

Postgres first (portable install, no admin needed):

```sh
# start server (data dir keeps everything)
pg_ctl -D C:\Users\ADMIN\Tools\pgsql\data -l C:\Users\ADMIN\Tools\pgsql\logfile -o "-p 5433" start
```

Then the app:

```sh
cd norris-site/server
npm install   # once (express + pg driver)
node migrate.js   # once (creates ln4db + tables + seed)
npm start     # http://localhost:3000 (serves site + API, no CORS needed)
```

Try it:

```sh
curl http://localhost:3000/api/next-race
curl -X POST http://localhost:3000/api/signup -H "Content-Type: application/json" -d "{\"email\":\"you@fast.com\"}"
curl http://localhost:3000/api/signups -H "x-admin-key: dev-key-change-me"
curl -X PUT http://localhost:3000/api/next-race -H "Content-Type: application/json" -H "x-admin-key: dev-key-change-me" -d "{\"gp\":\"Singapore GP\",\"circuit\":\"Marina Bay\",\"lightsOut\":\"2026-10-11T12:00:00Z\"}"
```

Data lives in `ln4.db` (gitignored in real projects). Change `ADMIN_KEY` via environment in production.
