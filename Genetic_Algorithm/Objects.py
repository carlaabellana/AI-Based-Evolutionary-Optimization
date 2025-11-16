# Lliberies necesàries
import pygame
from Box2D import b2PolygonShape, b2CircleShape

# Classe que representa un rectangle estàtic
class Rectangle:
    # Constructor del rectangle
    def __init__(self, world, position, angle, half_length, half_width):
        self.body = world.CreateStaticBody(position=position, angle=angle)
        self.fixture = self.body.CreateFixture(
            shape=b2PolygonShape(box=(half_length, half_width)),
            density=1,
            friction=0.3
        )
    # Mètode per dibuixar el rectangle a la pantalla
    def draw(self, screen, ppm):
        for fixture in self.body.fixtures:
            shape = fixture.shape
            vertices = [(self.body.transform * v) * ppm for v in shape.vertices]
            pygame.draw.polygon(screen, (0, 255, 0), [(int(v.x), int(v.y)) for v in vertices])
    # Mètode per eliminar el cos del món de Box2D
    def destroy(self, world):
        world.DestroyBody(self.body)

# Classe que representa una pilota
class Ball:
    # Constructor de la pilota
    def __init__(self, world, position, radius):
        self.body = world.CreateDynamicBody(position=position)
        self.fixture = self.body.CreateFixture(
            shape=b2CircleShape(radius=radius),
            density=1,
            friction=0.1,
            restitution=0.25
        )
    # Mètode per dibuixar la pilota a la pantalla
    def draw(self, screen, ppm):
        pos = self.body.position * ppm
        radius = int(self.fixture.shape.radius * ppm)
        pygame.draw.circle(screen, (0, 0, 255), (int(pos.x), int(pos.y)), radius)
        pygame.draw.circle(screen, (0, 0, 0), (int(pos.x), int(pos.y)), radius, 2)  
    def destroy(self, world):
        world.DestroyBody(self.body)

# Classe que representa les parets laterals i la zona vermella
class Environment:
    # Constructor
    def __init__(self, world, width, height, wall_thickness, ppm):
        self.width = width
        self.height = height
        self.ppm = ppm
        self.wall_thickness = wall_thickness
        self.walls = []
        # Calcular la posició vertical del centre de les parets
        half_height = height / (2 * ppm)
        # Crear la paret esquerra com a cos estàtic
        self.left_wall = world.CreateStaticBody(
            position=(0, half_height),
            shapes=b2PolygonShape(box=(wall_thickness / ppm, half_height))
        )
        # Crear la paret dreta
        self.right_wall = world.CreateStaticBody(
            position=(width / ppm, half_height),
            shapes=b2PolygonShape(box=(wall_thickness / ppm, half_height))
        )
        self.walls.extend([self.left_wall, self.right_wall])
    # Mètode per dibuixar la zona vermella a la part inferior de la pantalla
    def draw_zone_red(self, screen, zone_red_height):
        pygame.draw.rect(screen, (255, 0, 0), (0, self.height - zone_red_height, self.width, zone_red_height))
    # Mètode per destruir totes les parets del món
    def destroy(self, world):
        for wall in self.walls:
            world.DestroyBody(wall)