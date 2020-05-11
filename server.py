import socket
from _thread import *
from player import Player
from ball import Ball
from game import Game, check_game_state, reset
import pickle
import pygame

server = socket.gethostbyname(socket.gethostname())
port = 5555

w, h = 788,444
players = [Player(50, 414, 30, (255,0,0),30,w/2-30,pygame.K_a,pygame.K_d,pygame.K_w),
           Player(w - 50, 414, 30, (0,255,0), w/2+30, w-30, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP)]
ball_exemplary = Ball(200, 250, 0, 0, 20)
ball = ball_exemplary
game = Game()
players_pause_game = [False, False]
master_connected = False
guest_connected = False

def get_server_address():
    return server

def threaded_client(conn, player):
    global master_connected, guest_connected
    if player == 0:
        conn.send(pickle.dumps([players[0], players[1], ball, game, guest_connected]))
    else:
        conn.send(pickle.dumps([players[1], players[0], ball, game, guest_connected]))
    reply = ""

    while True:
        try:
            data = pickle.loads(conn.recv(2048))

            if not data or master_connected == False:
                print("Disconnected")
                break
            else:
                players[player], flag_pause, flag_resume = data

                if flag_resume:
                    players_pause_game[player] = False
                if flag_pause:
                    players_pause_game[player] = True
                if players_pause_game[0] or players_pause_game[1]:
                    game.pause = True
                else:
                    game.pause = False
                if player == 0:
                    reply = [players[1], ball, game, guest_connected]
                else:
                    reply = [players[0], ball, game, guest_connected]

                if player == 1 and game.pause == False and guest_connected == True:
                    ball.move(players,game,w)
                    check_game_state(ball, players[0], players[1], game, w)

            conn.send(pickle.dumps(reply))
        except:
            break

    print("Lost connection with player " + str(player))
    conn.close()
    if player == 0:
        master_connected = False
    else:
        guest_connected = False


def start_server():
    global master_connected, guest_connected, game, ball, ball_exemplary, players_pause_game
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind((server, port))
    except socket.error as e:
        str(e)

    s.listen(2)
    print("Waiting for a connection, Server Started")
    conn, addr = s.accept()
    print("Connected to:", addr)
    master_connected = True
    start_new_thread(threaded_client, (conn, 0))

    s.settimeout(2)
    run = True
    while run:
        if master_connected == False:
            run = False

        if guest_connected == False:
            try:
                conn, addr = s.accept()
                print("Connected to:", addr)
                game = Game()
                ball = ball_exemplary
                players_pause_game[1] = False
                guest_connected = True
                start_new_thread(threaded_client, (conn, 1))
            except socket.timeout:
                pass
        pygame.time.delay(100)

    print("stopping server")
    s.close()
