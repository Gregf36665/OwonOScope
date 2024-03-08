import socket
from typing import Tuple, Iterable, List

from tkinter import simpledialog

import matplotlib.axes._axes
import matplotlib.pyplot as plt

# For some reason there is noise at the start of the waveform
# It's probably a header that needs to be decoded
HEADER_1k = 228
PAYLOAD_1k = 850

# Of course the header changes length for 10k
HEADER_10k = 578
PAYLOAD_10k = 8500


DISPLAY_SIZE = 8500  # How much to display on the graph

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


def convert_1_to_10(data: Iterable) -> List:
    """
    Converd 1k data to 10k data.
    This assumes that the header has been removed
    :param data:
    :return: The data bulked out
    """
    data_out = []
    for idx, d in enumerate(data):
        data_out[idx * 10: idx * 10 + 9] = [d] * 10
    return data_out


def parse_data(data: List) -> [Iterable, Tuple]:
    """
    Parse the raw data into 2 channels
    :param data: The raw stream of data, should be DATA_LENGTH long
    :return: Tuple(Tuple[Ch1 data, Ch2 data], Tuple[Ch1 enabled, Ch2 enabled])
    """
    # Set defaults for all parameters
    ch1_data = [0] * DISPLAY_SIZE
    ch2_data = [0] * DISPLAY_SIZE
    ch1_enb = False
    ch2_enb = False

    match len(data):
        case 1125:
            ch1_enb = True
            data = data[HEADER_1k:HEADER_1k + PAYLOAD_1k]
            ch1_data = convert_1_to_10(data)[:DISPLAY_SIZE]
        case 10125:
            ch1_data = data[HEADER_10k:HEADER_10k + PAYLOAD_10k]
            ch1_enb = True
        case 2184:
            ch1_enb = True
            ch2_enb = True
        case 20184:
            ch1_enb = True
            ch2_enb = True
        case _:
            raise ValueError(f"Data is {len(data)} bytes long. It should be one of {DATA_LENGTH}")

    return (ch1_data, ch2_data), (ch1_enb, ch2_enb)
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

        # Set the defaults for the graph
        timescale = [*range(DISPLAY_SIZE)]
        voltage1 = [0] * DISPLAY_SIZE
        voltage2 = [0] * DISPLAY_SIZE

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
