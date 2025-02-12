from Sensing.CameraSensor import Camera
from Sensing.ImageProcessing import ImageProcessor, Target
from Actuating.Motion import Motion, MOTION
from threading import Thread
import re
import cv2

baseline = (bx, by) = (320, 420)
footline = (fx, fy) = (320, 420)


# class Target:
#     def __init__(self):
#         self.mainTarget =
#         self.target =
#     def update(self):
#         self.target

class Robot:
    def __init__(self):
        self.cam = Camera(0.1)
        self.imageProcessor = ImageProcessor(self.cam.width, self.cam.height)
        self.cam_t = Thread(target=self.cam.produce, args=(self.imageProcessor,))  # 카메라 센싱 쓰레드
        self.cam_t.start()  # 카메라 프레임 공급 쓰레드 동작
        self.motion = Motion()
        self.motion.init()
        self.j = 0
        self.i = 0
        self.str = ""
        self.total_result = {}
        self.possible = []  # 가능한 방향 선택하기  (left45, 30)

    def traceTarget(self):
        VIEWS = ["DOWN60", "DOWN45", "DOWN35", "DOWN30", "DOWN10"]
        idx = 0
        self.motion.init()
        while (True):
            print("**traceTarget**")
            target = self.imageProcessor.detectTarget(color="RED", debug=True)
            if target is None:  # 만약에 객체가 없거나 이탈하면, 다시 객체를 찾아야한다.
                print("**No Target**")
                VIEW = self.findTarget(color="RED", turn="LEFT", debug=True)
                idx = VIEWS.index(VIEW)
                continue
            (dx, dy) = target.getDistance(baseline=baseline)
            print("distance gap . dx : {} , dy : {}".format(dx, dy))
            if (dy > 10):  # 기준선 보다 위에 있다면
                if (-40 <= dx <= 40):
                    print("walk")
                    self.motion.walk()
                elif (dx < -40):  # 른쪽
                    self.motion.move(direct=MOTION["DIR"]["RIGHT"])
                elif (dx > 40):  # 왼쪽
                    self.motion.move(direct=MOTION["DIR"]["LEFT"])
            elif (dy <= 10):
                if idx < len(VIEWS) - 1:  # 대가리를 다 내린게 아닌데 기준선보다 아래이면
                    self.motion.head(view=MOTION["VIEW"][VIEWS[idx]])
                    idx += 1
                    idx = idx % len(VIEWS)  # 인덱스 초과시
                    print("head down")
                elif idx == len(VIEWS) - 1:  # 대가리를 다 내린 상태에서 기준선 보다 아래이면 잡기 시전
                    print("catch: Target, doing grab")
                    self.motion.grab()

    def findTarget(self, color="RED", turn="LEFT", debug=False):  # 타깃이 발견될때까지 대가리 상하 좌우 & 몸 틀기 시전
        VIEWS = ["DOWN60", "DOWN45", "DOWN35", "DOWN30", "DOWN10"]
        HEADS = ["CENTER", "LEFT30", "RIGHT30"]
        TURNS = ["LEFT", "RIGHT"]
        HEAD_MOVING = [(VIEW, HEAD) for HEAD in HEADS for VIEW in VIEWS]

        self.motion.init()

        for VIEW, HEAD in HEAD_MOVING:  # 센터 위아래 -> 왼쪽 위아래 -> 오른쪽 위아래 순으로 탐색
            self.motion.head(view=MOTION["VIEW"][VIEW], direction=MOTION["DIR"][HEAD])
            target = self.imageProcessor.detectTarget(color=color, debug=debug)
            if target is None:  # 해당 방향에 타깃이 없다면
                continue
            else:  # 해당 방향에 타깃이 있다면 , 방향으로 몸을 틀고
                if "LEFT" in VIEW:  # 왼쪽에서 발견했으면 왼쪽으로 틀고
                    self.motion.turn(direct=MOTION["DIR"]["LEFT"])
                    self.motion.head(view=MOTION["VIEW"][VIEW])  # 대가리 바로
                    print("find left Target, turn left")
                elif "RIGHT" in VIEW:  # 오른쪽에서 발견했으면 오른쪽으로 틀고
                    self.motion.turn(direct=MOTION["DIR"]["RIGHT"])  # 대가리 바로
                    self.motion.head(view=MOTION["VIEW"][VIEW])
                    print("find right Target, turn right")
                else:
                    print("find center Target, not turn")
                return VIEW

        # 모든 탐색을 했지만 아무도 없다면 왼쪽 또는 오른 쪽으로 몸을 틀고 재탐색
        print("cannot find Target, turn " + turn)
        self.motion.turn(direct=MOTION["DIR"][turn])
        return self.findTarget(color=color)

    def changeAngle(self, i, j):
        # 목각도를 변경하기위해 로봇에게 통신을 한다음 다시 track을 시작한다
        # self.motion.walk(walk_signal=MOTION["WALK"]["END"])  # 로봇의 전진을 끝내는거
        head = ["", "DOWN80", "DOWN60", "DOWN45", "DOWN35", "DOWN30", "DOWN10"]  # index = i
        head_LR = ["", "CENTER", "LEFT30", "LEFT45", "LEFT60", "RIGHT30", "RIGHT45", "RIGHT60"]  # index = j
        self.motion.head(view=MOTION["VIEW"][head[i]], direction=MOTION["DIR"][head_LR[j]])
        self.str = head_LR[j]
        print(head[i], head_LR[j])
        if self.j == len(head_LR) - 1:
            self.j = 0
            self.i += 1
        try:
            self.mean_tracking()
        except:
            print("hello")
            self.changeAngle(self.i, self.j)

    def mean_tracking(self):
        cnt = 0
        flag = 0
        img_color, trackWindow, roi_hist, termination = self.imageProcessor.selectObject_mean("RED")
        # 몸도 움직이기 코드
        if "LEFT" in self.str:
            self.motion.init()
            self.motion.turn()
        else:
            self.motion.init()
            self.motion.turn(direct=MOTION["DIR"]["RIGHT"])
        while True:
            try:

                if cnt % 10 == 10:  # 추적대상 update 하기
                    img_color, trackWindow, roi_hist, termination = self.imageProcessor.selectObject_mean("GREEN2")
                # 만약 추적되는 객체가 없으면 False 를 반환한다
                print("8888")
                print("8888")
                need_to_change = self.imageProcessor.meanShiftTracking_color(img_color, trackWindow, roi_hist,
                                                                             termination)
                cnt += 1
                # 물체를 찾은적이 있으면 움직인다 / 물체를 찾은 적없이 처음 시작하면 무작정 walk 하지 않음
                if cnt == 1:
                    flag = 1
                print("8888")
                print("8888")
                self.motion.walk()
            except:
                if flag == 1:  # 무작정 처음부터 움직이는것 방지하기
                    self.motion.walk()
                    self.motion.walk()
                    self.motion.walk()
                self.j += 1
                self.changeAngle(self.i, self.j)

    ###### 현재 블록의 상태 확인################
    def checkCitizen(self):
        # 목각도를 꺾으면서 사진에 해당하는
        head = ["DOWN80", "DOWN60", "DOWN45", "DOWN30"]  # index = i
        head_LR = ["LEFT45", "LEFT30", "CENTER", "RIGHT30", "RIGHT45"]  # index = j

        # 각도를 돌리면서 물체를 확인한다
        for j in range(len(head_LR)):
            store_color = ""
            for i in range(len(head)):
                # 목각도 움직이고 사진찍어서 분석
                self.motion.head(view=MOTION["VIEW"][head[i]], direction=MOTION["DIR"][head_LR[j]])
                print("!!!!!!!!!!방향!!!!!!!!", head_LR[j], head[i])
                print("......")
                result = self.imageProcessor.selectObject_many()  # 반환값 : ["RED", "BLUE", "GREEN"]
                print("......")
                print("......")

                # 각 라인에 대해 분석한 결과를 저장
                store_color += result  # 문자열 결과인 GGRGB 따위를 더해준다
                # 각 라인에 대한 데이터를 저장
                if len(result) != 0:
                    self.total_result[head_LR[j]] = store_color  # {라인: RRGBRRG}
                    angle = re.findall("\d+", head[i])
                    self.possible.append((head_LR[j], angle[0]))
        print("resu;t:::", self.possible)

    def return_result(self):
        self.possible = sorted(self.possible, key=lambda x: x[1])
        print(self.possible)
        print("몸을 돌릴 방향", self.possible[0])
        target_turn = self.possible[0][0]
        angle = self.possible[0][1]
        # 몸 방향 돌리기

        if "LEFT" in target_turn:
            self.motion.init()
            self.motion.turn(repeat=4)
        elif "RIGHT" in target_turn:
            self.motion.init()
            self.motion.turn(direct=MOTION["DIR"]["RIGHT"], repeat=4)
        # 몸 방향 돌리기 2: 디테일하게 중심점을 맞춰서 (움직여야할 방향을 인자로 넘겨준다)
        self.centralize(target_turn, angle)

    def centralize(self, direction=None, angle=None, debug=True):
        if direction is not None and angle is not None:
            targetAngle = "DOWN" + angle
            self.motion.head(view=MOTION["VIEW"][targetAngle])

        while True:
            self.motion.head(view=MOTION["VIEW"][targetAngle])
            img_color, img_mask = self.imageProcessor.getBinImage(color="GREEN")

            height = img_color.shape[0]  # y 행
            width = img_color.shape[1]  # x 열

            # 등고선 따기 (화면에 다 안들어온 이미지는 등고선이 안그려질 수도...)
            contours, hierarchy = cv2.findContours(img_mask, cv2.RETR_TREE,
                                                   cv2.CHAIN_APPROX_SIMPLE)
            print("세부 조정을 시작합니다!")
            print("세부 조정을 시작합니다!")
            print("세부 조정을 시작합니다!")
            print("세부 조정을 시작합니다!")

            # 만약 앞선 전처리방향으로 몸을 돌렸는데도 보이는게 없다면
            if len(contours) == 0:
                print("객체가 없습니다.")
                if "LEFT" in direction:
                    self.motion.turn()
                else:
                    self.motion.turn(direct=MOTION["DIR"]["RIGHT"])
            else:
                sorted_list = sorted(contours, key=lambda cc: len(cc))
                x, y, w, h = cv2.boundingRect(sorted_list[-1])
                # 무게중심
                Cx = x + w // 2
                Cy = y + h // 2
                area = cv2.contourArea(sorted_list[-1])
                print("area:", area)
                if (width // 2) - 200 < Cx < 200 + (width // 2):
                    # 몸을 완전히 숙인다 발끝이 보이게 그리고 전진
                    self.motion.head(view=MOTION["VIEW"]["DOWN10"])
                    self.initwalking(angle)
                    break

                self.motion.init()
                if Cx < (width // 2) - 200:  # 중심보다 왼쪽이면 -> 몸을 왼쪽으로 돌린다
                    self.motion.turn()
                    print("왼쪽으로 몸을 돌립니다.")
                elif Cx > 200 + (width // 2):
                    self.motion.turn(direct=MOTION["DIR"]["RIGHT"])
                    print("오른쪽으로 몸을 돌립니다.")

    def initwalking(self, angle):
        # 목각도와 걸음수 dic
        angle_walk = {"30": 1, "45": 4, "60": 8, "80": 14}
        # 걸음수를 담는 변수
        walkCount = angle_walk[angle]
        cnt = 0
        walkCount = 20
        # 첫 걸음을 내딛을때 그린이 아니면 안보일때까지 옆걸음
        while True:
            obstacle_lst = []
            avoid = False
            avoid_color = ""
            screen_center = 0
            for color in ["RED", "BLUE"]:
                img_color, img_mask = self.imageProcessor.getBinImage(color=color)
                self.imageProcessor.debug(img_color)
                contours, hierarchy = cv2.findContours(img_mask, cv2.RETR_TREE,
                                                       cv2.CHAIN_APPROX_SIMPLE)
                screen_center = img_color.shape[1]
                if len(contours) != 0:  # 장애물이 발견되면 (파란색, 빨간색) avoid 를 킨다
                    print(color, " is traced!!!!")
                    obstacle_lst = sorted(contours, key=lambda cc: len(cc))
                    avoid = True
                    avoid_color = color
                    break

            # 1.....장애물이 있는 경우
            if avoid:
                x, y, w, h = cv2.boundingRect(obstacle_lst[-1])
                while True:
                    img_color, img_mask = self.imageProcessor.getBinImage(color=avoid_color)
                    contours, hierarchy = cv2.findContours(img_mask, cv2.RETR_TREE,
                                                           cv2.CHAIN_APPROX_SIMPLE)
                    if len(contours) == 0:
                        break
                    else:
                        obstacle_lst = sorted(contours, key=lambda cc: len(cc))
                        x, y, w, h = cv2.boundingRect(obstacle_lst[-1])
                        Cx = x + w // 2
                        # 왼쪽으로 장애물이 있으면 오른쪽으로 걷기
                        print(avoid_color, "의 물체를 피합니다 : ", x + w // 2)
                        if 0 < Cx < screen_center:
                            self.motion.move(direct=MOTION["DIR"]["RIGHT"])
                        elif screen_center < Cx < 2*screen_center:
                            self.motion.move()
            # 2........장애물이 없는 경우
            else:
                self.motion.walk()
                img_color, img_mask = self.imageProcessor.getBinImage(color="GREEN")
                contours, hierarchy = cv2.findContours(img_mask, cv2.RETR_TREE,
                                                       cv2.CHAIN_APPROX_SIMPLE)

                # 걷다가 초록색이 발견되면 멈춰서 몸을 돈다
                if len(contours) != 0:
                    while True:
                        print("잡을 물체를 탐색합니다: ")
                        img_color, img_mask = self.imageProcessor.getBinImage(color="GREEN")
                        contours, hierarchy = cv2.findContours(img_mask, cv2.RETR_TREE,
                                                               cv2.CHAIN_APPROX_SIMPLE)
                        obstacle_lst = sorted(contours, key=lambda cc: len(cc))
                        x, y, w, h = cv2.boundingRect(obstacle_lst[-1])
                        Cx = x + w // 2
                        if screen_center - 200 < Cx < screen_center + 200:  # 왼쪽으로 장애물이 있으면 오른쯕으로 걷기
                            print("물건을 집습니다.")
                            self.motion.grab()
                            self.motion.graboff()
                            ############################## 이부분에  while을 놓치는 경우대비 계속잡기
                        elif Cx > screen_center + 200:
                            self.motion.move(direct=MOTION["DIR"]["RIGHT"])
                        elif Cx < screen_center - 200:
                            self.motion.move()

                cnt += 1

            if cnt == walkCount:
                break

    def debuggingMode(self, direction, angle):
        self.motion.init()
        targetAngle = "DOWN" + angle
        self.motion.head(view=MOTION["VIEW"][targetAngle], direction=MOTION["DIR"][direction])
        while True:
            img = self.imageProcessor.getImage()
            self.imageProcessor.debug(img)


    # 물건을
    def turnMode(self):
        self.motion.init()
        self.motion.turn(repeat=5)
        while True:
            pass


if __name__ == "__main__":
    cam = Camera(0.1)
    imageProcessor = ImageProcessor(cam.width, cam.height)
    # p = Process(target=cam.produce, args=[imageProcessor]) # 카메라 센싱 데이터 한 프로세스 내에서 자원의 공유는 가능하다. 그러나 서로 다른 프로세스에서 자원의 공유는 불가능하다....
    # p.start()
    t = Thread(target=cam.produce, args=(imageProcessor,))  # 카메라 센싱 쓰레드
    t.start()




