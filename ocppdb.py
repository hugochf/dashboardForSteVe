from tkinter import *
from tkinter import ttk
import mysql.connector
from datetime import datetime, timedelta

#########################################
####    Connect to SteVe Database    ####
#########################################
mydb = mysql.connector.connect(
    host="54.248.208.140",
    user="steve",
    passwd="changeme",
    database="stevedb",
)
# Define query for getting data from database
queries = [
    # Get Transaction Start Time and Meter Value
    "SELECT * FROM transaction_start JOIN connector ON transaction_start.connector_pk = connector.connector_pk ORDER BY event_timestamp DESC LIMIT 1;",
    # Get Transaction Stop Time and Meter Value
    "SELECT * FROM transaction_stop ORDER BY event_timestamp DESC LIMIT 1;",
    # Get Connector status
    "SELECT * FROM connector_status WHERE connector_pk = 8 ORDER BY status_timestamp DESC LIMIT 1;",
    # Get last Meter Value
    "SELECT * FROM connector_meter_value WHERE measurand = 'Energy.Active.Import.Register' ORDER BY value_timestamp DESC LIMIT 1;"
]


def state_update():  # Loop function for updating the contents for display
    try:
        mydb.reconnect()  # Refresh the database connection for new contents
        my_cursor = mydb.cursor()
        statusBar.config(text="Connected to steVe Database")
    except mysql.connector.Error as err:
        statusBar.config(text=f"Error: {err}", fg='red')
    try:
        my_cursor.execute(queries[2])
        rows = my_cursor.fetchall()
        conn_status.set(rows[0][2])  # Status
        if (conn_status.get() == 'Available'):
            status.config(fg='green', font=('Helvetica bold', 24))
        elif (conn_status.get() == 'Charging'):
            status.config(fg='red', font=('Helvetica bold', 24))
            meterValue.config(fg='blue', font=('Helvetica bold', 24))
            meterUpdate.config(fg='blue', font=('Helvetica bold', 24))
    except mysql.connector.Error as err:
        statusBar.config(text=f"Error: {err}", fg='red')
    try:
        my_cursor.execute(queries[0])
        rows = my_cursor.fetchall()
        if (conn_status.get() != 'Available'):
            idTag.set(rows[0][3])  # Charging Tag ID
            conID.set(rows[0][8])  # Active Connector ID
        else:
            idTag.set('')
            conID.set('')
        start_time.set(rows[0][4])
        start_meter.set(rows[0][5])
        boxID.set(rows[0][7])
    except mysql.connector.Error as err:
        statusBar.config(text=f"Error: {err}", fg='red')
    try:
        my_cursor.execute(queries[1])
        rows = my_cursor.fetchall()
        if (conn_status.get() != 'Charging'):
            stop_time.set(rows[0][3])
            stop_meter.set(rows[0][4])
        else:
            stop_time.set('')
            stop_meter.set('')
    except mysql.connector.Error as err:
        statusBar.config(text=f"Error: {err}")
    try:
        my_cursor.execute(queries[3])
        rows = my_cursor.fetchall()
        meter_value.set(rows[0][3])
        meter_time.set(rows[0][2])
    except mysql.connector.Error as err:
        statusBar.config(text=f"Error: {err}", fg='red')

    # Calculate last charging time
    format = "%Y-%m-%d %H:%M:%S"
    if (conn_status.get() == 'Available'):
        datetime_t1 = datetime.strptime(start_time.get(), format)
        datetime_t2 = datetime.strptime(stop_time.get(), format)
        duration.set(datetime_t2 - datetime_t1)
        consumed.set(int(stop_meter.get())-int(start_meter.get()))
    # Runnig timer for chargine
    elif (conn_status.get() == 'Charging'):
        datetime_t1 = datetime.strptime(start_time.get(), format)
        dt = datetime.now() + timedelta(hours=1) - datetime_t1
        seconds = dt.total_seconds()
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        duration.set(f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}")
        consumed.set(int(meter_value.get())-int(start_meter.get()))
    my_cursor.close()
    mydb.close()
    root.after(1000, state_update)  # Update every 1 second


