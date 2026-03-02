"""
Script to seed initial database data.
"""
import asyncio
import logging

from app.database import connect_db, disconnect_db, get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_database():
    """Seed the database with initial data."""
    await connect_db()
    db = get_db()
    
    # Add seed data here
    logger.info("Seeding database...")
    
    await disconnect_db()
    logger.info("Database seeding complete")


if __name__ == "__main__":
    asyncio.run(seed_database())
