from player import *
from ball import Ball
from network import Network
from server import start_server, get_server_address
from game import Game, check_game_state
from _thread import *
from textpanel import TextPanel
from screens import *
from buffer import Buffer
import copy

pygame.init()

pygame.display.set_caption("Blobby Volley")
bg = pygame.image.load("tlo3.png")
w, h = 788, 444
print(w, h)
win = pygame.display.set_mode((w, h))
clock = pygame.time.Clock()

def redraw_game_window(win, bg, player1, player2, ball, game):  # Wyświetlanie
    win.blit(bg, (0, 0))
    ball.draw(win)
    player1.draw(win)
    player2.draw(win)
    pygame.draw.line(win, (0, 0, 0,), (394, 450), (394, 200))
    game.show_stats(w, h, win)
    if ball.y < ball.radius:
        pygame.draw.polygon(win, (0, 0, 0),
        # Dodaje strzałkę pokazującą gdzie jest piłka w przypadku wylecenia za ekran
        ((int(ball.x), 6), (int(ball.x) - 6, 12), (int(ball.x) - 2, 8), (int(ball.x) - 2, 26),
        (int(ball.x) + 2, 26), (int(ball.x) + 2, 8), (int(ball.x) + 6, 12)))
    pygame.display.update()


def LAN_game(server_address):
    n = Network(server_address)
    try:
        player1, player2, ball, game, guest_connected = n.getP()
    except:
        win.blit(bg, (0, 0))
        if confirmation_screen("Cannot connect. Do you want try again?"):
            LAN_game(server_address)
        else:
            menu_screen()

    run = True
    while run:
        clock.tick(75)

        try:
            # n.send([player1, flag_pause, flat_resume])
            player2, ball, game, guest_connected = n.send([player1, False, False])
        except:
            win.blit(bg, (0,0))
            text1 = TextPanel(w // 2, h // 4.5, "comicsans", 30, "Lost connection with server " + str(get_server_address()), (0, 0, 0))
            text2 = TextPanel(w // 2, h // 3.4, "comicsans", 34, "Back to menu...", (0, 0, 0))
            text1.draw(win)
            text2.draw(win)
            pygame.display.update()
            pygame.time.delay(2000)
            break


        redraw_game_window(win, bg, player1, player2, ball, game)
        if game.pause or guest_connected == False:
            text1 = TextPanel(w//2, h//4.5, "comicsans", 30, "Server " + str(get_server_address()), (0, 0, 0))
            if guest_connected == False:
                text2 = TextPanel(w // 2, h//3.4, "comicsans", 34, "Waiting for opponent...", (0, 0, 0))
            else:
                text2 = TextPanel(w // 2, h // 3.4, "comicsans", 34, "Game paused...", (0, 0, 0))
            text1.draw(win)
            text2.draw(win)
            pygame.display.update()
            pygame.time.delay(50)
        else:
            player1.move()

        if game.is_game_over():
            n.disconnect()
            run = False
            game_over_screen(game)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            n.send([player1, True, False])
            if confirmation_screen("Are you sure you want to quit?"):
                n.disconnect()
                run = False
            else:
                n.send([player1, False, True])
    menu_screen()


game = Game()
opponent_connected = False
pause_game = False
buffer_player1 = Buffer()
buffer_player1_recv = Buffer()
buffer_player2 = Buffer()
buffer_ball = Buffer()
def thread_updating_data(n,c):
    global buffer_player1, buffer_player1_recv, buffer_player2, buffer_ball, game, opponent_connected, pause_game
    while True:
        try:
            bufp1 = buffer_player1
            buffer_player1 = Buffer()
            buffer_player1_recv, buffer_player2, buffer_ball, game, opponent_connected, pause_game = n.send([bufp1, False, False])

            #pygame.time.delay(50)
        except:
            break

def online_game(server_address):
    n = Network(server_address)
    global buffer_player1, buffer_player1_recv, buffer_player2, buffer_ball, game, ball, opponent_connected, pause_game
    try:
        player1, player2, ball, game, player = n.getP()
        player1_recv = copy.copy(player1)
    except:
        win.blit(bg, (0, 0))
        if confirmation_screen("Cannot connect. Do you want try again?"):
            online_game(server_address)
        else:
            menu_screen()

    print("connected")
    start_new_thread(thread_updating_data, (n,0))

    run = True
    while run:
        clock.tick(75)
        keys = pygame.key.get_pressed()

        if opponent_connected == False:
            game = Game()
            ball = Ball(200, 250, 0, 0, 20)
            text = TextPanel(w // 2, h // 3.4, "comicsans", 34, "Waiting for opponent...", (0, 0, 0))
            text.draw(win)
            pygame.display.update()
            pygame.time.delay(50)
        elif pause_game:
            text = TextPanel(w // 2, h // 3.4, "comicsans", 34, "Game paused...", (0, 0, 0))
            text.draw(win)
            pygame.display.update()
            pygame.time.delay(50)
        else:
            player1.move()
            buffer_player1.buf.append([player1.x, player1.y])

            if len(buffer_player1_recv.buf) > 0:
                player1_recv.x, player1_recv.y = buffer_player1_recv.buf[0][0], buffer_player1_recv.buf[0][1]
                buffer_player1_recv.buf = buffer_player1_recv.buf[1:]

            if len(buffer_player2.buf) > 0:
                player2.x, player2.y = buffer_player2.buf[0][0], buffer_player2.buf[0][1]
                buffer_player2.buf = buffer_player2.buf[1:]

            if len(buffer_ball.buf) > 0:
                ball.x, ball.y = buffer_ball.buf[0][0], buffer_ball.buf[0][1]
                buffer_ball.buf = buffer_ball.buf[1:]




        redraw_game_window(win, bg, player1_recv, player2, ball, game)
        if game.is_game_over():
            n.send([Buffer(), False, False])
            n.disconnect()
            run = False
            game_over_screen(game)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        if keys[pygame.K_ESCAPE]:
            n.send([Buffer(), True, False])
            if confirmation_screen("Are you sure you want to quit?"):
                n.disconnect()
                run = False
            else:
                n.send([Buffer(), False, True])
    menu_screen()

def human_vs_human():
    run = True
    player1 = Player(50, 414, 30, (255, 0, 0), 30, w / 2 - 30, pygame.K_a, pygame.K_d, pygame.K_w)
    player2 = Player(w - 50, 414, 30, (0, 255, 0), w / 2 + 30, w - 30, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP)
    ball = Ball(200, 250, 0, 0, 20)
    game = Game()

    while run:
        clock.tick(75)
        player1.move()
        player2.move()
        ball.move([player1, player2], game, w)
        check_game_state(ball, player1, player2, game, w)
        redraw_game_window(win, bg, player1, player2, ball, game)
        if game.is_game_over():
            run = False
            game_over_screen(game)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            if confirmation_screen("Are you sure you want to quit?"):
                run = False

    menu_screen()


def game_over_screen(game):
    run = True
    clock = pygame.time.Clock()
    if game.left_player_points > game.right_player_points:
        text = TextButton(w / 2, h / 3, "comicsans", 40, game.left_player_name + " has won the game", (0, 0, 0))
    else:
        text = TextButton(w / 2, h / 3, "comicsans", 40, game.right_player_name + " has won the game", (0, 0, 0))
    button = TextButton(w / 2, h / 2.1, "comicsans", 40, "Back to menu", (0, 0, 0))

    while run:
        clock.tick(60)
        button_hover = button.cursor_hover()

        if button_hover:
            button.update("Back to menu", (0, 200, 0))
        else:
            button.update("Back to menu", (0, 0, 0))

        text.draw(win)
        button.draw(win)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_hover:
                    run = False

    menu_screen()

def menu_screen():
    run = True
    clock = pygame.time.Clock()
    bg = pygame.image.load("tlo3.png")
    start_n_game = TextButton(w/2, h/3, "comicsans", 40, "START HUMAN vs HUMAN", (0, 0, 0))
    start_LAN_game = TextButton(w/2, h/2.1, "comicsans", 40, "START LAN GAME", (0, 0, 0))
    start_online_game = TextButton(w / 2, h / 1.6, "comicsans", 40, "START ONLINE GAME", (0, 0, 0))

    while run:
        clock.tick(60)
        start_n_game_hover = start_n_game.cursor_hover()
        start_LAN_game_hover = start_LAN_game.cursor_hover()
        start_online_game_hover = start_online_game.cursor_hover()

        if start_n_game_hover:
            start_n_game.update("START HUMAN vs HUMAN", (0, 200, 0))
        else:
            start_n_game.update("START HUMAN vs HUMAN", (0, 0, 0))

        if start_LAN_game_hover:
            start_LAN_game.update("START LAN GAME", (0, 200, 0))
        else:
            start_LAN_game.update("START LAN GAME", (0, 0, 0))

        if start_online_game_hover:
            start_online_game.update("START ONLINE GAME", (0, 200, 0))
        else:
            start_online_game.update("START ONLINE GAME", (0, 0, 0))

        win.blit(bg, (0, 0))
        start_n_game.draw(win)
        start_LAN_game.draw(win)
        start_online_game.draw(win)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_n_game_hover or start_LAN_game_hover or start_online_game_hover:
                    run = False

    if start_n_game_hover:
        human_vs_human()

    if start_LAN_game_hover:
        server_screen()

    if start_online_game_hover:
        online_game('172.104.130.211')
        #online_game('127.0.0.1')

def server_screen():
    run = True
    clock = pygame.time.Clock()
    host_game = TextButton(w/2, h/3, "comicsans", 40, "HOST GAME", (0, 0, 0))
    join_ex_server = TextButton(w/2, h/2, "comicsans", 40, "JOIN EXISTING SERVER", (0, 0, 0))

    while run:
        clock.tick(60)
        host_game_hover = host_game.cursor_hover()
        join_ex_server_hover = join_ex_server.cursor_hover()

        if host_game_hover:
            host_game.update("HOST GAME", (0, 200, 0))
        else:
            host_game.update("HOST GAME", (0, 0, 0))

        if join_ex_server_hover:
            join_ex_server.update("JOIN EXISTING SERVER", (0, 200, 0))
        else:
            join_ex_server.update("JOIN EXISTING SERVER", (0, 0, 0))

        win.blit(bg, (0, 0))
        host_game.draw(win)
        join_ex_server.draw(win)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if host_game_hover or join_ex_server_hover:
                    run = False

    if host_game_hover:
        start_new_thread(start_server,())
        LAN_game(get_server_address())

    if join_ex_server_hover:
        ip = get_LAN_address_screen()
        if ip == '-1':
            menu_screen()
        else:
            LAN_game(ip)

def confirmation_screen(message):
    run = True
    clock = pygame.time.Clock()
    text = TextPanel(w/2, h/2 - 50, "comicsans", 40, message, (0, 0, 0))
    yes = TextButton(w/2 - 60, h/2, "comicsans", 40, "Yes", (0, 0, 0))
    no = TextButton(w/2 + 50, h/2, "comicsans", 40, "No", (0, 0, 0))

    while run:
        clock.tick(60)
        yes_hover = yes.cursor_hover()
        no_hover = no.cursor_hover()

        if yes_hover:
            yes.update("Yes", (200, 0, 0))
        else:
            yes.update("Yes", (0, 0, 0))

        if no_hover:
            no.update("No", (0, 0, 200))
        else:
            no.update("No", (0, 0, 0))

        text.draw(win)
        yes.draw(win)
        no.draw(win)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if yes_hover or no_hover:
                    run = False


    if yes_hover:
        return True
    else:
        return False


def get_LAN_address_screen():
    run = True
    clock = pygame.time.Clock()
    textinput = TextInput()
    textinput.max_string_length = 15
    text_button = TextButton(w//2, h//2.5, "comicsans", 40, "Enter LAN server ip address", (0, 0, 0))
    connect_button = TextButton(w//2 - 70, h//1.6, "comicsans", 40, "Connect", (0, 0, 0))
    cancel_button = TextButton(w // 2 + 70, h//1.6, "comicsans", 40, "Cancel", (0, 0, 0))

    while run:
        clock.tick(60)
        win.blit(bg, (0, 0))
        pygame.draw.rect(win,(255,255,255), (w//2 - 110, h//2 - 15, 220,31))
        connect_button_hover = connect_button.cursor_hover()
        cancel_button_hover = cancel_button.cursor_hover()

        if connect_button_hover:
            connect_button.update("Connect", (0,255,0))
        else:
            connect_button.update("Connect", (0, 0, 0))

        if cancel_button_hover:
            cancel_button.update("Cancel", (255,0,0))
        else:
            cancel_button.update("Cancel", (0, 0, 0))


        tr = textinput.get_surface().get_rect()
        tr.center = (w // 2, h // 2)
        win.blit(textinput.get_surface(), tr)
        text_button.draw(win)
        connect_button.draw(win)
        cancel_button.draw(win)

        pygame.display.update()


        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if connect_button_hover or cancel_button_hover:
                    run = False

        textinput.update(events)

    if connect_button_hover:
        return textinput.get_text()
    else:
        return '-1'

menu_screen()
#online_game('172.104.130.211')
#online_game('127.0.0.1')