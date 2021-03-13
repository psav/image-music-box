import numpy as np
import cv2
import math
import mido
import sys

for lport in mido.get_output_names():
    if "FLUID" in lport:
        port = mido.open_output(lport)

note_data = [60, 62, 67, 69, 71, 72, 74, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 98, 100]
note_data = note_data[::-1]
note_data = [note - 12 for note in note_data]

cap = cv2.VideoCapture(2)

class ROOB(Exception):
    pass

def do_thang(last_notes):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)

    thresh = cv2.threshold(gray, 0, 255,
	    cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]


    top_finished_streaks = []
    streak = []
    for a in range(len(thresh[10])):
        if thresh[10][a] == 0:
            streak.append(a)
        if thresh[10][a] == 255 and len(streak) > 0:
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

    print(top_finished_streaks[0][0], 10, top_finished_streaks[-1][-1], 10, bottom_finished_streaks[0][0], 478, bottom_finished_streaks[-1][-1], 478)
    top_l = (top_finished_streaks[0][0], 10)
    top_r = (top_finished_streaks[-1][-1], 10)
    bot_l = (bottom_finished_streaks[0][0], 478)
    bot_r = (bottom_finished_streaks[-1][-1], 478)
    coords = [top_l, top_r, bot_l, bot_r]

    top_m = (((top_r[0] - top_l[0]) / 2) + top_l[0], 10)
    bot_m = (((bot_r[0] - bot_l[0]) / 2) + bot_l[0], 478)

    top_m_i = (int(top_m[0]), int(top_m[1]))
    bot_m_i = (int(bot_m[0]), int(bot_m[1]))

    print("midpt", top_m, bot_m, (bot_m[0] - top_m[0]))

    cv2.line(frame, top_m_i, bot_m_i, (0, 0, 255), thickness=1)

    if bot_m[0] != top_m[0]:

        ang = math.atan(478 / (bot_m[0] - top_m[0]))

        print("nang", math.degrees(ang))

        top_mid_dis_a = (top_r[0] - top_l[0]) / 2

        hyp = top_mid_dis_a * math.sin(ang) * 2

        side_ang = math.pi / 2 - ang

        xer = hyp * math.cos(side_ang)
        yer = hyp * math.sin(side_ang)
        print("nadj", xer, yer, side_ang)
        print("nhyp", hyp, top_mid_dis_a)

        if ang > 0:
            top_mod = (int(top_r[0] - xer), int(top_r[1] + yer))

            p = (top_mod, top_r)

        elif ang < 0:
            top_mod = (int(top_l[0] + xer), int(top_l[1] - yer))

            p = (top_l, top_mod)

        xstep = abs(xer / hyp)
        ystep = - (yer / hyp)
        
        xc = p[0][0]
        yc = min(p[0][1], p[1][1])

        liner = []

        while xc < p[1][0]:
            xc = xc + xstep
            yc = yc + ystep
            liner.append(thresh[int(yc)][int(xc)])

        paper_width = 70

        xstep = abs(xer / paper_width)
        ystep = - yer / paper_width
        
        xc = p[0][0]
        yc = p[0][1]

        new_notes = []

        for bb in range(30):
            ccy = int(yc + (6.3 * ystep) + (bb * ystep * 2))
            ccx = int(xc + (6.3 * xstep) + (bb * xstep * 2))
            
            new_notes.append(thresh[ccy][ccx])
            if thresh[ccy][ccx] == 255:
                thickness = -1
            else:
                thickness = 1
            cv2.circle(frame, (ccx, ccy), int(xstep), (0, 0, 255), thickness=thickness,)

        for i, pair in enumerate(zip(last_notes, new_notes)):
            msg = False
            if pair == (0, 255):
                print("trigger a ", note_data[i])
                msg = mido.Message('note_on', note=note_data[i])
            elif pair == (255, 0):
                print("trigger a ", note_data[i])
                msg = mido.Message('note_off', note=note_data[i])
            if msg:            
                port.send(msg)

    else:
        p = (top_l, top_r)

    cv2.line(frame, p[0], p[1], (0, 0, 255), thickness=1)

    # for pix in range(int(hyp)):


    for coord in coords:
        # Display the resulting frame
        cv2.circle(frame, coord, 10, (255, 255, 0), thickness=1)

    cv2.imshow('thresh',thresh)
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        raise ROOB

    return new_notes

last_notes = []
while(True):
    try:
        last_notes = do_thang(last_notes)
    except ROOB:
        break
    except Exception as e:
        print(e)
        continue

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()