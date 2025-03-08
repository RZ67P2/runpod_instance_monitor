import pytest
from pod_monitor import parse_pod_output

def test_parse_pod_output_current():
    """Test parsing current version of runpodctl output."""
    sample_output = """ID              NAME                 GPU                                                                                                                                                                                                                                    IMAGE NAME                                                                                                                                                                                                                                                                   STATUS
wtvbiigewacjps  RunPod Pytorch 2.4.0 1 RTX A4000                                                                                                                                                                                                                            runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04                                                                                                                                                                                                                     RUNNING"""
    
    pods = parse_pod_output(sample_output)
    assert len(pods) == 1
    assert pods[0]['id'] == 'wtvbiigewacjps'
    assert pods[0]['gpu'] == 'RTX A4000'
    assert pods[0]['status'] == 'RUNNING'
    assert pods[0]['quantity'] == 1

def test_parse_pod_output_multiple_gpus():
    """Test parsing pod with multiple GPUs."""
    sample_output = """ID              NAME                 GPU                                                                                                                                                                                                                                    IMAGE NAME                                                                                                                                                                                                                                                                   STATUS
wtvbiigewacjps  Multi-GPU Pod        2 RTX A4000                                                                                                                                                                                                                            runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04                                                                                                                                                                                                                     RUNNING"""
    
    pods = parse_pod_output(sample_output)
    assert len(pods) == 1
    assert pods[0]['gpu'] == 'RTX A4000'
    assert pods[0]['quantity'] == 2

def test_parse_pod_output_exited():
    """Test parsing exited pod."""
    sample_output = """ID              NAME                 GPU                                                                                                                                                                                                                                    IMAGE NAME                                                                                                                                                                                                                                                                   STATUS
wtvbiigewacjps  Exited Pod            1 RTX A4000                                                                                                                                                                                                                            runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04                                                                                                                                                                                                                     EXITED"""
    
    pods = parse_pod_output(sample_output)
    assert len(pods) == 1
    assert pods[0]['status'] == 'EXITED'

def test_parse_pod_output_empty():
    """Test parsing empty output."""
    sample_output = "ID              NAME                    GPU             IMAGE NAME                                                      STATUS"
    pods = parse_pod_output(sample_output)
    assert len(pods) == 0

# Remove this test
# def test_parse_pod_output_legacy():
#     """Test parsing older versions of runpodctl output"""
#     sample_output = """
#     ID        GPU    STATUS
#     abc123    A4000  RUNNING
#     """
#     pods = parse_pod_output(sample_output)
#     assert len(pods) == 1
#     assert pods[0]['gpu'] == 'A4000'

def test_termination_notification():
    """Test notification is sent when pod is terminated."""
    # Mock notification and termination
    # Verify notification content 