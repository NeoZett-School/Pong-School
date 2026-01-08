from turtle import Turtle, Screen
from Frames import clock
from enum import Enum, auto
import random
import time

class GameState(Enum):
    PLAYING = auto()
    PAUSED = auto()

# Screen
WIDTH, HEIGHT = 800, 600
screen = Screen()
screen.setup(WIDTH, HEIGHT)
screen.bgcolor(0.0, 0.15, 0.3)
screen.colormode()
screen.tracer(0)
active = True

# Objects
class Ball(Turtle):
    def __init__(self, speed=1.0):
        super().__init__("square")
        self.shapesize(2, 2)
        self.color(1.0, 1.0, 1.0)
        self.penup()
        self.vx = speed
        self.vy = speed
    def collides(self, sides):
        x_cor, y_cor = self.xcor(), self.ycor()
        def check(side):
            match side.lower().strip():
                case "top":
                    return y_cor >= TOP_SIDE - PLAYER_OFFSET
                case "bottom":
                    return y_cor <= BOTTOM_SIDE + PLAYER_OFFSET // 2
                case "left":
                    return x_cor <= LEFT_SIDE + PLAYER_OFFSET // 2
                case "right":
                    return x_cor >= RIGHT_SIDE - PLAYER_OFFSET // 2
            return False
        if isinstance(sides, str):
            return check(sides)
        for side in sides:
            if check(side):
                return True
        return False
    def update(self):
        x_cor, y_cor = self.xcor(), self.ycor()
        if self.collides(["top", "bottom"]):
            self.vy *= -1
        self.goto(
            x_cor+self.vx,
            y_cor+self.vy
        )

class Player(Turtle):
    def __init__(self):
        super().__init__("square")
        self.shapesize(3, 0.5)
        self.speed(10)
        self.penup()
        self.score = 0

        self._prev_delta = 0
    def draw_score(self, func):
        func(self.score)
    def update_ai(self):
        global AI_target

        # Ball moving away → idle behavior
        if ball.vx <= 0:

            # Spring force toward center
            stiffness = 0.05
            delta = stiffness * (0 - AI_y)

            # Smooth noise (not frame-random jitter)
            noise_strength = 0.4
            noise = random.uniform(-1, 1) * noise_strength
            delta += noise

            # Clamp to max paddle speed
            delta = max(-AI_SPEED, min(AI_SPEED, delta))

            self.sety(AI_y + delta)
            return delta

        # Time until ball reaches AI paddle
        time_to_reach = (AI_x - ball_x) / ball.vx

        predicted_y = ball_y + ball.vy * time_to_reach

        # Reflect off top/bottom walls
        while predicted_y > TOP_SIDE or predicted_y < BOTTOM_SIDE:
            if predicted_y > TOP_SIDE:
                predicted_y = 2 * TOP_SIDE - predicted_y
            elif predicted_y < BOTTOM_SIDE:
                predicted_y = 2 * BOTTOM_SIDE - predicted_y

        # Update target every N frames (reaction delay)
        if frame_count % 10 == 0:
            AI_target = predicted_y + random.uniform(-30, 30)

        # Move toward target with speed limit
        delta = AI_target - AI_y
        delta = max(-AI_SPEED, min(AI_SPEED, delta))
        self.sety(AI_y + delta)
        return delta

