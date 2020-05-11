import socket
from _thread import *
from player import Player
from ball import Ball
from game import Game, check_game_state
import pickle
import pygame
from buffer import Buffer
import copy
import math

server = '172.104.130.211'
#server = '127.0.0.1'
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)


w, h = 788,444
pairs = 5
player1_exemplary = Player(50, 414, 30, (255,0,0),30,w/2-30,pygame.K_a,pygame.K_d,pygame.K_w)
player2_exemplary = Player(w - 50, 414, 30, (0,255,0), w/2+30, w-30, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP)
ball_exemplary = Ball(200, 250, 0, 0, 20)

player1_slots_taken = []
player2_slots_taken = []
players1 = []
players2 = []
buffers_player1 = []
buffers_player2 = []
buffers_ball = []
games = []
balls = []
players_pause_game = []
pause_game = []
update_players1 = []
update_players2 = []

for i in range(0,pairs):
    player1_slots_taken.append(False)
    player2_slots_taken.append(False)
    players1.append(player1_exemplary)
    players2.append(player2_exemplary)
    buffers_player1.append(Buffer())
    buffers_player2.append(Buffer())
    buffers_ball.append(Buffer())
    games.append(Game())
    players_pause_game.append([False, False])
    pause_game.append(False)
    balls.append(ball_exemplary)
    update_players1.append(False)
    update_players2.append(False)


def get_server_address():
    return server

def threaded_client(conn, player, slot):
    if player == 0:
        conn.send(pickle.dumps([player1_exemplary, player2_exemplary, balls[slot], games[slot], player]))
    else:
        conn.send(pickle.dumps([player2_exemplary, player1_exemplary, balls[slot], games[slot], player]))

    reply = ""
    while True:
        try:
            data = pickle.loads(conn.recv(2048))

            if not data:
                print("Disconnected")
                break
            else:
                flag_pause, flag_resume = data[1], data[2]
                if flag_resume:
                    players_pause_game[slot][player] = False
                if flag_pause:
                    players_pause_game[slot][player] = True
                if players_pause_game[slot][0] or players_pause_game[slot][1]:
                    pause_game[slot] = True
                else:
                    pause_game[slot] = False

                if player == 0:
                    update_players1[slot] = True
                    buffers_player1[slot] = data[0]
                    reply = [buffers_player1[slot], buffers_player2[slot], buffers_ball[slot], games[slot], player2_slots_taken[slot], pause_game[slot]]
                else:
                    update_players2[slot] = True
                    buffers_player2[slot] = data[0]
                    reply = [buffers_player2[slot], buffers_player1[slot], buffers_ball[slot], games[slot], player1_slots_taken[slot], pause_game[slot]]

            # if we got updates from both of players
            if update_players1[slot] and update_players2[slot]:
                buf1 = buffers_player1[slot]
                buf2 = buffers_player2[slot]
                shortest = min(len(buf1.buf), len(buf2.buf))
                buffers_ball[slot] = Buffer()
                for i in range(0, shortest):
                    players1[slot].x = buf1.buf[math.ceil(i/shortest*len(buf1.buf))][0]
                    players1[slot].y = buf1.buf[math.ceil(i/shortest*len(buf1.buf))][1]
                    players2[slot].x = buf2.buf[math.ceil(i/shortest*len(buf2.buf))][0]
                    players2[slot].y = buf2.buf[math.ceil(i/shortest*len(buf2.buf))][1]
                    balls[slot].move([players1[slot], players2[slot]], games[slot], w)
                    buffers_ball[slot].buf.append([balls[slot].x, balls[slot].y])
                    check_game_state(balls[slot], players1[slot], players2[slot], games[slot], w)
                update_players1[slot] = False
                update_players2[slot] = False

            conn.send(pickle.dumps(reply))
        except:
            break


    print("Lost connection")
    print("Player " + str(player+1) + " slot " + str(slot))
    conn.close()
    if player == 0:
        player1_slots_taken[slot] = False
    else:
        player2_slots_taken[slot] = False

def reset_game(slot):
    buffers_player1[slot] = Buffer()
    buffers_player2[slot] = Buffer()
    players1[slot] = copy.copy(player1_exemplary)
    players2[slot] = copy.copy(player2_exemplary)
    buffers_ball[slot] = Buffer()
    games[slot] = Game()
    players_pause_game[slot] = [False, False]
    pause_game[slot] = False
    balls[slot] = copy.copy(ball_exemplary)
    update_players1[slot] = False
    update_players2[slot] = False

s.listen(pairs*2)
print("Waiting for a connection, Server Started")
run = True
while run:
    conn, addr = s.accept()
    print("Connected to:", addr)

    first_player1_free_slot = pairs
    first_player2_free_slot = pairs
    for i in range(0,pairs):
        if player1_slots_taken[i] == False and i < first_player1_free_slot:
            first_player1_free_slot = i
        if player2_slots_taken[i] == False and i < first_player2_free_slot:
            first_player2_free_slot = i

    if first_player1_free_slot == pairs and first_player2_free_slot == pairs:
        print("No empty slots...")
    else:
        if first_player1_free_slot == first_player2_free_slot:
            print("Player 1 slot " + str(first_player1_free_slot))
            player1_slots_taken[first_player1_free_slot] = True
            start_new_thread(threaded_client, (conn, 0, first_player1_free_slot))
        elif first_player1_free_slot < first_player2_free_slot:
            print("Player 1 slot " + str(first_player1_free_slot))
            reset_game(first_player1_free_slot)
            player1_slots_taken[first_player1_free_slot] = True
            start_new_thread(threaded_client, (conn, 0, first_player1_free_slot))
        else:
            print("Player 2 slot " + str(first_player2_free_slot))
            reset_game(first_player2_free_slot)
            player2_slots_taken[first_player2_free_slot] = True
            start_new_thread(threaded_client, (conn, 1, first_player2_free_slot))
