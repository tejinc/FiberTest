#!/usr/local/bin/python3.8

from ft_arduino import Arduino
from time import sleep

# allow me to turn off board stuff
no_board = False  # True

# # Arduino params and variables
b_port = '/dev/cu.usbserial-D306E6BB'  # # <- this can vary
steps_to_inch = 100
full_steps_to_inch = 100  # use full speed as a reference
steps_to_cm = 39.37
speed_dict = {
              'Full': ("LOW", "LOW"),
              'Half': ("HIGH", "LOW"),
              'Quarter': ("LOW", "HIGH"),
              'Eigth': ("HIGH", "HIGH")
             }
# board named pin values
b_stp = 2  # step
b_dir = 3  # direction
b_MS1 = 4  # logic input 1
b_MS2 = 5  # logic input 2
b_en = 6   # enable FET
b_x = 0
b_y = 0
b_baud = "9600"  # # Stepper seems to need to be at this baud

# for ease set up some globals here BAD!!
cbl_len = 26.0  # inches
num_intrv = 8.0
in_intrv = cbl_len / num_intrv
start_home = steps_to_inch / 2
end_home = cbl_len * steps_to_inch - (steps_to_inch / 2)  # leave half an inch on each end
interval = end_home // num_intrv  # we floor this so nothing breaks
home_return = interval * num_intrv  # how many steps to get back home
home = start_home
current_speed = 2


a_board = Arduino(b_baud, b_port)  # # <-
# a_board = 'Fake for testing'  # # <-


def board_setup():

    if not no_board:

        a_board.pinMode(b_stp, "OUTPUT")
        a_board.pinMode(b_dir, "OUTPUT")
        a_board.pinMode(b_MS1, "OUTPUT")
        a_board.pinMode(b_MS2, "OUTPUT")
        a_board.pinMode(b_en, "OUTPUT")
        # board_set_speed(a_board, 'Full')
        board_set_speed(a_board, 'Half')
        # print('board setup')
        # #

    return a_board


def board_set_speed(a_board, speed):

    ms1 = ''
    ms2 = ''

    ms1 = speed_dict[speed][0]
    ms2 = speed_dict[speed][1]
    if not no_board:
        a_board.digitalWrite(b_MS1, ms1)  # #
        a_board.digitalWrite(b_MS2, ms2)  # #

    return


def zero_carriage(a_board):

    global home_return

    if not no_board:
        print('Zeroing carriage.')
        a_board.digitalWrite(b_dir, "HIGH")
        a_board.digitalStepper('B', b_dir, b_stp, int(home_return))  # home should be the distance from 0
        sleep(5.0)  # need to wait for the board to react before quitting

    return


def board_reset(a_board):

    if not no_board:
        a_board.digitalWrite(b_stp, "LOW")
        a_board.digitalWrite(b_dir, "LOW")
        a_board.digitalWrite(b_MS1, "LOW")
        a_board.digitalWrite(b_MS2, "LOW")
        a_board.digitalWrite(b_en, "HIGH")

    return


def return_back_home(a_board):

    global home_return

    print('Stepping backward to home ', home_return)
    if not no_board:
        a_board.digitalWrite(b_dir, "HIGH")  # #  move backward to home
        a_board.digitalStepper('B', b_dir, b_stp, int(home_return))

    return


def return_forward_home(a_board):

    global home_return

    print('Stepping forward to home ', home_return)
    if not no_board:
        a_board.digitalWrite(b_dir, "LOW")  # #  move forward to home
        a_board.digitalStepper('F', b_dir, b_stp, int(home_return))

    return


def move_forward(a_board):

    global home
    global in_intrv

    intv_cnt = 0

    print('Home is at ', home/steps_to_inch, ' inches. Moving forward!')
    print('Press Return when you are ready to move.')

    while intv_cnt < num_intrv:
        istr = str(intv_cnt) + '> '
        move_it = input(istr)
        intv_cnt += 1
        print('Stepping forward to -> ', intv_cnt*in_intrv)
        if not no_board:
            a_board.digitalWrite(b_dir, "LOW")  # #  move forward from home
            a_board.digitalStepper('F', b_dir, b_stp, int(interval))
        print(intv_cnt * interval, '>>')

    istr = str(intv_cnt) + '> '
    move_it = input(istr)  # wait for the last return
    print(intv_cnt * interval, '>>')

    return_back_home(a_board)

    return


