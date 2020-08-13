import cv2
import numpy as np
from threading import Thread
import time

DONT_DEBUG = False
DEBUG = True
# COLORS HSV THRESHOLD RANGE
COLORS = dict()
COLORS["YELLOW"] = {
    "lower": [[], [], []],
    "upper": [[], [], []]
}
COLORS["GREEN"] = {
    "lower": [[77, 30, 30], [67, 30, 30], [67, 30, 30]],
    "upper": [[87, 255, 255], [77, 255, 255], [77, 255, 255]]
}
COLORS["BLUE"] = {
<<<<<<< HEAD
    "lower": [[108, 30, 30], [98, 30, 30], [98, 30, 30]],
    "upper": [[118, 255, 255], [108, 255, 255], [108, 255, 255]]
=======
    "lower" : [[101,95,63],[81,95,63],[81,95,63]],
    "upper" : [[121,255,255],[101,255,255],[101,255,255]]
}
COLORS["RED"] = {
    "lower" : [[178,98,121],[0,98,121],[158,98,121]],
    "upper" : [[180,255,255],[18,255,255],[178,255,255]]
>>>>>>> 3bf4c7fe9a7db3fe6fa3f01414ebc2a0af460482
}
# COLORS["RED"] = {
#    "upper" : [[182,255,162],[182,255,162],[182,255,162]],
#    "lower" : [[98,163,39],[98,163,39],[98,163,39]]
# }
COLORS["RED2"] = {
    "lower": [[139, 145, 186], [139, 145, 186], [139, 145, 186]],
    "upper": [[55, 94, 149], [55, 94, 149], [55, 94, 149]]
}
COLORS["RED3"] = {
    "upper": [[180, 255, 255], [0, 255, 255], [20, 255, 255]],
    "lower": [[160, 30, 30], [68, 30, 30], [68, 30, 30]]
}
COLORS["RED"] = {
    "upper": [[182, 255, 190], [182, 255, 190], [182, 255, 190]],
    "lower": [[102, 163, 68], [102, 163, 68], [102, 163, 68]]
}
COLORS[""] = {
    "lower": [[], [], []],
    "upper": [[], [], []]
}
COLORS[""] = {
    "lower": [[], [], []],
    "upper": [[], [], []]
}


class Target():
    def __init__(self, stats=None, centroid=None):
        self.x, self.y, self.width, self.height, self.area = stats
        self.centerX, self.centerY = int(centroid[0]), int(centroid[1])

    def getDistance(self, baseline):
        (bx, by) = baseline
        return (bx - self.centerX, by - self.centerY)


class ImageProcessor:
    def __init__(self, width, height):
        self.__src = np.zeros((height, width, 3), np.uint8)

    def getBinImage(self, color, debug=False):  # 인자로 넘겨 받은 색상만 남기고 리턴
        img = self.getImage()
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower1, lower2, lower3  = COLORS[color]["lower"]
        upper1, upper2, upper3 = COLORS[color]["upper"]
        img_mask1 = cv2.inRange(img_hsv, np.array(lower1), np.array(upper1))
        img_mask2 = cv2.inRange(img_hsv, np.array(lower2), np.array(upper2))
        img_mask3 = cv2.inRange(img_hsv, np.array(lower3), np.array(upper3))
        temp = cv2.bitwise_or(img_mask1, img_mask2)
        img_mask = cv2.bitwise_or(img_mask3, temp)
        k = (11, 11)
        # kernel = np.ones(k, np.uint8)
        # img_mask = cv2.morphologyEx(img_mask, cv2.MORPH_OPEN, kernel)
        # img_mask = cv2.morphologyEx(img_mask, cv2.MORPH_CLOSE, kernel)
        # img_result = cv2.bitwise_and(img, img, mask=img_mask) # 해당 색상값만 남기기

        if (debug):
            self.debug(img_mask)
        return img, img_mask

    def updateImage(self, src):  # 카메라 쓰레드가 fresh 이미지를 계속해서 갱신해줌
        self.__src = src

    def debug(self, result):  # 디버그용 (영상을 출력해서 봐야할때)
        cv2.imshow("debug", result)
        cv2.waitKey(1)

    def getImage(self):  # 이미지를 필요로 할때
        return self.__src.copy()

<<<<<<< HEAD
    def detectTarget(self, color="RED", debug=False):
        targets = []  # 인식한 타깃들을 감지
