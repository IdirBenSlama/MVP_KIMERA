#!/usr/bin/env python3
"""
Script to convert BAAI/bge-m3 model to ONNX format for optimized inference.
This script handles the conversion process and saves the ONNX model for use with ONNX Runtime.
"""

import os
import logging
from pathlib import Path

try:
    from optimum.onnxruntime import ORTModelForFeatureExtraction
    from transformers import AutoTokenizer
    import torch
except ImportError as e:
    print(f"Missing required packages: {e}")
    print("Please install: pip install optimum[onnxruntime] transformers torch")
    exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_bge_to_onnx(
    model_name: str = "BAAI/bge-m3",
    output_dir: str = "./models/bge-m3-onnx",
    optimize: bool = True
):
    """
    Convert BGE model to ONNX format.
    
    Args:
        model_name: HuggingFace model name
        output_dir: Directory to save ONNX model
        optimize: Whether to optimize the ONNX model
    """
    
    logger.info(f"Converting {model_name} to ONNX format...")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load and convert model
        logger.info("Loading model for conversion...")
        ort_model = ORTModelForFeatureExtraction.from_pretrained(
            model_name,
            export=True,
            provider="CPUExecutionProvider"  # Start with CPU, can be changed later
        )
        
        # Save ONNX model
        logger.info(f"Saving ONNX model to {output_dir}...")
        ort_model.save_pretrained(output_dir)
        
        # Save tokenizer
        logger.info("Saving tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.save_pretrained(output_dir)
        
        # Test the converted model
        logger.info("Testing converted model...")
        test_text = "This is a test sentence for embedding."
        inputs = tokenizer(test_text, return_tensors="pt", padding=True, truncation=True)
        
        with torch.no_grad():
            outputs = ort_model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1)  # Mean pooling
            logger.info(f"Test successful! Embedding shape: {embeddings.shape}")
        
        logger.info("✅ ONNX conversion completed successfully!")
        logger.info(f"Model saved to: {output_path.absolute()}")
        
        # Create a simple config file
        config_content = f"""# ONNX Model Configuration
MODEL_NAME={model_name}
ONNX_MODEL_PATH={output_dir}
USE_ONNX=1
EMBEDDING_DIM={embeddings.shape[-1]}
"""
        
        with open(output_path / "config.env", "w") as f:
            f.write(config_content)
        
        logger.info("Configuration file created: config.env")
        
    except Exception as e:
        logger.error(f"❌ Conversion failed: {e}")
        raise

def verify_onnx_model(model_dir: str = "./models/bge-m3-onnx"):
    """Verify the ONNX model works correctly."""
    
    try:
        import onnxruntime as ort
        from transformers import AutoTokenizer
        
        logger.info(f"Verifying ONNX model in {model_dir}...")
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_dir)
        
        # Load ONNX model
        providers = ['CPUExecutionProvider']
        if ort.get_device() == 'GPU':
            providers.insert(0, 'CUDAExecutionProvider')
            
        session = ort.InferenceSession(f"{model_dir}/model.onnx", providers=providers)
        
        # Test inference
        test_texts = [
            "This is a test sentence.",
            "Another example for testing embeddings.",
            "Final test case for verification."
        ]
        
        for i, text in enumerate(test_texts):
            inputs = tokenizer(text, return_tensors="np", padding=True, truncation=True, max_length=512)
            outputs = session.run(None, {
                'input_ids': inputs['input_ids'],
                'attention_mask': inputs['attention_mask']
            })
            
            embedding = outputs[0][0]  # Remove batch dimension
            logger.info(f"Test {i+1}: Embedding shape {embedding.shape}, norm: {(embedding**2).sum()**0.5:.4f}")
        
        logger.info("✅ ONNX model verification successful!")
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert BGE model to ONNX format")
    parser.add_argument("--model", default="BAAI/bge-m3", help="Model name to convert")
    parser.add_argument("--output", default="./models/bge-m3-onnx", help="Output directory")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing ONNX model")
    parser.add_argument("--no-optimize", action="store_true", help="Skip optimization")
    
    args = parser.parse_args()
    
    if args.verify_only:
        verify_onnx_model(args.output)
    else:
        convert_bge_to_onnx(
            model_name=args.model,
            output_dir=args.output,
            optimize=not args.no_optimize
        )
        
        # Verify after conversion
        verify_onnx_model(args.output)