import os
from pathlib import Path
from moviepy import VideoFileClip

def convert_mp4_to_gif(input_folder, output_folder=None, resize_factor=None):
    """
    Convert all MP4 files in the input folder to GIF format.
    
    Parameters:
    - input_folder: Path to folder containing MP4 files
    - output_folder: Path to save GIF files (default: same as input_folder)
    - resize_factor: Resize factor for GIFs (smaller number = smaller GIF, default: None)
    """
    if output_folder is None:
        output_folder = input_folder
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Get all MP4 files in the input folder
    input_path = Path(input_folder)
    mp4_files = list(input_path.glob('*.mp4'))
    
    if not mp4_files:
        print(f"No MP4 files found in {input_folder}")
        return
    
    print(f"Found {len(mp4_files)} MP4 files to convert...")
    
    # Convert each MP4 to GIF
    for mp4_file in mp4_files:
        gif_file = Path(output_folder) / f"{mp4_file.stem}.gif"
        print(f"Converting {mp4_file.name} to {gif_file.name}...")
        
        try:
            # Load the video clip
            video_clip = VideoFileClip(str(mp4_file))
            
            # Resize if specified
            if resize_factor is not None:
                video_clip = video_clip.resize(resize_factor)
            
            # Write the GIF file
            video_clip.write_gif(str(gif_file), fps=10)
            
            # Close the video clip to free up resources
            video_clip.close()
            
            print(f"Successfully converted {mp4_file.name} to GIF")
        
        except Exception as e:
            print(f"Error converting {mp4_file.name}: {str(e)}")

if __name__ == "__main__":
    input_folder = "data/example_invalid_videos"
    output_folder = "data/example_invalid_videos/gifs"
    
    # Convert with default parameters (no resizing)
    convert_mp4_to_gif(input_folder, output_folder)
    
    # Alternatively, you can resize to save space (0.5 = half size)
    # convert_mp4_to_gif(input_folder, output_folder, resize_factor=0.5)
