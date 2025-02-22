from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import random
import threading
import logging

# 配置日志记录
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

def random_write(context):
    """
    定时任务：在地址 0 上随机写入 0 或 1
    """
    # 获取从站上下文
    slave_context = context[0]  # 单从站模式

    # 生成随机值（0 或 1）
    value = random.randint(0, 1)

    # 写入线圈（地址 0）
    slave_context.setValues(1, 0, [value])  # 使用 "coils" 表示线圈
    print(f"随机写入线圈地址 0 的值: {value}")

    # 每隔 2 秒执行一次
    threading.Timer(2.0, random_write, args=(context,)).start()

def monitor_data(context):
    """
    定时任务：监听并打印地址 0、1、2、3 的数据
    """
    # 获取从站上下文
    slave_context = context[0]  # 单从站模式

    # 读取地址 0、1、2、3 的数据
    coil_values = slave_context.getValues("coils", 0, count=4)            # 线圈
    discrete_input_values = slave_context.getValues("discrete_inputs", 0, count=4)  # 离散输入
    holding_register_values = slave_context.getValues("holding_registers", 0, count=4)  # 保持寄存器
    input_register_values = slave_context.getValues("input_registers", 0, count=4)      # 输入寄存器

    # 打印数据
    print(f"线圈地址 0-3 的值: {coil_values}")
    print(f"离散输入地址 0-3 的值: {discrete_input_values}")
    print(f"保持寄存器地址 0-3 的值: {holding_register_values}")
    print(f"输入寄存器地址 0-3 的值: {input_register_values}")
    print("-" * 40)

    # 每隔 1 秒执行一次
    threading.Timer(1.0, monitor_data, args=(context,)).start()

def run_modbus_server():
    """
    启动 Modbus TCP 服务器
    """
    # 创建数据存储（模拟线圈、离散输入、保持寄存器和输入寄存器）
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0] * 100),  # 离散输入（只读）
        co=ModbusSequentialDataBlock(0, [0] * 100),  # 线圈（可读写）
        hr=ModbusSequentialDataBlock(0, [0] * 100),  # 保持寄存器（可读写）
        ir=ModbusSequentialDataBlock(0, [0] * 100)   # 输入寄存器（只读）
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