import pytest
import psutil

def test_psutil_available():
    processes = list(psutil.process_iter(['pid', 'name']))
    assert len(processes) > 0

def test_process_has_name():
    for proc in psutil.process_iter(['name']):
        assert proc.info['name'] is not None
        break

def test_memory_info():
    for proc in psutil.process_iter(['memory_info']):
        mem = proc.info['memory_info']
        assert mem is not None
        break