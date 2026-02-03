"""
RabbitMQ Queue Manager
Manages connection and message publishing to RabbitMQ for async job processing.
"""
import json
import logging
from typing import Optional
import pika
from pika.exceptions import AMQPConnectionError
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class RabbitMQManager:
    """Manages RabbitMQ connection and message publishing."""
    
    def __init__(self):
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
    
    def connect(self) -> bool:
        """Establish connection to RabbitMQ."""
        try:
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
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queue (idempotent - creates if doesn't exist)
            self.channel.queue_declare(queue=settings.rabbitmq_queue, durable=True)
            
            logger.info(f"Connected to RabbitMQ at {settings.rabbitmq_host}:{settings.rabbitmq_port}")
            return True
            
        except AMQPConnectionError as e:
            logger.warning(f"Failed to connect to RabbitMQ: {e}")
            return False
    
    def close(self):
        """Close the RabbitMQ connection."""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")
    
    def publish_job(
        self, 
        job_id: str, 
        storage_path: str, 
        ledger_name: str = None, 
        financial_year: str = None
    ) -> bool:
        """
        Publish a job message to the queue.
        
        Args:
            job_id: Unique identifier for the job
            storage_path: Path to the uploaded file
            ledger_name: Associated ledger name
            financial_year: Financial year for the document
            
        Returns:
            True if message was published successfully, False otherwise
        """
        if not self.channel or self.connection.is_closed:
            logger.warning("RabbitMQ not connected, attempting to reconnect...")
            if not self.connect():
                logger.error("Failed to reconnect to RabbitMQ")
                return False
        
        try:
            message = json.dumps({
                "job_id": job_id,
                "storage_path": storage_path,
                "ledger_name": ledger_name,
                "financial_year": financial_year
            })
            
            self.channel.basic_publish(
                exchange='',
                routing_key=settings.rabbitmq_queue,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Published job {job_id} to queue")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish job {job_id}: {e}")
            return False


# Global instance for use in FastAPI
rabbitmq_manager = RabbitMQManager()
