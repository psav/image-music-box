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
    ls_ang = math.tan((top_l[0] - bot_l[0]) / 478)
    rs_ang = math.tan((top_r[0] - bot_r[0]) / 478)
    av_ang = (ls_ang + rs_ang) / 2

    print("angles", ls_ang, rs_ang)

    # if top_l[0] < bot_l[0]:
    #     av_ang = -av_ang

    if top_l[0] < bot_l[0]:

        av_ang = -av_ang

        a = top_r[0] - top_r[1]
        y1 = a * math.sin(av_ang)
        x1 = a * math.sin(av_ang) * math.tan(av_ang)
        print(x1, y1)

        cv2.line(frame, (int(top_l[0] + x1), int(top_l[1] + y1)), top_r, (255, 255, 0), thickness=1)

        x1r = (int(top_l[0] + x1), int(top_l[1] + y1))
        x2r = top_r
        d = a * math.cos(av_ang)
        print(av_ang)

    else:
        #av_ang = -av_ang

        a = top_l[0] - top_l[1]
        y1 = a * math.sin(av_ang)
        x1 = a * math.sin(av_ang) * math.tan(av_ang)
        print(x1, y1)

        cv2.line(frame, (int(top_r[0] + x1), int(top_r[1] + y1)), top_l, (255, 255, 0), thickness=1)

        x1r = top_l
        x2r = (int(top_r[0] + x1), int(top_r[1] + y1))
        d = a * math.cos(av_ang)
        print(av_ang)

    for coord in coords:
        # Display the resulting frame
        cv2.circle(frame, coord, 10, (255, 255, 0), thickness=1)

    print(d)
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