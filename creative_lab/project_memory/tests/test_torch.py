import torch

def test_torch_installation():
    """Test that PyTorch is installed and working correctly."""
    # Create a simple tensor
    x = torch.tensor([1, 2, 3])
    y = torch.tensor([4, 5, 6])
    
    # Perform a basic operation
    z = x + y
    
    # Check the result
    assert torch.equal(z, torch.tensor([5, 7, 9]))
    
    # Check CUDA availability (will be False for CPU-only installation)
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    # Check PyTorch version
    print(f"PyTorch version: {torch.__version__}")
