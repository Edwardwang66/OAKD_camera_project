"""
Script to download the trained model from GitHub repository
Downloads rps_model_improved.pth or rps_model.pth from ECE176_final
"""
import os
import urllib.request
import sys


def download_file(url, filename):
    """Download a file from URL"""
    try:
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, filename)
        print(f"Successfully downloaded {filename}")
        return True
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False


def download_model():
    """Download model files from GitHub"""
    base_url = "https://github.com/edwardw005/ECE176_final/raw/main/"
    
    models = [
        "rps_model_improved.pth",
        "rps_model.pth"
    ]
    
    print("=" * 60)
    print("Downloading Rock-Paper-Scissors Model")
    print("=" * 60)
    print(f"Repository: https://github.com/edwardw005/ECE176_final")
    print()
    
    downloaded = False
    
    for model_name in models:
        if os.path.exists(model_name):
            print(f"{model_name} already exists, skipping...")
            downloaded = True
            continue
        
        url = base_url + model_name
        if download_file(url, model_name):
            downloaded = True
            break  # Only need one model
    
    if downloaded:
        print("\nModel download complete!")
        print("You can now run the game with: python main.py")
    else:
        print("\nFailed to download model.")
        print("Please manually download from:")
        print("https://github.com/edwardw005/ECE176_final")
        print("\nPlace rps_model_improved.pth or rps_model.pth in this directory.")
    
    return downloaded


if __name__ == "__main__":
    download_model()

