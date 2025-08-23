import cv2
import numpy as np
import os
import shutil
from typing import List

def extract_key_frames(video_path: str, output_folder: str, num_frames: int = 8) -> List[str]:
    """
    Extract key frames from video - generates 9 frames, removes first black one
    Returns list of saved frame paths (8 final frames)
    """
    # Clean up old frames first
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    frames = []
    frame_paths = []
    
    # Read all frames
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    
    cap.release()
    
    if len(frames) <= 9:
        # If video has 9 or fewer frames, save all except first
        for i, frame in enumerate(frames[1:]):  # Skip first frame
            path = os.path.join(output_folder, f'frame_{i:04d}.jpg')
            cv2.imwrite(path, frame)
            frame_paths.append(path)
    else:
        # Generate 9 frames evenly distributed, then remove first
        total_frames = len(frames)
        step = total_frames // 9
        
        # Select 9 frames evenly distributed
        selected_indices = []
        for i in range(9):
            frame_idx = i * step
            if frame_idx < total_frames:
                selected_indices.append(frame_idx)
        
        # Remove first frame (black frame) and save the rest
        for idx, frame_idx in enumerate(selected_indices[1:]):  # Skip first frame
            path = os.path.join(output_folder, f'frame_{idx:04d}.jpg')
            cv2.imwrite(path, frames[frame_idx])
            frame_paths.append(path)
    
    return frame_paths
