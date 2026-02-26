# Integration Visualizer

A web tool for computing and visualizing integrals — from basic definite integrals to surface integrals and flux. Built for exploring vector calculus interactively.

[**Live Demo**](https://erikloffelholz.github.io/integration-visualizer/) · [API Docs (local)](http://localhost:8000/api/docs)

## What it does

- Computes single, double, triple, line, surface, and flux integrals
- Symbolic solutions (SymPy), numerical quadrature (SciPy), Monte Carlo for 3D (PyTorch)
- Interactive 3D visualization with Three.js — surfaces, vector fields, integration regions
- Vector operations: gradient, divergence, curl
- Theorem verification: Green's, Stokes', Divergence
- Step-by-step solutions for 1D integrals
- MessagePack binary protocol for fast client-server communication

## Stack

**Frontend:** React 19, Vite, Three.js
**Backend:** FastAPI, SymPy, SciPy, PyTorch
**Protocol:** MessagePack

## Setup

Needs Python 3.10+ and Node.js 20+.

```bash
./setup.sh        # install everything
./run.sh          # start frontend (:3000) + backend (:8000)
```

Or with Docker:

```bash
docker compose up --build    # runs at localhost:8000
```

## Project layout

```
backend/
  app.py               # FastAPI endpoints (msgpack)
  parsers.py            # expression parsing + validation
  integrators/          # 1D, 2D, 3D, line, surface, flux, vector ops
  visualizers/          # curve, surface, and vector field data gen
  theorems/             # Green's, Stokes', Divergence verification
  tests/                # pytest suite
src/
  App.jsx               # main UI
  components/           # input fields, results, 3D views
  utils/api.js          # msgpack API client
```

## API

All POST endpoints use MessagePack (`application/x-msgpack`). JSON request bodies also accepted.

**Integrals:** `POST /api/integrate/1d` · `2d` · `3d` · `line/scalar` · `line/vector` · `surface/scalar` · `flux`

**Vector calculus:** `POST /api/vector/operations` · `/api/visualize/vector_field` · `/api/theorem/greens` · `stokes` · `divergence`

**Other:** `POST /api/physics/field_lines` · `equipotential` · `export/latex` · `GET /api/examples` · `health`

## Config

Set via environment variables (see `.env.example`):

- `APP_PORT` (default `8000`) — server port
- `APP_HOST` (default `0.0.0.0`) — bind address
- `CORS_ORIGINS` (default `*`) — allowed origins
- `MAX_MONTE_CARLO_SAMPLES` (default `100000`)
- `RATE_LIMIT_PER_MINUTE` (default `60`)

## Testing

```bash
cd backend && python -m pytest tests/ -v    # backend
npm run build                                # frontend
```

## License

MIT — see [LICENSE](LICENSE)
