import fastf1
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import BoundaryNorm
import numpy as np

fastf1.Cache.enable_cache('cache')

# user chooses which year, location, and event type
gp_data = pd.read_csv("grand_prix.csv")

# choosing year
possible_years = [str(y) for y in range(2018, 2027)]
print("You will be able to visualize any event from the years 2018 - 2026.")
year_input = input("Please enter a year: ").strip()
while year_input not in possible_years:
    print(f"Invalid year. Pleae try again with years from 2018 - 2026.")
    year_input = input("Please enter a year: ").strip()

# choosing circuit
circuits_per_year = gp_data[gp_data[year_input] == "Yes"][["Circuit Name", "Official Grand Prix Name"]]
valid_circuits = circuits_per_year["Circuit Name"].tolist()
print(f"\n These are the circuits that ran in {year_input}: ")
for _, row in circuits_per_year.iterrows():
    print(f" {row['Circuit Name']} - {row['Official Grand Prix Name']}") 

print("When entering a location of the Grand Prix, please use the circuit name.")
location_input = input("Please enter a location: ").strip()

while location_input not in valid_circuits:
    print(f"The location you requested is not recognized or did not run in {year_input}. Please try again.")
    location_input = input("Please enter a location: ").strip()


# choosing event
print(f"Here are the possible event types: \n"
      f"'FP1', 'FP2', 'FP3' for Free Practices \n"
      f"'Q' for Qualifying \n"
      f"'R' for the main Race"
      )
possible_events = ["FP1", "FP2", "FP3", "Q"]
event_input = input("Please enter the chosen event: ").strip().upper()
while event_input not in possible_events:
    print(f"Please try again. This event is not recognized.")
    event_input = input("Please enter the chosen event: ").strip().upper()

# specific session chosen
session = fastf1.get_session(int(year_input), location_input, event_input)
session.load()

# fastest lap
laps = session.laps
fast_lap = session.laps.pick_fastest()
car_data = fast_lap.get_car_data()
pos_data = fast_lap.get_pos_data()
telemetry = car_data.merge_channels(pos_data)

# channel choices for user input
channels = {
    "speed": {"col": "Speed", "label": "Speed (km/h)", "cmap": "magma", "categorical": False},
    "gear": {"col": "nGear", "label": "Gear", "cmap": "Blues", "categorical": True},
    "throttle": {"col": "Throttle", "label": "Throttle %", "cmap": "YlOrRd_r", "categorical": False},
    "drs": {"col": "DRS", "label": "DRS", "cmap": "Paired", "categorical": True, "binary": True},
    "brake": {"col": "Brake", "label": "Brake (on/off)", "cmap": "coolwarm", "categorical": True, "binary": True}
}

