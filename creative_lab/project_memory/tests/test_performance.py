"""
Performance tests for the Project Memory System.
Tests system performance under various conditions and loads.
"""

import pytest
from app import ProjectMemory
import time
from pathlib import Path

@pytest.fixture
def test_memory(tmp_path):
    """Create a test memory instance with temporary directory"""
    memory = ProjectMemory()
    memory.base_path = tmp_path / "test_memory"
    memory.entries_path = memory.base_path / "entries"
    memory.abstracts_path = memory.base_path / "abstracts"
    memory.entries_path.mkdir(parents=True)
    memory.abstracts_path.mkdir(parents=True)
    return memory

def test_entry_save_performance(benchmark, test_memory):
    """Benchmark entry saving performance"""
    content = "This is a test entry for performance testing." * 10
    
    def save_entry():
        return test_memory.save_entry(content, "Performance Test")
    
    # Run the benchmark
    result = benchmark(save_entry)
    
    # Verify the operation was successful
    assert Path(result["entry_file"]).exists()
    assert Path(result["abstract_file"]).exists()

def test_abstract_generation_performance(benchmark, test_memory):
    """Benchmark abstract generation performance for different content sizes"""
    # Test with different content sizes
    content_sizes = [100, 500, 1000, 5000]
    
    for size in content_sizes:
        content = " ".join(["This is sentence {}".format(i) for i in range(size)])
        
        def generate_abstract():
            return test_memory.generate_abstract(content)
        
        # Run the benchmark
        result = benchmark(generate_abstract)
        
        # Verify the result
        assert isinstance(result, str)
        assert len(result) > 0

def test_entry_retrieval_performance(benchmark, test_memory):
    """Benchmark entry retrieval performance with different numbers of entries"""
    # Create test entries
    num_entries = 100
    for i in range(num_entries):
        test_memory.save_entry(
            f"Content for entry {i}",
            f"Title {i}"
        )
    
    def get_entries():
        return test_memory.get_all_entries()
    
    # Run the benchmark
    results = benchmark(get_entries)
    
    # Verify results
    assert len(results) == num_entries

@pytest.mark.asyncio
async def test_concurrent_performance(test_memory):
    """Test performance under concurrent load"""
    import asyncio
    import time
    
    async def save_entry(i):
        content = f"Content for concurrent test {i}"
        title = f"Concurrent Test {i}"
        return test_memory.save_entry(content, title)
    
    # Measure time to save multiple entries concurrently
    start_time = time.time()
    
    # Create multiple tasks
    tasks = [save_entry(i) for i in range(20)]
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Verify all operations were successful
    assert len(results) == 20
    for result in results:
        assert Path(result["entry_file"]).exists()
        assert Path(result["abstract_file"]).exists()
    
    # Check execution time is reasonable
    assert execution_time < 60  # Should complete within 60 seconds

def test_memory_usage(test_memory):
    """Test memory usage during operations"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Perform operations that might impact memory
    large_content = "Test content " * 1000
    for i in range(10):
        test_memory.save_entry(large_content, f"Memory Test {i}")
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Check memory increase is reasonable (less than 100MB)
    assert memory_increase < 100 * 1024 * 1024

def test_storage_efficiency(test_memory):
    """Test storage space efficiency"""
    import os
    
    # Create test content
    content = "Test content " * 100
    
    # Save multiple entries
    for i in range(10):
        test_memory.save_entry(content, f"Storage Test {i}")
    
    # Calculate total storage used
    total_size = 0
    for path in [test_memory.entries_path, test_memory.abstracts_path]:
        for file_path in path.glob("**/*"):
            if file_path.is_file():
                total_size += os.path.getsize(file_path)
    
    # Check storage efficiency (should be less than 1MB for test data)
    assert total_size < 1024 * 1024
