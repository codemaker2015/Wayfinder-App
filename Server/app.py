import os
import uuid
from flask import Flask, request, send_file
import base64
from io import BytesIO
from PIL import Image
from pathlib import Path

import my_hloc as my_hloc

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/image', methods=['POST'])
def process_image():
    # read json key "image_data"
    # without the `data:image/jpeg;base64,` prefix
    image_data = request.json['image_data']

    # Convert the base64-encoded image data to bytes
    image_bytes = base64.b64decode(str(image_data))
    
    # Generate a unique filename using UUID
    filename = str(uuid.uuid4()) + '.png'
    
    # Specify the temp directory path for saving the images
    temp_save_directory = 'images_temp'
    
    # Create the save directory if it doesn't exist
    os.makedirs(temp_save_directory, exist_ok=True)
    
    # Construct the full path to save the image
    temp_save_path = os.path.join(temp_save_directory, filename)
    
    img = Image.open(BytesIO(image_bytes))
    img.save(temp_save_path, 'png')

    saved_new_path = resize_image(temp_save_path)

    print('saved_new_path = ', saved_new_path)

    result = my_hloc.check_location(saved_new_path)

    if result == None:
        return {"result": "No match found"}, 404

    return {"result": result}, 200

def resize_image(image_path):
    # open the image file
    image = Image.open(image_path)

    # get image dimension
    width, height = image.size

    # calculate the height of the cropped area to maintain a 3:4 aspect ratio
    cropped_height = int(width * 4 / 3)

    # define the crop area
    # gambaran cropping area: https://imgur.com/2SDm80v.png
    left = 0
    top = 140
    right = width
    bottom = cropped_height + top

    # crop the image
    res_image = image.crop((left, top, right, bottom))

    width, height = res_image.size # new width & height value

    # resize the cropped image to fit into a 512x512 box
    base_height = 512
    wpercent = (base_height/float(height))
    wsize = int((float(width)*float(wpercent)))
    res_image = res_image.resize((wsize,base_height), Image.Resampling.LANCZOS)

    # Extract the filename from original file
    file_name = Path(image_path).stem + '.png'
    
    # Specify the directory path for saving the images
    # the inference image need to be the same path as the 'training' image
    # so, set this variable same as variable `images` in my_hloc.py:13
    save_dir = 'koe-datasets/new'
    
    # Create the save directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)
    
    # Construct the full path to save the image
    temp_save_path = os.path.join(save_dir, file_name)
    
    # save the resized image
    res_image.save(temp_save_path, 'png')

    return file_name
    

if __name__ == '__main__':
    # app.run(debug=True)
    app.run()
