"""
Created on Sat Aug  3 11:50:14 2024

@author: xfeng
"""

import ctypes
import time
import csv
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from picosdk.picohrdl import picohrdl as hrdl
from picosdk.functions import assert_pico2000_ok
from picosdk.functions import adc2mVpl1000

# Initialize variables
chandle = ctypes.c_int16()
status = {}

# Open the HRDL unit
status["openUnit"] = hrdl.HRDLOpenUnit()
assert_pico2000_ok(status["openUnit"])  # Check if the unit opened successfully
chandle = status["openUnit"]
print(f"Unit opened successfully with handle: {chandle}")

# Set mains noise rejection (0 for 50Hz, 1 for 60Hz)
status["mainsRejection"] = hrdl.HRDLSetMains(chandle, 0)
assert_pico2000_ok(status["mainsRejection"])  # Check if mains noise rejection was set successfully

# Set analog channel (enable channel 1, set voltage range to 2500mV, single-ended)
channel = ctypes.c_int16(1)  # Channel number
enabled = ctypes.c_int16(1)  # Enable channel
voltage_range = ctypes.c_int16(0)  # Voltage range index (0 corresponds to 2500mV), only choose 0 or 1 for ADC20
single_ended = ctypes.c_int16(1)  # Single-ended mode

status["setAnalogInChannel"] = hrdl.HRDLSetAnalogInChannel(chandle, channel, enabled, voltage_range, single_ended)
assert_pico2000_ok(status["setAnalogInChannel"])  # Check if the analog channel was set successfully

# Set sample interval (in milliseconds) and conversion time
sample_interval_ms = 110  # Sample interval in milliseconds, need to ne bigger than the conversionTime
conversionTime = hrdl.HRDL_CONVERSIONTIME["HRDL_60MS"]  # Conversion time setting
status["setInterval"] = hrdl.HRDLSetInterval(chandle, sample_interval_ms, conversionTime)
assert_pico2000_ok(status["setInterval"])  # Check if the sample interval was set successfully

# Start data collection in streaming mode (method = 0 for BM_block; 1 for BM_window; 2 for BM_stream)
nValues = int(2 / (sample_interval_ms / 1000.0)+1)  # Number of samples to collect for 1 second
status["run"] = hrdl.HRDLRun(chandle, nValues, 0)
assert_pico2000_ok(status["run"])  # Check if data collection started successfully

# Collect data until ready
values = (ctypes.c_int32 * nValues)()  # Array to hold ADC values
time_data = (ctypes.c_int32 * nValues)()  # Array to hold time data
overflow = (ctypes.c_int16 * nValues)()  # Array to hold overflow flags
while True:
    status["ready"] = hrdl.HRDLReady(chandle)
    if status["ready"]:  # Check if the device is ready to collect data
        break

status["getValues"] = hrdl.HRDLGetTimesAndValues(chandle, time_data, values, overflow, nValues)
assert_pico2000_ok(status["getValues"])  # Check if data was collected successfully

# Stop data collection
status["stop"] = hrdl.HRDLStop(chandle)
#assert_pico2000_ok(status["stop"])  # Check if data collection stopped successfully

# Convert ADC counts data to mV
maxADC = ctypes.c_uint32()
minADC = ctypes.c_uint32()
status["getMinMaxAdcCounts"] = hrdl.HRDLGetMinMaxAdcCounts(chandle, ctypes.byref(minADC), ctypes.byref(maxADC), channel)
assert_pico2000_ok(status["getMinMaxAdcCounts"])  # Check if the ADC count range was retrieved successfully
inputRange = 2500  # Input range in mV corresponding to the voltage range index
mVvalues = adc2mVpl1000(values, inputRange, maxADC)  # Convert ADC counts to mV

# Close the HRDL unit
status["closeUnit"] = hrdl.HRDLCloseUnit(chandle)
assert_pico2000_ok(status["closeUnit"])  # Check if the unit was closed successfully
print("Unit closed successfully")

# Save the data to a CSV file
filename = f"recorded_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Sample Number", "Time (ms)", "Value (mV)", "Timestamp"])  # Write CSV header
    for i in range(nValues):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get current timestamp
        writer.writerow([i + 1, time_data[i], mVvalues[i], timestamp])  # Write data to CSV file

print(f"Data saved to {filename}")

# Print the recorded values
for i in range(nValues):
    print(f"Sample {i + 1}: {mVvalues[i]} mV at time {time_data[i]} ms")

# Convert time_data to seconds
time_seconds = np.array(time_data) / 1000.0

# Plot the recorded values
plt.figure(figsize=(10, 6))
plt.plot(time_seconds, mVvalues, marker='o', linestyle='-')
plt.title("Recorded Voltage Values Over Time")
plt.xlabel("Time (s)")
plt.ylabel("Voltage (mV)")
plt.grid(True)
plt.show()

# Print status
print(status)