class Score(Turtle):
    def __init__(self):
        super().__init__()
        self.hideturtle()
        self.color(0.0, 1.0, 0.0)
        self.penup()
    def draw_player_score(self, score):
        self.goto(LEFT_SIDE//2, 0)
        self.pendown()
        self.write(score, align="center", font=SCORE_FONT)
        self.penup()
    def draw_AI_score(self, score):
        self.goto(RIGHT_SIDE//2, 0)
        self.pendown()
        self.write(score, align="center", font=SCORE_FONT)
        self.penup()

class Text(Turtle):
    def __init__(self):
        super().__init__()
        self.hideturtle()
        self.color(1.0, 1.0, 1.0)
        self.penup()
    def draw_title(self):
        self.goto(0, 200)
        self.pendown()
        self.write("PONG", align="center", font=TITLE_FONT)
        self.penup()
    def draw_info(self):
        self.goto(0, 170)
        self.pendown()
        self.write("<arrow up> to go up", align="center", font=TEXT_FONT)
        self.penup()
        self.goto(0, 190)
        self.pendown()
        self.write("<arrow down> to go down", align="center", font=TEXT_FONT)
        self.penup()
    def draw_hits(self):
        self.goto(0, 280)
        self.pendown()
        self.write(f"{hits} Hits", align="center", font=SMALL_FONT)
        self.penup()
    def draw_game_info(self):
        self.goto(0, 260)
        self.pendown()
        hours = int(play_time // 3600)
        minutes = int((play_time % 3600) // 60)
        seconds = int(play_time % 60)
        self.write(f"{hours:02}:{minutes:02}:{seconds:02}",
           align="center",
           font=SMALL_FONT)
        self.penup()
    def draw_constant_text(self):
        self.goto(0, -280)
        self.pendown()
        self.write("Press space to toggle pause menu", align="center", font=SMALL_FONT)
        self.penup()

# Constants
TOP_SIDE = (HEIGHT // 2)
BOTTOM_SIDE = -(HEIGHT // 2)
RIGHT_SIDE = (WIDTH // 2)
LEFT_SIDE = -(WIDTH // 2)
PLAYER_SPEED = 4.0
AI_SPEED = 4.0
BALL_SPEED = 5.0
WALL_OFFSET = 10
PLAYER_OFFSET = 40
ALLOWED_ERROR = 47
TITLE_FONT = ("Courier", 60, "normal")
SCORE_FONT = ("Courier", 80, "normal")
TEXT_FONT = ("Courier", 20, "normal")
SMALL_FONT = ("Courier", 10, "normal")

clock.target_fps(60)

# Adjust the FPS stab and target fps to adjust frame stability and game speed

# Turtles
ball = Ball(BALL_SPEED)
player = Player()
player.color(0, 0, 1.0)
player.setpos(LEFT_SIDE+13+WALL_OFFSET, 0)
AIn = Player()
AIn.color(1.0, 0, 0)
AIn.setpos(RIGHT_SIDE-19-WALL_OFFSET, 0)
score = Score()
player.draw_score(score.draw_player_score)
AIn.draw_score(score.draw_AI_score)
text = Text()
text.draw_title()
text.draw_info()
text.draw_constant_text()

start_time = time.monotonic()
play_time = 0
pause_time = 0

additional_speed = 0
hits = 0
frame_count = 0
AI_target = 0
state = GameState.PAUSED

#AIn.setpos(ball.ycor())
screen.listen()
keys_down = {"up": False, "down": False}
def keydown(key): keys_down[key] = True
def keyup(key): keys_down[key] = False
screen.onkeypress(lambda: keydown("up"), "Up")
screen.onkeypress(lambda: keydown("down"), "Down")
screen.onkeyrelease(lambda: keyup("up"), "Up")
screen.onkeyrelease(lambda: keyup("down"), "Down")

def pause():
    global state
    text.draw_title()
    text.draw_info()
    state = GameState.PAUSED

def resume():
    global state
    text.clear()
    text.draw_constant_text()
    state = GameState.PLAYING

def toggle_pause():
    if state == GameState.PLAYING:
        pause()
    else:
        resume()

def restart():
    screen.reset()
    ball.__init__()
    player.__init__()
    player.color(0, 0, 1.0)
    player.setpos(LEFT_SIDE+13+WALL_OFFSET, 0)
    AIn.__init__()
    AIn.color(1.0, 0, 0)
    AIn.setpos(RIGHT_SIDE-19-WALL_OFFSET, 0)
    score.__init__()
    player.draw_score(score.draw_player_score)
    AIn.draw_score(score.draw_AI_score)
    text.__init__()
    text.draw_title()
    text.draw_info()
    text.draw_constant_text()

screen.onkeypress(toggle_pause, "space")
screen.onkeypress(restart, "r")

while active:
    match state:
        case GameState.PLAYING:
            if clock.try_frame():
                player_vy = PLAYER_SPEED * (keys_down["up"] - keys_down["down"])
                ball_x, ball_y, player_y, AI_x, AI_y = ball.xcor(), ball.ycor(), player.ycor(), AIn.xcor(), AIn.ycor()
                player.sety(player_y + player_vy)

                AI_vy = AIn.update_ai()

                # Collision
                if abs(ball_y - player_y) <= ALLOWED_ERROR and ball_x < LEFT_SIDE + 13 + WALL_OFFSET + PLAYER_OFFSET // 2:
                    ball.vx = BALL_SPEED + additional_speed
                    allowed_speed = BALL_SPEED * 1.25
                    ball.vy = max(min(ball.vy + player_vy / 10, allowed_speed), -allowed_speed)
                    additional_speed += 0.15
                    hits += 1
                    text.clear()
                    text.draw_constant_text()
                    text.draw_game_info()
                    text.draw_hits()
                elif ball.collides("right"):
                    ball.goto(0, 0)
                    player.score += 1
                    score.clear()
                    player.draw_score(score.draw_player_score)
                    AIn.draw_score(score.draw_AI_score)
                    additional_speed = 0
                if abs(ball_y - AI_y) <= ALLOWED_ERROR and ball_x > RIGHT_SIDE - 19 - WALL_OFFSET - PLAYER_OFFSET // 2:
                    ball.vx = -BALL_SPEED - additional_speed
                    allowed_speed = BALL_SPEED * 1.25
                    ball.vy = max(min(ball.vy + AI_vy / 10, allowed_speed), -allowed_speed)
                    additional_speed += 0.15
                    hits += 1
                    text.clear()
                    text.draw_constant_text()
                    text.draw_game_info()
                    text.draw_hits()
                elif ball.collides("left"):
                    ball.goto(0, 0)
                    AIn.score += 1
                    score.clear()
                    player.draw_score(score.draw_player_score)
                    AIn.draw_score(score.draw_AI_score)
                    additional_speed = 0
                ball.update()
                screen.update()

                if frame_count % 60 * 5 == 0:
                    now = time.monotonic()
                    play_time = now - start_time - pause_time
                    text.clear()
                    text.draw_constant_text()
                    text.draw_game_info()
                    text.draw_hits()

                frame_count += 1
        case GameState.PAUSED:
            now = time.monotonic()
            pause_time = now - start_time - play_time
            screen.update()