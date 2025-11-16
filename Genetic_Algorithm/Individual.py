# Lliberies necesàries
import random
import math

# Definim la classe Individual, que representa un possible individu d'una població evolutiva
class Individual:
    # Constructor de la classe
    def __init__(self, num_genes=20, angles=None):
        self.num_genes = num_genes
        if angles is None:
            # Inicialització aleatòria
            self.angles = [random.uniform(-math.pi, math.pi) for _ in range(self.num_genes)]
        else:
            # Copia d’un altre individu
            self.angles = angles.copy()
        self.fitness = 0.0
    # Mètode per aplicar mutació aleatòria sobre els angles de l'individu
    def mutate(self, mutation_rate=0.2):
        for i in range(self.num_genes):
            # Si toca mutar
            if random.random() < mutation_rate:
                # Asignem un nou angle aleatori
                self.angles[i] = random.uniform(-math.pi, math.pi)
    # Mètode per fer un clon de l'individu
    def copy(self):
        clone = Individual(angles=self.angles)
        clone.fitness = self.fitness 
        return clone
