"""System resource monitoring using ClearML."""
import psutil
import time
import logging
from clearml import Task
import numpy as np
from typing import Dict, Any, Optional
import torch
import threading

logger = logging.getLogger(__name__)

class ResourceMonitor:
    """Monitor system resources and log them to ClearML."""

    def __init__(self, task: Optional[Task] = None):
        """Initialize the resource monitor."""
        try:
            # Use existing task if provided, otherwise get current task
            self.task = task or Task.current_task()
            if not self.task:
                logger.warning("No ClearML task found. Resource monitoring will be disabled.")
                return

            self.logger = self.task.get_logger()
            self.start_time = time.time()
            
            # Initialize metrics
            self.cpu_percent = 0
            self.memory_percent = 0
            self.disk_usage = 0
            self.network_io = {"bytes_sent": 0, "bytes_recv": 0}
            
            logger.info("Resource monitor initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing resource monitor: {e}")
            raise

    def start_monitoring(self):
        """Start resource monitoring in a background thread."""
        if hasattr(self, '_monitor_thread') and self._monitor_thread is not None:
            logger.warning("Resource monitoring already running")
            return
            
        self._stop_monitoring = threading.Event()
        self._monitor_thread = threading.Thread(
            target=self._monitor_resources,
            daemon=True
        )
        self._monitor_thread.start()
        logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring."""
        if not hasattr(self, '_monitor_thread') or self._monitor_thread is None:
            return
            
        self._stop_monitoring.set()
        self._monitor_thread.join()
        self._monitor_thread = None
        logger.info("Resource monitoring stopped")
    
    def _monitor_resources(self):
        """Monitor system resources periodically."""
        iteration = 0
        
        while not hasattr(self, '_stop_monitoring') or not self._stop_monitoring.is_set():
            try:
                # CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                self.logger.report_scalar(
                    "CPU",
                    "utilization",
                    value=cpu_percent,
                    iteration=iteration
                )
                
                self.logger.report_scalar(
                    "Memory",
                    "used_percent",
                    value=memory.percent,
                    iteration=iteration
                )
                
                self.logger.report_scalar(
                    "Disk",
                    "used_percent",
                    value=disk.percent,
                    iteration=iteration
                )
                
                # GPU metrics if available
                if torch.cuda.is_available():
                    for gpu_id in range(torch.cuda.device_count()):
                        gpu_stats = self._get_gpu_stats(gpu_id)
                        for metric, value in gpu_stats.items():
                            self.logger.report_scalar(
                                f"GPU {gpu_id}",
                                metric,
                                value=value,
                                iteration=iteration
                            )
                
                # Process-specific metrics
                process = psutil.Process()
                process_memory = process.memory_info()
                
                self.logger.report_scalar(
                    "Process",
                    "memory_rss",
                    value=process_memory.rss / (1024 * 1024),  # MB
                    iteration=iteration
                )
                
                self.logger.report_scalar(
                    "Process",
                    "memory_vms",
                    value=process_memory.vms / (1024 * 1024),  # MB
                    iteration=iteration
                )
                
                iteration += 1
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error monitoring resources: {str(e)}")
                time.sleep(30)
    
    def _get_gpu_stats(self, gpu_id: int) -> Dict[str, Any]:
        """Get GPU statistics.
        
        Args:
            gpu_id: GPU device ID
            
        Returns:
            Dictionary of GPU statistics
        """
        try:
            gpu = torch.cuda.get_device_properties(gpu_id)
            memory = torch.cuda.memory_stats(gpu_id)
            
            return {
                'memory_allocated': torch.cuda.memory_allocated(gpu_id) / (1024 * 1024),  # MB
                'memory_reserved': torch.cuda.memory_reserved(gpu_id) / (1024 * 1024),  # MB
                'max_memory_allocated': torch.cuda.max_memory_allocated(gpu_id) / (1024 * 1024),  # MB
                'memory_utilization': memory.get('allocated_bytes.all.current', 0) / gpu.total_memory * 100
            }
        except Exception as e:
            logger.error(f"Error getting GPU stats: {str(e)}")
            return {}
