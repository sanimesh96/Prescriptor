import cv2

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
    print(annotation, image_path)
    return annotation