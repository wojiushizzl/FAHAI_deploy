import random
import time
from pymodbus.client import ModbusTcpClient

def random_write(value):
    # 连接 Modbus 服务器
    client = ModbusTcpClient("127.0.0.1", port=5020)
    client.connect()

    # 读取保持寄存器（地址 0，长度 5）
    result = client.read_holding_registers(address=0, count=1, slave=1)


    client.write_registers(address=0, values=[value], slave=1)

    # 再次读取保持寄存器
    result1 = client.read_holding_registers(address=0, count=1, slave=1)
    result2 = client.read_holding_registers(address=1, count=1, slave=1)
    result3 = client.read_holding_registers(address=2, count=1, slave=1)
    result4 = client.read_holding_registers(address=3, count=1, slave=1)

    if not result.isError():
        print(f"写入后保持寄存器的值: {result1.registers}")
        print(f"写入后保持寄存器的值: {result2.registers}")
        print(f"写入后保持寄存器的值: {result3.registers}")
        print(f"写入后保持寄存器的值: {result4.registers}")
        print('*'*40)
    else:
        print("读取失败")

    # 断开连接
    client.close()

if __name__ == '__main__':
    while True:
        value=random.randint(0, 1)
        random_write(value)
        time.sleep(2)