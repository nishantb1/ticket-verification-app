"""
Cloudflare R2 Storage Service
Handles file uploads and downloads to/from Cloudflare R2 bucket
"""

import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import logging
from typing import Optional, BinaryIO
import tempfile

logger = logging.getLogger(__name__)

class R2StorageService:
    """Service for handling Cloudflare R2 storage operations"""
    
    def __init__(self):
        """Initialize R2 client with environment variables"""
        self.account_id = os.environ.get('R2_ACCOUNT_ID')
        self.bucket_name = os.environ.get('R2_BUCKET_NAME')
        self.access_key_id = os.environ.get('R2_ACCESS_KEY_ID')
        self.secret_access_key = os.environ.get('R2_SECRET_ACCESS_KEY')
        self.endpoint = os.environ.get('R2_ENDPOINT')
        
        # Validate required environment variables
        required_vars = [
            'R2_ACCOUNT_ID', 'R2_BUCKET_NAME', 'R2_ACCESS_KEY_ID', 
            'R2_SECRET_ACCESS_KEY', 'R2_ENDPOINT'
        ]
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            logger.warning(f"Missing R2 environment variables: {missing_vars}. Falling back to local storage.")
            self.enabled = False
            self.client = None
        else:
            try:
                # Initialize boto3 client for R2
                self.client = boto3.client(
                    's3',
                    endpoint_url=self.endpoint,
                    aws_access_key_id=self.access_key_id,
                    aws_secret_access_key=self.secret_access_key,
                    region_name='auto'  # R2 uses 'auto' as region
                )
                
                # Test connection by listing bucket
                self.client.head_bucket(Bucket=self.bucket_name)
                self.enabled = True
                logger.info(f"R2 storage initialized successfully. Bucket: {self.bucket_name}")
                
            except (ClientError, NoCredentialsError) as e:
                logger.error(f"Failed to initialize R2 client: {e}")
                self.enabled = False
                self.client = None
    
    def is_enabled(self) -> bool:
        """Check if R2 storage is properly configured and enabled"""
        return self.enabled and self.client is not None
    
    def upload_file(self, file_obj: BinaryIO, key: str, content_type: str = None) -> bool:
        """
        Upload a file to R2 bucket
        
        Args:
            file_obj: File-like object to upload
            key: Object key (path) in the bucket
            content_type: MIME type of the file
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        if not self.is_enabled():
            logger.warning("R2 storage not enabled, cannot upload file")
            return False
        
        try:
            # Prepare upload arguments
            upload_args = {'Bucket': self.bucket_name, 'Key': key, 'Body': file_obj}
            
            if content_type:
                upload_args['ContentType'] = content_type
            
            # Upload file
            self.client.put_object(**upload_args)
            logger.info(f"Successfully uploaded file to R2: {key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to upload file to R2: {e}")
            return False
    
    def upload_file_from_path(self, file_path: str, key: str, content_type: str = None) -> bool:
        """
        Upload a file from local path to R2 bucket
        
        Args:
            file_path: Local path to the file
            key: Object key (path) in the bucket
            content_type: MIME type of the file
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        if not self.is_enabled():
            logger.warning("R2 storage not enabled, cannot upload file")
            return False
        
        try:
            with open(file_path, 'rb') as file_obj:
                return self.upload_file(file_obj, key, content_type)
                
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return False
        except Exception as e:
            logger.error(f"Failed to upload file from path: {e}")
            return False
    
    def download_file(self, key: str, local_path: str = None) -> Optional[str]:
        """
        Download a file from R2 bucket
        
        Args:
            key: Object key (path) in the bucket
            local_path: Local path to save the file (optional, creates temp file if not provided)
            
        Returns:
            str: Path to downloaded file, None if failed
        """
        if not self.is_enabled():
            logger.warning("R2 storage not enabled, cannot download file")
            return None
        
        try:
            # Create temporary file if no local path provided
            if not local_path:
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                local_path = temp_file.name
                temp_file.close()
            
            # Download file
            self.client.download_file(self.bucket_name, key, local_path)
            logger.info(f"Successfully downloaded file from R2: {key} -> {local_path}")
            return local_path
            
        except ClientError as e:
            logger.error(f"Failed to download file from R2: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading file: {e}")
            return None
    
    def get_file_stream(self, key: str) -> Optional[BinaryIO]:
        """
        Get a file stream from R2 bucket
        
        Args:
            key: Object key (path) in the bucket
            
        Returns:
            BinaryIO: File stream, None if failed
        """
        if not self.is_enabled():
            logger.warning("R2 storage not enabled, cannot get file stream")
            return None
        
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=key)
            return response['Body']
            
        except ClientError as e:
            logger.error(f"Failed to get file stream from R2: {e}")
            return None
    
    def delete_file(self, key: str) -> bool:
        """
        Delete a file from R2 bucket
        
        Args:
            key: Object key (path) in the bucket
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        if not self.is_enabled():
            logger.warning("R2 storage not enabled, cannot delete file")
            return False
        
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"Successfully deleted file from R2: {key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete file from R2: {e}")
            return False
    
    def file_exists(self, key: str) -> bool:
        """
        Check if a file exists in R2 bucket
        
        Args:
            key: Object key (path) in the bucket
            
        Returns:
            bool: True if file exists, False otherwise
        """
        if not self.is_enabled():
            return False
        
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=key)
            return True
            
        except ClientError:
            return False
    
    def list_files(self, prefix: str = '') -> list:
        """
        List files in R2 bucket with optional prefix
        
        Args:
            prefix: Prefix to filter files
            
        Returns:
            list: List of file keys
        """
        if not self.is_enabled():
            return []
        
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            else:
                return []
                
        except ClientError as e:
            logger.error(f"Failed to list files from R2: {e}")
            return []


# Global storage service instance
storage_service = R2StorageService()


def get_storage_service() -> R2StorageService:
    """Get the global storage service instance"""
    return storage_service


def upload_receipt(file_obj: BinaryIO, filename: str) -> tuple[bool, str]:
    """
    Upload a receipt file to storage
    
    Args:
        file_obj: File object to upload
        filename: Name of the file
        
    Returns:
        tuple: (success: bool, storage_path: str)
    """
    storage = get_storage_service()
    
    if storage.is_enabled():
        # Upload to R2
        key = f"receipts/{filename}"
        success = storage.upload_file(file_obj, key)
        return success, key if success else filename
    else:
        # Fallback to local storage
        logger.info("R2 not available, using local storage for receipt")
        local_path = os.path.join('uploads', filename)
        
        # Ensure uploads directory exists
        os.makedirs('uploads', exist_ok=True)
        
        try:
            with open(local_path, 'wb') as f:
                file_obj.seek(0)  # Reset file pointer
                f.write(file_obj.read())
            return True, filename
        except Exception as e:
            logger.error(f"Failed to save file locally: {e}")
            return False, filename


def upload_csv(file_obj: BinaryIO, filename: str) -> tuple[bool, str]:
    """
    Upload a CSV file to storage
    
    Args:
        file_obj: File object to upload
        filename: Name of the file
        
    Returns:
        tuple: (success: bool, storage_path: str)
    """
    storage = get_storage_service()
    
    if storage.is_enabled():
        # Upload to R2
        key = f"csv_uploads/{filename}"
        success = storage.upload_file(file_obj, key, 'text/csv')
        return success, key if success else filename
    else:
        # Fallback to local storage
        logger.info("R2 not available, using local storage for CSV")
        local_path = os.path.join('csv_uploads', filename)
        
        # Ensure csv_uploads directory exists
        os.makedirs('csv_uploads', exist_ok=True)
        
        try:
            with open(local_path, 'wb') as f:
                file_obj.seek(0)  # Reset file pointer
                f.write(file_obj.read())
            return True, filename
        except Exception as e:
            logger.error(f"Failed to save CSV file locally: {e}")
            return False, filename


def get_file_path(storage_path: str) -> Optional[str]:
    """
    Get local file path for a stored file (downloads from R2 if needed)
    
    Args:
        storage_path: Path where file is stored (R2 key or local filename)
        
    Returns:
        str: Local file path, None if file not accessible
    """
    storage = get_storage_service()
    
    if storage.is_enabled() and not os.path.exists(storage_path):
        # File is in R2, download it temporarily
        return storage.download_file(storage_path)
    else:
        # File is local or R2 not available
        if storage_path.startswith('receipts/') or storage_path.startswith('csv_uploads/'):
            # R2 key format, but R2 not available - try local fallback
            filename = os.path.basename(storage_path)
            if storage_path.startswith('receipts/'):
                local_path = os.path.join('uploads', filename)
            else:
                local_path = os.path.join('csv_uploads', filename)
            
            return local_path if os.path.exists(local_path) else None
        else:
            # Local filename format
            if '/' not in storage_path:
                # Just filename, check both upload directories
                receipt_path = os.path.join('uploads', storage_path)
                csv_path = os.path.join('csv_uploads', storage_path)
                
                if os.path.exists(receipt_path):
                    return receipt_path
                elif os.path.exists(csv_path):
                    return csv_path
            
            return storage_path if os.path.exists(storage_path) else None


def cleanup_temp_file(file_path: str):
    """
    Clean up temporary files downloaded from R2
    
    Args:
        file_path: Path to temporary file
    """
    try:
        if file_path and file_path.startswith('/tmp/') and os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup temporary file {file_path}: {e}")