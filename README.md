# OwonOScope
Software to parse [OWON SDS5000 scopes](git@github.com:Gregf36665/OwonOScope.git)

## Overview
Currently, this software allows you to connect to an owon scope and display the waveform on your screen.

## Known issues
- If you turn off channel 1 channel 2 displays as if it is channel 1 on your computer
- Some distros of linux are missing simpledialog from tkinter [see here](git@github.com:Gregf36665/OwonOScope.git). To fix this make sure you have >3.9.5

If you find any other issues please report them as an issue


## Setup instructions
### Windows stand alone
Head over to releases and download the latest .exe

### Build it yourself
The only dependency is matplotlib


### Configuring an ethernet adaptor

A recommended way to use this software is to create a new network using a USB to Ethernet adaptor. 
In order to do this follow these steps:
1) Plug in your USB to Ethernet adaptor
2) Configure your computer to have a static IP on the same subnet as the scope