# coding:UTF-8
"""
    测试文件
    Test file
"""
import time
import datetime
import platform
import threading
import lib.device_model as deviceModel
from lib.data_processor.roles.jy901s_dataProcessor import JY901SDataProcessor
from lib.protocol_resolver.roles.protocol_485_resolver import Protocol485Resolver

welcome = """
Welcome to the Wit-Motoin sample program
"""
_writeF = None                    #  Write file
_IsWriteF = False                 # Write file identification
def readConfig(device):
    """
    读取配置信息示例    Example of reading configuration information
    :param device: 设备模型 Device model
    :return:
    """
    tVals = device.readReg(0x02,3)  # Read data content, return rate, communication rate
    if (len(tVals)>0):
        print("Result：" + str(tVals))
    else:
        print("No Result")
    tVals = device.readReg(0x23,2)  # Read the installation direction and algorithm
    if (len(tVals)>0):
        print("Result：" + str(tVals))
    else:
        print("No Result")

def setConfig(device):
    """
    Example setting configuration information
    :param device: Device model
    :return:
    """
    device.unlock()                #unlock
    time.sleep(0.1)                #Sleep 100ms
    device.writeReg(0x03, 6)       #Set the transmission back rate to 10HZ
    time.sleep(0.1)                #Sleep 100ms
    device.writeReg(0x23, 0)       # Set the installation direction: horizontal and vertical
    time.sleep(0.1)                #Sleep 100ms
    device.writeReg(0x24, 0)       #Set the installation direction: nine axis, six axis
    time.sleep(0.1)                #Sleep 100ms
    device.save()                  #Save

def AccelerationCalibration(device):
    """
        Acceleration calibration
    :param device:  Device model
    :return:
    """
    device.AccelerationCalibration()                 # Acceleration calibration
    print("End of acceleration calibration")

def FiledCalibration(device):
    """
        Magnetic field calibration
    :param device:  Device model
    :return:
    """
    device.BeginFiledCalibration()                   # 开始磁场校准   Starting field calibration
    if input("Please rotate around axis XYZ at a slow speed one time, and finish the calibration after completing the rotation of three axis（Y/N)？").lower()=="y":
        device.EndFiledCalibration()                 # 结束磁场校准   End field calibration
        print("End field calibration")

def startRecord():
    """
      Start recording data
    :return:
    """
    global _writeF
    global _IsWriteF
    _writeF = open(str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')) + ".txt", "w")    #New file
    _IsWriteF = True                                                                        #Write mark
    Tempstr = "Chiptime"
    Tempstr +=  "\tax(g)\tay(g)\taz(g)"
    Tempstr += "\twx(deg/s)\twy(deg/s)\twz(deg/s)"
    Tempstr += "\tAngleX(deg)\tAngleY(deg)\tAngleZ(deg)"
    Tempstr += "\tT(°)"
    Tempstr += "\tmagx\tmagy\tmagz"
    Tempstr += "\r\n"
    _writeF.write(Tempstr)
    print("Start recording data")

def endRecord():
    """
     End record data
    :return:
    """
    global _writeF
    global _IsWriteF
    _IsWriteF = False             #     Tag cannot write the identity
    _writeF.close()               #     Close file
    print("End recording data")

def onUpdate(deviceModel):
    """
    数据更新事件  Data update event
    :param deviceModel: 设备模型    Device model
    :return:
    """
    print("Time:" + str(deviceModel.getDeviceData("Chiptime"))
         , " Temp:" + str(deviceModel.getDeviceData("temperature"))
         , " Acc：" + str(deviceModel.getDeviceData("accX")) +","+  str(deviceModel.getDeviceData("accY")) +","+ str(deviceModel.getDeviceData("accZ"))
         ,  " Gyro:" + str(deviceModel.getDeviceData("gyroX")) +","+ str(deviceModel.getDeviceData("gyroY")) +","+ str(deviceModel.getDeviceData("gyroZ"))
         , " Angle:" + str(deviceModel.getDeviceData("angleX")) +","+ str(deviceModel.getDeviceData("angleY")) +","+ str(deviceModel.getDeviceData("angleZ"))
        , " Mag:" + str(deviceModel.getDeviceData("magX")) +","+ str(deviceModel.getDeviceData("magY"))+","+ str(deviceModel.getDeviceData("magZ"))
          )
    if (_IsWriteF):    #记录数据    Record data
        Tempstr = " " + str(deviceModel.getDeviceData("Chiptime"))
        Tempstr += "\t"+str(deviceModel.getDeviceData("accX")) + "\t"+str(deviceModel.getDeviceData("accY"))+"\t"+ str(deviceModel.getDeviceData("accZ"))
        Tempstr += "\t" + str(deviceModel.getDeviceData("gyroX")) +"\t"+ str(deviceModel.getDeviceData("gyroY")) +"\t"+ str(deviceModel.getDeviceData("gyroZ"))
        Tempstr += "\t" + str(deviceModel.getDeviceData("angleX")) +"\t" + str(deviceModel.getDeviceData("angleY")) +"\t"+ str(deviceModel.getDeviceData("angleZ"))
        Tempstr += "\t" + str(deviceModel.getDeviceData("temperature"))
        Tempstr += "\t" + str(deviceModel.getDeviceData("magX")) +"\t" + str(deviceModel.getDeviceData("magY")) +"\t"+ str(deviceModel.getDeviceData("magZ"))
        Tempstr += "\r\n"
        _writeF.write(Tempstr)

def LoopReadThead(device):
    """
    循环读取数据  Cyclic read data
    :param device:
    :return:
    """
    while(True):                            #循环读取数据 Cyclic read data
        device.readReg(0x30, 41)            #读取 数据  Read data

if __name__ == '__main__':

    print(welcome)
    device = deviceModel.DeviceModel(
        "My JY901",
        Protocol485Resolver(),
        JY901SDataProcessor(),
        "51_0"
    )
    device.ADDR = 0x50                                       #设置传感器ID   Setting the Sensor ID
    if (platform.system().lower() == 'linux'):
        device.serialConfig.portName = "/dev/ttyS0"        #设置串口  Set serial port
    else:
        device.serialConfig.portName = "COM82"               #设置串口  Set serial port
    device.serialConfig.baud = 9600                          #设置波特率 Set baud rate
    device.openDevice()                                      #打开串口  Open serial port
    readConfig(device)                                       #读取配置信息    Read configuration information
    device.dataProcessor.onVarChanged.append(onUpdate)       #数据更新事件    Data update event
    onUpdate(device)
    # startRecord()                                            # 开始记录数据   Start recording data
    # t = threading.Thread(target=LoopReadThead, args=(device,))  #开启一个线程读取数据 Start a thread to read data
    # t.start()

    # input()
    # device.closeDevice()
    # endRecord()                             # 结束记录数据    End record data
