import cv2
import numpy as np
import os
import pandas as pd

# Define your 6 gene channels with their target RGB values
COLOR_CHANNELS = [
    ("Gene_A_Red", (255, 0, 0)),
    ("Gene_B_Green", (0, 255, 0)),
    ("Gene_C_Blue", (0, 0, 255)),
    ("Gene_D_Yellow", (255, 255, 0)),
    ("Gene_E_Cyan", (0, 255, 255)),
    ("Gene_F_Magenta", (255, 0, 255))
]

def find_images(folder, extensions=("jpg", "jpeg", "png", "bmp", "tif", "tiff")):
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(extensions)]

def extract_color_masks(image, thresholds):
    masks = {}
    R, G, B = cv2.split(image)
    
    masks["Gene_A_Red"] = np.where((R > thresholds["Red"]) & (G < thresholds["G_Red"]) & (B < thresholds["B_Red"]), 255, 0).astype(np.uint8)
    masks["Gene_B_Green"] = np.where((G > thresholds["Green"]) & (R < thresholds["R_Green"]) & (B < thresholds["B_Green"]), 255, 0).astype(np.uint8)
    masks["Gene_C_Blue"] = np.where((B > thresholds["Blue"]) & (R < thresholds["R_Blue"]) & (G < thresholds["G_Blue"]), 255, 0).astype(np.uint8)
    masks["Gene_D_Yellow"] = np.where((R > thresholds["Yellow_R"]) & (G > thresholds["Yellow_G"]) & (B < thresholds["Yellow_B"]), 255, 0).astype(np.uint8)
    masks["Gene_E_Cyan"] = np.where((G > thresholds["Cyan_G"]) & (B > thresholds["Cyan_B"]) & (R < thresholds["Cyan_R"]), 255, 0).astype(np.uint8)
    masks["Gene_F_Magenta"] = np.where((R > thresholds["Magenta_R"]) & (B > thresholds["Magenta_B"]) & (G < thresholds["Magenta_G"]), 255, 0).astype(np.uint8)
    return masks

def detect_spots(mask):
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 3
    params.maxArea = 10000
    params.filterByCircularity = False
    params.filterByConvexity = False
    params.filterByInertia = False
    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(mask)
    return len(keypoints)

def save_masks(masks, output_dir, image_name):
    os.makedirs(output_dir, exist_ok=True)
    for name, mask in masks.items():
        filename = os.path.join(output_dir, f"{image_name}_{name}.png")
        cv2.imwrite(filename, mask)

def auto_calibrate_threshold(image):
    R, G, B = cv2.split(image)
    thresholds = {
        "Red": np.percentile(R, 90),    "G_Red": np.percentile(G, 70),   "B_Red": np.percentile(B, 70),
        "Green": np.percentile(G, 92),  "R_Green": np.percentile(R, 65), "B_Green": np.percentile(B, 65),
        "Blue": np.percentile(B, 90),   "R_Blue": np.percentile(R, 75),  "G_Blue": np.percentile(G, 75),
        "Yellow_R": np.percentile(R, 85), "Yellow_G": np.percentile(G, 85), "Yellow_B": np.percentile(B, 70),
        "Cyan_G": np.percentile(G, 85), "Cyan_B": np.percentile(B, 85), "Cyan_R": np.percentile(R, 80),
        "Magenta_R": np.percentile(R, 85), "Magenta_B": np.percentile(B, 85), "Magenta_G": np.percentile(G, 80),
    }
    return thresholds

def process_image(image_path, output_folder):
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    image_bgr = cv2.imread(image_path)
    if image_bgr is None:
        print(f"❌ Failed to load image: {image_path}")
        return
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    thresholds = auto_calibrate_threshold(image_rgb)
    masks = extract_color_masks(image_rgb, thresholds)
    save_masks(masks, output_folder, image_name)

    results = []
    for name, mask in masks.items():
        spot_count = detect_spots(mask)
        results.append({"Image": image_name, "Gene": name, "Spot_Count": spot_count})
    return results

def main():
    current_folder = os.path.dirname(os.path.abspath(__file__))
    images = find_images(current_folder)
    if not images:
        print("❌ No image files found in current folder!")
        return

    output_folder = os.path.join(current_folder, "output_gene_channels")
    os.makedirs(output_folder, exist_ok=True)
    all_results = []

    for image_path in images:
        print(f"📷 Processing image: {os.path.basename(image_path)}")
        results = process_image(image_path, output_folder)
        all_results.extend(results)

    df = pd.DataFrame(all_results)
    excel_file = os.path.join(output_folder, "spot_counts.xlsx")
    df.to_excel(excel_file, index=False)
    print(f"📊 Quantification saved to {excel_file}")

if __name__ == "__main__":
    main()