# Windows display configuration
root = Tk()
root.title('Asuka OCPP Gateway Dashboard')
root.geometry("1047x550")
# Divided in to two sections
frame_upper = LabelFrame(root, padx=5, pady=5, border=1)
frame_upper.grid(row=0, column=0, padx=10, pady=10, sticky=E+W+S)
frame_lower = LabelFrame(root, padx=5, pady=5, border=1)
frame_lower.grid(row=1, column=0, padx=10, pady=10, sticky=E+W+S)
# Status bar for showing the error message and the status of connection with database
statusBar = Label(root, text="Ready", bd=1, relief=SUNKEN, anchor=W)
statusBar.grid(row=2, column=0, sticky=E+W+S)

# First Row
# Charge Box ID
boxID = StringVar()
boxID.set('')
chargeBoxLabel = Label(frame_upper, text="Gateway ID:",
                       font=('Helvetica', 24))
chargeBoxLabel.grid(row=0, column=0, padx=10, pady=15, sticky=W)
chargeBoxId = Entry(frame_upper, textvariable=boxID,
                    width=17, font=('Helvetica', 24), bd=0, state='readonly')  # boxID
chargeBoxId.grid(row=0, column=1, padx=10, sticky=E)

# Connector ID
conID = StringVar()
conID.set('')
connectorLabel = Label(frame_upper, text="Connector ID:",
                       font=('Helvetica', 24))
connectorLabel.grid(row=0, column=2, padx=10, pady=15, sticky=W)
connectorId = Entry(frame_upper, textvariable=conID,
                    width=17, font=('Helvetica', 24), bd=0, state='readonly')
connectorId.grid(row=0, column=3, padx=10, sticky=E)

# Second Row
# ID tag
idTag = StringVar()
idTag.set('')
idTagLabel = Label(frame_upper, text="Tag ID:", font=('Helvetica', 24))
idTagLabel.grid(row=1, column=0, padx=10, pady=15, sticky=W)
id = Entry(frame_upper, textvariable=idTag, width=17,
           font=('Helvetica', 24), bd=0, state='readonly')
id.grid(row=1, column=1, padx=10, sticky=E)
# Charge Box Status
conn_status = StringVar()
conn_status.set('')
statusLabel = Label(frame_upper, text="Status:", font=('Helvetica', 24))
statusLabel.grid(row=1, column=2, padx=10, pady=3, sticky=W)
status = Entry(frame_upper, textvariable=conn_status,
               width=17, font=('Helvetica', 24), bd=0, state='readonly')
status.grid(row=1, column=3, padx=10, sticky=E)

# Third Row
tranStartLabel = Label(
    frame_lower, text="Transaction Start", font=('Helvetica bold', 24))
tranStartLabel.grid(row=2, column=0, padx=10, pady=3, sticky=W)

# Forth Row
# Transaction Start
start_time = StringVar()
start_time.set('')
startLabel = Label(frame_lower, text="Start Time:", font=('Helvetica', 24))
startLabel.grid(row=3, column=0, padx=10, pady=3, sticky=W)
startTime = Entry(frame_lower, textvariable=start_time,
                  width=17, font=('Helvetica', 24), bd=0, state='readonly')
startTime.grid(row=3, column=1, columnspan=2, padx=10, sticky=W)
# Meter Value at Transaction Start
start_meter = StringVar()
start_meter.set('')
StartMeterLabel = Label(frame_lower, text="Meter Value:",
                        font=('Helvetica', 24))
StartMeterLabel.grid(row=3, column=3, padx=10, pady=3, sticky=W)
StartMeter = Entry(frame_lower, textvariable=start_meter,
                   width=5, font=('Helvetica', 24), bd=0, state='readonly')
StartMeter.grid(row=3, column=4, padx=10, sticky=W)
unitLabel = Label(frame_lower, text="Wh",
                  font=('Helvetica', 24))
