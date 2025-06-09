import os
try:
    if os.getenv("LIGHTWEIGHT_CLIP", "0") == "1":
        raise ImportError
    from transformers import CLIPProcessor, CLIPModel
    import torch
except Exception:  # pragma: no cover - allow tests without heavy deps
    CLIPProcessor = None  # type: ignore
    CLIPModel = None  # type: ignore
    torch = None  # type: ignore
from PIL import Image
import numpy as np


class CLIPService:
    """Wrapper around OpenAI's CLIP model with graceful fallbacks."""

    def __init__(self, model_name: str = "openai/clip-vit-base-patch32") -> None:
        self.device = "cuda" if torch is not None and torch.cuda.is_available() else "cpu"
        if CLIPModel is not None and torch is not None:
            self.model = CLIPModel.from_pretrained(model_name).to(self.device)
            self.processor = CLIPProcessor.from_pretrained(model_name)
        else:  # pragma: no cover - lightweight fallback for tests
            self.model = None
            self.processor = None

    def get_image_embedding(self, image: Image.Image) -> np.ndarray:
        if self.model is None or self.processor is None or torch is None:
            return np.zeros(512)
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        return image_features.cpu().numpy()[0]

    def get_text_embedding(self, text: str) -> np.ndarray:
        if self.model is None or self.processor is None or torch is None:
            return np.zeros(512)
        inputs = self.processor(text=text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        return text_features.cpu().numpy()[0]


clip_service = CLIPService()
