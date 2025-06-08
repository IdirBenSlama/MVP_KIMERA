# KIMERA SWM Dashboard

This folder contains a minimal React dashboard for interacting with the MVP API.

Open `index.html` in a web browser while the FastAPI server is running
(on `http://localhost:8000` by default). The dashboard provides three main views:

- **System Health** – displays metrics from `/system/status` and `/system/stability`.
- **Geoid Explorer** – search for geoids and trigger contradiction processing.
- **Vault Inspector** – lists recent scars from `vault_a` and `vault_b`.

No build step is required as React is loaded from a CDN.