unitLabel.grid(row=3, column=5, padx=3, pady=15, sticky=W)

# Fifth Row
tranStopLabel = Label(frame_lower, text="Transaction Stop",
                      font=('Helvetica bold', 24))
tranStopLabel.grid(row=4, column=0, padx=10, pady=(15, 3), sticky=W)

# Sixth Row
# Transaction Stop
stop_time = StringVar()
stop_time.set('')
stopLabel = Label(frame_lower, text="Stop Time:", font=('Helvetica', 24))
stopLabel.grid(row=5, column=0, padx=10, pady=(3, 15), sticky=W)
stopTime = Entry(frame_lower, textvariable=stop_time,
                 width=17, font=('Helvetica', 24), bd=0, state='readonly')
stopTime.grid(row=5, column=1, columnspan=2, padx=10, pady=(3, 15), sticky=W)
# Meter Value at Transaction Start
stop_meter = StringVar()
stop_meter.set('')
StopMeterLabel = Label(frame_lower, text="Meter Value:",
                       font=('Helvetica', 24))
StopMeterLabel.grid(row=5, column=3, padx=10, pady=(3, 15), sticky=W)
StopMeter = Entry(frame_lower, textvariable=stop_meter,
                  width=5, font=('Helvetica', 24), bd=0, state='readonly')
StopMeter.grid(row=5, column=4, padx=10, pady=(3, 15), sticky=W)
unitLabel = Label(frame_lower, text="Wh",
                  font=('Helvetica', 24))
unitLabel.grid(row=5, column=5, padx=3, pady=(3, 15), sticky=W)

# Seventh Row
duration = StringVar()
duration.set('')
consumed = StringVar()
consumed.set('')
meterLabel = Label(frame_lower, text="Charge Duration:",
                   font=('Helvetica', 24))
meterLabel.grid(row=6, column=0, padx=10, pady=15, sticky=W)
meterValue = Entry(frame_lower, textvariable=duration,
                   width=17, font=('Helvetica', 24), bd=0, state='readonly')
meterValue.grid(row=6, column=1, columnspan=2, padx=10, sticky=W)
meterUpdateLabel = Label(
    frame_lower, text="Consumed Energy:", font=('Helvetica', 24))
meterUpdateLabel.grid(row=6, column=3, padx=10, pady=15, sticky=W)
meterUpdate = Entry(frame_lower, textvariable=consumed,
                    width=5, font=('Helvetica', 24), bd=0, state='readonly')
meterUpdate.grid(row=6, column=4, padx=10, sticky=W)
unitLabel = Label(frame_lower, text="Wh",
                  font=('Helvetica', 24))
unitLabel.grid(row=6, column=5, padx=3, pady=15, sticky=W)

# Eight Row
# Current Meter Value
meter_value = StringVar()
meter_value.set('')
meter_time = StringVar()
meter_time.set('')
meterLabel = Label(frame_lower, text="Current Meter Value:",
                   font=('Helvetica', 24))
meterLabel.grid(row=7, column=0, padx=10, pady=15, sticky=W)
meterValue = Entry(frame_lower, textvariable=meter_value,
                   width=5, font=('Helvetica', 24), bd=0, state='readonly')
meterValue.grid(row=7, column=1, padx=10, sticky=W)
unitLabel = Label(frame_lower, text="Wh",
                  font=('Helvetica', 24))
unitLabel.grid(row=7, column=2, padx=1, pady=15, sticky=W)
meterUpdateLabel = Label(
    frame_lower, text="Last update:", font=('Helvetica', 24))
meterUpdateLabel.grid(row=7, column=3, padx=10, pady=15, sticky=W)
meterUpdate = Entry(frame_lower, textvariable=meter_time,
                    width=17, font=('Helvetica', 24), bd=0, state='readonly')
meterUpdate.grid(row=7, column=4, columnspan=2, padx=10, sticky=W)

# Start connecting to steVe database and retrieving data to display
state_update()

mainloop()
