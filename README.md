# 📰 News Data Pipeline

An end-to-end automated data pipeline that ingests top news headlines, cleans them, stores them in a database, and serves them via a REST API.

Built with: **Python · Pandas · Prefect · FastAPI · SQLite · Docker**

---

## 🏗️ Architecture

```
NewsAPI ──► fetch_news.py ──► Pandas cleaning ──► SQLite DB ──► FastAPI
                ▲
         Prefect (hourly schedule)
```

---

## 📁 Project Structure

```
news-pipeline/
├── ingestion/
│   └── fetch_news.py       # Phase 1: Fetch, clean, store
├── pipeline/
│   └── flow.py             # Phase 2: Prefect automation
├── api/
│   └── main.py             # Phase 3: FastAPI endpoints
├── db/
│   └── database.py         # SQLite connection & schema
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone & install

```bash
git clone https://github.com/SoulaymaneBoulaich/news-pipeline.git
cd news-pipeline
pip install -r requirements.txt
```

### 2. Set your API key

Get a free key at [newsapi.org](https://newsapi.org)

```bash
export NEWSAPI_KEY=your_key_here
```

Or create a `.env` file:
```
NEWSAPI_KEY=your_key_here
```

### 3. Run Phase 1 — ingest data once

```bash
python ingestion/fetch_news.py
```

### 4. Run Phase 2 — automated pipeline

```bash
python pipeline/flow.py
```

### 5. Run Phase 3 — start the API

```bash
uvicorn api.main:app --reload
```

Visit **http://127.0.0.1:8000/docs** for the interactive API docs.

---

## 🐳 Run with Docker

```bash
docker-compose up --build
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/articles` | List articles (filter by category, source) |
| GET | `/articles/{id}` | Get single article |
| GET | `/search?q=keyword` | Full-text search |
| GET | `/categories` | Article counts per category |
| GET | `/stats` | Pipeline stats |

### Example request

```bash
curl "http://localhost:8000/articles?category=technology&limit=5"
```

---

## 🚀 Deploy (free)

1. Push to GitHub
2. Connect repo to [Render](https://render.com) or [Railway](https://railway.app)
3. Set `NEWSAPI_KEY` as an environment variable
4. Deploy — your API will be live at a public URL

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| NewsAPI | Data source |
| Pandas | Data cleaning & transformation |
| SQLite | Local database storage |
| Prefect | Pipeline orchestration & scheduling |
| FastAPI | REST API layer |
| Docker | Containerization |

---

## 📈 Future Improvements

- [ ] Migrate from SQLite to PostgreSQL
- [ ] Add sentiment analysis on headlines (NLP layer)
- [ ] Build a live dashboard with Streamlit
- [ ] Add Elasticsearch for better full-text search
- [ ] Deploy Prefect to Prefect Cloud for managed scheduling

---

## 👤 Author

Made by [Soulaymane](https://github.com/SoulaymaneBoualich) — Big Data & AI Engineering Student
