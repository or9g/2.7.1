import socket
import glob
import os
import shutil
import subprocess
import pyautogui
import base64
MAX_PACKET = 1024
QUEUE_LEN = 1


def dir(path):
    try:
        my_file = path + '/.'
        file_dir = glob.glob(my_file)
        file_dir = ', '.join(file_dir).replace('\\', '/')
        print(file_dir)
    except FileNotFoundError:
        file_dir = 'Error'
    return file_dir


def delete(path_file):
    try:
        os.remove(path_file)
        message = "successfully deleted file"
        return message
    except:
        return "File doesn't exist"


def copy(original_path, copy_path):
    try:
        shutil.copy(original_path,copy_path)
        return "File has been successfully copied"

    except:
        return "File hasn't been copied"


def execute(process_name):
    try:
        subprocess.call('C:/Windows/System32/' + process_name)
        return "file has been succefully executed"

    except:
        return "Couldn't run process"


def screenshot():
    try:
        image = pyautogui.screenshot()
        image.save(r'screen.jpg')
        with open('screen.jpg', 'rb') as image_file:
            encoded_image = base64.b64encode(image_file.read())
            encoded_string = encoded_image.decode("utf-8")
            return encoded_string

    except:
        return "Couldn't take screenshot or convert it to a string"


def send_protocol(cmd, msg):
    cmd_len = len(cmd)
    msg_len = len(msg)
    total_message = str(cmd_len).encode() + '$'.encode() + cmd.encode() + str(msg_len).encode() + '$'.encode() + msg.encode()
    return total_message


def receive_protocol(my_socket):
    cur_char = ''
    cmd_len = ''
    msg_len = ''
    try:
        while cur_char != '$':
            cur_char = my_socket.recv(1).decode()
            cmd_len += cur_char
        cmd_len = cmd_len[:-1]

        cmd = my_socket.recv(int(cmd_len)).decode()

        cur_char = ''

        while cur_char != '$':
            cur_char = my_socket.recv(1).decode()
            msg_len += cur_char
        msg_len = msg_len[:-1]

        msg = my_socket.recv(int(msg_len)).decode()

        final_message = (cmd, msg)
    except socket.error:
        final_message = ('There was an eror', '')
    return final_message


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind(('0.0.0.0', 1729))
        server_socket.listen(QUEUE_LEN)
        while True:
            client_socket, client_address = server_socket.accept()
            try:
                while True:
                    request = receive_protocol(client_socket)
                    cmd = request[0]
                    other = request[1]
                    if request[0] == 'Dir':
                        sent_message = dir(other)
                    elif request[0] == 'Delete':
                        sent_message = delete(other)
                    elif request[0] == 'Copy':
                        lst = other.split("!")
                        part1 = lst[0]
                        part2 = lst[1]
                        sent_message = copy(part1, part2)

                    elif request[0] == 'Execute':
                        sent_message = execute(other)

                    elif request[0] == "Screenshot":
                        sent_message = screenshot()

                    elif request[0] == 'Exit':
                        client_socket.send(send_protocol('You were disconnected from the server', ''))
                        break
                    else:
                        sent_message = 'not a valid command'
                    client_socket.send(send_protocol(cmd, sent_message))
            except socket.error as err:
                print('received socket error on client socket' + str(err))
            finally:
                client_socket.close()
    except socket.error as err:
        print('received socket error on server socket' + str(err))
    finally:
        server_socket.close()


if __name__ == '__main__':
    main()