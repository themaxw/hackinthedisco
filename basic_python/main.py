import math

from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server, udp_client
from threading import Thread

from time import sleep

update_rate = 1 / 10
check_trackers_up_to = 15
game_dim_x = 17.0
game_dim_y = 10.0
update_rate = 1 / 20
# from functools import partial


def print_volume_handler(unused_addr, args, volume):
    print("[{0}] ~ {1}".format(args[0], volume))


def print_compute_handler(unused_addr, args, volume):
    try:
        print("[{0}] ~ {1}".format(args[0], args[1](volume)))
    except ValueError:
        pass


def handle_x(unused_addr, args, x_pos, *mehr_args):
    ball_position[0] = x_pos
    print(f"{unused_addr}, {args[0]}")


def handle_y(unused_addr, args, y_pos, *mehr_args):
    ball_position[1] = y_pos


def handle_speed(unused_addr, args, speed, *mehr_args):
    # lmao was soll ich denn damit?
    pass


positions = []
ball_position = [0, 0, 0]

listen_ip = "0.0.0.0"
listen_port = 10000
# send_ip = "127.0.0.1"
send_ip = "192.168.0.232"
send_port = 10009

n_trackers = 15
n_lights = 20

recv_path = "/tracker_{}:vals:{}"
send_path = "/light{}/{}"

thread_runs = True


def send_all(client: udp_client.SimpleUDPClient, x, y, z):
    for i in range(n_lights):
        print(x, y)
        client.send_message(send_path.format(i + 1, "xpos"), x)
        client.send_message(send_path.format(i + 1, "ypos"), y)
        client.send_message(send_path.format(i + 1, "height"), z)
        client.send_message(send_path.format(i + 1, "intensity"), 0.8)


def send_thread():
    client = udp_client.SimpleUDPClient(send_ip, send_port)

    while thread_runs:
        #update_game()
        #send_all(client, *ball_position)
        sleep(update_rate)


if __name__ == "__main__":
    # Init array of tracker positions
    for i in range(1, check_trackers_up_to+1):
        positions.append((0.0, 0.0))
    print(positions)
    sleep(10)

    dispatcher = Dispatcher()
    for i in range(1):
        dispatcher.map(recv_path.format(i + 1, "pos_x"), handle_x, i)
        dispatcher.map(recv_path.format(i + 1, "pos_y"), handle_y, i)
        dispatcher.map(recv_path.format(i + 1, "speed"), handle_speed, i)
    send_thread = Thread(target=send_thread).start()
    server = osc_server.ThreadingOSCUDPServer((listen_ip, listen_port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
    thread_runs = False