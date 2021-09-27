''' searches for ALL png files in current directory and all subdirectories and converts them to native jpg and crops to 5/1 ratio '''

from PIL import Image
import os

def process_file(path_file, ratio = 5):
    if path_file.split('.')[-1] == 'png':
            im = Image.open(path_file)
            rgb_img = im.convert('RGB')
            w, h = rgb_img.size
            if h / w > float(ratio):
                print(w, h)
                rgb_img = rgb_img.crop((0, 0, w, w * ratio))

            rgb_img.save(''.join([path_file[:-3], 'jpg']))
            os.remove(path_file)
    else:
        pass

for root, _, files in os.walk('.'):
    for file in files:
        file = os.path.join(root, file)
        process_file(file, ratio = 3)
