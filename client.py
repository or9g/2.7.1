import socket
import base64
from io import BytesIO
from PIL import Image


MAX_PACKET = 1024

commands = ["Delete", "Copy", "Execute", "Screenshot", "Dir", "Exit"]


def command(message):
    """
    checks to see if message is a valid command
    :param message: the command the user has entered
    :type: string
    :return: if the message is a command then it will return the message and if it isn't it will return 'not valid'
    """
    if message not in commands:
        message = 'not valid'
    return message


def convert_string_to_image(string):
    """
        converts a string to an image and saves the image
        :param string: the string of the image to convert
        :type: string
        :return: if image has been successfully generated or not
    """
    try:
        decoded_image = base64.b64decode(string)
        image_data = BytesIO(decoded_image)
        image = Image.open(image_data)
        image.save(r'decoded_img.jpg')
        return "image has been successfully saved"

    except:
        return "couldnt convert image"


def send_protocol(cmd, msg):
    cmd_len = len(cmd)
    msg_len = len(msg)
    total_message = str(cmd_len).encode() + '$'.encode() + cmd.encode() + str(msg_len).encode() + '$'.encode() + msg.encode()
    return total_message


def receive_protocol(client_socket):
    cur_char = ''
    cmd_len = ''
    msg_len = ''
    try:
        while cur_char != '$':
            cur_char = client_socket.recv(1).decode()
            cmd_len += cur_char
        cmd_len = cmd_len[:-1]

        cmd = client_socket.recv(int(cmd_len)).decode()

        cur_char = ''

        while cur_char != '$':
            cur_char = client_socket.recv(1).decode()
            msg_len += cur_char
        msg_len = msg_len[:-1]

        msg = client_socket.recv(int(msg_len)).decode()

        final_message = (cmd, msg)
    except socket.error:
        final_message = ('Error', '')
    return final_message


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('127.0.0.1', 1729))
        while True:
            cmd = input("Enter command:")
            cmd = command(cmd)
            if cmd == "Copy":
                path1 = input("Enter original path:")
                path2 = input("Enter path to copy to:")
                msg = path1 + "!" + path2
            elif cmd == "Screenshot" or cmd == "Exit":
                msg = ""
            else:
                msg = input("enter path:")

            if cmd != 'not valid':
                client_socket.send(send_protocol(cmd, msg))
                response = receive_protocol(client_socket)
                print(response[1])
                if response[0] == "Screenshot":
                    convert_string_to_image(response[1])

                elif response[0] == 'You were disconnected from the server':
                    print("Exiting....")
                    break
            else:
                print('not a valid command')
    except socket.error as err:
        print("Received socket error " + str(err))
    finally:
        client_socket.close()


if __name__ == '__main__':
    main()