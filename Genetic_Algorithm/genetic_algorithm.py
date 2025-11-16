# Lliberies necesàries
import pygame
import json
import math
import random
import matplotlib.pyplot as plt
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
POPULATION_SIZE = 100
MAX_GENERATIONS = 30
TARGET_FITNESS = len(json.load(open('data.json'))['balls']) 

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
def evaluate_individual(individual, ball_data):
    world = b2World(gravity=(0, 9.81), doSleep=True)
    # Crear el món
    env = Environment(world, WIDTH, HEIGHT, 10, PPM)
    # Crear les pilotes
    balls = [Ball(world, (b['position'][0]/PPM, b['position'][1]/PPM), b['radius']/PPM) for b in ball_data]
    # Crear la cadena de rectangles
    rectangles = create_connected_rectangles(
        world, individual.angles, INITIAL_POS, RECTANGLE_SIZE, PPM)
    # Bucle on simulem la física 
    for _ in range(1000):
        world.Step(TIME_STEP, VEL_ITERS, POS_ITERS)
    # Calcular fitness
    red_zone_top = (HEIGHT - ZONE_RED_HEIGHT) / PPM
    fitness = sum(1 for ball in balls if ball.body.position[1] < red_zone_top)

    return fitness
# Funció per evaluar tota la població
def evaluate_population(population, ball_data):
    for individual in population:
        individual.fitness = evaluate_individual(individual, ball_data)
    # Ordenem la població per fitness
    population.sort(key=lambda x: x.fitness, reverse=True)
# Funció per creuar dos individus
def mate(parent1, parent2):
    crossover_point = random.randint(1, NUM_RECTANGLES - 1)
     # Creem rls dos fills combinant els angles dels pares
    child1_angles = parent1.angles[:crossover_point] + parent2.angles[crossover_point:]
    child2_angles = parent2.angles[:crossover_point] + parent1.angles[crossover_point:]
    return Individual(angles=child1_angles), Individual(angles=child2_angles)
# Funció per mutar un individu 
def mutate(individual, mutation_rate=0.15, mutation_strength=0.3):
    for i in range(len(individual.angles)):
        if random.random() < mutation_rate:
            individual.angles[i] += random.uniform(-mutation_strength, mutation_strength)
            individual.angles[i] = max(-math.pi, min(math.pi, individual.angles[i]))
# Funció principal de l'algorisme genètic
def genetic_algorithm():
    # Crear una població inicial aleatòria
    population = [Individual() for _ in range(POPULATION_SIZE)]
    best_individual = None
    generations = 0
    fitness_history = []
    # Bucle principal de l'algorisme
    while generations < MAX_GENERATIONS:
        generations += 1
        evaluate_population(population, ball_data)
        # Agafar el millor individu d'aquesta generació
        current_best = population[0]
        fitness_history.append(current_best.fitness)
        print(f"Generació {generations} - Millor Fitness: {current_best.fitness:.2f}")
        # Actualitzem el millor
        if best_individual is None or current_best.fitness > best_individual.fitness:
            best_individual = current_best.copy()
            if current_best.fitness == TARGET_FITNESS:
                print("Solució òptima trobada")
                break

        # Fer la selecció utilitzant elitisme + torneig
        elite_size = 5
        selected = population[:elite_size]
        while len(selected) < POPULATION_SIZE:
            # Triem 3 aleatoris i ens quedem amb el millor
            contenders = random.sample(population, 3)
            winner = max(contenders, key=lambda x: x.fitness)
            selected.append(winner.copy())

        # Fem l'encreuament i la mutació
        new_population = []
        for i in range(0, POPULATION_SIZE, 2):
            p1, p2 = random.sample(selected, 2)
            c1, c2 = mate(p1, p2)
            mutate(c1)
            mutate(c2)
            new_population.extend([c1, c2])
        # Es substitueix la població
        population = new_population[:POPULATION_SIZE]

    return best_individual, generations, fitness_history
# Fem la visualització i execució principal
def show_best_individual(best_individual, ball_data):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True

    world = b2World(gravity=(0, 9.81), doSleep=True)
    # Crear el món
    env = Environment(world, WIDTH, HEIGHT, 5, PPM)

    # crear les pilotes
    balls = [Ball(world, (b['position'][0]/PPM, b['position'][1]/PPM), b['radius']/PPM) for b in ball_data]

    # Crear els rectangles amb els angles del millor individu
    rectangles = create_connected_rectangles(
        world, best_individual.angles, INITIAL_POS, RECTANGLE_SIZE, PPM)
    # Guardar el temps inicial per limitar la simulació a 10 segons
    start_time = pygame.time.get_ticks()
    # Bucle principal de visualització
    while running and pygame.time.get_ticks() - start_time < 10000:
        # Gestió d'events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        world.Step(TIME_STEP, VEL_ITERS, POS_ITERS)
        screen.fill((200, 200, 200))
        # Dibuixar la zona vermella
        env.draw_zone_red(screen, ZONE_RED_HEIGHT)
        # Dibuixar les pilotes
        for ball in balls:
            ball.draw(screen, PPM)
        # Dibuixar els rectangles
        for rect in rectangles:
            rect.draw(screen, PPM)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

# Algoritme Genètic
best_individual, total_generations, fitness_history = genetic_algorithm()

print(f"\nAlgorisme finalitzat en {total_generations} generacions.")
print("Fitness final:", best_individual.fitness)

# Dibuixar l'evolució de la funció de fitness
plt.figure(figsize=(10, 5))
plt.plot(fitness_history, color='blue', linewidth=2)
plt.title("Evolució del Fitness", fontsize=14)
plt.xlabel("Generació")
plt.ylabel("Fitness")
plt.grid(True, linestyle='--', alpha=0.7)
plt.ylim(0, max(fitness_history) + 2)
plt.show()

# Només mostrem per pygame, el millor
show_best_individual(best_individual, ball_data)
