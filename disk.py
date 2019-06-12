import psutil


class DiskUsage:

    def getUsage(self, mount):
        usage = psutil.disk_usage(str(mount))
        usage_output = []
        usage_output.append(usage.used)
        usage_output.append(usage.total)
        return usage_output

    def getPartitionOutput(self, partition):
        partition_output = []
        partition_output.append(partition.device)
        partition_output.append(partition.mountpoint)
        partition_output.append(self.getUsage(partition.mountpoint))
        return partition_output

    def getPartitionsInfo(self):
        output = []
        partitions =  psutil.disk_partitions(all=False)
        for partition in partitions:
            if (partition.fstype and not partition.device.startswith('/dev/loop')): 
            #if not partition.device.startswith('/dev/loop'): 
                output.append(self.getPartitionOutput(partition))
        return output

    def getOutput(self):
        return self.getPartitionsInfo()
