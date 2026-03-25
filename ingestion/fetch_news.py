import requests
import pandas as pd
import sqlite3
import os
from datetime import datetime
from db.database import get_connection, init_db

# ── CONFIG ──────────────────────────────────────────────────────────────────
API_KEY  = os.getenv("NEWSAPI_KEY", "Your_API_KEY_Here")  # set as env variable
BASE_URL = "https://newsapi.org/v2/top-headlines"
CATEGORY = "technology"   # change to: business | sports | science | health
COUNTRY  = "us"
PAGE_SIZE = 20
# ────────────────────────────────────────────────────────────────────────────


def fetch_articles(category: str = CATEGORY) -> list[dict]:
    """Fetch raw articles from NewsAPI."""
    params = {
        "apiKey":   API_KEY,
        "country":  COUNTRY,
        "category": category,
        "pageSize": PAGE_SIZE,
    }
    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if data.get("status") != "ok":
        raise ValueError(f"NewsAPI error: {data.get('message')}")

    print(f"✅ Fetched {len(data['articles'])} raw articles.")
    return data["articles"]


def clean_articles(raw: list[dict], category: str = CATEGORY) -> pd.DataFrame:
    """Normalize and clean the raw article list into a DataFrame."""
    df = pd.DataFrame(raw)

    # Flatten nested 'source' dict → just the name
    df["source"] = df["source"].apply(
        lambda s: s.get("name", "Unknown") if isinstance(s, dict) else "Unknown"
    )

    # Keep only the columns we care about
    df = df[["source", "author", "title", "description", "url", "publishedAt"]]
    df = df.rename(columns={"publishedAt": "published_at"})

    # Drop rows with no title or no url (unusable)
    df = df.dropna(subset=["title", "url"])

    # Strip whitespace from text fields
    for col in ["title", "description", "author"]:
        df[col] = df[col].astype(str).str.strip()

    # Replace literal "None" strings with actual None
    df = df.replace("None", None)

    # Normalize datetime format
    df["published_at"] = pd.to_datetime(
        df["published_at"], errors="coerce"
    ).dt.strftime("%Y-%m-%d %H:%M:%S")

    # Add the category tag
    df["category"] = category

    # Remove duplicates within this batch
    df = df.drop_duplicates(subset=["title"])

    print(f"✅ Cleaned down to {len(df)} valid articles.")
    return df


def store_articles(df: pd.DataFrame) -> int:
    """Insert articles into SQLite, skipping duplicates by title."""
    conn = get_connection()
    cursor = conn.cursor()

    inserted = 0
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO articles (source, author, title, description, url, published_at, category)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                row["source"], row["author"], row["title"],
                row["description"], row["url"],
                row["published_at"], row["category"]
            ))
            inserted += 1
        except sqlite3.IntegrityError:
            # Title already exists → skip duplicate
            pass

    conn.commit()
    conn.close()
    print(f"✅ Stored {inserted} new articles (duplicates skipped).")
    return inserted


def run_ingestion(category: str = CATEGORY):
    """Full Phase 1 pipeline: fetch → clean → store."""
    print(f"\n{'='*50}")
    print(f"  Running ingestion  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    init_db()
    raw      = fetch_articles(category)
    cleaned  = clean_articles(raw, category)
    inserted = store_articles(cleaned)

    print(f"\n🏁 Done. {inserted} new articles added to the database.\n")
    return inserted


if __name__ == "__main__":
    run_ingestion()
