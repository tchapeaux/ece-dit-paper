from Model import algorithms
from Model import Task, TaskGenerator
from Simulator import Simulator
from Simulator import Scheduler, ChooseKeepEDF, PALLF, LBLScheduler
import systems

import random
import pylab


domin_scores = {}
results = {}
NUMBER_OF_SYSTEMS = 1000
uRange = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
schedulers = [Scheduler.EDF, Scheduler.PTEDF]
names = ["EDF", "PA-EDF"]

failures = []


def oneTest(utilization):
    global failureCnt
    domin_scores[utilization] = {}
    results[utilization] = {}
    for sched in schedulers:
        results[utilization][sched] = []
        domin_scores[utilization][sched] = 0

    for i in range(NUMBER_OF_SYSTEMS):
        print("u = ", utilization, ", i = ", i, "/", NUMBER_OF_SYSTEMS)
        Umin = 0.55
        Umax = 0.95
        # Utot = 1.0*random.randint(int(Umin*100), int(Umax*100))/100
        Utot = utilization
        maxHyperT = 360  # PPCM(2, 3, 5, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 22, 24, 25, 28, 30, 32)
        # maxHyperT = -1
        Tmin = 3
        Tmax = 50
        n = random.randint(2, 5)
        preemptionCost = 2
        constrDeadlineFactor = 0  # 0 is implicit, 1 is constrained
        tasks = TaskGenerator.generateTasks(Utot, n, maxHyperT, Tmin, Tmax, preemptionCost=preemptionCost, synchronous=False, constrDeadlineFactor=constrDeadlineFactor)
        tau = Task.TaskSystem(tasks)
        # print(tau)

        Omax = max([task.O for task in tau.tasks])
        H = tau.hyperPeriod()
        fpdit = algorithms.findFirstDIT(tau)
        stop = Omax + 10 * H  # FIXME
        if fpdit:
            stop = fpdit + H

        for schedClass in schedulers:
            if schedClass is Scheduler.ExhaustiveFixedPriority:
                sched = schedClass(tau, 1, False)
            else:
                sched = schedClass(tau)
            simu = Simulator.Simulator(tau, stop=stop, nbrCPUs=1, scheduler=sched, abortAndRestart=False, drawing=False)
            simu.run(stopAtDeadlineMiss=True, stopAtStableConfig=True)
            results[utilization][schedClass].append(simu.success())

        if results[utilization][schedulers[0]][-1] and not results[utilization][schedulers[1]][-1]:
            failures.append(tau)

    # compute score
    for i in range(NUMBER_OF_SYSTEMS):
        for sched in schedulers:
            if results[utilization][sched][i]:
                undefeated = True
                for otherSched in schedulers:
                    if otherSched is not sched and results[utilization][otherSched][i]:
                        undefeated = False
                        break
                if undefeated:
                    domin_scores[utilization][sched] += 1


    # for i, sched in enumerate(schedulers):
    #     print("Feasable under sched", i, ":", len([r for r in results[utilization][sched] if r is True]))
    #     print("Scheduler", i, "score:", domin_scores[utilization][sched], "(", 100 * domin_scores[utilization][sched]/NUMBER_OF_SYSTEMS, "%)")

for u in uRange:
    oneTest(u)

pylab.figure()
for i, sched in enumerate(schedulers):
    dom_pct = [100 * domin_scores[u][sched] / NUMBER_OF_SYSTEMS for u in uRange]
    result = [len([r for r in results[u][sched] if r is True]) for u in uRange]
    result_pct = list(map(lambda r: 100 * r / NUMBER_OF_SYSTEMS, result))
    print("result_pct of ", names[i], result_pct)
    pylab.plot(uRange, result_pct, "--o", label=names[i])

pylab.ylabel("% schedulable")
pylab.xlabel("System utilization")
pylab.title("Schedulability of implicit systems (n = " + str(NUMBER_OF_SYSTEMS) + ")")
pylab.legend(loc=0)
pylab.axis([uRange[0] - 0.1, uRange[-1] + 0.1, 0,  100])
pylab.grid()
pylab.show()

for fail in failures:
    print("FAIL", str(fail))