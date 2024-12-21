"""
Tests for the model caching system.
"""

import pytest
from pathlib import Path
import json
from src.models.model_cache import ModelCache

def test_model_cache_initialization(temp_cache_dir):
    """Test that ModelCache initializes correctly."""
    cache = ModelCache(temp_cache_dir)
    assert cache.cache_dir == Path(temp_cache_dir)
    assert cache.metadata_file.exists()
    assert cache.metadata == {}

def test_model_caching(temp_cache_dir):
    """Test model caching functionality."""
    cache = ModelCache(temp_cache_dir)
    
    # Create a dummy model file
    model_path = Path(temp_cache_dir) / "dummy_model"
    model_path.write_text("dummy model content")
    
    # Cache the model
    assert cache.cache_model("t5", "base", str(model_path))
    
    # Check if model is cached
    assert cache.is_model_cached("t5", "base")
    
    # Get cached model path
    cached_path = cache.get_cached_model_path("t5", "base")
    assert cached_path is not None
    assert Path(cached_path).exists()

def test_metadata_persistence(temp_cache_dir):
    """Test that metadata is saved and loaded correctly."""
    cache = ModelCache(temp_cache_dir)
    
    # Create a dummy model file
    model_path = Path(temp_cache_dir) / "dummy_model"
    model_path.write_text("dummy model content")
    
    # Cache the model
    cache.cache_model("t5", "base", str(model_path))
    
    # Create a new cache instance and check metadata
    new_cache = ModelCache(temp_cache_dir)
    assert "t5-base" in new_cache.metadata
    assert new_cache.metadata["t5-base"]["type"] == "t5"
    assert new_cache.metadata["t5-base"]["size"] == "base"

def test_clear_cache(temp_cache_dir):
    """Test cache clearing functionality."""
    cache = ModelCache(temp_cache_dir)
    
    # Create dummy model files
    models = [("t5", "base"), ("gpt2", "medium")]
    for model_type, size in models:
        model_path = Path(temp_cache_dir) / f"dummy_{model_type}_{size}"
        model_path.write_text("dummy model content")
        cache.cache_model(model_type, size, str(model_path))
    
    # Clear specific model
    cache.clear_cache("t5", "base")
    assert not cache.is_model_cached("t5", "base")
    assert cache.is_model_cached("gpt2", "medium")
    
    # Clear all models
    cache.clear_cache()
    assert not cache.is_model_cached("gpt2", "medium")
    assert cache.metadata == {}
