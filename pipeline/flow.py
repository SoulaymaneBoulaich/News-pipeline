"""
Phase 2 — Automation with Prefect
Run once:     python pipeline/flow.py
Schedule it:  prefect deployment build pipeline/flow.py:news_pipeline_flow
              then serve or deploy to Prefect Cloud
"""

from prefect import flow, task
from ingestion.fetch_news import fetch_articles, clean_articles, store_articles
from db.database import init_db


CATEGORIES = ["technology", "business", "science", "health"]


@task(name="initialize-database", retries=1)
def task_init_db():
    init_db()


@task(name="fetch-articles", retries=3, retry_delay_seconds=30)
def task_fetch(category: str):
    return fetch_articles(category)


@task(name="clean-articles")
def task_clean(raw: list, category: str):
    return clean_articles(raw, category)


@task(name="store-articles")
def task_store(df):
    return store_articles(df)


@flow(
    name="news-pipeline-flow",
    description="Fetches, cleans and stores top headlines every hour.",
)
def news_pipeline_flow():
    task_init_db()

    for category in CATEGORIES:
        print(f"\n📰 Processing category: {category}")
        raw     = task_fetch(category)
        cleaned = task_clean(raw, category)
        task_store(cleaned)

    print("\n✅ All categories processed.")


if __name__ == "__main__":
    # Run immediately once
    news_pipeline_flow()

    # To schedule it every hour, replace news_pipeline_flow() above with:
    # news_pipeline_flow.serve(
    #     name="hourly-news-ingestion",
    #     interval=3600,  # seconds
    # )