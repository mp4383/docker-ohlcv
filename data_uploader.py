import boto3
import os
from datetime import datetime, timedelta
import logging

class DataUploader:
    def __init__(self, bucket_name: str, local_retention_days: int = 7):
        self.s3 = boto3.client('s3')
        self.bucket = bucket_name
        self.retention_days = local_retention_days

    async def upload_and_cleanup(self, data_dir: str = 'data'):
        """Upload files to S3 and cleanup old local files"""
        try:
            # Upload all CSV files
            for filename in os.listdir(data_dir):
                if filename.endswith('.csv'):
                    filepath = os.path.join(data_dir, filename)
                    
                    # Organize files by date in S3
                    date_str = datetime.now().strftime('%Y/%m/%d')
                    s3_path = f"{date_str}/{filename}"
                    
                    # Upload to S3
                    self.s3.upload_file(filepath, self.bucket, s3_path)
                    logging.info(f"Uploaded {filename} to s3://{self.bucket}/{s3_path}")

            # Cleanup old local files
            self.cleanup_old_files(data_dir)

        except Exception as e:
            logging.error(f"Error in upload process: {str(e)}")

    def cleanup_old_files(self, data_dir: str):
        """Remove files older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for filename in os.listdir(data_dir):
            filepath = os.path.join(data_dir, filename)
            file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            if file_modified < cutoff_date:
                os.remove(filepath)
                logging.info(f"Removed old file: {filename}") 