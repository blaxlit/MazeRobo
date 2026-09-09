"""Display the live video feed from a connected DJI RoboMaster robot."""

import argparse
import sys

import cv2
from robomaster import robot

from config_loader import load_config


def parse_args():
    parser = argparse.ArgumentParser(
        description="Show the camera feed from a connected RoboMaster robot."
    )
    parser.add_argument(
        "--connection",
        choices=("ap", "sta", "rndis"),
        help="RoboMaster connection type (defaults to config/settings.yaml).",
    )
    parser.add_argument(
        "--resolution",
        choices=("360p", "540p", "720p"),
        default="720p",
        help="Video resolution (default: 720p).",
    )
    return parser.parse_args()


def show_camera(connection_type, resolution):
    ep_robot = robot.Robot()
    stream_started = False

    try:
        print(f"Connecting to RoboMaster using '{connection_type}' mode...")
        ep_robot.initialize(conn_type=connection_type)

        ep_camera = ep_robot.camera
        ep_camera.start_video_stream(display=False, resolution=resolution)
        stream_started = True

        print("Camera connected. Press q or Esc in the video window to quit.")
        while True:
            frame = ep_camera.read_cv2_image(strategy="newest", timeout=1.0)
            if frame is None:
                print("Waiting for a camera frame...", end="\r")
                continue

            cv2.imshow("RoboMaster Camera", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
    finally:
        if stream_started:
            ep_robot.camera.stop_video_stream()
        ep_robot.close()
        cv2.destroyAllWindows()


def main():
    args = parse_args()
    config = load_config()
    connection_type = args.connection or config.get("robot", {}).get(
        "connection_type", "ap"
    )

    try:
        show_camera(connection_type, args.resolution)
    except KeyboardInterrupt:
        print("\nCamera viewer stopped.")
    except Exception as error:
        print(f"Camera viewer error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
