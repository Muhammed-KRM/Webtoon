"""
Scraper Config Service - Manages dynamic scraper configurations
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from loguru import logger
from app.models.scraper_config import ScraperConfig


class ScraperConfigService:
    """Service for managing scraper configurations"""
    
    @staticmethod
    def get_config(db: Session, site_name: str) -> Optional[ScraperConfig]:
        """
        Get scraper configuration for a site
        
        Args:
            db: Database session
            site_name: Site name (e.g., "webtoons.com")
            
        Returns:
            ScraperConfig if found, None otherwise
        """
        config = db.query(ScraperConfig).filter(
            ScraperConfig.site_name == site_name,
            ScraperConfig.is_active == True
        ).first()
        
        return config
    
    @staticmethod
    def get_default_selectors(site_name: str) -> Dict[str, Any]:
        """
        Get default selectors for a site (fallback if DB config not found)
        
        Args:
            site_name: Site name
            
        Returns:
            Dictionary with default selectors
        """
        defaults = {
            "webtoons.com": {
                "container": "div#viewer, div.viewer",
                "image": "img",
                "image_attr": "data-url, src, data-src",
                "title": "h1, .episode-title",
                "next_chapter": "a.next-episode"
            },
            "asuracomic.net": {
                "container": "div.reading-content, div.reader-content",
                "image": "img",
                "image_attr": "data-src, data-lazy-src, src, data-url",
                "title": "h1.chapter-title, h1",
                "next_chapter": "a.next-chapter"
            },
            "asurascans.com.tr": {
                "container": "div.reading-content, div.reader-content",
                "image": "img",
                "image_attr": "data-src, data-lazy-src, src",
                "title": "h1.chapter-title",
                "next_chapter": "a.next-chapter"
            }
        }
        
        return defaults.get(site_name, {
            "container": "div.reading-content, div.reader-content, div.chapter-content",
            "image": "img",
            "image_attr": "data-src, src, data-lazy-src",
            "title": "h1, h2",
            "next_chapter": "a.next"
        })
    
    @staticmethod
    def get_selectors(db: Session, site_name: str) -> Dict[str, Any]:
        """
        Get selectors for a site (from DB or defaults)
        
        Args:
            db: Database session
            site_name: Site name
            
        Returns:
            Dictionary with selectors
        """
        config = ScraperConfigService.get_config(db, site_name)
        
        if config and config.selectors:
            return config.selectors
        
        # Fallback to defaults
        return ScraperConfigService.get_default_selectors(site_name)
    
    @staticmethod
    def update_config(
        db: Session,
        site_name: str,
        selectors: Dict[str, Any],
        updated_by: Optional[str] = None,
        notes: Optional[str] = None
    ) -> ScraperConfig:
        """
        Update scraper configuration
        
        Args:
            db: Database session
            site_name: Site name
            selectors: New selectors dictionary
            updated_by: Admin username
            notes: Admin notes
            
        Returns:
            Updated ScraperConfig
        """
        config = db.query(ScraperConfig).filter(
            ScraperConfig.site_name == site_name
        ).first()
        
        if config:
            config.selectors = selectors
            config.updated_by = updated_by
            config.notes = notes
        else:
            # Create new config
            config = ScraperConfig(
                site_name=site_name,
                site_domain=site_name,
                selectors=selectors,
                updated_by=updated_by,
                notes=notes,
                is_active=True
            )
            db.add(config)
        
        db.commit()
        db.refresh(config)
        
        logger.info(f"Updated scraper config for {site_name}")
        return config

