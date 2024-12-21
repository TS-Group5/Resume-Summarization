"""
This module handles caching of transformer models to avoid repeated downloads.
"""

import os
from pathlib import Path
import shutil
import json
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelCache:
    """Manages downloading and caching of transformer models."""
    
    def __init__(self, cache_dir=None):
        """Initialize the model cache.
        
        Args:
            cache_dir (str, optional): Directory to store cached models.
                                     Defaults to 'models/cache' in the project root.
        """
        if cache_dir is None:
            # Get the project root directory (two levels up from this file)
            project_root = Path(__file__).parent.parent.parent
            cache_dir = project_root / "models" / "cache"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Create or load cache metadata
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self):
        """Load or create cache metadata."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self):
        """Save cache metadata."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def get_model_dir(self, model_type, model_size):
        """Get the directory for a specific model."""
        model_name = f"{model_type}-{model_size}"
        return self.cache_dir / model_name
    
    def is_model_cached(self, model_type, model_size):
        """Check if a model is already cached."""
        model_name = f"{model_type}-{model_size}"
        model_dir = self.get_model_dir(model_type, model_size)
        
        # Check if model exists in cache and metadata
        if model_dir.exists() and model_name in self.metadata:
            return True
        return False
    
    def cache_model(self, model_type, model_size, model_path):
        """Cache a model for future use.
        
        Args:
            model_type (str): Type of the model (e.g., 't5', 'gpt2', 'bart')
            model_size (str): Size of the model (e.g., 'base', 'medium', 'large')
            model_path (str): Path to the downloaded model files
        """
        model_name = f"{model_type}-{model_size}"
        model_dir = self.get_model_dir(model_type, model_size)
        
        try:
            # Create model directory if it doesn't exist
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy model files to cache
            if os.path.isdir(model_path):
                shutil.copytree(model_path, model_dir, dirs_exist_ok=True)
            else:
                shutil.copy2(model_path, model_dir)
            
            # Update metadata
            self.metadata[model_name] = {
                "cached_at": datetime.now().isoformat(),
                "type": model_type,
                "size": model_size,
                "path": str(model_dir)
            }
            self._save_metadata()
            
            logger.info(f"Successfully cached model: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error caching model {model_name}: {str(e)}")
            return False
    
    def get_cached_model_path(self, model_type, model_size):
        """Get the path to a cached model.
        
        Args:
            model_type (str): Type of the model
            model_size (str): Size of the model
            
        Returns:
            str: Path to the cached model, or None if not cached
        """
        model_name = f"{model_type}-{model_size}"
        if model_name in self.metadata:
            model_dir = self.get_model_dir(model_type, model_size)
            if model_dir.exists():
                return str(model_dir)
        return None
    
    def clear_cache(self, model_type=None, model_size=None):
        """Clear the model cache.
        
        Args:
            model_type (str, optional): Type of model to clear. If None, clears all.
            model_size (str, optional): Size of model to clear. If None, clears all.
        """
        try:
            if model_type and model_size:
                # Clear specific model
                model_name = f"{model_type}-{model_size}"
                model_dir = self.get_model_dir(model_type, model_size)
                if model_dir.exists():
                    shutil.rmtree(model_dir)
                if model_name in self.metadata:
                    del self.metadata[model_name]
            else:
                # Clear all models
                if self.cache_dir.exists():
                    shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True)
                self.metadata = {}
            
            self._save_metadata()
            logger.info("Cache cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False
