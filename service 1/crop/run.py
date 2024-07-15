from PIL import Image
import json
from backtracking import BacktrackingCrop

def crop_image(image_path, info_path):
    info = json.load(open(info_path))
    cropper = BacktrackingCrop(info)
    crop_box = cropper.calculate()
    if not crop_box['success']:
        return
    image = Image.open(image_path)
    cropped_image = image.crop((crop_box['x_min'], crop_box['y_min'], crop_box['x_max'], crop_box['y_max']))
    cropped_image.save(image_path.replace(".jpg", f"_{crop_box['chunks']}_{crop_box['ratio_tolerance']}_{crop_box['center_tolerance']}_cropped.jpg"))
    cropped_image.show()


# Usage example
crop_image("../subjects/1.jpg", "../subjects/1.json")
crop_image("../subjects/2.jpg", "../subjects/2.json")
crop_image("../subjects/3.jpg", "../subjects/3.json")
crop_image("../subjects/4.jpg", "../subjects/4.json")
crop_image("../subjects/5.jpg", "../subjects/5.json")
