from collections import defaultdict
from enum import IntEnum
from struct import *
import monitor

class MessageType(IntEnum):
    SUB = 0x00
    ACK = 0x01
    REPORT = 0x02
    CONTROL = 0x03

class SubStatus(IntEnum):
    UNSUBSCRIBE = 0x00
    SUBSCRIBE = 0x01

class AckStatus(IntEnum):
    OK = 0x00
    NOT_SUBSCRIBED = 0x01
    ALREADY_SUBSCRIBED = 0x02
    NOT_SUPPORTED = 0x03

class MessageId(IntEnum):
    CPU = 0x01
    DISK = 0x02
    RAM = 0x03

class ControlId(IntEnum):
    MONITORING_SWITCH = 0x01

class MonitoringSwitch(IntEnum):
    OFF = 0x00
    ON = 0x01


class Manager:

    monitoringFlag = True
    actFlag = True
    clients = dict()
    clientsSettings = defaultdict(set)
    my_monitor = monitor.Monitor("Monitoring-thread", 0.3)
    my_monitor.start()

    @classmethod
    def getMonitoringFlag(cls):
        return cls.monitoringFlag

    @classmethod
    def getActFlag(cls):
        return cls.actFlag

    @classmethod
    def setActFlag(cls, flag):
        cls.actFlag = flag

    @classmethod
    def add_client(cls, client_id, handler):
        cls.clients[client_id] = handler
        print "Client %d added!" % client_id

    @classmethod
    def handle_message(cls, client_id, msg):
        print "Handling message"
        msg_type, msg_id = unpack_from('BB', msg)
        print "Message type: %u, id: %u" % (msg_type, msg_id)
        cls.dispatch_msg(client_id, msg_type, msg_id, msg[2:])

    @classmethod
    def dispatch_msg(cls, client_id, msg_type, msg_id, data):
        print "Dispatch: %u, %u" % (msg_type, msg_id)
        if msg_type == MessageType.SUB:
            cls.handle_subscription(client_id, msg_id, data)
        elif msg_type == MessageType.CONTROL:
            cls.handle_control(msg_id, data)
        else:
            print "Unknown message type: %d" % msg_type

    @classmethod
    def handle_subscription(cls, client_id, msg_id, data):
        print "Handle sub"
        sub_switch = unpack('B', data)[0]
        if sub_switch == SubStatus.UNSUBSCRIBE:
            print "Client %u Msg %u UNSUBSCRIBE" % (client_id, msg_id)
            cls.unsubscribe(client_id, msg_id)
        elif sub_switch == SubStatus.SUBSCRIBE:
            print "Client %u Msg %u SUBSCRIBE" % (client_id, msg_id)
            cls.subscribe(client_id, msg_id)
        else:
            print "Wrong switch value: %u" % sub_switch

    @classmethod
    def handle_control(cls, msg_id, data):
        print "Handle control"
        if msg_id == ControlId.MONITORING_SWITCH:
            cls.handle_monitor_switch(data)
        else:
            print "Unknown control message: %u" % msg_id

    @classmethod
    def handle_monitor_switch(cls, data):
        print "Handle monitor switch"
        monitor_switch = unpack('B', data)[0]
        print "Monitoring: %u" % monitor_switch
        if monitor_switch == MonitoringStatus.OFF:
            cls.monitoringFlag = False
        elif monitor_switch == MonitoringStatus.ON:
            cls.monitoringFlag = True
        else:
            print "Wrong switch value %u" % monitor_switch

    @classmethod
    def isInEnum(cls, value, enum):
        for e in enum:
            if value == e.value:
                return True
        return False

    @classmethod
    def subscribe(cls, client_id, msg_id):
        print "Subscribe: client_id[%u] message_id[%u]" % (client_id, msg_id)
        if msg_id in cls.clientsSettings[client_id]:
            print "Subscribe: %u ALREADY SUBSCRIBED" % msg_id
            cls.send_ack(client_id, msg_id, AckStatus.ALREADY_SUBSCRIBED)
        elif cls.isInEnum(msg_id, MessageId):
            print "Subscribe: OK"
            cls.clientsSettings[client_id].add(msg_id)
            cls.send_ack(client_id, msg_id, AckStatus.OK)
        else:
            print "Subscribe: %u NOT SUPPORTED" % msg_id
            cls.send_ack(client_id, msg_id, AckStatus.NOT_SUPPORTED)

    @classmethod
    def unsubscribe(cls, client_id, msg_id):
        print "Unsubscribe: client_id[%u] message_id[%u]" % (client_id, msg_id)
        if msg_id in cls.clientsSettings[client_id]:
            print "Unsubscribe: OK"
            cls.clientsSettings[client_id].remove(msg_id)
            cls.send_ack(client_id, msg_id, AckStatus.OK)
        else:
            print "Unsubscribe: %u NOT SUBSCRIBED" % msg_id
            cls.send_ack(client_id, msg_id, AckStatus.NOT_SUBSCRIBED)

    @classmethod
    def send_ack(cls, client_id, msg_id, status):
        ack = pack('BBB', MessageType.ACK, msg_id, status)
        cls.send(client_id, ack)

    @classmethod
    def send(cls, client_id, msg):
        cls.print_sent(client_id, msg)
        cls.clients[client_id].write_message(msg, True)

    @classmethod
    def print_sent(cls, client_id, msg):
        print "Sending to [%d]: %s" % (client_id, cls.hexvalues(msg))

    @classmethod
    def hexvalues(cls, msg):
        out = ""
        for c in msg:
            value = "0x%0.2X " % ord(c)
            out += value
        return out

    @classmethod
    def remove_client(cls, client_id):
        if client_id in cls.clients:
            cls.clients.pop(client_id)
        if client_id in cls.clientsSettings:
            cls.clientsSettings.pop(client_id)
        print "Client %s disconnected." % client_id

    @classmethod
    def generateReport(cls, results):
        print results
        for client_id in cls.clients:
            cls.generateClientReport(client_id, results)

    @classmethod
    def generateClientReport(cls, client_id, results):
        for msg_id in cls.clientsSettings[client_id]:
            report = cls.generateMsgIdReport(msg_id, results)
            cls.send(client_id, report)

    @classmethod
    def generateMsgIdReport(cls, msg_id, results):
        if msg_id == MessageId.CPU:
            return cls.generateCpuReport(results[0])
        elif msg_id == MessageId.DISK:
            return cls.generateDiskReport(results[1])
        elif msg_id == MessageId.RAM:
            return cls.generateRamReport(results[2])

    @classmethod
    def generateCpuReport(cls, cpuStats):
        report = pack('<BBH', MessageType.REPORT, MessageId.CPU, len(cpuStats))
        for cpuStat in cpuStats:
            packedStat = pack('<H', int(cpuStat * 10))
            report += packedStat
        return report

    @classmethod
    def generateDiskReport(cls, partitions):
        report = pack('<BBH', MessageType.REPORT, MessageId.DISK, len(partitions))
        for partition in partitions:
            device = ""

            # device_name
            device += pack('<H', len(partition[0]))
            for device_name_character in partition[0]:
                device += pack('B', ord(device_name_character))

            # mountpoint
            device += pack('<H', len(partition[1]))
            for mountpoint_character in partition[1]:
                device += pack('B', ord(mountpoint_character))

            # used / total
            device += pack('<QQ', partition[2][0], partition[2][1])
            report += device

        return report

    @classmethod
    def generateRamReport(cls, ramStats):
        report = pack('<BBQQ', MessageType.REPORT, MessageId.RAM, ramStats[0], ramStats[1])
        return report
