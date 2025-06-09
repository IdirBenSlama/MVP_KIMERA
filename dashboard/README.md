# KIMERA SWM Dashboard

This folder contains a feature-complete React interface for interacting with the MVP prototype.

## Launching the backend

1. Install the Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Optionally configure environment variables:
   - `DATABASE_URL` – connection string for the database (defaults to the
     SQLite file `kimera_swm.db`).
   - `ENABLE_JOBS` – set to `0` to disable periodic background jobs.
3. Start the FastAPI server:
   ```bash
   uvicorn backend.api.main:app --reload
   ```

## Using the dashboard

Open `index.html` in a web browser after the server is running (on
`http://localhost:8000` by default). The dashboard provides three main views:

- **System Health** – displays metrics from `/system/status` and `/system/stability`.
- **Geoid Explorer** – search for geoids and trigger contradiction processing.
- **Vault Inspector** – lists recent scars from `vault_a` and `vault_b`.

The System Health view now includes:
- **Run Cycle** – calls `POST /system/cycle`.
The Vault Inspector provides:
- **Rebalance Vaults** – sends `POST /vaults/rebalance`.
Clicking these buttons updates the displayed metrics or scar lists automatically.

No build step is required as React is loaded from a CDN.
