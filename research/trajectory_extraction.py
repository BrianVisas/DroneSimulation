#!/usr/bin/env python3
"""Extract 2-D motion trajectories from recorded drone-simulation video.

This maintained research utility is derived from Brian Visas' historical
`openCV trajectory extraction` commit:
8835e7180176cc11edf68a0ce8bcf041199c6c3f.

It keeps the original two experimental extraction approaches while replacing
machine-specific paths with a reusable command-line interface.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Literal

import cv2
import numpy as np
import pandas as pd

ExtractionMethod = Literal["background_subtraction", "optical_flow"]


class DroneTrajectoryExtractor:
    """Extract image-space trajectory observations from an MP4/video file."""

    def __init__(self, video_path: Path, output_csv: Path) -> None:
        self.video_path = Path(video_path)
        self.output_csv = Path(output_csv)
        self.trajectories: list[dict] = []

    def extract_trajectories(
        self,
        method: ExtractionMethod = "background_subtraction",
        min_contour_area: float = 100.0,
        max_contour_area: float = 10_000.0,
    ) -> pd.DataFrame:
        """Run the selected extractor and return the resulting observations."""
        cap = cv2.VideoCapture(str(self.video_path))
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {self.video_path}")

        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            print(f"Processing {frame_count} frames at {fps:.3f} FPS")

            if method == "background_subtraction":
                self._extract_with_background_subtraction(
                    cap,
                    min_area=min_contour_area,
                    max_area=max_contour_area,
                    fps=fps,
                )
            elif method == "optical_flow":
                self._extract_with_optical_flow(cap, fps=fps)
            else:
                raise ValueError(f"Unsupported extraction method: {method}")
        finally:
            cap.release()

        return pd.DataFrame(self.trajectories)

    def _extract_with_background_subtraction(
        self,
        cap: cv2.VideoCapture,
        *,
        min_area: float,
        max_area: float,
        fps: float,
    ) -> None:
        """Extract moving regions using MOG2 background subtraction."""
        back_sub = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=16,
            detectShadows=True,
        )
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        frame_number = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            fg_mask = back_sub.apply(frame)
            _, fg_mask = cv2.threshold(fg_mask, 250, 255, cv2.THRESH_BINARY)
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

            contours, _ = cv2.findContours(
                fg_mask,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE,
            )

            for detection_index, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if not min_area < area < max_area:
                    continue

                moments = cv2.moments(contour)
                if moments["m00"] == 0:
                    continue

                center_x = int(moments["m10"] / moments["m00"])
                center_y = int(moments["m01"] / moments["m00"])
                x, y, width, height = cv2.boundingRect(contour)

                self.trajectories.append(
                    {
                        "frame": frame_number,
                        "timestamp": self._timestamp(frame_number, fps),
                        "track_id": detection_index,
                        "center_x": center_x,
                        "center_y": center_y,
                        "bbox_x": x,
                        "bbox_y": y,
                        "bbox_width": width,
                        "bbox_height": height,
                        "contour_area": float(area),
                        "method": "background_subtraction",
                    }
                )

            frame_number += 1

    def _extract_with_optical_flow(
        self,
        cap: cv2.VideoCapture,
        *,
        fps: float,
    ) -> None:
        """Extract moving image features with pyramidal Lucas-Kanade flow."""
        feature_params = {
            "maxCorners": 100,
            "qualityLevel": 0.3,
            "minDistance": 7,
            "blockSize": 7,
        }
        lk_params = {
            "winSize": (15, 15),
            "maxLevel": 2,
            "criteria": (
                cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
                10,
                0.03,
            ),
        }

        ret, old_frame = cap.read()
        if not ret:
            return

        old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
        points = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)
        frame_number = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if points is not None and len(points) > 0:
                next_points, status, _ = cv2.calcOpticalFlowPyrLK(
                    old_gray,
                    frame_gray,
                    points,
                    None,
                    **lk_params,
                )

                if next_points is not None and status is not None:
                    good_new = next_points[status == 1]
                    good_old = points[status == 1]

                    for track_id, (new, old) in enumerate(zip(good_new, good_old)):
                        x_new, y_new = new.ravel()
                        x_old, y_old = old.ravel()
                        dx = float(x_new - x_old)
                        dy = float(y_new - y_old)
                        distance = float(np.hypot(dx, dy))

                        if distance <= 1.0:
                            continue

                        self.trajectories.append(
                            {
                                "frame": frame_number,
                                "timestamp": self._timestamp(frame_number, fps),
                                "track_id": track_id,
                                "center_x": float(x_new),
                                "center_y": float(y_new),
                                "velocity_x": dx,
                                "velocity_y": dy,
                                "distance_moved": distance,
                                "method": "optical_flow",
                            }
                        )

                    points = good_new.reshape(-1, 1, 2)

            if frame_number % 30 == 0:
                points = cv2.goodFeaturesToTrack(
                    frame_gray,
                    mask=None,
                    **feature_params,
                )

            old_gray = frame_gray
            frame_number += 1

    def save_csv(self, frame: pd.DataFrame | None = None) -> Path:
        """Write observations to CSV and return the output path."""
        if frame is None:
            frame = pd.DataFrame(self.trajectories)
        if frame.empty:
            raise ValueError("No trajectory observations were extracted")

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(self.output_csv, index=False)
        return self.output_csv

    def render_overlay(self, output_video: Path, trail_frames: int = 30) -> Path:
        """Render extracted observations and recent trails onto the input video."""
        frame_data = pd.DataFrame(self.trajectories)
        if frame_data.empty:
            raise ValueError("No trajectory observations are available to render")

        cap = cv2.VideoCapture(str(self.video_path))
        if not cap.isOpened():
            raise ValueError(f"Cannot reopen video file: {self.video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        output_video = Path(output_video)
        output_video.parent.mkdir(parents=True, exist_ok=True)

        writer = cv2.VideoWriter(
            str(output_video),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (width, height),
        )

        try:
            frame_number = 0
            while True:
                ret, image = cap.read()
                if not ret:
                    break

                current = frame_data[frame_data["frame"] == frame_number]
                for _, row in current.iterrows():
                    center = (int(row["center_x"]), int(row["center_y"]))
                    cv2.circle(image, center, 5, (0, 255, 0), -1)

                    bbox_x = row.get("bbox_x")
                    if pd.notna(bbox_x):
                        x = int(bbox_x)
                        y = int(row["bbox_y"])
                        w = int(row["bbox_width"])
                        h = int(row["bbox_height"])
                        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

                recent = frame_data[
                    (frame_data["frame"] < frame_number)
                    & (frame_data["frame"] >= frame_number - trail_frames)
                ]
                for track_id in recent["track_id"].dropna().unique():
                    trail = recent[recent["track_id"] == track_id]
                    points = trail[["center_x", "center_y"]].to_numpy(dtype=np.int32)
                    if len(points) > 1:
                        cv2.polylines(image, [points], False, (0, 0, 255), 2)

                writer.write(image)
                frame_number += 1
        finally:
            cap.release()
            writer.release()

        return output_video

    @staticmethod
    def _timestamp(frame_number: int, fps: float) -> float:
        return frame_number / fps if fps > 0 else 0.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract image-space trajectories from drone-simulation video."
    )
    parser.add_argument("video", type=Path, help="Input video file")
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("trajectory_observations.csv"),
        help="CSV output path",
    )
    parser.add_argument(
        "--method",
        choices=("background_subtraction", "optical_flow"),
        default="background_subtraction",
    )
    parser.add_argument("--min-contour-area", type=float, default=100.0)
    parser.add_argument("--max-contour-area", type=float, default=10_000.0)
    parser.add_argument(
        "--overlay",
        type=Path,
        help="Optional MP4 path for an annotated trajectory overlay",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    extractor = DroneTrajectoryExtractor(args.video, args.output_csv)
    frame = extractor.extract_trajectories(
        method=args.method,
        min_contour_area=args.min_contour_area,
        max_contour_area=args.max_contour_area,
    )
    csv_path = extractor.save_csv(frame)
    print(f"Saved {len(frame)} observations to {csv_path}")

    if args.overlay:
        overlay_path = extractor.render_overlay(args.overlay)
        print(f"Saved overlay video to {overlay_path}")


if __name__ == "__main__":
    main()