=======
    def avoidObstacle1(self): # 1안
        _, mask1 = self.getBinImage(color="RED")
        #mask2 = self.getBinImage(color="GREEN")
        _ ,mask3 = self.getBinImage(color="BLUE")
        #temp = cv2.bitwise_or(mask1, mask3)
        mask = cv2.bitwise_or(mask3, mask1)
        cv2.imshow("mask", mask)
        h, w = mask.shape[:2]
        row_inds = np.indices((h, w))[0]  # gives row indices in shape of img
        row_inds_at_edges = row_inds.copy()
        row_inds_at_edges[mask == 0] = 0  # only get indices at edges, 0 elsewhere
        max_row_inds = np.amax(row_inds_at_edges, axis=0)  # find the max row ind over each col
        inds_after_edges = row_inds >= max_row_inds
        filled_from_bottom = np.zeros((h, w), dtype=np.uint8)
        filled_from_bottom[inds_after_edges] = 255
        # 침식, 팽창 연산
        vertical_size = int(w / 30)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (vertical_size, vertical_size))
        erosion = cv2.erode(filled_from_bottom, kernel, iterations=1)
        dilate = cv2.dilate(erosion, kernel, iterations=1)
        dilate = cv2.GaussianBlur(dilate, (5, 5), 0)
        # 비트연산
        src = self.getImage()
        dst = cv2.bitwise_and(src,src, mask=dilate)
        cv2.imshow("dst", dst)
        cv2.waitKey(1)

    def avoidObstacle2(self): # 2안
        _, mask1 = self.getBinImage(color="RED")
        #mask2 = self.getBinImage(color="GREEN")
        _ ,mask3 = self.getBinImage(color="BLUE")
        #temp = cv2.bitwise_or(mask1, mask3)
        mask = cv2.bitwise_or(mask3, mask1)
        cv2.imshow("mask", mask)
        h, w = mask.shape[:2]
        max_row_inds = h - np.argmax(mask[::-1], axis=0)
        max_row_inds %= h
        row_inds = np.indices((h, w))[0]
        inds_after_edges = row_inds >= max_row_inds
        filled_from_bottom = np.zeros((h, w), dtype=np.uint8)
        filled_from_bottom[inds_after_edges] = 255
        # 침식, 팽창 연산
        vertical_size = int(w / 30)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (vertical_size, vertical_size))
        erosion = cv2.erode(filled_from_bottom, kernel, iterations=1)
        dilate = cv2.dilate(erosion, kernel, iterations=1)
        dilate = cv2.GaussianBlur(dilate, (5, 5), 0)
        # 비트연산
        src = self.getImage()
        dst = cv2.bitwise_and(src,src, mask=dilate)
        cv2.imshow("dst", dst)
        cv2.waitKey(1)




    def detectTarget(self, color="RED", debug = False):
        targets = [] # 인식한 타깃들을 감지
>>>>>>> 3bf4c7fe9a7db3fe6fa3f01414ebc2a0af460482
        img, img_mask = self.getBinImage(color=color)
        img_result = cv2.bitwise_and(img, img, mask=img_mask)  # 해당 색상값만 남기기
        if (debug):
            self.debug(img_result)
        # 라벨링
        _, _, stats, centroids = cv2.connectedComponentsWithStats(img_mask, connectivity=8)
        for idx, centroid in enumerate(centroids):  # enumerate 함수는 순서가 있는 자료형을 받아 인덱스와 데이터를 반환한다.
            if stats[idx][0] == 0 and stats[idx][1] == 0:
                continue

            if np.any(np.isnan(centroid)):  # 배열에 하나이상의 원소라도 참이라면 true (즉, 하나이상의 중심점이 숫자가 아니면)
                continue
            _, _, _, _, area = stats[idx]
            if area > 100:
                targets.append(Target(stats[idx], centroid))  #
        if targets:  # 타깃이 인식 됐다면 제일 가까운놈 리턴
            targets.sort(key=lambda x: x.y + x.height, reverse=True)  # 인식된 애들중 가까운 놈 기준으로 정렬
            target = targets[0]  # 제일 가까운 놈만 남김
            if (debug):
                cv2.circle(img, (target.centerX, target.centerY), 10, (0, 255, 0), 10)
                cv2.rectangle(img, (target.x, target.y), (target.x + target.width, target.y + target.height),
                              (0, 255, 0))
                self.debug(img)
            return target
        else:  # 인식된 놈이 없다면 None 리턴
            if (debug):
                cv2.putText(img, "** NO TARGET **", (320, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255))
                self.debug(img)
            return None

    def selectObject_mean(self, color):
        centers = []
        img_color, img_mask = self.getBinImage(color)
        self.debug(img_color)
        # 등고선 따기
        contours, hierarchy = cv2.findContours(img_mask, cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)
            if area > 10:
                # cv2.rectangle(img_color, (x, y), (x + w, h + y), (0, 0, 255), 2)
                # 무게중심
                self.Cx = x + w // 2
                self.Cy = y + h // 2
                # bcv2.line(img_color, (self.Cx, self.Cy), (self.Cx, self.Cy), (0, 0, 255), 10)
                # 같은 색상이라도 무게중심의 y값이 큰것일 수록 더 가까이 있음
                centers.append([x, y, w, h])
        print("center1: ", centers)
        if centers:
            centers = sorted(centers, key=lambda x: x[1] + x[3] // 2, reverse=True)[0]
            # 타겟인 영역만큼 그림그리기
            col, row, width, height = centers[0], centers[1], centers[2], centers[3]
            trackWindow = (col, row, width, height)  # 추적할 객체
            roi = img_color[row:row + height, col:col + width]
            roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            roi_hist = cv2.calcHist([roi], [0], None, [180], [0, 180])
            cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
            termination = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
            print("center2: ", centers)
            return img_color, trackWindow, roi_hist, termination
        else:
            return None, None, None, None

    def meanShiftTracking_color(self, img_color, trackWindow, roi_hist, termination,
                                debug=True):  # 추적할 대상이 정해지면 그 좌표기준으로 사각형을 그려서 추적대상을 잡는다
        need_to_update = True
        ######################## target의 업데이트 ####################
        img_color, trackWindow, roi_hist, termination = self.selectObject_mean()

        if trackWindow is None:
            need_to_update = False

        if trackWindow is not None:
            hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)
            dst = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)  # roi_hist 설정하기
            ret, trackWindow = cv2.meanShift(dst, trackWindow, termination)
            x, y, w, h = trackWindow
            Cx = x + w // 2
            Cy = y + h // 2

        if (debug):
            result = img_color.copy()
            cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.line(result, (Cx, Cy), (Cx, Cy), (0, 0, 255), 10)
            self.debug(result)

        if Cx < 10 or Cx > img_color.shape[1] - 10 or Cy < 10 or Cy > img_color.shape[0] - 10:
            print("객체가 벗어났습니다.")
            need_to_update = False  # 새로운 객체를 찾으라는 명령을 내린다