while True:

    # user input
    print("These are the avaiable channels:", list(channels.keys()))
    user_input = input("Enter chosen channel for visualization or 'quit' to exit: ").strip().lower()
    
    if user_input == "quit":
        print("Exiting. Thank you!")
        break

    while user_input not in channels:
        print("Sorry, this input was not recognized. Please try again.")
        print("Your options are:", list(channels.keys()))
        user_input = input("Enter chosen channel for visualization or 'quit' to exit: ").strip().lower()
        if user_input == "quit":
            break
    
    if user_input == "quit":
        print("Exiting. Thank you!")
        break

    # all parameters needed based on user_input
    chosen_channel = channels[user_input]
    col = chosen_channel["col"]
    label = chosen_channel["label"]
    cmap_color = chosen_channel["cmap"]
    categorical_decision = chosen_channel["categorical"]

    # get values from telemetry for plotting
    x_val = telemetry["X"]
    y_val = telemetry["Y"]
    color = telemetry[col]

    if chosen_channel.get("binary"):
        if col == "DRS":
            color = (color >= 10).astype(int)
        else:
            color = (color > 0).astype(int)

    # categorical visualization (color differentials)
    if categorical_decision:
        unique_values = sorted(color.unique())
        total = len(unique_values)
        cmap = plt.get_cmap(cmap_color, total)
        bounds = [b - 0.5 for b in unique_values] + [unique_values[-1] + 0.5]
        norm = BoundaryNorm(bounds, ncolors = total)
    else:
        cmap = cmap_color
        norm = plt.Normalize(color.min(), color.max())


    # plotting
    points = np.array([x_val,y_val]).T.reshape(-1, 1, 2)      # reshape the data and one list for x,y coords, reshape(number of points, wrapper dim, (x,y) pair)
    segments = np.concatenate([points[:-1], points[1:]], axis = 1)      # for continuos look of track

    # background color + mapping
    fig, ax = plt.subplots(sharex = True, sharey = True, figsize = (15, 7))
    fig.patch.set_facecolor('#E6E3E3')
    ax.set_facecolor('#E6E3E3')

    line_c = LineCollection(segments, cmap = cmap, norm = norm, linestyle = "-", linewidth = 10) # forming the track

    line_c.set_array(color)
    ax.add_collection(line_c)

    # axes limits
    five_percent_add_x = (x_val.max() - x_val.min()) * 0.05  # adding 5% to the axes limits
    five_percent_add_y = (y_val.max() - y_val.min()) * 0.05

    ax.set_xlim(x_val.min() - five_percent_add_x, x_val.max() + five_percent_add_x)
    ax.set_ylim(y_val.min() - five_percent_add_y, y_val.max() + five_percent_add_y)

    # colorbar
    cbar = fig.colorbar(line_c, ax = ax)
    cbar.set_label(label)

    if categorical_decision:
        if chosen_channel.get("binary"): # colorbar must be Off or On for DRS and Braking visualizations
            cbar.set_ticks([0, 1])
            cbar.set_ticklabels(["Off", "On"])
        else:
            cbar.set_ticks(sorted(color.unique()))
            cbar.set_ticklabels([str(int(b)) for b in sorted(color.unique())])

    ax.axis("off")

    # titles + subtitles
    plt.suptitle(f"Fastest Lap Visualization: {session.event['EventName']} {session.event.year}",
                size = 20, color = "black", fontweight = "bold")

    # sector times
    sec_1 = fast_lap["Sector1Time"].total_seconds()
    sec_2 = fast_lap["Sector2Time"].total_seconds()
    sec_3 = fast_lap["Sector3Time"].total_seconds()

    sectors_label = (f"Sector Times: \n"
                    f"Sector 1: {sec_1: .3f}s \n"
                    f"Sector 2: {sec_2: .3f}s \n"
                    f" Sector 3: {sec_3: .3f}s")

    plt.subplots_adjust(left = 0.2) # adding space to the left for the sector times

    boxes = dict(boxstyle = "round,pad = 0.5", facecolor = "#9e4ac7", edgecolor = "black")

    fig.text(0.02, 0.45, sectors_label, fontsize = 16,
            verticalalignment = "top", horizontalalignment = "left", color = "white",
            bbox = boxes)
    
    # key notes on left side (Driver, Team, Lap Time, Compound)
    key_notes = (f"Key Notes \n"
                 f"Driver: {fast_lap['Driver']}, {fast_lap['DriverNumber']} \n"
                 f"Team: {fast_lap['Team']} \n"
                 f"Lap Time: {fast_lap['LapTime'].total_seconds()} \n"
                 f"Compound: {fast_lap['Compound']} \n"
                 f"Lap Number: {fast_lap['LapNumber']}")
    boxes = dict(boxstyle = "round,pad = 0.5", facecolor = "#0491C4", edgecolor = "black")

    fig.text(0.02, 0.75, key_notes, fontsize = 16, verticalalignment = "top", horizontalalignment = "left", 
             color = "white", bbox = boxes)

    # show the plot
    plt.show()
