# image_processing.py

import cv2
import numpy as np
import os

def preprocess_image(image_path: str):
    # Loads image and applies pre-processing pipeline
    # TODO: Figure out automation and testing for best fit perhaps... 

    settings = {
        "auto_crop": True,
        "denoise": True,
        "sharpen": True,
        "threshold": False,
    }

    # --- Load Image ---
    img = cv2.imread(image_path)
    if img is None:
        print(f"[ERROR] Could not load image at path: {image_path}")
        return None

    if not os.path.exists('logs'):
        os.makedirs('logs')

    # This will be the image we work on throughout the pipeline.
    # It starts as the original image.
    processed_image = img.copy()

    # --- 1. Auto-Crop and Perspective Transform (Runs First) ---
    if settings["auto_crop"]:
        print("Step 1: Attempting to auto-crop receipt...")
        
        # We perform edge detection on a grayscaled version, but warp the original color image.
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 50, 200) # Adjusted Canny thresholds for better edge detection
        cv2.imwrite('logs/debug_0_edges.png', edged)

        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

        screenCnt = None
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4:
                screenCnt = approx
                break
        
        if screenCnt is not None:
            print("[SUCCESS] Found a 4-point contour. Applying perspective transform.")
            cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 3)
            cv2.imwrite('logs/debug_0_contour.png', img)

            # Manually perform the four-point transform
            pts = screenCnt.reshape(4, 2)
            rect = np.zeros((4, 2), dtype="float32")
            s = pts.sum(axis=1)
            rect[0] = pts[np.argmin(s)]
            rect[2] = pts[np.argmax(s)]
            diff = np.diff(pts, axis=1)
            rect[1] = pts[np.argmin(diff)]
            rect[3] = pts[np.argmax(diff)]
            
            (tl, tr, br, bl) = rect
            widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
            widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
            maxWidth = max(int(widthA), int(widthB))
            heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
            heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
            maxHeight = max(int(heightA), int(heightB))
            
            dst = np.array([[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]], dtype="float32")
            M = cv2.getPerspectiveTransform(rect, dst)
            
            # The result of the warp is our new image to process for the rest of the pipeline
            processed_image = cv2.warpPerspective(img, M, (maxWidth, maxHeight))
        else:
            print("[WARNING] Could not find a 4-point contour. Using full image.")
    
    # --- 2. Grayscale ---
    # This is now the first mandatory processing step, running on either the cropped or full image.
    processed_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)
    print("Step 2: Grayscale conversion complete.")
    cv2.imwrite('logs/debug_1_grayscale.png', processed_image)

    # --- The rest of the pipeline runs on the grayscaled image ---
    if settings["denoise"]:
        print("Step 3: Applying median blur for denoising...")
        processed_image = cv2.medianBlur(processed_image, 3)
        cv2.imwrite('logs/debug_2_denoised.png', processed_image)

    if settings["sharpen"]:
        print("Step 4: Applying sharpening filter...")
        sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        processed_image = cv2.filter2D(processed_image, -1, sharpen_kernel)
        cv2.imwrite('logs/debug_3_sharpened.png', processed_image)

    if settings["threshold"]:
        print("Step 5: Applying adaptive threshold...")
        processed_image = cv2.adaptiveThreshold(
            processed_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2)
        cv2.imwrite('logs/debug_4_threshold.png', processed_image)

    print("\n[SUCCESS] Image processing complete.")
    cv2.imwrite('logs/debug_final.png', processed_image)
    print("Final processed image saved to 'logs/debug_final.png'")
    
    return processed_image