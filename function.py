from PIL import Image
import cv2, numpy

YOUR_IMAGE_PATH = '001.png'
get_important_part = True      # 如果你想只看关键部分结果



originimg = cv2.imread(YOUR_IMAGE_PATH)
hsv = cv2.cvtColor(originimg, cv2.COLOR_BGR2HSV)
# 阈值分割模块
lower_yellow = numpy.array([100, 10, 20])
upper_yellow = numpy.array([130, 100, 120])
mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

# 关键部分提取
if get_important_part:
    h, w, d = originimg.shape
    search_top = int(h/2)
    search_bot = int(h/2 + 20)
    mask[0:search_top, 0:w] = 0
    mask[search_bot:h, 0:w] = 0


img = Image.fromarray(mask)
img.save('阈值分割结果.png')

kernel1 = numpy.ones((3, 3), numpy.uint8)
# kernel2 = numpy.ones((10, 10), numpy.uint8)

mask = cv2.erode(mask, kernel1, iterations=1)
img = Image.fromarray(mask)
img.save('腐蚀后结果.png')

mask = cv2.dilate(mask, kernel1, iterations=1)
img = Image.fromarray(mask)
img.save('腐蚀后膨胀结果.png')

if get_important_part:
    M = cv2.moments(mask)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    cv2.circle(originimg, (cx, cy), 20, (0,0,255), -1)
    cv2.imwrite('找到的关键点.png', originimg)
