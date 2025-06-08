try:
    from transformers import CLIPProcessor, CLIPModel
except Exception:  # pragma: no cover - allow tests without heavy deps
    CLIPProcessor = None  # type: ignore
    CLIPModel = None  # type: ignore
from PIL import Image
import numpy as np
import torch


class CLIPService:
    """Singleton-like service wrapper around OpenAI's CLIP model."""

    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"CLIPService using device: {self.device}")
        if CLIPModel is not None:
            self.model = CLIPModel.from_pretrained(model_name).to(self.device)
            self.processor = CLIPProcessor.from_pretrained(model_name)
        else:  # pragma: no cover - lightweight fallback for tests
            self.model = None
            self.processor = None

    def get_image_embedding(self, image: Image.Image):
        if self.model is None or self.processor is None:
            return np.zeros(512)
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        return image_features.cpu().numpy()[0]

    def get_text_embedding(self, text: str):
        if self.model is None or self.processor is None:
            return np.zeros(512)
        inputs = self.processor(text=text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        return text_features.cpu().numpy()[0]


clip_service = CLIPService()
