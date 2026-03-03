"""File storage service with AWS S3 integration."""
import logging
from typing import Optional, BinaryIO
import uuid
import boto3
from botocore.exceptions import ClientError

from app.config import settings

logger = logging.getLogger(__name__)


class FileStorageService:
    """AWS S3 file storage service."""
    
    def __init__(self):
        self.bucket_name = settings.S3_BUCKET_NAME if hasattr(settings, 'S3_BUCKET_NAME') else None
        self.region = settings.AWS_REGION if hasattr(settings, 'AWS_REGION') else 'us-east-1'
        
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            self.s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=self.region
            )
        else:
            # Use IAM role (for EC2/ECS/EKS)
            self.s3 = boto3.client('s3', region_name=self.region)
    
    async def upload_file(
        self,
        file_data: bytes,
        original_filename: str,
        folder: str = "uploads",
        content_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Upload file to S3.
        
        Args:
            file_data: File binary data
            original_filename: Original filename
            folder: S3 folder path
            content_type: MIME type
            
        Returns:
            S3 URL if successful
        """
        if not self.bucket_name:
            logger.warning("S3 bucket not configured")
            return None
        
        try:
            # Generate unique filename
            file_ext = original_filename.split('.')[-1] if '.' in original_filename else ''
            unique_filename = f"{folder}/{uuid.uuid4()}.{file_ext}" if file_ext else f"{folder}/{uuid.uuid4()}"
            
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=unique_filename,
                Body=file_data,
                **extra_args
            )
            
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{unique_filename}"
            logger.info(f"File uploaded: {url}")
            return url
            
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            return None
    
    async def delete_file(self, file_url: str) -> bool:
        """
        Delete file from S3.
        
        Args:
            file_url: Full S3 URL
            
        Returns:
            True if deleted successfully
        """
        if not self.bucket_name:
            return False
        
        try:
            # Extract key from URL
            key = file_url.split(f"{self.bucket_name}.s3.")[1].split('/', 1)[1]
            
            self.s3.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"File deleted: {key}")
            return True
            
        except Exception as e:
            logger.error(f"S3 delete error: {e}")
            return False
    
    async def generate_presigned_url(
        self,
        key: str,
        expiration: int = 3600
    ) -> Optional[str]:
        """
        Generate presigned URL for temporary access.
        
        Args:
            key: S3 object key
            expiration: URL expiration in seconds
            
        Returns:
            Presigned URL
        """
        if not self.bucket_name:
            return None
        
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            logger.error(f"Presigned URL error: {e}")
            return None


# Alternative: Cloudinary for image optimization
class CloudinaryService:
    """Cloudinary image storage and optimization."""
    
    def __init__(self):
        self.cloud_name = settings.CLOUDINARY_CLOUD_NAME if hasattr(settings, 'CLOUDINARY_CLOUD_NAME') else None
        self.api_key = settings.CLOUDINARY_API_KEY if hasattr(settings, 'CLOUDINARY_API_KEY') else None
        self.api_secret = settings.CLOUDINARY_API_SECRET if hasattr(settings, 'CLOUDINARY_API_SECRET') else None
        
        if self.cloud_name and self.api_key and self.api_secret:
            import cloudinary
            cloudinary.config(
                cloud_name=self.cloud_name,
                api_key=self.api_key,
                api_secret=self.api_secret
            )
            self.configured = True
        else:
            self.configured = False
    
    async def upload_image(self, file_data: bytes, folder: str = "delivery_app") -> Optional[str]:
        """Upload image to Cloudinary with optimization."""
        if not self.configured:
            logger.warning("Cloudinary not configured")
            return None
        
        try:
            import cloudinary.uploader
            result = cloudinary.uploader.upload(
                file_data,
                folder=folder,
                transformation=[
                    {"quality": "auto:good"},
                    {"fetch_format": "auto"}
                ]
            )
            return result['secure_url']
        except Exception as e:
            logger.error(f"Cloudinary upload error: {e}")
            return None
