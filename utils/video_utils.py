import cv2
import os
import tempfile
import subprocess
from PIL import Image
import logging

logger = logging.getLogger(__name__)

def process_video_frames(input_path, output_path, style, style_transfer):
    """Process video by applying style transfer to each frame"""
    try:
        # Create temporary directory for frames
        with tempfile.TemporaryDirectory() as temp_dir:
            frames_dir = os.path.join(temp_dir, 'frames')
            os.makedirs(frames_dir, exist_ok=True)
            
            # Extract frames using OpenCV
            cap = cv2.VideoCapture(input_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            logger.info(f"Processing {frame_count} frames at {fps} FPS")
            
            # Process frames
            frame_paths = []
            frame_num = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Save frame
                frame_path = os.path.join(frames_dir, f'frame_{frame_num:06d}.jpg')
                cv2.imwrite(frame_path, frame)
                
                # Apply style transfer
                styled_frame_path = os.path.join(frames_dir, f'styled_{frame_num:06d}.jpg')
                style_transfer.apply_style(frame_path, styled_frame_path, style)
                
                frame_paths.append(styled_frame_path)
                frame_num += 1
                
                # Log progress every 30 frames
                if frame_num % 30 == 0:
                    logger.info(f"Processed {frame_num}/{frame_count} frames")
            
            cap.release()
            
            # Combine frames back to video using OpenCV
            if frame_paths:
                combine_frames_to_video(frame_paths, output_path, fps)
            
            logger.info(f"Video processing completed: {output_path}")
    
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        raise

def combine_frames_to_video(frame_paths, output_path, fps):
    """Combine processed frames back into a video"""
    if not frame_paths:
        raise ValueError("No frames to combine")
    
    # Get frame dimensions
    first_frame = cv2.imread(frame_paths[0])
    height, width, layers = first_frame.shape
    
    # Define codec and create VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    try:
        for frame_path in frame_paths:
            frame = cv2.imread(frame_path)
            if frame is not None:
                video_writer.write(frame)
    finally:
        video_writer.release()