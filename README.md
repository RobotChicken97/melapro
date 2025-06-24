# Melapro Inventory System

This repository contains a minimal offline-first inventory management MVP built with Flask and React.

## Prerequisites

- Python 3.11+
- Node.js 18+

## Backend Setup

Install Python dependencies and run the API:

```bash
pip install -r requirements.txt
python app.py
```

The API will start on `http://localhost:5000`.

## Frontend Setup

Install Node dependencies and start the dev server:

```bash
npm install
npm run dev
```

The Vite dev server runs on `http://localhost:5173`.

Build a production bundle with:

```bash
npm run build
```

## Docker Setup

To run the entire stack using Docker:

```bash
make up
```

The frontend will be available at `http://localhost:3000` and the backend API at `http://localhost:5000`.

## Project Structure

- `src/` – React source code
- `public/` – static assets and service worker
- `app.py` – Flask API entry point

## Running Tests

Lint the project and run unit tests with coverage:

```bash
npm run lint
npm run test:unit
```

