#!/usr/bin/env python3
"""
AI-enhanced image upscaling for FreeCol unit sprites.

Uses OpenCV's DNN Super-Resolution with the EDSR model to improve
unit image quality through AI-based upscaling. The script upscales
each source image by 4x, then downscales to the target dimensions
to produce cleaner, more detailed sprites.

Requirements:
    pip install opencv-contrib-python-headless numpy

Usage:
    # Process specific unit images:
    python scripts/ai_upscale_units.py --units soldier freeColonist caravel

    # Process all unit images found in the default data directory:
    python scripts/ai_upscale_units.py --all

    # Specify a custom EDSR model path:
    python scripts/ai_upscale_units.py --units soldier --model /path/to/EDSR_x4.pb
"""

import argparse
import os
import sys
import urllib.request

import cv2
import numpy as np

# Default paths relative to the repository root
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UNITS_DIR = os.path.join(REPO_ROOT, "data", "default", "resources", "images", "units")
MODEL_DIR = os.path.join(REPO_ROOT, "scripts", "models")
EDSR_X4_URL = "https://raw.githubusercontent.com/Saafke/EDSR_Tensorflow/master/models/EDSR_x4.pb"
EDSR_X4_PATH = os.path.join(MODEL_DIR, "EDSR_x4.pb")

# Known unit image mappings: unit_key -> (subdirectory, filename_stem)
KNOWN_UNITS = {
    "soldier": ("soldier", "soldier"),
    "freeColonist": ("civilian", "freeColonist"),
    "caravel": ("ship", "caravel"),
}


def download_model(url, dest_path):
    """Download the EDSR model if not already present."""
    if os.path.exists(dest_path):
        print(f"  Model already exists: {dest_path}")
        return
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    print(f"  Downloading EDSR model from {url} ...")
    urllib.request.urlretrieve(url, dest_path)
    print(f"  Saved model to {dest_path}")


def ai_upscale(image, model_path, scale=4):
    """
    Apply EDSR AI super-resolution to an RGBA or BGR image.

    The BGR channels are upscaled using the neural network, while the
    alpha channel (if present) is upscaled with Lanczos interpolation
    to preserve sharp transparency edges.
    """
    has_alpha = len(image.shape) == 3 and image.shape[2] == 4

    if has_alpha:
        bgr = image[:, :, :3]
        alpha = image[:, :, 3]
    else:
        bgr = image
        alpha = None

    sr = cv2.dnn_superres.DnnSuperResImpl.create()
    sr.readModel(model_path)
    sr.setModel("edsr", scale)
    result_bgr = sr.upsample(bgr)

    if alpha is not None:
        h, w = result_bgr.shape[:2]
        alpha_resized = cv2.resize(alpha, (w, h), interpolation=cv2.INTER_LANCZOS4)
        return np.dstack([result_bgr, alpha_resized])

    return result_bgr


def process_unit(subdir, stem, model_path):
    """Process a single unit's base and size2 images."""
    base_path = os.path.join(UNITS_DIR, subdir, f"{stem}.png")
    size2_path = os.path.join(UNITS_DIR, subdir, f"{stem}.size2.png")

    if not os.path.exists(base_path):
        print(f"  WARNING: {base_path} not found, skipping.")
        return False

    img = cv2.imread(base_path, cv2.IMREAD_UNCHANGED)
    h, w = img.shape[:2]
    print(f"  Original: {w}x{h}")

    # AI upscale by 4x
    upscaled = ai_upscale(img, model_path, scale=4)
    uh, uw = upscaled.shape[:2]
    print(f"  AI upscaled: {uw}x{uh}")

    # Generate improved base image (downscale 4x back to original size)
    improved_base = cv2.resize(upscaled, (w, h), interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(base_path, improved_base)
    print(f"  Saved improved {stem}.png ({w}x{h})")

    # Generate improved size2 image (downscale 4x to 2x)
    w2, h2 = w * 2, h * 2
    if os.path.exists(size2_path):
        # Use existing size2 dimensions in case they differ from simple 2x
        existing_s2 = cv2.imread(size2_path, cv2.IMREAD_UNCHANGED)
        h2, w2 = existing_s2.shape[:2]

    improved_s2 = cv2.resize(upscaled, (w2, h2), interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(size2_path, improved_s2)
    print(f"  Saved improved {stem}.size2.png ({w2}x{h2})")

    return True


def find_all_units():
    """Discover all unit images in the units directory."""
    units = []
    if not os.path.isdir(UNITS_DIR):
        return units
    for subdir in sorted(os.listdir(UNITS_DIR)):
        subdir_path = os.path.join(UNITS_DIR, subdir)
        if not os.path.isdir(subdir_path):
            continue
        for fname in sorted(os.listdir(subdir_path)):
            if fname.endswith(".png") and ".size2" not in fname:
                stem = fname[:-4]  # remove .png
                units.append((subdir, stem))
    return units


def main():
    parser = argparse.ArgumentParser(
        description="AI-enhanced upscaling for FreeCol unit images"
    )
    parser.add_argument(
        "--units",
        nargs="+",
        help="Unit names to process (e.g., soldier freeColonist caravel)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all unit images in the default data directory",
    )
    parser.add_argument(
        "--model",
        default=EDSR_X4_PATH,
        help="Path to the EDSR x4 model file (.pb)",
    )
    args = parser.parse_args()

    if not args.units and not args.all:
        parser.print_help()
        sys.exit(1)

    # Download model if needed
    if not os.path.exists(args.model):
        download_model(EDSR_X4_URL, args.model)

    if args.all:
        units_to_process = find_all_units()
        if not units_to_process:
            print("No unit images found.")
            sys.exit(1)
        print(f"Found {len(units_to_process)} unit images to process.")
    else:
        units_to_process = []
        for name in args.units:
            if name in KNOWN_UNITS:
                units_to_process.append(KNOWN_UNITS[name])
            else:
                # Try to find the unit by searching subdirectories
                found = False
                for subdir in os.listdir(UNITS_DIR):
                    candidate = os.path.join(UNITS_DIR, subdir, f"{name}.png")
                    if os.path.exists(candidate):
                        units_to_process.append((subdir, name))
                        found = True
                        break
                if not found:
                    print(f"WARNING: Unit '{name}' not found, skipping.")

    success_count = 0
    for subdir, stem in units_to_process:
        print(f"\n=== Processing {stem} ({subdir}) ===")
        if process_unit(subdir, stem, args.model):
            success_count += 1

    print(f"\n✅ Successfully processed {success_count}/{len(units_to_process)} units.")


if __name__ == "__main__":
    main()
