# coding=utf-8
# reference: https://ssamko.tistory.com/47

from google.cloud import vision
import os


# extract description from response
def get_text(response):
    if not response or response.error.message:
        error = response.error.message if response else 'no response from Google Cloud Vision API'
        print('[ERROR] %s at vision.get_text' % error)
        return None
    temp = list(map(lambda x: x.description, response.text_annotations))
    if len(temp) == 0:
        return None
    return temp[0]


# read file as binary format
def get_content(img_uri):
    content = None
    with open(img_uri, 'rb') as f:
        content = f.read()
    return content


class GoogleVision:

    client = None
    img_list = None

    def __init__(self, img_list):
        self.client = vision.ImageAnnotatorClient()
        self.img_list = img_list

    # call vision api by client
    def call_api(self, content):
        if not content:
            return None
        image = vision.Image(content=content)
        response = self.client.text_detection(image=image)
        return response

    # the caller
    def read(self):
        text_list = list()
        for img_uri in self.img_list:
            content = get_content(img_uri)
            response = self.call_api(content)
            text = get_text(response)
            if text:
                text_list.append(text)
                os.remove(img_uri)

        return text_list

