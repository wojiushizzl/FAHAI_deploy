from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import random
import threading
import logging

def run_modbus_server():
    """
    启动 Modbus TCP 服务器
    """
    # 创建数据存储（模拟线圈、离散输入、保持寄存器和输入寄存器）
    store = ModbusSlaveContext(
        adr1=ModbusSequentialDataBlock(0, [0] * 100),  # 离散输入（只读）
        adr2=ModbusSequentialDataBlock(0, [0] * 100),  # 线圈（可读写）
        adr3=ModbusSequentialDataBlock(0, [0] * 100),  # 保持寄存器（可读写）
        adr4=ModbusSequentialDataBlock(0, [0] * 100),   # 输入寄存器（只读）
        adr5=ModbusSequentialDataBlock(0, [0] * 100),   # 输入寄存器（只读）
        adr6=ModbusSequentialDataBlock(0, [0] * 100),   # 
        adr7=ModbusSequentialDataBlock(0, [0] * 100),   # 
        adr8=ModbusSequentialDataBlock(0, [0] * 100),   # 
        adr9=ModbusSequentialDataBlock(0, [0] * 100),   # 
        adr10=ModbusSequentialDataBlock(0, [0] * 100)   # 
    )

    # 创建 Modbus 服务器上下文（单从站模式）
    context = ModbusServerContext(slaves=store, single=True)

    # # 启动随机写入任务
    # random_write(context)
    #
    # # 启动数据监听任务
    # monitor_data(context)

    # 启动 Modbus TCP 服务器
    print("启动 Modbus TCP 服务器...")
    StartTcpServer(context=context, address=("127.0.0.1", 5020))

if __name__ == "__main__":
    run_modbus_server()