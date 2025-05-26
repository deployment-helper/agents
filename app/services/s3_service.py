import os
import boto3
import requests
from urllib.parse import urlparse
import logging

from app.config import storage_config

logger = logging.getLogger(__name__)

class S3Service:
    """
    Service to handle S3-related operations including downloading public files
    """

    @staticmethod
    def download_from_public_url(url: str, local_dir: str = None) -> str:
        """
        Download a file from a public URL (S3 or any other) and save it locally
        
        Args:
            url (str): The public URL of the file to download
            local_dir (str, optional): Directory to save the file. Defaults to temp directory.
            
        Returns:
            str: The local path of the downloaded file
        """
        try:
            if not local_dir:
                local_dir = storage_config.temp_file_path
                
            # Ensure directory exists
            os.makedirs(local_dir, exist_ok=True)
            
            # Extract filename from URL
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            # If filename is empty or doesn't have an extension, create a unique name
            if not filename or '.' not in filename:
                import uuid
                ext = S3Service._guess_extension_from_url(url)
                filename = f"{uuid.uuid4()}{ext}"
                
            local_path = os.path.join(local_dir, filename)
            
            # Download the file
            logger.info(f"Downloading file from {url} to {local_path}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            logger.info(f"File downloaded successfully to {local_path}")
            return local_path
        
        except Exception as e:
            logger.error(f"Error downloading file from {url}: {str(e)}")
            raise
    
    @staticmethod
    def _guess_extension_from_url(url: str) -> str:
        """
        Attempt to guess file extension from URL or Content-Type
        
        Args:
            url (str): The URL of the file
            
        Returns:
            str: The guessed file extension including the dot (e.g., '.pdf')
        """
        try:
            # Try to get content type from HEAD request
            response = requests.head(url, allow_redirects=True)
            content_type = response.headers.get('content-type', '').lower()
            
            # Map common MIME types to extensions
            if 'pdf' in content_type:
                return '.pdf'
            elif 'image/jpeg' in content_type or 'image/jpg' in content_type:
                return '.jpg'
            elif 'image/png' in content_type:
                return '.png'
            elif 'text/plain' in content_type:
                return '.txt'
            elif 'application/msword' in content_type:
                return '.doc'
            elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type:
                return '.docx'
            
            # If we can't determine from content-type, try from URL
            parsed_url = urlparse(url)
            path = parsed_url.path.lower()
            
            if path.endswith('.pdf'):
                return '.pdf'
            elif path.endswith('.jpg') or path.endswith('.jpeg'):
                return '.jpg'
            elif path.endswith('.png'):
                return '.png'
            elif path.endswith('.txt'):
                return '.txt'
            elif path.endswith('.doc'):
                return '.doc'
            elif path.endswith('.docx'):
                return '.docx'
            
            # Default to .bin if we can't determine
            return '.bin'
            
        except Exception:
            # If all else fails, return a generic binary extension
            return '.bin'
            
    @staticmethod
    def upload_to_s3(local_path: str, bucket: str, key: str = None) -> str:
        """
        Upload a local file to S3
        
        Args:
            local_path (str): Path to the local file
            bucket (str): S3 bucket name
            key (str, optional): S3 key for the file. Defaults to filename.
            
        Returns:
            str: The S3 URL of the uploaded file
        """
        if not key:
            key = os.path.basename(local_path)
            
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=storage_config.aws_access_key,
                aws_secret_access_key=storage_config.aws_secret_key
            )
            
            s3_client.upload_file(local_path, bucket, key)
            return f"https://{bucket}.s3.amazonaws.com/{key}"
        
        except Exception as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            raise
