import socket
from typing import Tuple

from tkinter import simpledialog

import matplotlib.pyplot as plt

START = 150
SAMPLES = 850
OFFSET = 100


DATA_LENGTH = 1024
HEADER_LENGTH = 136


def getConfig() -> Tuple[str, int]:
    """
    Prompt the user for host name/IP and port
    :return: IP address, port
    """
    host = simpledialog.askstring("Host", "Enter the IP address", initialvalue="192.168.1.72")
    if host is None:
        exit(0)
    port = simpledialog.askinteger("Port", "Enter the port", initialvalue=3000)
    if port is None:
        exit(0)
    return host, port


def main():
    host, port = getConfig()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.settimeout(0.1)
        plt.ion()

        timescale = [*range(SAMPLES)]
        voltage1 = [0]*SAMPLES
        voltage2 = [0]*SAMPLES

        # Set some values to get the y-axis scaled correctly
        voltage1[0] = 127
        voltage1[1] = -128

        fig = plt.figure()
        ax = fig.add_subplot(111)

        line1, = ax.plot(timescale, voltage1, 'r-')
        line2, = ax.plot(timescale, voltage2, 'y-')

        while True:
            data = []
            s.sendall(b"STARTMEMDEPTH")
            while True:
                try:
                    data.append(int.from_bytes(s.recv(1), "big", signed=True))
                except TimeoutError:
                    # End of the packet
                    break

            print(len(data))
            if len(data) > 1024:
                # For some reason data
                data = data[OFFSET:1024+OFFSET]
            data = data[START:START+SAMPLES]
            if not plt.fignum_exists(fig.number):
                break
            if len(data) == SAMPLES:
                line1.set_ydata(data)
                fig.canvas.draw()
                fig.canvas.flush_events()
            else:
                print(f"The data was only {len(data)} samples. Expected {SAMPLES}")


if __name__ == '__main__':
    main()
