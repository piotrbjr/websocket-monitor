import disk
import vmem
import cpu_percent
import manager
import threading
import time

class Monitor(threading.Thread):

    def __init__(self, name, delay):
        threading.Thread.__init__(self)
        self.cpu = cpu_percent.Cpu()
        self.disk = disk.DiskUsage()
        self.mem = vmem.VirtualMemory()
        self.name = name
        self.delay = delay

    def run(self):
        print "Starting monitor"
        self.startSending()

    def startSending(self):
        print "Sending"
        while True:
            if manager.Manager.getActFlag() == False:
                return
            if manager.Manager.getMonitoringFlag():
                self.sendMeasurement()
            time.sleep(self.delay)

    def getOutput(self):
        output = []
        output.append(self.cpu.getOutput())
        output.append(self.disk.getOutput())
        output.append(self.mem.getOutput())
        return output

    def sendMeasurement(self):
        manager.Manager.generateReport(self.getOutput())
