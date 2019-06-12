import psutil


class Cpu:

    def getActualCpuStats(self):
        return psutil.cpu_percent(percpu=True)

    def getOutput(self):
        return self.getActualCpuStats()
