"""
This module contains the configuration for different models.
"""

T5_CONFIG = {
    'model': {
        'name': 't5-base',
        'generation_params': {
            'max_length': 200,
            'min_length': 100,
            'num_beams': 5,
            'length_penalty': 1.5,
            'early_stopping': True,
            'no_repeat_ngram_size': 3,
            'num_beam_groups': 5,
            'diversity_penalty': 0.5,
            'repetition_penalty': 1.2,
            'do_sample': False
        }
    }
}

GPT2_CONFIG = {
    'model': {
        'name': 'gpt2-medium',
        'generation_params': {
            'max_new_tokens': 150,
            'num_beams': 5,
            'length_penalty': 1.2,
            'early_stopping': True,
            'no_repeat_ngram_size': 3,
            'do_sample': True,
            'temperature': 0.6,
            'top_p': 0.9
        }
    }
}

BART_CONFIG = {
    'model': {
        'name': 'facebook/bart-large',
        'generation_params': {
            'max_length': 150,
            'num_beams': 5,
            'length_penalty': 1.2,
            'early_stopping': True,
            'no_repeat_ngram_size': 3,
            'do_sample': True,
            'temperature': 0.6,
            'top_p': 0.9,
            'repetition_penalty': 1.2
        }
    }
}
