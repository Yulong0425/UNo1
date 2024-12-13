from cnocr import CnOcr

def read_img(path):
    img_fp = path
    ocr = CnOcr()  # 所有参数都使用默认值
    out = ocr.ocr(img_fp)
    string = ''
    for i in out:
        if len(i['text']) > 10:
            string += (i['text'])

    return string




if __name__ == '__main__':
    print(read_img('resources/a0bec358252dd42aee57198f453b5bb5c8eab8ca.jpg'))
# sharpen = ImageEnhance.Sharpness(img)
# img_sharpen = sharpen.enhance(2.0)
# enhancer = ImageEnhance.Contrast(img_sharpen)
# img_contrast = enhancer.enhance(5.0)

