import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def compress_with_filters(input_path, output_path, bitrate='96k', highpass=100, lowpass=15000):
    """
    Compress an audio file using FFmpeg with specified filters.

    :param input_path: Path to the input file
    :param output_path: Path to the output file
    :param bitrate: Target bitrate (default: 96k)
    :param highpass: High-pass filter frequency (default: 100Hz)
    :param lowpass: Low-pass filter frequency (default: 15kHz)
    """
    command = [
        'ffmpeg', '-i', input_path,
        '-b:a', bitrate, '-af', f"highpass=f={highpass}, lowpass=f={lowpass}", '-y',
        output_path
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def compress_file_parallel(file_path, extract_path, compressed_path):
    """
    Compress a single file, preserving relative path structure.

    :param file_path: Path to the original file
    :param extract_path: Base path of the original files
    :param compressed_path: Base path for compressed files
    :return: Path to the compressed file
    """
    relative_path = os.path.relpath(file_path, extract_path)
    output_file_path = os.path.join(compressed_path, f"{relative_path}")
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    compress_with_filters(file_path, output_file_path)
    return output_file_path

def main():
    # Define paths
    extract_path = "./sounds"  # Path to the extracted folder
    compressed_path = "./compressed_sounds"  # Output folder for compressed files
    
    # Gather files
    file_list = []
    for root, dirs, files in os.walk(extract_path):
        for file in files:
            if file.endswith('.ogg'):
                file_list.append(os.path.join(root, file))

    # Compress files in parallel
    os.makedirs(compressed_path, exist_ok=True)
    with ThreadPoolExecutor(max_workers=8) as executor:
        compressed_files = list(executor.map(
            lambda f: compress_file_parallel(f, extract_path, compressed_path),
            file_list
        ))

    # Calculate sizes
    original_total_size = sum(Path(file).stat().st_size for file in file_list) / (1024 * 1024)  # MB
    compressed_total_size = sum(Path(file).stat().st_size for file in compressed_files) / (1024 * 1024)  # MB

    print(f"Original Total Size: {original_total_size:.2f} MB")
    print(f"Compressed Total Size: {compressed_total_size:.2f} MB")

if __name__ == "__main__":
    main()
