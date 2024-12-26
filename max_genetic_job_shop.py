#генетический алгоритм, находящий максимально долгое возможное решение

import random
import json
import matplotlib.pyplot as plt
from bisect import bisect

with open('JSPLIB-master\instances.json') as f:
    instances = json.load(f)

class Machine:
    def __init__(self) -> None:
        self.time = 0
        self.job_id = None
    def set_active(self, time, job_id):
        self.time = time
        self.job_id = job_id
    def shut_down(self):
        self.job_id = None
    def is_working(self):
        return self.time > 0
        
def equal(a, b):
    for i in range(len(a)):
        if a[i] != b[i]:
            return False
    return True
    
def fitness(chromosome, m, jobs):
    machines = []
    for i in range(m):
        machines.append(Machine())
    jobs_len = [len(job) for job in jobs]
    jobs_done = [0] * len(jobs)
    t = 1
    while not equal(jobs_done, jobs_len):
        # min_machine_time = min([machine.time for machine in machines])
        # if min_machine_time > 1:
        #     for machine in machines:
        #         machine.time -= min_machine_time 
        #     t += min_machine_time
        for machine_id in range(len(machines)):
            for i in range(len(chromosome[machine_id])):
                job_id, op_id = chromosome[machine_id][i]
                if jobs_done[job_id] == op_id and not machines[machine_id].is_working():
                    machines[machine_id].set_active(jobs[job_id][op_id][1], job_id)
                    break
            if machines[machine_id].is_working():
                machines[machine_id].time -= 1
                if machines[machine_id].time == 0:
                    jobs_done[machines[machine_id].job_id] += 1
                    machines[machine_id].shut_down()
        t += 1
    return t

#популяция - массив хромосом, хромосома - массив субхромосом, субхромосома - массив пар (номер работы и номер операции в работе)
def create_population(m, jobs, population_size):
    population = []
    for _ in range(population_size):
        chromosome = [[] for _ in range(m)]
        all_operations = []
        for job_id in range(len(jobs)):
            for op_id in range(len(jobs[job_id])):
                all_operations.append((job_id, op_id))
        random.shuffle(all_operations)

        for i in range(len(all_operations)):
            op = all_operations[i]
            job_id, op_id = op
            
            machine_id = jobs[job_id][op_id][0]
            chromosome[machine_id].append(op)

        population.append(chromosome)

    return population

def LOX(parent_1, parent_2, border_1, border_2): #Linear Order Crossover
    cross_section = parent_1[border_1:border_2]
    child = [(gene if gene not in cross_section else (float('inf'), float('inf'))) for gene in parent_2]
    
    for gene_id in range(border_1):
        if child[gene_id][0] == float('inf'):
            offset = 1
            while child[gene_id + offset][0] == float('inf'):
                offset += 1

            child[gene_id], child[gene_id + offset] = child[gene_id + offset], child[gene_id]

    for gene_id in range(len(parent_1) - border_2):
        if child[-gene_id - 1][0] == float('inf'):
            offset = -1
            while child[-gene_id - 1 + offset][0] == float('inf'):
                offset -= 1

            child[-gene_id - 1], child[-gene_id - 1 + offset] = child[-gene_id - 1 + offset], child[-gene_id - 1]

    for gene_id in range(border_1, border_2):
        child[gene_id] = cross_section[gene_id - border_1]

    return child

def crossover(parent_1, parent_2):
    child_1, child_2 = [], []
    for subchromosome_id in range(len(parent_1)):
        border_1, border_2 = sorted(random.sample(range(len(parent_1[subchromosome_id])), 2))
        child_subchromosome_1 = LOX(parent_1[subchromosome_id], parent_2[subchromosome_id], border_1,  border_2)
        child_subchromosome_2 = LOX(parent_2[subchromosome_id], parent_1[subchromosome_id], border_1, border_2)
        child_1.append(child_subchromosome_1)
        child_2.append(child_subchromosome_2)

    return child_1, child_2

def mutation(chromosome):
    subchromosome_id = random.randint(0, len(chromosome)-1)
    gene_id_1, gene_id_2 = random.sample(range(len(chromosome[subchromosome_id])), 2)
    chromosome[subchromosome_id][gene_id_1], chromosome[subchromosome_id][gene_id_2] = chromosome[subchromosome_id][gene_id_2], chromosome[subchromosome_id][gene_id_1]

    return chromosome

def composed_operator(parent_1, parent_2):
    child_1, child_2 = crossover(parent_1, parent_2)
    if random.randint(1, 1000) < 4:
        child_1 = mutation(child_1)

    if random.randint(1, 1000) < 4:
        child_2 = mutation(child_2)

    return child_1, child_2

def sort_population(population, fitnesses):
    fitness_and_population = [(fitnesses[i], population[i]) for i in range(len(population))]
    fitness_and_population = sorted(fitness_and_population, key=lambda t: t[0])
    max_fit = fitness_and_population[-1][0]
    min_fit = fitness_and_population[0][0]
    sorted_population = []
    weight = []
    sorted_fitnesses = []
    for i in range(len(population)):
        sorted_population.append(fitness_and_population[i][1])
        weight.append(fitness_and_population[i][0])
        sorted_fitnesses.append(fitness_and_population[i][0])

    if max_fit == min_fit:
        weight = [1 for i in range(len(population))]
        
    return sorted_population, weight, min_fit, sorted_fitnesses, max_fit

def main(m, jobs, generations_amount, population_size, optimum): #m - число машин, jobs - массив работ, работа - массив операций, операция - пара чисел (номер машины и время выполнения)
    population = create_population(m, jobs, population_size)
    fitnesses = [fitness(t, m, jobs) for t in population]
    population, weight, min_fit, fitnesses, max_fit = sort_population(population, fitnesses)


    for _ in range(generations_amount):
        children = []

        for i in range(5):
            a, b = random.choices(population, weights = weight, k = 2)
            child_1, child_2 = composed_operator(a, b)
            children.append(child_1)
            children.append(child_2)
        
        for child in children:
            child_fit = fitness(child, m, jobs)
            ins_place = bisect(fitnesses, child_fit)
            fitnesses.insert(ins_place, child_fit)
            population.insert(ins_place, child)

        population = population[10:]
        fitnesses = fitnesses[10:]
        min_fit = fitnesses[0]
        max_fit = fitnesses[-1]
        if min_fit != max_fit:
            for i in range(population_size):
                weight[i] = fitnesses[i]

    return max_fit


def take_instance(instance_name):
    for x in instances:
        if x['name'] == instance_name:
            instance = x

    optimum = instance['optimum']
    m = instance['machines']

    with open('C:/Code/JobShopProblem/JSPLIB-master/' + instance['path']) as f:
        data = list(f)[5:]
    
    arr = []
    for line in data:
        arr.append(list(map(int, line.split())))
    
    jobs = []
    for x in arr:
        jobs.append([])
        for i in range(0, len(x), 2):
            jobs[-1].append((x[i], x[i+1]))

    return m, jobs, optimum

m, jobs, optimum = take_instance('orb09')    


print(main(m, jobs, 1000, 50, optimum))