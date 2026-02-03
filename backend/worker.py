"""
Background Worker Service for Async Document Processing.

This standalone service:
1. Connects to RabbitMQ and listens for job messages
2. Processes documents using Azure AI Content Understanding
3. Updates job status in the database

Run with: python worker.py
"""
import os
import sys
import json
import logging
import time
import pika
from pika.exceptions import AMQPConnectionError

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.models.job import Job, JobStatus
from app.core.azure import azure_client
from app.core.config import get_settings

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("worker")


def process_job(ch, method, properties, body):
    """
    Process a single job from the queue.
    
    1. Parse the job message
    2. Update status to PROCESSING
    3. Send file to Azure AI
    4. Update status to COMPLETED/FAILED with results
    5. Acknowledge the message
    """
    db = SessionLocal()
    job_id = None
    
    try:
        # Parse message
        message = json.loads(body)
        job_id = message.get("job_id")
        storage_path = message.get("storage_path")
        
        logger.info(f"[*] Processing job: {job_id}")
        logger.info(f"    Storage path: {storage_path}")
        
        # Get job from database
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            logger.error(f"[-] Job {job_id} not found in database")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        # Update status to PROCESSING
        job.status = JobStatus.PROCESSING
        db.commit()
        logger.info(f"    Status: PROCESSING")
        
        # Verify file exists
        if not os.path.exists(storage_path):
            raise FileNotFoundError(f"File not found: {storage_path}")
        
        # Read file data
        with open(storage_path, 'rb') as f:
            file_data = f.read()
        
        logger.info(f"    File size: {len(file_data)} bytes")
        
        # Process with Azure AI
        result = azure_client.analyze_document(file_data)
        
        # Check result
        if result.get("status") == "completed":
            job.status = JobStatus.COMPLETED
            job.result_data = result.get("data")
            logger.info(f"[+] Job {job_id} COMPLETED")
        elif result.get("status") == "skipped":
            # Azure not configured - mark as completed with message
            job.status = JobStatus.COMPLETED
            job.result_data = {"message": "Azure AI not configured", "raw_data": None}
            logger.info(f"[+] Job {job_id} COMPLETED (AI skipped)")
        else:
            job.status = JobStatus.FAILED
            job.error_message = result.get("error", "Unknown error")
            job.result_data = result
            logger.error(f"[-] Job {job_id} FAILED: {job.error_message}")
        
        db.commit()
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except FileNotFoundError as e:
        logger.error(f"[-] File not found: {e}")
        if job_id:
            try:
                job = db.query(Job).filter(Job.job_id == job_id).first()
                if job:
                    job.status = JobStatus.FAILED
                    job.error_message = str(e)
                    db.commit()
            except Exception:
                pass
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        logger.error(f"[-] Error processing job {job_id}: {e}")
        if job_id:
            try:
                job = db.query(Job).filter(Job.job_id == job_id).first()
                if job:
                    job.status = JobStatus.FAILED
                    job.error_message = str(e)
                    db.commit()
            except Exception:
                pass
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    finally:
        db.close()


def main():
    """Main entry point for the worker service."""
    logger.info("=" * 50)
    logger.info("Document Processing Worker Starting...")
    logger.info("=" * 50)
    
    retry_delay = 5
    max_retries = None  # Retry indefinitely
    
    while True:
        try:
            # Connect to RabbitMQ
            credentials = pika.PlainCredentials(
                settings.rabbitmq_user,
                settings.rabbitmq_password
            )
            parameters = pika.ConnectionParameters(
                host=settings.rabbitmq_host,
                port=settings.rabbitmq_port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            logger.info(f"Connecting to RabbitMQ at {settings.rabbitmq_host}:{settings.rabbitmq_port}...")
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            
            # Declare queue
            channel.queue_declare(queue=settings.rabbitmq_queue, durable=True)
            
            # Fair dispatch - don't give more than one message to a worker at a time
            channel.basic_qos(prefetch_count=1)
            
            # Start consuming
            channel.basic_consume(
                queue=settings.rabbitmq_queue,
                on_message_callback=process_job
            )
            
            logger.info(f"[*] Waiting for messages in queue: {settings.rabbitmq_queue}")
            logger.info("[*] Press CTRL+C to exit")
            
            channel.start_consuming()
            
        except AMQPConnectionError as e:
            logger.error(f"[-] RabbitMQ connection failed: {e}")
            logger.info(f"    Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            
        except KeyboardInterrupt:
            logger.info("\n[*] Worker shutting down...")
            break
            
        except Exception as e:
            logger.error(f"[-] Unexpected error: {e}")
            logger.info(f"    Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)


if __name__ == "__main__":
    main()
