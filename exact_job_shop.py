#Точный алгоритм при двух машинах (m == 2). Реализован алгоритм Джексона

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

def Johnson_Algorithm(jobs):    
    schedule_first = []
    schedule_last = []
    while jobs:
        min_job = min(jobs, key=min)
        if min_job[0] > min_job[1]:
            schedule_last.append(min_job)
        else:
            schedule_first.append(min_job)
        jobs.remove(min_job)
    return schedule_first + schedule_last[::-1]

def create_schedule(jobs): #массив работ в формате (длительность операции для 1 машины, длительность операции для 2 машины)
    schedule = [[], []]
    for i in range(len(jobs)):
        schedule[0].append((i, 0))
        schedule[1].append((i, 1))
        jobs[i][0] = (0, jobs[i][0])
        jobs[i][1] = (1, jobs[i][1])
    return schedule, jobs

def Jackson_Algorithm(jobs):
    FirstMachineStart = []
    SecondMachineStart = []
    for job in jobs:    
        if job[0][0] == 0:
            FirstMachineStart.append([job[0][1], job[1][1]])
        else:
            SecondMachineStart.append([job[1][1], job[0][1]])

    FirstJobsSchedule = Johnson_Algorithm(FirstMachineStart)
    print(FirstJobsSchedule)
    SecondJobSchedule = Johnson_Algorithm(SecondMachineStart)
    print(SecondJobSchedule)
    FirstJobsSchedule, SecondJobSchedule = FirstJobsSchedule + SecondJobSchedule, SecondJobSchedule + FirstJobsSchedule
    JobsSchedule = [[] for i in range(len(FirstJobsSchedule))]

    for i in range(len(FirstJobsSchedule)):
        JobsSchedule[i].append(FirstJobsSchedule[i][0])
        JobsSchedule[i].append(SecondJobSchedule[i][1])

    return JobsSchedule

jobs = [[(0, 12), (1, 10)], [(1, 5), (0, 11)], [(0, 7), (1, 6)]]
jobs = Jackson_Algorithm(jobs)
schedule, jobs = create_schedule(jobs)
print(fitness(schedule, 2, jobs))