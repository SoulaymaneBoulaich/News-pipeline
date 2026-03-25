"""
Phase 3 — Serve It with FastAPI
Run locally:  uvicorn api.main:app --reload
Docs UI:      http://127.0.0.1:8000/docs
"""
from scalar_fastapi import get_scalar_api_reference
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
from db.database import get_connection

app = FastAPI(
    title="News Pipeline API",
    description="Query headlines collected by the automated news pipeline.",
    version="1.0.0",
)


# ── Response schema ──────────────────────────────────────────────────────────
class Article(BaseModel):
    id:           int
    source:       Optional[str]
    author:       Optional[str]
    title:        str
    description:  Optional[str]
    url:          str
    published_at: Optional[str]
    category:     Optional[str]
    fetched_at:   Optional[str]


# ── Helpers ──────────────────────────────────────────────────────────────────
def query_db(sql: str, params: tuple = ()) -> list[dict]:
    conn   = get_connection()
    conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
    cursor = conn.cursor()
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "News Pipeline API is running"}


@app.get("/articles", response_model=list[Article], tags=["Articles"])
def get_articles(
    category: Optional[str] = Query(None, description="Filter by category: technology, business, science, health"),
    source:   Optional[str] = Query(None, description="Filter by source name (partial match)"),
    limit:    int           = Query(20, ge=1, le=100, description="Number of results (max 100)"),
    offset:   int           = Query(0, ge=0, description="Pagination offset"),
):
    """Return a paginated list of articles, optionally filtered."""
    sql    = "SELECT * FROM articles WHERE 1=1"
    params = []

    if category:
        sql += " AND category = ?"
        params.append(category)
    if source:
        sql += " AND source LIKE ?"
        params.append(f"%{source}%")

    sql += " ORDER BY published_at DESC LIMIT ? OFFSET ?"
    params += [limit, offset]

    rows = query_db(sql, tuple(params))
    return rows


@app.get("/articles/{article_id}", response_model=Article, tags=["Articles"])
def get_article(article_id: int):
    """Return a single article by ID."""
    rows = query_db("SELECT * FROM articles WHERE id = ?", (article_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Article not found.")
    return rows[0]


@app.get("/categories", tags=["Stats"])
def get_categories():
    """List all available categories and their article counts."""
    rows = query_db("""
        SELECT category, COUNT(*) as total
        FROM articles
        GROUP BY category
        ORDER BY total DESC
    """)
    return rows


@app.get("/stats", tags=["Stats"])
def get_stats():
    """High-level stats about the pipeline database."""
    total    = query_db("SELECT COUNT(*) as count FROM articles")[0]["count"]
    sources  = query_db("SELECT COUNT(DISTINCT source) as count FROM articles")[0]["count"]
    latest   = query_db("SELECT MAX(fetched_at) as latest FROM articles")[0]["latest"]
    return {
        "total_articles": total,
        "unique_sources": sources,
        "last_ingestion": latest,
    }


@app.get("/search", response_model=list[Article], tags=["Articles"])
def search_articles(
    q:     str = Query(..., min_length=2, description="Keyword to search in title/description"),
    limit: int = Query(20, ge=1, le=100),
):
    """Full-text keyword search across title and description."""
    rows = query_db("""
        SELECT * FROM articles
        WHERE title LIKE ? OR description LIKE ?
        ORDER BY published_at DESC
        LIMIT ?
    """, (f"%{q}%", f"%{q}%", limit))
    return rows

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar Documentation"
    )