"""
Celery application initialization for the Retail Kiosk worker service.

This module creates and configures the Celery application instance used for
asynchronous task processing. It loads configuration from the WorkerSettings
and sets up proper task discovery.
"""

from celery import Celery
from celery.signals import setup_logging, worker_process_init

from config import settings

# Create Celery application instance
celery_app = Celery(
    "retail_kiosk_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["tasks"],  # Auto-discover tasks from tasks.py
)

# Configure Celery from settings
celery_app.conf.update(settings.get_celery_config())

# Additional Celery configuration
celery_app.conf.update(
    task_routes={
        "tasks.sync_product_data": {"queue": "product_sync"},
        "tasks.optimize_image": {"queue": "image_processing"},
        "tasks.update_vector_embeddings": {"queue": "vector_db"},
        "tasks.generate_report": {"queue": "reports"},
    },
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    task_create_missing_queues=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_send_task_events=True,
    task_send_sent_event=True,
)


@setup_logging.connect
def setup_celery_logging(**kwargs) -> None:
    """
    Configure logging for Celery workers.

    This signal handler is called when Celery sets up logging. We override
    the default logging configuration to use Loguru for consistent logging
    across the application.
    """
    from loguru import logger
    import sys

    # Remove default handlers
    logger.remove()

    # Add custom handler with format from settings
    logger.add(
        sys.stdout,
        format=settings.log_format,
        level=settings.log_level,
        colorize=True,
    )

    # Add file handler with rotation
    logger.add(
        "logs/worker_{time}.log",
        format=settings.log_format,
        level=settings.log_level,
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        compression="zip",
    )


@worker_process_init.connect
def init_worker_process(**kwargs) -> None:
    """
    Initialize worker process resources.

    This signal handler is called when a worker process is initialized.
    Use this to set up database connections, cache connections, or other
    resources that should be created per worker process.
    """
    from loguru import logger

    logger.info(
        "Initializing worker process",
        extra={
            "worker_name": kwargs.get("sender"),
            "environment": settings.environment,
        },
    )

    # TODO: Initialize database connection pool for worker process
    # TODO: Initialize Redis connection pool for caching
    # TODO: Initialize Qdrant client for vector operations


if __name__ == "__main__":
    """
    Run Celery worker for development/testing.

    In production, use the celery command directly:
        celery -A celery_app worker --loglevel=info
    """
    celery_app.start()
