"""
Database Logger - Save logs to database
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from loguru import logger
from app.models.log import Log
from app.core.database import SessionLocal
from datetime import datetime
import asyncio
from queue import Queue
import threading

# Queue for async log writing
_log_queue = Queue()
_log_thread = None
_log_thread_running = False


def _log_writer_thread():
    """Background thread for writing logs to database"""
    global _log_thread_running
    _log_thread_running = True
    
    while _log_thread_running:
        try:
            # Get log entry from queue (with timeout)
            try:
                log_data = _log_queue.get(timeout=1)
            except:
                continue
            
            db = SessionLocal()
            try:
                log_entry = Log(**log_data)
                db.add(log_entry)
                db.commit()
            except Exception as e:
                logger.error(f"Error writing log to database: {e}")
                db.rollback()
            finally:
                db.close()
                _log_queue.task_done()
        except Exception as e:
            logger.error(f"Error in log writer thread: {e}")


def start_log_writer():
    """Start background thread for log writing"""
    global _log_thread
    if _log_thread is None or not _log_thread.is_alive():
        _log_thread = threading.Thread(target=_log_writer_thread, daemon=True)
        _log_thread.start()


def stop_log_writer():
    """Stop background thread"""
    global _log_thread_running
    _log_thread_running = False
    if _log_thread:
        _log_thread.join(timeout=5)


class DatabaseLogger:
    """Logger that saves to database"""
    
    @staticmethod
    def log(
        level: str,
        message: str,
        module: Optional[str] = None,
        request_id: Optional[str] = None,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        """Log to database"""
        try:
            # Start writer thread if not running
            start_log_writer()
            
            log_data = {
                "level": level,
                "message": message,
                "module": module,
                "request_id": request_id,
                "user_id": user_id,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "extra_data": extra_data
            }
            
            # Add to queue (non-blocking)
            _log_queue.put_nowait(log_data)
        except Exception as e:
            # Fallback to console logging if queue is full
            logger.warning(f"Log queue full, falling back to console: {e}")
    
    @staticmethod
    def info(message: str, **kwargs):
        """Log info level"""
        DatabaseLogger.log("INFO", message, **kwargs)
    
    @staticmethod
    def warning(message: str, **kwargs):
        """Log warning level"""
        DatabaseLogger.log("WARNING", message, **kwargs)
    
    @staticmethod
    def error(message: str, **kwargs):
        """Log error level"""
        DatabaseLogger.log("ERROR", message, **kwargs)
    
    @staticmethod
    def debug(message: str, **kwargs):
        """Log debug level"""
        DatabaseLogger.log("DEBUG", message, **kwargs)


# Initialize logger on import
start_log_writer()

