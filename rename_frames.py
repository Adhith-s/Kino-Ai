# Frame Renaming Helper
# Place your 46 frames in this folder (frontend/assets/frames/)
# and run this script to rename them sequentially.
#
# Usage: python rename_frames.py

import os
import sys

FRAMES_DIR = os.path.join(os.path.dirname(__file__), "frontend", "assets", "frames")

def rename_frames():
    if not os.path.exists(FRAMES_DIR):
        print(f"❌ Directory not found: {FRAMES_DIR}")
        sys.exit(1)

    # Get all image files sorted by name
    extensions = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')
    files = sorted([
        f for f in os.listdir(FRAMES_DIR)
        if os.path.isfile(os.path.join(FRAMES_DIR, f)) and f.lower().endswith(extensions)
    ])

    if not files:
        print(f"❌ No image files found in {FRAMES_DIR}")
        print("   Place your 46 frames here and run again.")
        sys.exit(1)

    print(f"🎬 Found {len(files)} frames. Renaming...")

    for i, filename in enumerate(files, start=1):
        ext = os.path.splitext(filename)[1].lower()
        new_name = f"frame_{str(i).zfill(3)}{ext}"
        old_path = os.path.join(FRAMES_DIR, filename)
        new_path = os.path.join(FRAMES_DIR, new_name)

        if old_path != new_path:
            os.rename(old_path, new_path)
            print(f"   {filename} → {new_name}")
        else:
            print(f"   {filename} (already correct)")

    print(f"\n✅ Done! {len(files)} frames renamed as frame_001 through frame_{str(len(files)).zfill(3)}")
    print("   Your cinematic loader is ready to go!")

if __name__ == "__main__":
    rename_frames()