<<<<<<< HEAD
        return need_to_update

    #  한 화면에서 3가지의 색을 검출해서 가장 많은 블록의 색을 return한다
    def selectObject_many(self, debug=True):

        # 디버깅용
        img_show = self.getImage()

        # 원하는 색깔을 주면 됨
        color_lst = ["RED", "BLUE", "GREEN"]
        color = "GREEN"

        # for color in color_lst:
        RBG_lst = ""  # 한 화면의 결과를 담는 창 "RED", "BLUE", "GREEN" 순으로
        img_color, img_mask = self.getBinImage(color=color)

        height, width = img_color.shape[:2]
        # 등고선 따기 (화면에 다 안들어온 이미지는 등고선이 안그려질 수도...)
        contours, hierarchy = cv2.findContours(img_mask, cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)
=======

        return need_to_update
>>>>>>> 3bf4c7fe9a7db3fe6fa3f01414ebc2a0af460482

        for cnt in contours:
            area = cv2.contourArea(cnt)
            print("area: ", area)
            if area > 30000:  # 노이즈를 제거하기 위해 일정 넓이 이상의 물체만 잡는다
                x, y, w, h = cv2.boundingRect(cnt)
                # 무게중심
                Cx = x + w // 2
                Cy = y + h // 2
                # 같은 색상이라도 무게중심의 y값이 작은것일 수록 더 가까이 있음
                # 무게중심이 아래로 내려가서 시야에서 가려지기전에 가려질 듯하면-> 목각도를 내려서 타깃을 확인한다 : 주의 끊기면 안됨 물체추적 끝남
                if 50 <= Cy <= height - 50 and 60 <= Cx <= width - 60:
                    RBG_lst += color[0]  # 색상값RGB를 집어넣는다
                    cv2.rectangle(img_color, (x, y), (x + w, h + y), (0, 0, 255), 2)
                    cv2.line(img_color, (Cx, Cy), (Cx, Cy), (0, 0, 255), 10)
        if (debug):
            # re_mask = img_mask.copy()
            # self.debug(re_mask)
            self.debug(img_color)
        if len(RBG_lst) != 0:
            print("한화면의 색상리스트: ", RBG_lst)

        return RBG_lst  # 문자열로 반환한다 RGGRRBB


if __name__ == "__main__":
    from Sensing.CameraSensor import Camera
<<<<<<< HEAD

    cam = Camera(1)
    imageProcessor = ImageProcessor(cam.width, cam.height)
    cam_t = Thread(target=cam.produce, args=(imageProcessor,))  # 카메라 센싱 쓰레드
    cam_t.start()  # 카메라 프레임 공급 쓰레드 동작

    while (True):
        i = imageProcessor.getBinImage(color="RED1", debug=DEBUG)
=======
    import time
    cam = Camera(0.1)
    imageProcessor = ImageProcessor(cam.width, cam.height)
    cam_t = Thread(target=cam.produce, args=(imageProcessor,))  # 카메라 센싱 쓰레드
    cam_t.start()  # 카메라 프레임 공급 쓰레드 동작
    times = range(1000)
    prev = time.time()
    for _ in times:
        imageProcessor.avoidObstacle1()
    curr = time.time()
    print("method1:" , curr - prev)
    prev = time.time()
    for _ in times:
        imageProcessor.avoidObstacle2()
    curr = time.time()
    print("method2: ", curr - prev)
>>>>>>> 3bf4c7fe9a7db3fe6fa3f01414ebc2a0af460482
    pass

