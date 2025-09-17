"""
Seed script to create initial departments
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_departments():
    """Create initial departments using raw SQL to avoid model relationship issues"""
    
    # Create engine directly
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # Check if departments table exists and has data
            result = connection.execute(text("SELECT COUNT(*) FROM departments"))
            existing_count = result.scalar()
            
            if existing_count > 0:
                logger.info(f"Departments already exist ({existing_count} found). Skipping creation.")
                return

            departments = [
                ("IT Support", "General IT support and helpdesk services"),
                ("Network Operations", "Network infrastructure and connectivity management"),
                ("Security", "Information security and compliance"),
                ("Database Administration", "Database management and optimization"),
                ("Application Development", "Software development and maintenance")
            ]
            
            for name, description in departments:
                connection.execute(
                    text("INSERT INTO departments (name, description, created_at) VALUES (:name, :description, NOW())"),
                    {"name": name, "description": description}
                )
            
            connection.commit()
            logger.info(f"Successfully created {len(departments)} departments")
            
            # List created departments
            result = connection.execute(text("SELECT id, name FROM departments ORDER BY id"))
            for row in result:
                logger.info(f"Department: {row.id} - {row.name}")
                
    except Exception as e:
        logger.error(f"Error creating departments: {str(e)}")
        raise

if __name__ == "__main__":
    create_departments()
