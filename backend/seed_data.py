import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")

from app.database.session import init_db
from app.services.ingestion import IngestionManager

def main():
    logger.info("Initializing database...")
    init_db()

    logger.info("Seeding verified WHO and Government of India documents...")
    ingestion = IngestionManager()
    total = ingestion.seed_initial_knowledge()
    logger.info(f"Seeding completed! Total chunks indexed: {total}")
    logger.info(f"Registry has {len(ingestion.registry)} documents.")

if __name__ == "__main__":
    main()
