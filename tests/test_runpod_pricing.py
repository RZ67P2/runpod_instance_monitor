import pytest
from unittest.mock import patch
from utils.runpod_pricing import fetch_runpod_pricing

def test_pricing_structure():
    """Test the structure of returned pricing data."""
    with patch('requests.get') as mock_get:
        pricing = fetch_runpod_pricing()
        
        assert isinstance(pricing, dict)
        assert 'gpus' in pricing
        assert 'storage' in pricing
        assert 'idle' in pricing['storage']
        assert 'running' in pricing['storage']

def test_pricing_values():
    """Test the default pricing values."""
    with patch('requests.get') as mock_get:
        # Mock successful response
        mock_get.return_value.ok = True
        mock_get.return_value.text = "Mocked response"  # The actual response isn't used anymore
        
        pricing = fetch_runpod_pricing()
        
        # Check storage costs
        assert pricing['storage']['idle'] == 0.20
        assert pricing['storage']['running'] == 0.10
        
        # Check some GPU prices exist
        assert len(pricing['gpus']) > 0
        assert 'RTX A4000' in pricing['gpus']
        assert isinstance(pricing['gpus']['RTX A4000'], float)

def test_pricing_failure_handling():
    """Test handling of pricing fetch failures."""
    with patch('requests.get', side_effect=Exception("Network error")):
        pricing = fetch_runpod_pricing()
        
        # Should return default values on error
        assert pricing['storage']['idle'] == 0.20
        assert pricing['storage']['running'] == 0.10
        assert isinstance(pricing['gpus'], dict) 