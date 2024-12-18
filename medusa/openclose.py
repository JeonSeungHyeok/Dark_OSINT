import cv2
import numpy as np
import pytesseract
from PIL import Image

def apply_morph_close(image_path, output_path):
    """
    Morphological Close를 적용하여 이미지 전처리
    """
    # 이미지 읽기 (그레이스케일)
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"이미지 파일을 찾을 수 없습니다: {image_path}")
        return

    # 커널 설정 (3x3, 필요시 조정)
    kernel = np.ones((3, 3), dtype=np.uint8)

    # Erosion 후 Dilation 적용 (Closing)
    erode = cv2.erode(img, kernel, iterations=3)
    close = cv2.dilate(erode, kernel, iterations=3)
    #erode = cv2.morphologyEx(close,cv2.MORPH_OPEN,kernel)
    #close = cv2.morphologyEx(erode,cv2.MORPH_CLOSE,kernel)
    cv2.imwrite(output_path, close)
    print(f"전처리된 이미지 저장: {output_path}")

    return output_path

def extract_text_with_ocr(image_path):
    """
    전처리된 이미지에서 Tesseract OCR로 텍스트 추출
    """
    # Tesseract 설정: 문자와 숫자만 인식
    custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    # OCR로 텍스트 추출
    text = pytesseract.image_to_string(Image.open(image_path), config=custom_config)

    print("추출된 텍스트:")
    print(text.strip())

    return text.strip()

def temp():
    # 입력 및 출력 이미지 경로 설정
    input_image = "zoomed_image.png"          # 원본 이미지 경로
    output_image = "processed_close.png"  # 전처리된 이미지 경로
    
    # Morphological Close 적용
    processed_image_path = apply_morph_close(input_image, output_image)


