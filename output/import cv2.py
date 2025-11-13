import cv2
import numpy as np
import pandas as pd
from pathlib import Path

class DroneTrajectoryExtractor:
    def __init__(self, video_path, output_csv='drone_trajectories.csv'):
        """
        Initialize the drone trajectory extractor.
        
        Args:
            video_path: Path to the input video file
            output_csv: Path for the output CSV file
        """
        self.video_path = video_path
        self.output_csv = output_csv
        self.trajectories = []
        
    def extract_trajectories(self, method='background_subtraction', 
                            min_contour_area=100, max_contour_area=10000):
        """
        Extract drone trajectories from video.
        
        Args:
            method: Detection method ('background_subtraction' or 'optical_flow')
            min_contour_area: Minimum contour area to consider as drone
            max_contour_area: Maximum contour area to consider as drone
        """
        cap = cv2.VideoCapture(self.video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {self.video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"Processing video: {frame_count} frames at {fps} FPS")
        
        if method == 'background_subtraction':
            self._extract_with_background_subtraction(cap, min_contour_area, max_contour_area)
        elif method == 'optical_flow':
            self._extract_with_optical_flow(cap)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        cap.release()
        
    def _extract_with_background_subtraction(self, cap, min_area, max_area):
        """Extract trajectories using background subtraction method."""
        # Create background subtractor
        back_sub = cv2.createBackgroundSubtractorMOG2(
            history=500, varThreshold=16, detectShadows=True
        )
        
        frame_number = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Apply background subtraction
            fg_mask = back_sub.apply(frame)
            
            # Remove shadows (they appear as gray)
            _, fg_mask = cv2.threshold(fg_mask, 250, 255, cv2.THRESH_BINARY)
            
            # Apply morphological operations to remove noise
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(
                fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Process each contour
            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                
                if min_area < area < max_area:
                    # Calculate centroid
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        
                        # Get bounding box
                        x, y, w, h = cv2.boundingRect(contour)
                        
                        # Store trajectory point
                        self.trajectories.append({
                            'frame': frame_number,
                            'timestamp': frame_number / cap.get(cv2.CAP_PROP_FPS),
                            'drone_id': i,  # Simple ID based on detection order
                            'center_x': cx,
                            'center_y': cy,
                            'bbox_x': x,
                            'bbox_y': y,
                            'bbox_width': w,
                            'bbox_height': h,
                            'contour_area': area
                        })
            
            frame_number += 1
            
            if frame_number % 100 == 0:
                print(f"Processed {frame_number} frames...")
    
    def _extract_with_optical_flow(self, cap):
        """Extract trajectories using optical flow method."""
        # Parameters for ShiTomasi corner detection
        feature_params = dict(
            maxCorners=100,
            qualityLevel=0.3,
            minDistance=7,
            blockSize=7
        )
        
        # Parameters for Lucas-Kanade optical flow
        lk_params = dict(
            winSize=(15, 15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
        )
        
        ret, old_frame = cap.read()
        if not ret:
            return
        
        old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
        p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)
        
        frame_number = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if p0 is not None and len(p0) > 0:
                # Calculate optical flow
                p1, st, err = cv2.calcOpticalFlowPyrLK(
                    old_gray, frame_gray, p0, None, **lk_params
                )
                
                if p1 is not None:
                    # Select good points
                    good_new = p1[st == 1]
                    good_old = p0[st == 1]
                    
                    # Store trajectory points
                    for i, (new, old) in enumerate(zip(good_new, good_old)):
                        x_new, y_new = new.ravel()
                        x_old, y_old = old.ravel()
                        
                        # Calculate movement
                        distance = np.sqrt((x_new - x_old)**2 + (y_new - y_old)**2)
                        
                        # Only store if there's significant movement
                        if distance > 1:
                            self.trajectories.append({
                                'frame': frame_number,
                                'timestamp': frame_number / cap.get(cv2.CAP_PROP_FPS),
                                'drone_id': i,
                                'center_x': int(x_new),
                                'center_y': int(y_new),
                                'velocity_x': x_new - x_old,
                                'velocity_y': y_new - y_old,
                                'distance_moved': distance
                            })
                    
                    # Update points for next iteration
                    p0 = good_new.reshape(-1, 1, 2)
            
            # Refresh feature points periodically
            if frame_number % 30 == 0:
                p0 = cv2.goodFeaturesToTrack(frame_gray, mask=None, **feature_params)
            
            old_gray = frame_gray.copy()
            frame_number += 1
            
            if frame_number % 100 == 0:
                print(f"Processed {frame_number} frames...")
    
    def save_to_csv(self):
        """Save extracted trajectories to CSV file."""
        if not self.trajectories:
            print("No trajectories to save!")
            return
        
        df = pd.DataFrame(self.trajectories)
        df.to_csv(self.output_csv, index=False)
        print(f"\nTrajectories saved to: {self.output_csv}")
        print(f"Total trajectory points: {len(df)}")
        print(f"\nDataFrame info:")
        print(df.head())
        
    def visualize_trajectories(self, output_video='trajectories_visualization.mp4'):
        """Create a video with trajectory visualization."""
        if not self.trajectories:
            print("No trajectories to visualize!")
            return
        
        df = pd.DataFrame(self.trajectories)
        
        cap = cv2.VideoCapture(self.video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
        
        frame_number = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Get trajectories for current frame
            frame_data = df[df['frame'] == frame_number]
            
            for _, row in frame_data.iterrows():
                # Draw circle at drone position
                cv2.circle(frame, (int(row['center_x']), int(row['center_y'])), 
                          5, (0, 255, 0), -1)
                
                # Draw bounding box if available
                if 'bbox_x' in row:
                    cv2.rectangle(frame, 
                                (int(row['bbox_x']), int(row['bbox_y'])),
                                (int(row['bbox_x'] + row['bbox_width']), 
                                 int(row['bbox_y'] + row['bbox_height'])),
                                (255, 0, 0), 2)
            
            # Draw trajectory trails
            if frame_number > 0:
                past_frames = df[df['frame'] < frame_number]
                past_frames = past_frames[past_frames['frame'] > frame_number - 30]
                
                for drone_id in past_frames['drone_id'].unique():
                    drone_trail = past_frames[past_frames['drone_id'] == drone_id]
                    points = drone_trail[['center_x', 'center_y']].values.astype(int)
                    
                    if len(points) > 1:
                        cv2.polylines(frame, [points], False, (0, 0, 255), 2)
            
            out.write(frame)
            frame_number += 1
            
            if frame_number % 100 == 0:
                print(f"Visualized {frame_number} frames...")
        
        cap.release()
        out.release()
        print(f"\nVisualization saved to: {output_video}")


# Example usage
if __name__ == "__main__":
    # Initialize extractor
    extractor = DroneTrajectoryExtractor(
        video_path='/Users/brianvisas/DroneSimulation/output/multi_view.mp4',
        output_csv='/Users/brianvisas/DroneSimulation/output/drone_trajectories.csv'
    )
    
    # Extract trajectories using background subtraction
    print("Extracting trajectories...")
    extractor.extract_trajectories(
        method='background_subtraction',  # or 'optical_flow'
        min_contour_area=100,
        max_contour_area=10000
    )
    
    # Save to CSV
    extractor.save_to_csv()
    
    # Optional: Create visualization video
    # extractor.visualize_trajectories('output_visualization.mp4')