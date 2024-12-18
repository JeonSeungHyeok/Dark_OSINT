import cv2

def median():
    src = "tmp.png"
    output_path = "mediantest.png"
    src = cv2.imread(src,cv2.IMREAD_GRAYSCALE)
    dst = cv2.medianBlur(src,3)

    cv2.imwrite(output_path, dst)
