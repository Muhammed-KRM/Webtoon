"""
Query Optimizer - Eager loading and query optimization
"""
from sqlalchemy.orm import joinedload, selectinload, subqueryload
from sqlalchemy import select
from typing import Type, List, Any


class QueryOptimizer:
    """Optimize database queries to prevent N+1 problems"""
    
    @staticmethod
    def optimize_series_query(query):
        """Optimize series query with eager loading"""
        return query.options(
            # Eager load chapters count (subquery)
            selectinload(Series.chapters),
            # Eager load comments count
            selectinload(Series.comments),
            # Eager load ratings
            selectinload(Series.ratings)
        )
    
    @staticmethod
    def optimize_chapter_query(query):
        """Optimize chapter query with eager loading"""
        from app.models.series import Chapter, Series
        return query.options(
            # Eager load series
            joinedload(Chapter.series),
            # Eager load translations
            selectinload(Chapter.translations),
            # Eager load comments
            selectinload(Chapter.comments)
        )
    
    @staticmethod
    def optimize_comment_query(query):
        """Optimize comment query with eager loading"""
        from app.models.comment import Comment
        return query.options(
            # Eager load user
            joinedload(Comment.user),
            # Eager load replies
            selectinload(Comment.replies).joinedload(Comment.user),
            # Eager load likes
            selectinload(Comment.likes)
        )
    
    @staticmethod
    def optimize_user_query(query):
        """Optimize user query with eager loading"""
        from app.models.user import User
        return query.options(
            # Eager load subscriptions
            selectinload(User.subscriptions),
            # Eager load bookmarks
            selectinload(User.bookmarks)
        )