def move_backward(a_board):

    global home
    global in_intrv
    global cbl_len

    intv_cnt = 0
    where = cbl_len

    print('Home is at ', home/steps_to_inch, ' inches. Moving backward!')
    print('Press Return when you are ready to move.')

    while intv_cnt < num_intrv:
        istr = str(intv_cnt) + '< '
        move_it = input(istr)
        intv_cnt += 1
        print('Stepping backward to -> ', where - (intv_cnt * in_intrv))
        if not no_board:
            a_board.digitalWrite(b_dir, "HIGH")  # #  move backward from home
            a_board.digitalStepper('B', b_dir, b_stp, int(interval))
        print(intv_cnt * interval, '<<')

    istr = str(intv_cnt) + '< '
    move_it = input(istr)  # wait for the last return
    print(intv_cnt * interval, '<<')

    return_forward_home(a_board)

    return


def toggle_home(a_board, for_bck_flag):

    diff_home_step = end_home - start_home

    if for_bck_flag == '0' and not no_board:
        a_board.digitalWrite(b_dir, "HIGH")  # #  move backward to new start_home
        a_board.digitalStepper('B', b_dir, b_stp, diff_home_step)
    elif not no_board:
        a_board.digitalWrite(b_dir, "LOW")  # #  move forward to new end_home
        a_board.digitalStepper('F', b_dir, b_stp, diff_home_step)

    return


def reset_direction(a_board, for_bck_flag):

    global home
    global start_home
    global end_home

    for_bck_flag = '0' if for_bck_flag == '1' else '1'
    home = start_home if home == end_home else end_home
    toggle_home(a_board, for_bck_flag)

    return for_bck_flag


def move_initial_home(home):

    print('Home -> ', home)
    if not no_board:
        a_board.digitalWrite(b_dir, "LOW")  # #  move forward
        a_board.digitalStepper('F', b_dir, b_stp, home)

    return


def set_direction(a_board):

    global home
    global start_home
    global end_home

    # for_bck_flag = 'n'  # flag the direction we are reading & set home
    for_bck_flag = '1'  # flag the direction we are reading & set home

    """
    while True:
        if for_bck_flag != '0' and for_bck_flag != '1':
            for_bck_flag = input('Enter 0 to travel forward, or 1 to travel backward : ')
        else:
            break
    """

    if for_bck_flag == '0':
        home = start_home
    else:
        home = end_home

    if not no_board:
        pass
        # move_initial_home(home)

    return for_bck_flag


def reset_globals(factor):

    global full_steps_to_inch
    global steps_to_inch
    global start_home
    global end_home
    global num_intrv
    global interval
    global home_return
    global home
    global current_speed

    if factor == 2:
        mult = 2
    elif factor == 3:
        mult = 4
    elif factor == 4:
        mult = 8
    else:
        mult = 1
    steps_to_inch = full_steps_to_inch * mult

    start_home = steps_to_inch / 2
    end_home = cbl_len * steps_to_inch - (steps_to_inch / 2)  # leave half an inch on each end
    interval = end_home / num_intrv  # we floor this so nothing breaks
    home_return = interval * num_intrv  # how many steps to get back home
    home = start_home


def change_speed(a_board):


    spd_sel = ''
    selections = {'1': 'Full',
                  '2': 'Half',
                  '3': 'Quarter',
                  '4': 'Eigth'}

    print(' The speed choices are : ')
    print('\t1. Full (default)\n\t2. Half\n\t3. Quarter\n\t4. Eigth')


    while spd_sel not in selections:
        spd_sel = input('Enter the number of your speed selection : ')

    board_set_speed(a_board, selections[spd_sel])
    print('Speed Changed to ', selections[spd_sel])
    reset_globals(int(spd_sel))

    return


def run_fibertest(a_board):

    board_set_speed(a_board, 'Half')
    reset_globals(2)

    next = input('Enter y : run again, s : set speed, q : quit : ')
    lnext = next.lower()

    for_bck_flag = set_direction(a_board)
    while lnext == 'y' or lnext == 'r' or lnext == 's':
        if lnext == 's':
            change_speed(a_board)
        else:
            if lnext == 'r':
                for_bck_flag = reset_direction(a_board, for_bck_flag)

            if for_bck_flag == '0':
                move_forward(a_board)
            else:
                move_backward(a_board)
            
        lnext = 'next'
        loop = True
        while loop:
            print('TRUE')
            if lnext == 'q':
                return
            elif lnext != 'y' and lnext != 'r' and lnext != 's':
                # next = input('Enter y : run again, r : reset direction, s : set speed, q : quit : ')
                next = input('Enter y : run again, s : set speed, q : quit : ')
                lnext = next.lower()
                if lnext == 'r':
                    lnext = 'y'  # disable reverse
            else:
                break

    return


def main():

    a_board = board_setup()  # Set up Arduino - nothing happens without this
    run_fibertest(a_board)
    zero_carriage(a_board)
    board_reset(a_board)

    return


if __name__ == '__main__':
    main()
