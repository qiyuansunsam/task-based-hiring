import cv2
import numpy as np
import os
import shutil
from typing import List, Dict, Tuple

def extract_key_frames(video_path: str, output_folder: str, num_frames: int = 8) -> List[str]:
    """
    Extract key frames from video with improved interactivity detection
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
        # Use intelligent frame selection for better interactivity detection
        selected_frames = _select_interactive_frames(frames, num_frames)
        
        # Save selected frames
        for idx, frame in enumerate(selected_frames):
            path = os.path.join(output_folder, f'frame_{idx:04d}.jpg')
            cv2.imwrite(path, frame)
            frame_paths.append(path)
    
    return frame_paths

def _select_interactive_frames(frames: List[np.ndarray], num_frames: int = 8) -> List[np.ndarray]:
    """
    Intelligently select frames that are most likely to show interactivity
    """
    if len(frames) <= num_frames + 1:
        return frames[1:]  # Skip first frame, return rest
    
    # Skip first frame (often black/loading)
    frames = frames[1:]
    
    # Calculate frame differences to detect activity/changes
    frame_scores = []
    for i in range(len(frames)):
        score = _calculate_interactivity_score(frames[i], i, frames)
        frame_scores.append((score, i, frames[i]))
    
    # Sort by interactivity score (highest first)
    frame_scores.sort(key=lambda x: x[0], reverse=True)
    
    # Select top frames, but ensure temporal distribution
    selected_indices = []
    selected_frames = []
    
    # First, take the highest scoring frames
    for score, idx, frame in frame_scores:
        if len(selected_indices) >= num_frames:
            break
        
        # Avoid selecting frames too close together
        if not selected_indices or min(abs(idx - si) for si in selected_indices) > len(frames) // (num_frames * 2):
            selected_indices.append(idx)
            selected_frames.append(frame)
    
    # If we don't have enough frames, fill with evenly distributed ones
    while len(selected_frames) < num_frames and len(selected_frames) < len(frames):
        # Find gaps in temporal coverage
        selected_indices.sort()
        for i in range(len(frames)):
            if i not in selected_indices:
                # Check if this frame adds good temporal coverage
                if not selected_indices or min(abs(i - si) for si in selected_indices) > 5:
                    selected_indices.append(i)
                    selected_frames.append(frames[i])
                    break
        else:
            break
    
    # Sort selected frames by original temporal order
    indexed_frames = [(selected_indices[i], selected_frames[i]) for i in range(len(selected_frames))]
    indexed_frames.sort(key=lambda x: x[0])
    
    return [frame for _, frame in indexed_frames]

def _calculate_interactivity_score(frame: np.ndarray, frame_idx: int, all_frames: List[np.ndarray]) -> float:
    """
    Calculate a score indicating how likely a frame is to show interactivity
    """
    score = 0.0
    
    # 1. Detect potential cursor/mouse indicators
    score += _detect_cursor_indicators(frame) * 3.0
    
    # 2. Detect UI state changes (hover effects, selections)
    score += _detect_ui_state_changes(frame) * 2.0
    
    # 3. Detect form interactions (focus states, input fields)
    score += _detect_form_interactions(frame) * 2.5
    
    # 4. Detect modal dialogs or popups
    score += _detect_modal_dialogs(frame) * 2.0
    
    # 5. Calculate frame difference (activity level)
    if frame_idx > 0 and frame_idx < len(all_frames) - 1:
        prev_frame = all_frames[frame_idx - 1]
        next_frame = all_frames[frame_idx + 1]
        score += _calculate_frame_difference(frame, prev_frame, next_frame) * 1.0
    
    # 6. Avoid completely black or white frames
    score += _avoid_blank_frames(frame) * 1.5
    
    # 7. Prefer frames with rich UI content
    score += _detect_ui_complexity(frame) * 1.0
    
    return score

def _detect_cursor_indicators(frame: np.ndarray) -> float:
    """
    Detect potential cursor or mouse interaction indicators
    """
    score = 0.0
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Look for small bright spots that could be cursors
    # Cursors are typically small, bright, and have distinct shapes
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if 10 < area < 200:  # Cursor-like size
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            if 0.5 < aspect_ratio < 2.0:  # Reasonable cursor proportions
                score += 0.3
    
    return min(score, 1.0)

def _detect_ui_state_changes(frame: np.ndarray) -> float:
    """
    Detect UI elements that might indicate hover states or selections
    """
    score = 0.0
    
    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Look for highlighted elements (often blue, green, or bright colors)
    # Define ranges for common highlight colors
    highlight_ranges = [
        ([100, 50, 50], [130, 255, 255]),  # Blue range
        ([35, 50, 50], [85, 255, 255]),    # Green range
        ([15, 50, 50], [35, 255, 255]),    # Orange/yellow range
    ]
    
    for lower, upper in highlight_ranges:
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
        highlight_pixels = cv2.countNonZero(mask)
        if highlight_pixels > 100:  # Significant highlighted area
            score += 0.2
    
    return min(score, 1.0)

def _detect_form_interactions(frame: np.ndarray) -> float:
    """
    Detect form fields with focus states or active cursors
    """
    score = 0.0
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect rectangular shapes that could be form fields
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        # Approximate contour to polygon
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        if len(approx) == 4:  # Rectangular shape
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            area = w * h
            
            # Form field characteristics
            if 2 < aspect_ratio < 10 and 500 < area < 50000:
                score += 0.1
    
    return min(score, 1.0)

def _detect_modal_dialogs(frame: np.ndarray) -> float:
    """
    Detect modal dialogs or popup windows
    """
    score = 0.0
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Look for overlay patterns (darker background with bright foreground)
    # Calculate histogram to detect bimodal distribution
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    
    # Find peaks in histogram
    peaks = []
    for i in range(1, 255):
        if hist[i] > hist[i-1] and hist[i] > hist[i+1] and hist[i] > 1000:
            peaks.append(i)
    
    # Modal dialogs often create bimodal intensity distribution
    if len(peaks) >= 2:
        peak_separation = max(peaks) - min(peaks)
        if peak_separation > 100:  # Significant contrast
            score += 0.5
    
    return min(score, 1.0)

def _calculate_frame_difference(current: np.ndarray, prev: np.ndarray, next: np.ndarray) -> float:
    """
    Calculate how much a frame differs from its neighbors (indicates activity)
    """
    # Convert to grayscale for comparison
    curr_gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    next_gray = cv2.cvtColor(next, cv2.COLOR_BGR2GRAY)
    
    # Calculate differences
    diff_prev = cv2.absdiff(curr_gray, prev_gray)
    diff_next = cv2.absdiff(curr_gray, next_gray)
    
    # Sum of differences normalized
    total_diff = np.sum(diff_prev) + np.sum(diff_next)
    max_possible = curr_gray.size * 255 * 2
    
    return total_diff / max_possible

def _avoid_blank_frames(frame: np.ndarray) -> float:
    """
    Penalize completely black, white, or very uniform frames
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Calculate standard deviation of pixel intensities
    std_dev = np.std(gray)
    
    # Frames with very low std dev are likely blank or uniform
    if std_dev < 10:
        return 0.0  # Heavily penalize blank frames
    elif std_dev < 30:
        return 0.3  # Moderately penalize uniform frames
    else:
        return 1.0  # Reward frames with good variation

def _detect_ui_complexity(frame: np.ndarray) -> float:
    """
    Detect UI complexity (more complex UIs are more likely to be interactive)
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Use edge detection to measure UI complexity
    edges = cv2.Canny(gray, 50, 150)
    edge_density = np.sum(edges > 0) / edges.size
    
    # Normalize edge density to 0-1 score
    return min(edge_density * 10, 1.0)
