
import cv2 
import numpy as np 
# from PIL import Image,ImageEnhance
import requests

def show(img):
    cv2.imshow("image",img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def order_points(pts):
    '''Rearrange coordinates to order:
      top-left, top-right, bottom-right, bottom-left'''
    rect = np.zeros((4, 2), dtype='float32')
    pts = np.array(pts)
    s = pts.sum(axis=1)
    # Top-left point will have the smallest sum.
    rect[0] = pts[np.argmin(s)]
    # Bottom-right point will have the largest sum.
    rect[2] = pts[np.argmax(s)]
 
    diff = np.diff(pts, axis=1)
    # Top-right point will have the smallest difference.
    rect[1] = pts[np.argmin(diff)]
    # Bottom-left will have the largest difference.
    rect[3] = pts[np.argmax(diff)]
    # return the ordered coordinates
    return rect.astype('int').tolist()


def find_dest(pts):
    (tl, tr, br, bl) = pts
    # Finding the maximum width.
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
 
    # Finding the maximum height.
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    # Final destination co-ordinates.
    destination_corners = [[0, 0], [maxWidth, 0], [maxWidth, maxHeight], [0, maxHeight]]
 
    return order_points(destination_corners)

def scan(img):
    # Resize image to workable size
    # img=cv2.imread(path)
    # if img is None:
    #     return None 
    dim_limit = 1080
    max_dim = max(img.shape)
    if max_dim > dim_limit:
        resize_scale = dim_limit / max_dim
        img = cv2.resize(img, None, fx=resize_scale, fy=resize_scale)
    # Create a copy of resized original image for later use
    orig_img = img.copy()
    # Repeated Closing operation to remove text from the document.
    kernel = np.ones((5, 5), np.uint8)
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, iterations=3)
    # GrabCut
    mask = np.zeros(img.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    rect = (20, 20, img.shape[1] - 20, img.shape[0] - 20)
    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    img = img * mask2[:, :, np.newaxis]
 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (11, 11), 0)
    # Edge Detection.
    canny = cv2.Canny(gray, 0, 200)
    canny = cv2.dilate(canny, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
 
    # Finding contours for the detected edges.
    contours, hierarchy = cv2.findContours(canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    # Keeping only the largest detected contour.
    page = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
 
    # Detecting Edges through Contour approximation.
    # Loop over the contours.
    if len(page) == 0:
        return orig_img
    for c in page:
        # Approximate the contour.
        epsilon = 0.02 * cv2.arcLength(c, True)
        corners = cv2.approxPolyDP(c, epsilon, True)
        # If our approximated contour has four points.
        if len(corners) == 4:
            break
    # Sorting the corners and converting them to desired shape.
    corners = sorted(np.concatenate(corners).tolist())
    # For 4 corner points being detected.
    corners = order_points(corners)
 
    destination_corners = find_dest(corners)
 
    h, w = orig_img.shape[:2]
    # Getting the homography.
    M = cv2.getPerspectiveTransform(np.float32(corners), np.float32(destination_corners))
    # Perspective transform using homography.
    final = cv2.warpPerspective(orig_img, M, (destination_corners[2][0], destination_corners[2][1]),
                                flags=cv2.INTER_LINEAR)
    
    show(final)

    return final

def automatic_brightness_and_contrast(image, clip_hist_percent=.10):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate grayscale histogram
    hist = cv2.calcHist([gray],[0],None,[256],[0,256])
    hist_size = len(hist)

    # Calculate cumulative distribution from the histogram
    accumulator = []
    accumulator.append(float(hist[0]))
    for index in range(1, hist_size):
        accumulator.append(accumulator[index -1] + float(hist[index]))

    # Locate points to clip
    maximum = accumulator[-1]
    clip_hist_percent *= (maximum/100.0)
    clip_hist_percent /= 2.0

    # Locate left cut
    minimum_gray = 0
    while accumulator[minimum_gray] < clip_hist_percent:
        minimum_gray += 1

    # Locate right cut
    maximum_gray = hist_size -1
    while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
        maximum_gray -= 1

    # Calculate alpha and beta values
    alpha = 255 / (maximum_gray - minimum_gray)
    beta = -minimum_gray * alpha

    '''
    # Calculate new histogram with desired range and show histogram 
    new_hist = cv2.calcHist([gray],[0],None,[256],[minimum_gray,maximum_gray])
    plt.plot(hist)
    plt.plot(new_hist)
    plt.xlim([0,256])
    plt.show()
    '''

    auto_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return (auto_result, alpha, beta)

def getResult(image):    
    final=scan(image)
    # if final is not None:
    #     img,_,_=automatic_brightness_and_contrast(final)
    #     return img
    return final

# if __name__=="__main__":
#     try:   
#         final=scan('test2.jpg')
#         show(final)
#         img,_,_=automatic_brightness_and_contrast(final)
        # show(img)
        # img=Image.fromarray(final)
       
       
        # contrast=ImageEnhance.Contrast(img)
       
        # contrast.enhance(1.5).save('contrast.jpg')
        
        # color=ImageEnhance.Color(img)
    
        # color.enhance(1.5).save('color.jpg')

        # brightness=ImageEnhance.Brightness(img)
   
        # brightness.enhance(1.5).save("brightness.jpg")
   
        # sharpness=ImageEnhance.Sharpness(img)
   
        # sharpness.enhance(1.5).save('sharpness.jpg')

        

    # except Exception as e:
    #     print(e)


























# import cv2 
# import numpy as np 


# def show(img):
#     cv2.imshow("image",img)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

# def order_points(pts):
#     '''Rearrange coordinates to order:
#       top-left, top-right, bottom-right, bottom-left'''
#     rect = np.zeros((4, 2), dtype='float32')
#     pts = np.array(pts)
#     s = pts.sum(axis=1)
#     # Top-left point will have the smallest sum.
#     rect[0] = pts[np.argmin(s)]
#     # Bottom-right point will have the largest sum.
#     rect[2] = pts[np.argmax(s)]
 
#     diff = np.diff(pts, axis=1)
#     # Top-right point will have the smallest difference.
#     rect[1] = pts[np.argmin(diff)]
#     # Bottom-left will have the largest difference.
#     rect[3] = pts[np.argmax(diff)]
#     # return the ordered coordinates
#     return rect.astype('int').tolist()


# def find_dest(pts):
#     (tl, tr, br, bl) = pts
#     # Finding the maximum width.
#     widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
#     widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
#     maxWidth = max(int(widthA), int(widthB))
 
#     # Finding the maximum height.
#     heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
#     heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
#     maxHeight = max(int(heightA), int(heightB))
#     # Final destination co-ordinates.
#     destination_corners = [[0, 0], [maxWidth, 0], [maxWidth, maxHeight], [0, maxHeight]]
 
#     return order_points(destination_corners)

# def scan(path):
#     # Resize image to workable size
#     img=cv2.imread(path)
#     if img is None:
#         return None 
#     dim_limit = 1080
#     max_dim = max(img.shape)
#     if max_dim > dim_limit:
#         resize_scale = dim_limit / max_dim
#         img = cv2.resize(img, None, fx=resize_scale, fy=resize_scale)
#     # Create a copy of resized original image for later use
#     orig_img = img.copy()
#     # Repeated Closing operation to remove text from the document.
#     kernel = np.ones((5, 5), np.uint8)
#     img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, iterations=3)
#     # GrabCut
#     mask = np.zeros(img.shape[:2], np.uint8)
#     bgdModel = np.zeros((1, 65), np.float64)
#     fgdModel = np.zeros((1, 65), np.float64)
#     rect = (20, 20, img.shape[1] - 20, img.shape[0] - 20)
#     cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
#     mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
#     img = img * mask2[:, :, np.newaxis]
 
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     gray = cv2.GaussianBlur(gray, (11, 11), 0)
#     # Edge Detection.
#     canny = cv2.Canny(gray, 0, 200)
#     canny = cv2.dilate(canny, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
 
#     # Finding contours for the detected edges.
#     contours, hierarchy = cv2.findContours(canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
#     # Keeping only the largest detected contour.
#     page = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
 
#     # Detecting Edges through Contour approximation.
#     # Loop over the contours.
#     if len(page) == 0:
#         return orig_img
#     for c in page:
#         # Approximate the contour.
#         epsilon = 0.02 * cv2.arcLength(c, True)
#         corners = cv2.approxPolyDP(c, epsilon, True)
#         # If our approximated contour has four points.
#         if len(corners) == 4:
#             break
#     # Sorting the corners and converting them to desired shape.
#     corners = sorted(np.concatenate(corners).tolist())
#     # For 4 corner points being detected.
#     corners = order_points(corners)
 
#     destination_corners = find_dest(corners)
 
#     h, w = orig_img.shape[:2]
#     # Getting the homography.
#     M = cv2.getPerspectiveTransform(np.float32(corners), np.float32(destination_corners))
#     # Perspective transform using homography.
#     final = cv2.warpPerspective(orig_img, M, (destination_corners[2][0], destination_corners[2][1]),
#                                 flags=cv2.INTER_LINEAR)
#     return final


