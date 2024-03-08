import socket

from tkinter import simpledialog

import matplotlib.pyplot as plt

START = 150
SAMPLES = 850
OFFSET = 100


def main():
    host = simpledialog.askstring("Host", "Enter the IP address")
    port = simpledialog.askinteger("Port", "Enter the port", initialvalue=3000)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.settimeout(0.1)
        plt.ion()

        timescale = [*range(SAMPLES)]
        voltage = [0]*SAMPLES
        voltage[0] = 0xFF

        fig = plt.figure()
        ax = fig.add_subplot(111)

        line1, = ax.plot(timescale, voltage, 'r-')

        while True:
            data = []
            s.sendall(b"STARTMEMDEPTH")
            while True:
                try:
                    data.append(int.from_bytes(s.recv(1), "big", signed=True))
                except TimeoutError:
                    # End of the packet
                    break
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
