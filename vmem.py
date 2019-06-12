import psutil


class VirtualMemory:

    def getActualVMemStats(self):
        return psutil.virtual_memory()
   
    def getTotalMemory(self, stats):
        return stats.total

    def getRealUsedMemory(self, stats):
        return stats.total - stats.available

    def getOutput(self):
        stats = self.getActualVMemStats()
        output = []
        output.append(self.getRealUsedMemory(stats))
        output.append(self.getTotalMemory(stats))
        return output
