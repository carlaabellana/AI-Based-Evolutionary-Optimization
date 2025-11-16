# Lliberies necesàries
import pygame
import json
import math
import numpy as np
import matplotlib.pyplot as plt
import cma
from Box2D import b2World
from Individual import Individual
from Objects import Rectangle, Ball, Environment

# Constants i paràmetres que s'han utilitzat durant tot el codi
WIDTH, HEIGHT = 640, 400
FPS = 60
ZONE_RED_HEIGHT = 100
PPM = 20  
TIME_STEP = 1.0 / FPS
VEL_ITERS, POS_ITERS = 8, 3
RECTANGLE_SIZE = (30, 10)  
INITIAL_POS = (20, 100)    
NUM_RECTANGLES = 20
MAX_ITERATIONS = 30
POPULATION_SIZE = 100 

clock = pygame.time.Clock()

# Carreguem les dades de les pilotes del JSON
with open('data.json') as f:
    ball_data = json.load(f)['balls']

# Funció per crear els rectangles concatenats en cadena
def create_connected_rectangles(world, angles, initial_pos, rect_size, ppm):
    rectangles = []
    half_length = rect_size[0] / (2 * ppm)
    half_width = rect_size[1] / (2 * ppm)
    # Bucle per crear el rectangle
    for i, angle in enumerate(angles):
        if i == 0:
            position = (initial_pos[0]/ppm, initial_pos[1]/ppm)
        else:
            # Agafem el rectangle anterior
            last = rectangles[-1].body
             # Calculem el punt final de l'anterior rectangle
            end_x = last.position.x + half_length * math.cos(last.angle)
            end_y = last.position.y + half_length * math.sin(last.angle)
             # Escribim la posició al nou rectangle
            position = (
                end_x + half_length * math.cos(angle),
                end_y + half_length * math.sin(angle)
            )
        # Creem objecte i el posem a la llista
        rect = Rectangle(world, position, angle, half_length, half_width)
        rectangles.append(rect)

    return rectangles
# Funció que evalua un individu
def evaluate_solution(x, ball_data):
    world = b2World(gravity=(0, 9.81), doSleep=True)
    # Crear el món
    env = Environment(world, WIDTH, HEIGHT, 10, PPM)
    # Crear les pilotes
    balls = [Ball(world, (b['position'][0]/PPM, b['position'][1]/PPM), b['radius']/PPM) for b in ball_data]
    # Crear la cadena de rectangles
    rectangles = create_connected_rectangles(world, x, INITIAL_POS, RECTANGLE_SIZE, PPM)
    # Bucle on simulem la física 
    for _ in range(1000):
        world.Step(TIME_STEP, VEL_ITERS, POS_ITERS)

    red_zone_top = (HEIGHT - ZONE_RED_HEIGHT) / PPM
    # Calcular fitness
    fitness = sum(1 for ball in balls if ball.body.position[1] >= red_zone_top)

    return fitness
# Funció que implementa l'algorisme d'optimització CMA-ES per trobar la millor configuració
def cmaes_algorithm():
    # Inicialitzem una solució aleatòria
    initial_solution = np.random.uniform(-np.pi, np.pi, NUM_RECTANGLES)
     # Desviació estàndard
    initial_sigma = 1.0
    # Configuració de CMA-ES
    opts = cma.CMAOptions()
    opts.set("bounds", [-np.pi, np.pi])
    opts.set("popsize", POPULATION_SIZE)
    opts.set("verbose", -1)
    # Creem l'estratègia d'evolució
    es = cma.CMAEvolutionStrategy(initial_solution, initial_sigma, opts)
    # Variable on es guarda el progrés
    fitness_history = []
    # Bucle principal d'optimització
    for iteration in range(MAX_ITERATIONS): 
        # Genera noves solucions
        solutions = es.ask()
        fitness_values = [evaluate_solution(x, ball_data) for x in solutions]
        # Actualitza CMA-ES amb els resultats
        es.tell(solutions, fitness_values)
        # Es registra el millor resultat d'aquesta iteració
        best_fitness = min(fitness_values)
        fitness_history.append(best_fitness)
        print(f"Generació {iteration + 1}: Han caigut {best_fitness} boles")
        if best_fitness == 0:
            print("solució òptima!")
            break
    # Processem el millor resultat
    best_solution = es.result.xbest
    best_individual = Individual(angles=best_solution.tolist())

    return best_individual, len(fitness_history), fitness_history
# Mostrar gràficament la millor solució trobada
def show_best_individual(best_individual, ball_data):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True
    # Configuració del món físic
    world = b2World(gravity=(0, 9.81), doSleep=True)
    env = Environment(world, WIDTH, HEIGHT, 5, PPM)
    # Creem les boles i rectangles
    balls = [Ball(world, (b['position'][0]/PPM, b['position'][1]/PPM), b['radius']/PPM) for b in ball_data]
    rectangles = create_connected_rectangles(world, best_individual.angles, INITIAL_POS, RECTANGLE_SIZE, PPM)
    # Bucle de visualització el qual dura 10 segons
    start_time = pygame.time.get_ticks()
    while running and pygame.time.get_ticks() - start_time < 10000:
         # Gestió d'events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # Simulació física
        world.Step(TIME_STEP, VEL_ITERS, POS_ITERS)

        screen.fill((255, 255, 255))
        env.draw_zone_red(screen, ZONE_RED_HEIGHT)
        # Dibuixem els objectes   
        for ball in balls:
            ball.draw(screen, PPM)

        for rect in rectangles:
            rect.draw(screen, PPM)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

# Executem CMA-ES
best_individual, total_iterations, fitness_history = cmaes_algorithm()
# Mostrem resultats per consola
print(f"\nCMA-ES generació: {total_iterations}")
print(f"Pilotes en la zona vermella: {fitness_history[-1]}")
fitness_final = 15 - fitness_history[-1]
print(f"Millor fitness: {fitness_final}")
# Es mostra un gràfic d'evolució
plt.figure(figsize=(10, 5))
plt.plot(fitness_history, color='red', linewidth=2)
plt.title("Evolució del CMA-ES", fontsize=14)
plt.xlabel("Generació")
plt.ylabel("Pilotes en la zona vermella")
plt.grid(True, linestyle='--', alpha=0.7)
plt.ylim(0, max(fitness_history) + 2)
plt.show()
# Visualització en pygame de la millor solució
show_best_individual(best_individual, ball_data)
