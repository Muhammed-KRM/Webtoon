"""
Database Base Model
"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models to ensure they are registered
from app.models import user, job, series, comment, subscription, site_settings

