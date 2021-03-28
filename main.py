import pygame
import os
import random
import neat
import math
GEN = 0
MAX_SCORE = 0
pygame.init()
pygame.font.init()
DINO_RUNNING = [pygame.image.load(os.path.join('Assets/Dino','DinoRun1.png')), pygame.image.load(os.path.join('Assets/Dino','DinoRun2.png'))]
DINO_DUCKING = [pygame.image.load(os.path.join('Assets/Dino','DinoDuck1.png')), pygame.image.load(os.path.join('Assets/Dino','DinoDuck2.png'))]
DINO_JUMP = pygame.image.load(os.path.join('Assets/Dino','DinoJump.png'))
DINO_START = pygame.image.load(os.path.join('Assets/Dino','DinoStart.png'))
BG_IMG = pygame.image.load(os.path.join('Assets/Other','Track.png'))
SMALL_CACTUSES = [pygame.image.load(os.path.join('Assets/Cactus','SmallCactus1.png')),
                  pygame.image.load(os.path.join('Assets/Cactus','SmallCactus2.png')), pygame.image.load(os.path.join('Assets/Cactus','SmallCactus3.png'))]
LARGE_CACTUSES = [pygame.image.load(os.path.join('Assets/Cactus','LargeCactus1.png')),
                  pygame.image.load(os.path.join('Assets/Cactus','LargeCactus2.png')), pygame.image.load(os.path.join('Assets/Cactus','LargeCactus3.png'))]
BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]
STAT_FONT = pygame.font.SysFont('comicsans', 50)

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100


def dist(f_x, f_y, s_x,s_y):
    return math.sqrt((f_x-s_x)**2+(f_y-s_y)**2)


