import socket
import random


# 配置TCP连接参数
HOST = '127.0.0.1'  # 设备的IP地址
PORT = 9005             # 设备的TCP端口号
BUFFER_SIZE = 1024      # 接收数据的缓冲区大小

#  创建TCPsocket服务端
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind((HOST, PORT))  #OSError: [Errno 48] Address already in use


while True:
    tcp_socket.listen(1)
    print(f"Server is listening on {HOST}:{PORT}")

    # 等待客户端连接
    print("Waiting for a connection...")
    client_socket, addr = tcp_socket.accept()
    print(f"Connected to {addr}")

    command = client_socket.recv(BUFFER_SIZE)
    if command:
        print(f"Received command: {command.decode('utf-8').strip()}")
        # 发送数据（如果需要）  
        # 例如，发送一个请求命令（根据设备协议）    
        response1 = '123123-6666666606'
        response2 = '123123-7777777777'

        #随机发送   
        if random.randint(0, 1) == 0:
            client_socket.sendall()
        else:
            client_socket.sendall(response2.encode('utf-8'))
    else:
        print("No data received.")
              
    


client_socket.close()
print("TCP connection closed.") 

