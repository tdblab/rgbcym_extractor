import cv2
import numpy as np
import os
import pandas as pd

# List of 50 gene channels with their RGB colors (replace these with your actual colors)
# Format: ("ChannelName", (R, G, B))
gene_colors = [
    ("Red", (255, 0, 0)),
    ("Green", (0, 255, 0)),
    ("Blue", (0, 0, 255)),
    ("Cyan", (0, 255, 255)),
    ("Magenta", (255, 0, 255)),
    ("Yellow", (255, 255, 0)),
    ("Orange", (255, 128, 0)),
    ("Lime", (128, 255, 0)),
    ("Sky Blue", (0, 128, 255)),
    ("Purple", (128, 0, 128)),
    ("Teal", (0, 255, 128)),
    ("Pink", (255, 128, 192)),
    ("Pastel Red", (255, 102, 102)),
    ("Pastel Green", (102, 255, 102)),
    ("Pastel Blue", (102, 102, 255)),
    ("Pastel Cyan", (102, 255, 255)),
    ("Pastel Magenta", (255, 102, 255)),
    ("Pastel Yellow", (255, 255, 102)),
    ("Peach", (255, 204, 153)),
    ("Mint", (153, 255, 204)),
    ("Lavender", (204, 153, 255)),
    ("Baby Blue", (153, 204, 255)),
    ("Pale Orange", (255, 178, 102)),
    ("Light Pink", (255, 204, 204)),
    ("Deep Red", (180, 0, 0)),
    ("Forest Green", (0, 180, 0)),
    ("Navy Blue", (0, 0, 128)),
    ("Deep Cyan", (0, 180, 180)),
    ("Deep Magenta", (180, 0, 180)),
    ("Deep Yellow", (180, 180, 0)),
    ("Burnt Orange", (200, 100, 0)),
    ("Olive", (100, 100, 0)),
    ("Turquoise", (64, 224, 208)),
    ("Hot Pink", (255, 105, 180)),
    ("Crimson", (220, 20, 60)),
    ("Steel Blue", (70, 130, 180)),
    ("Dark Red", (139, 0, 0)),
    ("Dark Green", (0, 100, 0)),
    ("Dark Blue", (0, 0, 139)),
    ("Charcoal", (54, 69, 79)),
    ("Indigo", (75, 0, 130)),
    ("Slate Gray", (112, 128, 144)),
    ("Saddle Brown", (139, 69, 19)),
    ("Gold", (255, 215, 0)),
    ("Silver", (192, 192, 192)),
    ("Light Gray", (211, 211, 211)),
    ("White (DAPI)", (255, 255, 255)),
    ("Bronze", (205, 127, 50)),
    ("Coral", (255, 127, 80)),
]

def create_color_mask(image, target_rgb, tolerance=30):
    lower = np.array([max(c - tolerance, 0) for c in target_rgb], dtype=np.uint8)
    upper = np.array([min(c + tolerance, 255) for c in target_rgb], dtype=np.uint8)
    mask = cv2.inRange(image, lower, upper)
    return mask

def save_masks_and_quantify(image, gene_colors, output_dir, tolerance=30):
    os.makedirs(output_dir, exist_ok=True)
    quant_data = []
    total_pixels = image.shape[0] * image.shape[1]

    for channel, rgb in gene_colors:
        mask = create_color_mask(image, rgb, tolerance)
        mask_path = os.path.join(output_dir, f"{channel}_mask.png")
        cv2.imwrite(mask_path, mask)

        area = cv2.countNonZero(mask)
        mean_intensity = cv2.mean(mask)[0]
        total_intensity = int(np.sum(mask))
        percent_area = (area / total_pixels) * 100

        quant_data.append({
            'Channel': channel,
            'Area (pixels)': area,
            'Percent Area (%)': round(percent_area, 3),
            'Mean Intensity': round(mean_intensity, 3),
            'Total Intensity': total_intensity
        })

    return quant_data

def find_first_image(folder, extensions=('jpg', 'jpeg', 'png', 'tif', 'tiff', 'bmp')):
    for filename in os.listdir(folder):
        if filename.lower().endswith(extensions):
            return os.path.join(folder, filename)
    return None

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = find_first_image(base_dir)

    if image_path is None:
        print("❌ No image file found in the current folder.")
        exit()

    print(f"📷 Processing image: {os.path.basename(image_path)}")

    # Load image (OpenCV loads as BGR, convert to RGB)
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    output_folder = os.path.join(base_dir, 'output_50_gene_masks')
    quant_results = save_masks_and_quantify(image, gene_colors, output_folder, tolerance=30)

    # Save quant results to Excel
    excel_path = os.path.join(output_folder, "quantified_50_genes.xlsx")
    pd.DataFrame(quant_results).to_excel(excel_path, index=False)
    print(f"✅ Saved all masks and quantification in folder: {output_folder}")
    print(f"✅ Quantification Excel saved as: {excel_path}")

    # Print summary
    print("\n📈 Quantification summary:")
    for item in quant_results:
        print(f"{item['Channel']}: Area={item['Area (pixels)']} px, Percent Area={item['Percent Area (%)']}%, Total Intensity={item['Total Intensity']}")
