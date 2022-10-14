import cv2
from PIL import Image
import base64
from io import BytesIO

def remove_single_quote(word):
    s = ''
    for i in range(len(word)):
        if word[i] != "'":
            s+=word[i]
    return s

def convert(aws_response, image_path, image_name):
    url = "/uploadedPrescriptions/{}/-1".format(image_name)
    url1="/uploadedPrescriptions/{}/".format(image_name)
    image = cv2.imread(image_path)
    height, width, _ = image.shape
    formatted_json = {
        url: {
            "filename": url1,
            "size": -1,
            "regions": [
            
            ],
            "file_attributes": {}
        }
    }
    for extracted_data in aws_response["Blocks"]:
        if extracted_data["BlockType"] == "LINE":
            new_dict = {
                "shape_attributes": {
                    "name": "rect",
                    "x": int(extracted_data["Geometry"]["BoundingBox"]["Left"] * width),
                    "y": int(extracted_data["Geometry"]["BoundingBox"]["Top"] * height),
                    "width": int(extracted_data["Geometry"]["BoundingBox"]["Width"] * width),
                    "height": int(extracted_data["Geometry"]["BoundingBox"]["Height"] * height)
                },
                "region_attributes": {
                    "text": remove_single_quote(extracted_data["Text"])
                }
            }
            formatted_json[url]["regions"].append(new_dict)
    return formatted_json

def viewAnnotation(annotation, image_path):
    print(annotation)
    img = cv2.imread('.'+image_path)
    print(image_path)
    for region in annotation[image_path+'/-1']["regions"]:
        start_x_coordinate = region["shape_attributes"]["x"]
        start_y_coordinate = region["shape_attributes"]["y"]
        height_of_box = region["shape_attributes"]["height"]
        width_of_box = region["shape_attributes"]["width"]
        end_x_coordinate = start_x_coordinate + width_of_box
        end_y_coordinate = start_y_coordinate + height_of_box
        cv2.rectangle(img, 
        (start_x_coordinate, start_y_coordinate),
        (end_x_coordinate, end_y_coordinate), 
        (0, 255, 255), 
        3)
    return numpyImg_to_base64img(img)

def to_data_uri(pil_img):
    data = BytesIO()
    pil_img.save(data, "JPEG") # pick your format
    data64 = base64.b64encode(data.getvalue())
    return u'data:img/jpeg;base64,'+data64.decode('utf-8') 

def numpyImg_to_base64img(np_img):
    pil_image = Image.fromarray(np_img).convert('RGB')
    return to_data_uri(pil_image)