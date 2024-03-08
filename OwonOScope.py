import socket
from typing import Tuple, Iterable, List

from tkinter import simpledialog

import matplotlib.axes._axes
import matplotlib.pyplot as plt

# For some reason there is noise at the start of the waveform
# It's probably a header that needs to be decoded
START = 250
SAMPLES = 1125-START


# The 4 different lengths (1 channel 1k.10k, 2 channel 1k,10k)
DATA_LENGTH = (1125, 10125, 2184, 21084)


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


def parse_data(data: List) -> [Iterable, Tuple]:
    """
    Parse the raw data into 2 channels
    :param data: The raw stream of data, should be DATA_LENGTH long
    :return: Tuple(Tuple[Ch1 data, Ch2 data], Tuple[Ch1 enabled, Ch2 enabled])
    """
    match len(data):
        case 1125:
            print("One Channel 1k")
        case 10125:
            print("One Channel 10k")
        case 2184:
            print("Two channel 1k")
        case 20184:
            print("Two channel 10k")
        case _:
            raise ValueError(f"Data is {len(data)} bytes long. It should be one of {DATA_LENGTH}")

    return ([0] * SAMPLES, [50] * SAMPLES), (True, True)
    pass


def plot_data(line: matplotlib.axes._axes.Axes, visible: bool, data: Iterable):
    line.set_visible(visible)
    line.set_ydata(data)


def main():
    host, port = getConfig()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.settimeout(0.2)
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
            try:
                (ch1_data, ch2_data), (ch1_enb, ch2_enb) = parse_data(data)
            except ValueError:
                pass
            else:
                # We have a valid packet
                if not plt.fignum_exists(fig.number):
                    break
                plot_data(line1, ch1_enb, ch1_data)
                plot_data(line2, ch2_enb, ch2_data)
                fig.canvas.draw()
                fig.canvas.flush_events()


if __name__ == '__main__':
    main()
