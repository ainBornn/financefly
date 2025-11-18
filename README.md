# Financefly Connector

Deploy instructions for Railway (and quick local notes).

## Summary

This repository contains a Streamlit app that uses Pluggy and a Postgres DB to save client connections.

## Quick notes before deploy
- The app requires the following environment variables (set these in Railway Secrets / Environment):
  - `PLUGGY_CLIENT_ID` (string)
  - `PLUGGY_CLIENT_SECRET` (string)
  - `DB_HOST` (Postgres host)
  - `DB_PORT` (Postgres port, e.g. `5432`)
  - `DB_USER` (Postgres user)
  - `DB_PASSWORD` (Postgres password)
  - `DB_NAME` (Postgres database name)
  - `DB_SSLMODE` (optional, default `require`)

## Deploy on Railway (recommended)
1. Create a new Railway project and choose **Deploy from GitHub**.
2. Connect your GitHub account and select the repository `ainBornn/financefly` (branch `main`).
3. Railway will detect the `Dockerfile` and build the image. The `Dockerfile` installs the native libs required by Pillow and `psycopg`.
4. In the Railway project, open the **Variables / Environment** section and add the variables listed above.
5. Trigger a deploy. Monitor the build logs — if you see `Building wheel for pillow`, the Dockerfile's system packages should prevent compilation errors (zlib, libjpeg headers are installed).

Notes:
- The Dockerfile uses `ENV PORT=8501` and runs Streamlit with `--server.port ${PORT}` so Railway can provide the port via `$PORT`.
- If you prefer to let Railway use a start command, you can set the `Start Command` to:
  `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`

## Troubleshooting
- If build fails with Pillow zlib errors, confirm the build logs show the `apt-get install` step ran successfully. The Dockerfile already includes `zlib1g-dev` and image should build on Railway.
- If the app starts but shows warnings in the UI about missing secrets, confirm those env vars are set in Railway and redeploy.

## Local testing
- To build the Docker image locally (requires Docker installed and running):
```
docker build -t connectormain:latest .
docker run --rm -p 8501:8501 -e PORT=8501 connectormain:latest
```

## Contact
If you want I can (a) help set the env vars in Railway step-by-step, (b) modify Dockerfile further, or (c) add CI.
