# CSCI-5673-Distributed-Systems

## Technology stack
- python 3
- python libraries: socket, threading, time, datetime, numpy, pandas

## How to run

1. Install python and all the libraries mentioned.
2. Start server file on one terminal
3. Use the public ip of the server as client UDP id
4. run client
5. Client will collect all the data - offsets, delays, updates, and timestamps - for an hour and generate plot and excel files.

## Limitations, potential errors
1. Difficulty with getting graph plot in the cloud LAN scenario.
2. There could be error due to not implementing the epoch part.
3. Time updates require admin permission and may create certain issues. Require different methods for Windows and Ubuntu

## What works
Offset seems to go down over the hour. The packets travel smoothly between client and server.




