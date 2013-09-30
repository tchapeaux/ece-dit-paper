from Simulator import Simulator
from Simulator.Scheduler import Scheduler, ChooseKeepEDF, PALLF
from Helper import systems

import unittest


class TestSimulator(unittest.TestCase):
    def setUp(self):
        pass

    def checkResult(self, tau, sched, expectedResult):
        Omax = max([task.O for task in tau.tasks])
        H = tau.hyperPeriod()
        # fpdit = algorithms.findFirstDIT(tau)
        stop = Omax + 10 * H

        simulator = Simulator.Simulator(tau, stop, nbrCPUs=1, scheduler=sched, abortAndRestart=False, verbose=False, drawing=False)
        simulator.run()
        self.assertIs(simulator.success(), expectedResult)

    def test_UnfeasibleLongTransitive(self):
        tau = systems.UnfeasibleLongTransitive
        # This system is unfeasible but does not miss any deadline before Omax + 2H
        self.assertGreater(tau.systemUtilization(), 1)
        self.checkResult(tau, Scheduler.EDF(tau), False)
        self.checkResult(tau, Scheduler.SpotlightEDF(tau), False)
        self.checkResult(tau, PALLF.PALLF(tau), False)

    def test_LongTransitive(self):
        tau = systems.LongTransitive
        self.checkResult(tau, Scheduler.EDF(tau), False)
        self.checkResult(tau, Scheduler.SpotlightEDF(tau), False)
        self.checkResult(tau, PALLF.PALLF(tau), True)
        self.checkResult(tau, Scheduler.ExhaustiveFixedPriority(tau, nbrCPUs=1, abortAndRestart=False), True)
        tau = systems.LongTransitive2
        self.checkResult(tau, Scheduler.EDF(tau), True)
        self.checkResult(tau, Scheduler.SpotlightEDF(tau), True)
        self.checkResult(tau, PALLF.PALLF(tau), True)
        self.checkResult(tau, Scheduler.ExhaustiveFixedPriority(tau, nbrCPUs=1, abortAndRestart=False), False)

    def test_AtomicPreemptionCost(self):
        tau = systems.AtomicPreemptionCost
        self.checkResult(tau, Scheduler.EDF(tau), True)
        self.checkResult(tau, Scheduler.SpotlightEDF(tau), True)
        self.checkResult(tau, PALLF.PALLF(tau), True)
        self.checkResult(tau, Scheduler.PTEDF(tau), True)

        sim = Simulator.Simulator(tau, stop=5, nbrCPUs=1, scheduler=Scheduler.EDF(tau), abortAndRestart=False, drawing=False)
        sim.run()
        self.assertEquals(sim.t, 6)
        blockedJob = sim.mostPrioritaryJob()
        self.assertIsNotNone(blockedJob)
        self.assertEquals(blockedJob.computation, 0)

    def test_Meumeu(self):
        tau = systems.Meumeu
        self.checkResult(tau, Scheduler.EDF(tau), True)
        self.checkResult(tau, Scheduler.SpotlightEDF(tau), True)
        self.checkResult(tau, PALLF.PALLF(tau), True)
        self.checkResult(tau, Scheduler.ExhaustiveFixedPriority(tau, nbrCPUs=1, abortAndRestart=False), True)
        self.checkResult(tau, Scheduler.PTEDF(tau), True)

    def test_EDFNonOptimal(self):
        tau = systems.EDFNonOptimal
        self.checkResult(tau, Scheduler.EDF(tau), False)
        self.checkResult(tau, Scheduler.SpotlightEDF(tau), True)
        self.checkResult(tau, ChooseKeepEDF.ChooseKeepEDF(tau), True)
        self.checkResult(tau, PALLF.PALLF(tau), True)
        self.checkResult(tau, Scheduler.PTEDF(tau), True)

    def test_SpotlightEDFNonOptimal(self):
        tau = systems.SpotlightEDFNonOptimal
        self.checkResult(tau, Scheduler.SpotlightEDF(tau), False)
        self.checkResult(tau, ChooseKeepEDF.ChooseKeepEDF(tau), True)
        self.checkResult(tau, PALLF.PALLF(tau), True)

    def test_PreemptNoIdle(self):
        # difficult case where idling seems preferable but leads to unfeasibility
        tau = systems.PreemptNoIdle
        self.checkResult(tau, ChooseKeepEDF.ChooseKeepEDF(tau), True)
        self.checkResult(tau, PALLF.PALLF(tau), True)

    def test_MustIdle(self):
        # unfeasible by non-idling algorithms
        tau = systems.MustIdle
        self.checkResult(tau, Scheduler.EDF(tau), False)
        self.checkResult(tau, Scheduler.SpotlightEDF(tau), False)
        self.checkResult(tau, ChooseKeepEDF.ChooseKeepEDF(tau), True)
        self.checkResult(tau, PALLF.PALLF(tau), True)
        self.checkResult(tau, Scheduler.PTEDF(tau), True)

    def test_DPOnly(self):
        tau = systems.DPOnly
        tau = systems.MustIdle
        self.checkResult(tau, Scheduler.EDF(tau), False)
        self.checkResult(tau, Scheduler.SpotlightEDF(tau), False)
        self.checkResult(tau, ChooseKeepEDF.ChooseKeepEDF(tau), True)
        self.checkResult(tau, PALLF.PALLF(tau), True)

    def test_KeepForLater(self):
        tau = systems.KeepForLater
        self.checkResult(tau, Scheduler.EDF(tau), False)
        self.checkResult(tau, Scheduler.SpotlightEDF(tau), False)
        self.checkResult(tau, ChooseKeepEDF.ChooseKeepEDF(tau), False)
        self.checkResult(tau, PALLF.PALLF(tau), False)

    def test_SamePriorityTrap(self):
        tau = systems.SamePriorityTrap
        self.checkResult(tau, ChooseKeepEDF.ChooseKeepEDF(tau), True)
        self.checkResult(tau, PALLF.PALLF(tau), True)

    def test_SamePriorityTrap2(self):
        tau2 = systems.SamePriorityTrap2
        self.checkResult(tau2, ChooseKeepEDF.ChooseKeepEDF(tau2), True)
        self.checkResult(tau2, PALLF.PALLF(tau2), True)

    def test_SamePriorityTrap3(self):
        tau3 = systems.SamePriorityTrap3
        self.checkResult(tau3, ChooseKeepEDF.ChooseKeepEDF(tau3), False)
        self.checkResult(tau3, PALLF.PALLF(tau3), True)

    def test_CKEDFKNonOptimal(self):
        tau = systems.CKEDFNonOptimal
        self.checkResult(tau, ChooseKeepEDF.ChooseKeepEDF(tau), False)
        self.checkResult(tau, PALLF.PALLF(tau), True)

    def test_ImpCumulLaxity(self):
        tau = systems.ImpCumulLaxity
        self.checkResult(tau, Scheduler.EDF(tau), True)
        self.checkResult(tau, PALLF.PALLF(tau), False)
        self.checkResult(tau, Scheduler.PTEDF(tau), True)

    def test_ImpFTPNonOptimal(self):
        tau = systems.ImpFTPNonOptimal
        self.checkResult(tau, Scheduler.PTEDF(tau), True)
        self.checkResult(tau, Scheduler.ExhaustiveFixedPriority(tau, nbrCPUs=1, abortAndRestart=False), False)