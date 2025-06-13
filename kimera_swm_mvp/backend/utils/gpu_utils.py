import torch
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_compute_device() -> str:
    """
    Checks for CUDA-enabled GPU and returns the appropriate torch device.

    Returns:
        str: 'cuda' if a GPU is available, otherwise 'cpu'.
    """
    if torch.cuda.is_available():
        device = 'cuda'
        logger.info("✅ CUDA GPU detected. Using 'cuda' device for computations.")
    else:
        device = 'cpu'
        logger.warning("⚠️ No CUDA GPU detected. Falling back to 'cpu' for computations.")
    return device 