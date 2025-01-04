# Evaluation Documentation

## MetricsCalculator

The `MetricsCalculator` class handles the calculation of various evaluation metrics.

### Class Definition
```python
class MetricsCalculator:
    def __init__(self):
        """Initialize metrics calculator with required models and tokenizers."""
```

### Key Methods

#### calculate_bleu
```python
def calculate_bleu(self, reference: str, candidate: str) -> float:
    """Calculate BLEU score.
    
    Args:
        reference (str): Reference text
        candidate (str): Generated text
        
    Returns:
        float: BLEU score
    """
```

#### calculate_rouge
```python
def calculate_rouge(self, reference: str, candidate: str) -> Dict[str, float]:
    """Calculate ROUGE scores.
    
    Args:
        reference (str): Reference text
        candidate (str): Generated text
        
    Returns:
        Dict[str, float]: Dictionary of ROUGE scores
    """
```

#### calculate_bert_score
```python
def calculate_bert_score(self, reference: str, candidate: str) -> float:
    """Calculate BERTScore.
    
    Args:
        reference (str): Reference text
        candidate (str): Generated text
        
    Returns:
        float: BERTScore
    """
```

## OutputEvaluator

The `OutputEvaluator` class evaluates and validates generated summaries.

### Class Definition
```python
class OutputEvaluator:
    def __init__(self, metrics_calculator: MetricsCalculator):
        """Initialize output evaluator.
        
        Args:
            metrics_calculator (MetricsCalculator): Instance for calculating metrics
        """
```

### Key Methods

#### evaluate_summary
```python
def evaluate_summary(self, generated: str, reference: str) -> Dict[str, float]:
    """Evaluate generated summary against reference.
    
    Args:
        generated (str): Generated summary
        reference (str): Reference summary
        
    Returns:
        Dict[str, float]: Dictionary of evaluation metrics
    """
```

#### validate_output
```python
def validate_output(self, summary: str) -> bool:
    """Validate summary meets quality requirements.
    
    Args:
        summary (str): Generated summary
        
    Returns:
        bool: True if summary meets requirements
    """
```
