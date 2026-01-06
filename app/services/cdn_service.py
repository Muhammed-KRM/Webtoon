"""
CDN Service - S3/MinIO integration for image storage
"""
from typing import Optional, List
from pathlib import Path
import io
from loguru import logger
from app.core.config import settings


class CDNService:
    """Service for CDN operations (S3/MinIO)"""
    
    def __init__(self):
        """Initialize CDN service"""
        self.cdn_enabled = getattr(settings, 'CDN_ENABLED', False)
        self.cdn_type = getattr(settings, 'CDN_TYPE', 's3')  # 's3' or 'minio'
        self.cdn_client = None
        
        if self.cdn_enabled:
            self._initialize_cdn()
    
    def _initialize_cdn(self):
        """Initialize CDN client based on type"""
        try:
            if self.cdn_type == 's3':
                self._init_s3()
            elif self.cdn_type == 'minio':
                self._init_minio()
            else:
                logger.warning(f"Unknown CDN type: {self.cdn_type}, CDN disabled")
                self.cdn_enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize CDN: {e}")
            self.cdn_enabled = False
    
    def _init_s3(self):
        """Initialize AWS S3 client"""
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            self.cdn_client = boto3.client(
                's3',
                aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', ''),
                aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', ''),
                region_name=getattr(settings, 'AWS_REGION', 'us-east-1')
            )
            self.bucket_name = getattr(settings, 'S3_BUCKET_NAME', '')
            logger.info("AWS S3 client initialized")
        except ImportError:
            logger.warning("boto3 not installed, S3 support disabled")
            self.cdn_enabled = False
        except Exception as e:
            logger.error(f"Error initializing S3: {e}")
            self.cdn_enabled = False
    
    def _init_minio(self):
        """Initialize MinIO client"""
        try:
            from minio import Minio
            from minio.error import S3Error
            
            self.cdn_client = Minio(
                getattr(settings, 'MINIO_ENDPOINT', 'localhost:9000'),
                access_key=getattr(settings, 'MINIO_ACCESS_KEY', ''),
                secret_key=getattr(settings, 'MINIO_SECRET_KEY', ''),
                secure=getattr(settings, 'MINIO_SECURE', False)
            )
            self.bucket_name = getattr(settings, 'MINIO_BUCKET_NAME', 'webtoon-images')
            self._ensure_bucket_exists()
            logger.info("MinIO client initialized")
        except ImportError:
            logger.warning("minio not installed, MinIO support disabled")
            self.cdn_enabled = False
        except Exception as e:
            logger.error(f"Error initializing MinIO: {e}")
            self.cdn_enabled = False
    
    def _ensure_bucket_exists(self):
        """Ensure MinIO bucket exists"""
        if self.cdn_type == 'minio' and self.cdn_client:
            try:
                if not self.cdn_client.bucket_exists(self.bucket_name):
                    self.cdn_client.make_bucket(self.bucket_name)
                    logger.info(f"Created MinIO bucket: {self.bucket_name}")
            except Exception as e:
                logger.error(f"Error ensuring bucket exists: {e}")
    
    def upload_image(
        self,
        image_bytes: bytes,
        object_key: str,
        content_type: str = "image/webp"
    ) -> Optional[str]:
        """
        Upload image to CDN
        
        Args:
            image_bytes: Image bytes
            object_key: S3/MinIO object key (path)
            content_type: Content type (image/webp, image/jpeg, etc.)
            
        Returns:
            CDN URL if successful, None otherwise
        """
        if not self.cdn_enabled or not self.cdn_client:
            return None
        
        try:
            if self.cdn_type == 's3':
                return self._upload_to_s3(image_bytes, object_key, content_type)
            elif self.cdn_type == 'minio':
                return self._upload_to_minio(image_bytes, object_key, content_type)
        except Exception as e:
            logger.error(f"Error uploading to CDN: {e}")
            return None
    
    def _upload_to_s3(self, image_bytes: bytes, object_key: str, content_type: str) -> str:
        """Upload to AWS S3"""
        try:
            self.cdn_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=image_bytes,
                ContentType=content_type,
                ACL='public-read'  # Make images publicly accessible
            )
            
            # Generate public URL
            url = f"https://{self.bucket_name}.s3.{getattr(settings, 'AWS_REGION', 'us-east-1')}.amazonaws.com/{object_key}"
            logger.info(f"Uploaded to S3: {object_key}")
            return url
        except Exception as e:
            logger.error(f"Error uploading to S3: {e}")
            raise
    
    def _upload_to_minio(self, image_bytes: bytes, object_key: str, content_type: str) -> str:
        """Upload to MinIO"""
        try:
            from minio.error import S3Error
            
            self.cdn_client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_key,
                data=io.BytesIO(image_bytes),
                length=len(image_bytes),
                content_type=content_type
            )
            
            # Generate public URL
            endpoint = getattr(settings, 'MINIO_ENDPOINT', 'localhost:9000')
            protocol = 'https' if getattr(settings, 'MINIO_SECURE', False) else 'http'
            url = f"{protocol}://{endpoint}/{self.bucket_name}/{object_key}"
            logger.info(f"Uploaded to MinIO: {object_key}")
            return url
        except Exception as e:
            logger.error(f"Error uploading to MinIO: {e}")
            raise
    
    def delete_image(self, object_key: str) -> bool:
        """
        Delete image from CDN
        
        Args:
            object_key: S3/MinIO object key
            
        Returns:
            True if successful, False otherwise
        """
        if not self.cdn_enabled or not self.cdn_client:
            return False
        
        try:
            if self.cdn_type == 's3':
                self.cdn_client.delete_object(Bucket=self.bucket_name, Key=object_key)
            elif self.cdn_type == 'minio':
                self.cdn_client.remove_object(self.bucket_name, object_key)
            
            logger.info(f"Deleted from CDN: {object_key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting from CDN: {e}")
            return False
    
    def get_url(self, object_key: str) -> Optional[str]:
        """
        Get CDN URL for an object
        
        Args:
            object_key: S3/MinIO object key
            
        Returns:
            CDN URL if CDN enabled, None otherwise
        """
        if not self.cdn_enabled:
            return None
        
        try:
            if self.cdn_type == 's3':
                endpoint = getattr(settings, 'AWS_REGION', 'us-east-1')
                return f"https://{self.bucket_name}.s3.{endpoint}.amazonaws.com/{object_key}"
            elif self.cdn_type == 'minio':
                endpoint = getattr(settings, 'MINIO_ENDPOINT', 'localhost:9000')
                protocol = 'https' if getattr(settings, 'MINIO_SECURE', False) else 'http'
                return f"{protocol}://{endpoint}/{self.bucket_name}/{object_key}"
        except Exception as e:
            logger.error(f"Error generating CDN URL: {e}")
            return None

