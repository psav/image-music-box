import numpy as np
import cv2
import math

cap = cv2.VideoCapture(2)

class ROOB(Exception):
    pass

def do_thang():
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)

    thresh = cv2.threshold(gray, 0, 255,
	    cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]


    top_finished_streaks = []
    streak = []
    for a in range(len(thresh[0])):
        if thresh[0][a] == 0:
            streak.append(a)
        if thresh[0][a] == 255 and len(streak) > 0:
            if len(streak) < 5:
                streak = []
            else:
                top_finished_streaks.append(streak)
                streak = []

    streak = []
    bottom_finished_streaks = []
    for a in range(len(thresh[478])):
        if thresh[478][a] == 0:
            streak.append(a)
        if thresh[478][a] == 255 and len(streak) > 0:
            if len(streak) < 5:
                streak = []
            else:
                bottom_finished_streaks.append(streak)
                streak = []
    print(len(top_finished_streaks), len(bottom_finished_streaks))

    print(top_finished_streaks[0][0], 0, top_finished_streaks[-1][-1], 0, bottom_finished_streaks[0][0], 478, bottom_finished_streaks[-1][-1], 478)
    top_l = (top_finished_streaks[0][0], 0)
    top_r = (top_finished_streaks[-1][-1], 0)
    bot_l = (bottom_finished_streaks[0][0], 478)
    bot_r = (bottom_finished_streaks[-1][-1], 478)
    coords = [top_l, top_r, bot_l, bot_r]

    top_m = (((top_r[0] - top_l[0]) / 2) + top_l[0], 0)
    bot_m = (((bot_r[0] - bot_l[0]) / 2) + bot_l[0], 478)

    top_m_i = (int(top_m[0]), int(top_m[1]))
    bot_m_i = (int(bot_m[0]), int(bot_m[1]))

    print("midpt", top_m, bot_m, (bot_m[0] - top_m[0]))

    cv2.line(frame, top_m_i, bot_m_i, (0, 0, 255), thickness=1)

    ang = math.atan(478 / (bot_m[0] - top_m[0]))

    print("nang", math.degrees(ang))

    top_mid_dis_a = (top_r[0] - top_l[0]) / 2

    hyp = top_mid_dis_a * math.sin(ang) * 2

    side_ang = math.pi / 2 - ang

    xer = hyp * math.cos(side_ang)
    yer = hyp * math.sin(side_ang)
    print("nadj", xer, yer, side_ang)
    print("nhyp", hyp, top_mid_dis_a)

    if top_l[0] < bot_l[0]:
        top_mod = (int(top_r[0] - xer), int(top_r[1] + yer))

        cv2.line(frame, top_r, top_mod, (0, 0, 255), thickness=1)

    if top_l[0] > bot_l[0]:
        top_mod = (int(top_l[0] + xer), int(top_l[1] - yer))

        cv2.line(frame, top_l, top_mod, (0, 0, 255), thickness=1)

    for coord in coords:
        # Display the resulting frame
        cv2.circle(frame, coord, 10, (255, 255, 0), thickness=1)

    cv2.imshow('thresh',thresh)
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        raise ROOB

while(True):
    try:
        do_thang()
    except ROOB:
        break
    except Exception as e:
        print(e)
        continue

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()