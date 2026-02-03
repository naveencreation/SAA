"""
Azure Content Understanding Client
Handles communication with Azure AI Content Understanding API for document extraction.
"""
import requests
import time
import logging
from typing import Optional, Dict
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class AzureContentUnderstandingClient:
    """Client for Azure AI Content Understanding API."""
    
    def __init__(self, azure_api_key: str = None):
        self.azure_api_key = azure_api_key or settings.azure_api_key

    def analyze_document(
        self,
        file_data: bytes,
        azure_endpoint: str = None,
        analyzer_id: str = None,
        api_version: str = "2025-11-01",
        timeout: int = 300
    ) -> Optional[Dict]:
        """
        Analyze a document using Azure Content Understanding API.
        
        Args:
            file_data: Document bytes (PDF, image, etc.)
            azure_endpoint: Azure endpoint URL (uses settings if not provided)
            analyzer_id: Azure analyzer ID (uses settings if not provided)
            api_version: API version to use
            timeout: Maximum time to wait for processing (seconds)
            
        Returns:
            Dict with extraction results or error information
        """
        endpoint = azure_endpoint or settings.azure_endpoint
        analyzer = analyzer_id or settings.effective_analyzer_id
        
        # Check configuration
        if not all([endpoint, self.azure_api_key, analyzer]):
            logger.warning("Azure AI not configured. Skipping document analysis.")
            return {"error": "Azure AI not configured", "status": "skipped"}
        
        try:
            logger.info(f"[Azure] Starting document analysis...")
            start_time = time.time()

            # Build request URL (using :analyzeBinary endpoint for binary PDF data)
            url = (
                f"{endpoint.rstrip('/')}"
                f"/contentunderstanding/analyzers/"
                f"{analyzer}:analyzeBinary"
                f"?api-version={api_version}"
            )

            headers = {
                "Content-Type": "application/pdf",
                "Ocp-Apim-Subscription-Key": self.azure_api_key,
                "x-ms-useragent": "azure-ai-content-understanding-python/smart_audit",
            }

            logger.info(f"[Azure] Sending document ({len(file_data)} bytes) to Azure...")
            response = requests.post(url, headers=headers, data=file_data, timeout=30)
            response.raise_for_status()

            # Get operation location for polling
            operation_location = response.headers.get("operation-location")
            if not operation_location:
                logger.error("[Azure] Operation-Location header missing in response")
                return {"error": "Operation-Location header missing", "status": "failed"}

            logger.info(f"[Azure] Processing initiated. Polling for results...")

            # Poll for results
            poll_headers = {
                "Ocp-Apim-Subscription-Key": self.azure_api_key,
                "Content-Type": "application/json",
            }

            poll_start = time.time()

            while True:
                elapsed = time.time() - poll_start
                if elapsed > timeout:
                    logger.error(f"[Azure] Timeout after {elapsed:.2f}s")
                    return {"error": f"Timeout after {timeout}s", "status": "failed"}

                poll_response = requests.get(operation_location, headers=poll_headers, timeout=10)
                poll_response.raise_for_status()
                result = poll_response.json()

                status = result.get("status", "").lower()

                if status == "succeeded":
                    elapsed_time = time.time() - start_time
                    logger.info(f"[Azure] Analysis completed in {elapsed_time:.2f}s")
                    return {
                        "status": "completed",
                        "data": result,
                        "processing_time": elapsed_time
                    }
                elif status == "failed":
                    error_details = result.get("error", {})
                    logger.error(f"[Azure] Analysis failed: {error_details}")
                    return {"error": error_details, "status": "failed"}
                elif status in ["running", "notstarted"]:
                    time.sleep(2)  # Wait before next poll
                else:
                    logger.warning(f"[Azure] Unknown status: {status}")
                    time.sleep(2)

        except requests.exceptions.Timeout:
            logger.error("[Azure] Request timeout")
            return {"error": "Request timeout", "status": "failed"}
        except requests.exceptions.RequestException as e:
            logger.error(f"[Azure] HTTP error: {e}")
            return {"error": str(e), "status": "failed"}
        except Exception as e:
            logger.error(f"[Azure] Unexpected error: {e}")
            return {"error": str(e), "status": "failed"}


# Global instance
azure_client = AzureContentUnderstandingClient()
