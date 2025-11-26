"""
Convert PyTorch Model to Blob Format for OAKD Edge AI
Converts the trained RPS model to OpenVINO blob format for running on OAKD camera
"""
import torch
import torch.onnx
import os
import subprocess
import sys


def convert_pytorch_to_blob(model_path, output_blob_path=None, input_size=(64, 64)):
    """
    Convert PyTorch model to OpenVINO blob format for OAKD
    
    Args:
        model_path: Path to PyTorch .pth model file
        output_blob_path: Output path for .blob file (optional)
        input_size: Input image size (width, height)
    
    Returns:
        str: Path to generated blob file
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    # Import model architecture
    from model_loader import RPSModel
    
    print(f"Loading PyTorch model from: {model_path}")
    
    # Load model
    model = RPSModel(num_classes=3)
    checkpoint = torch.load(model_path, map_location='cpu')
    
    # Handle different checkpoint formats
    if isinstance(checkpoint, dict):
        if 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
        elif 'state_dict' in checkpoint:
            model.load_state_dict(checkpoint['state_dict'])
        else:
            model.load_state_dict(checkpoint)
    else:
        model.load_state_dict(checkpoint)
    
    model.eval()
    
    # Create dummy input
    dummy_input = torch.randn(1, 3, input_size[1], input_size[0])
    
    # Export to ONNX
    onnx_path = model_path.replace('.pth', '.onnx')
    print(f"Exporting to ONNX: {onnx_path}")
    
    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    
    print(f"ONNX model saved to: {onnx_path}")
    
    # Convert ONNX to OpenVINO IR (Intermediate Representation)
    print("Converting ONNX to OpenVINO IR...")
    print("Note: This requires OpenVINO toolkit installed")
    print("Install with: pip install openvino")
    
    try:
        import openvino as ov
        
        # Convert ONNX to OpenVINO
        core = ov.Core()
        onnx_model = core.read_model(onnx_path)
        
        # Compile model for Myriad X (OAKD uses Myriad X VPU)
        compiled_model = core.compile_model(onnx_model, "MYRIAD")
        
        # Export to blob
        if output_blob_path is None:
            output_blob_path = model_path.replace('.pth', '.blob')
        
        # OpenVINO doesn't directly export to blob, need to use blobconverter
        print(f"\nTo convert to .blob format, use blobconverter:")
        print(f"  pip install blobconverter")
        print(f"  python -m blobconverter --onnx {onnx_path} --output-dir . --shaves 6")
        print(f"\nOr use online converter: https://blobconverter.luxonis.com/")
        
        return onnx_path
    
    except ImportError:
        print("\nOpenVINO not installed. Install with: pip install openvino")
        print(f"ONNX file saved at: {onnx_path}")
        print("You can convert ONNX to blob using:")
        print("  1. Online: https://blobconverter.luxonis.com/")
        print("  2. blobconverter: pip install blobconverter")
        return onnx_path


def main():
    """Main conversion function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert PyTorch model to OAKD blob format')
    parser.add_argument('--model', type=str, required=True,
                       help='Path to PyTorch .pth model file')
    parser.add_argument('--output', type=str, default=None,
                       help='Output blob file path (optional)')
    parser.add_argument('--input-size', type=int, nargs=2, default=[64, 64],
                       help='Input image size [width height] (default: 64 64)')
    
    args = parser.parse_args()
    
    try:
        result = convert_pytorch_to_blob(
            args.model,
            args.output,
            tuple(args.input_size)
        )
        print(f"\nConversion complete! Output: {result}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