class Dino:
    RUN_IMGS = DINO_RUNNING
    DUCK_IMGS = DINO_DUCKING
    JUMP_IMG = DINO_JUMP
    START_IMG = DINO_START
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 13

    def __init__(self):
        self.img = self.RUN_IMGS[0]
        self.dino_rect = self.img.get_rect()
        self.vel = 0
        self.tick_count = 0
        self.x = self.X_POS
        self.y = self.Y_POS
        self.run_img = 0

    def run(self):
        self.img = self.RUN_IMGS[self.run_img // 5]
        self.run_img+=1;
        if self.run_img==10:
            self.run_img=0
        self.img = self.RUN_IMGS[self.run_img // 5]
        d = 2.9* self.vel * self.tick_count - 1.2 * self.tick_count ** 2
        if d > 18:
            d = 18
        if d < -18:
            d = -18
        self.y = self.y - d
        self.tick_count += 1
        if self.vel != 0:
            if self.y < self.Y_POS:
                self.img =self.JUMP_IMG
            self.vel -= 1


        self.x = self.X_POS
        if self.y > self.Y_POS:
            self.y = self.Y_POS

    def duck(self):
        self.img = self.DUCK_IMGS[self.run_img // 5]
        self.x = self.X_POS
        self.y = self.Y_POS_DUCK

    def jump(self):
        self.tick_count = 0
        self.vel = self.JUMP_VEL

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

    def draw(self, WIN):
        WIN.blit(self.img, (self.x, self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Obstacle:
    def __init__(self, image, type):
        self.image = image[self.type]
        self.type = type
        self.y= self.image.get_height()
        self.x = SCREEN_WIDTH + random.randint(1, 200)
        self.height = self.y + self.image.get_height()
        self.passed = False

    def move(self, game_speed):
        self.x -= game_speed

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))

    def collide(self, dino):
        dino_mask = dino.get_mask()
        cactus_mask = pygame.mask.from_surface(self.image)
        offset = (self.x - dino.x,  self.y- round(dino.y))
        do_collide = dino_mask.overlap(cactus_mask, offset)
        if do_collide:
            return True
        else:
            return False


class SmallCactus(Obstacle):
        def __init__(self, image):
            self.type = random.randint(0, 2)
            super().__init__(image, self.type)
            self.y = 325
            self.height = self.y + self.image.get_height()


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.y = 300
        self.height = self.y + self.image.get_height()


class Bird(Obstacle):
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.imgs = image
        self.y = 252
        self.index = 0

    def draw(self, WIN):
        if self.index >= 9:
            self.index = 0
        self.image = self.imgs[self.index // 5]
        WIN.blit(self.image, (self.x,self.y))
        self.index += 1


class Base:
    WIDTH = BG_IMG.get_width()
    IMG = BG_IMG

    def __init__(self, VEL):
        self.y = 380
        self.x1 = 0
        self.x2 = self.WIDTH
        self.VEL =VEL

    def move(self,VEL):
        self.VEL =VEL
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, WIN):
        WIN.blit(self.IMG, (self.x1, self.y))
        WIN.blit(self.IMG, (self.x2, self.y))


def draw(WIN, dinosaurs, base, obstacles, score,gen, max ):
    text = STAT_FONT.render("Score = " + str(score), 1, (0, 0, 0))
    text1 = STAT_FONT.render("Gen = " + str(gen), 1, (0, 0, 0))
    text2 = STAT_FONT.render("Max Score = " + str(max), 1, (0, 0, 0))
    WIN.fill((255,255,255))
    for obstacle in obstacles:
        obstacle.draw(WIN)
    base.draw(WIN)
    for dino in dinosaurs:
        dino.draw(WIN)
    WIN.blit(text, (SCREEN_WIDTH - 10 - text.get_width(), 10))
    WIN.blit(text1, (10, 10))
    WIN.blit(text2, (SCREEN_WIDTH/2 - text.get_width(), 10))
    pygame.display.update()


def main(gnomes, config):
    global GEN
    global MAX_SCORE
    GEN += 1
    base = Base(20)
    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    run = True
    speed_counter = 1
    clock = pygame.time.Clock()
    obstacles = []
    nets = []
    ge = []
    dinosaurs = []
    score = 0
    for _, genome in gnomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        dinosaurs.append(Dino())
        genome.fitness = 0
        ge.append(genome)

    VEL = 20
    score = 0
    add_obstacle = False
    if random.randint(0, 1) == 0:
	    obstacles.append(LargeCactus(LARGE_CACTUSES))
    else:
	    obstacles.append(Bird(BIRD))

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        if speed_counter % 45 == 0:
            speed_counter = 0
            if VEL < 58:
                VEL += 1

            score += 1
        obstacle_index = 0
        speed_counter+=1

        if len(dinosaurs) > 0:
            if len(dinosaurs) > 0 and dinosaurs[0].x > dinosaurs[0].x + dinosaurs[0].img.get_width():
                obstacle_index = 1
        else:
            run = False
            break
        for x, dino in enumerate(dinosaurs):
            dino.run()
            ge[x].fitness += 0.3
            if dino.y == dino.Y_POS:
                output = nets[x].activate((dist(dino.x, dino.y,  obstacles[obstacle_index].x,
                                                obstacles[obstacle_index].y + obstacles[obstacle_index].image.get_height()),
                VEL, abs(obstacles[obstacle_index].y - dino.y)))
                i = output.index(max(output))
                if i ==0:
                    dino.run()
                elif i ==1:
                    dino.jump()
                else:
                    dino.duck()

        add_obstacle = False
        rem = []

        for obstacle in obstacles:
            obstacle.move(VEL)
            for x, dino in enumerate(dinosaurs):
                if obstacle.collide(dino):
                    ge[x].fitness -= 0.3
                    dinosaurs.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not obstacle.passed and obstacle.x < dino.x:
                    obstacle.passed = True
                    add_obstacle = True

            if obstacle.x + obstacle.image.get_width() < 0:
                rem.append(obstacle)

        if add_obstacle:
            for g in ge:
                g.fitness +=3

            if random.randint(0, 2) == 0:
                obstacles.append(SmallCactus(SMALL_CACTUSES))
            elif random.randint(0, 2) == 1:
                obstacles.append(LargeCactus(LARGE_CACTUSES))
            else:
                obstacles.append(Bird(BIRD))

        for r in rem:
            obstacles.remove(r)

        base.move(VEL)

        if MAX_SCORE < score:
            MAX_SCORE = score

        draw(window, dinosaurs, base, obstacles, score, GEN, MAX_SCORE)


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 500)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    configPath = os.path.join(local_dir, 'config-feedforward.txt')
    run(configPath)
