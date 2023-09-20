from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, HoverTool, LabelSet
from bokeh.io import output_notebook
import copy
import json
import re

source_file = "dblack_test_09_18_2023_12_11_40.json"

f = open(source_file)

boot_time_data = json.load(f)

# Data structure to be used by Bokeh
data = {
    "id": [],
    "start": [],
    "duration": [],
    "end": [],
    "name": [],
    "label": [],
    "log_source": [],
    "color": [],
    "bar_height": [],
}

# Copy of the data structure to hold the parallel sorted lists
sorted_data = copy.deepcopy(data)

# Min/Max time values to filter results on
min_duration = 0
max_duration = 100000
max_start_time = 20000

# Standard visualization formatting
dmesg_color = "blue"
systemd_color = "red"
standard_bar_height = 1
chart_width = 1000
chart_height = 700

# Highlight formatting based on regular expression match
highlight_re_pattern = "multi-user.target|initrd-switch-root"
highlight_color = "green"
highlight_bar_height = 2

# Parse the data file for metrics of interest
for item in boot_time_data:
    for i in item["timing_details"]:
        if (min_duration <= i["time"] / 1000 <= max_duration and i["activating"] / 1000 < max_start_time) or re.search(
                highlight_re_pattern, i["name"]):
            data["start"].append(round(i["activating"] / 1000, 3))
            data["duration"].append(round(i["time"] / 1000, 3))
            data["end"].append(round((i["activating"] + i["time"]) / 1000, 3))
            data["name"].append(i["name"])
            if "activated" in i:
                data["log_source"].append("systemd")
            else:
                data["log_source"].append("dmesg")
            if re.search(highlight_re_pattern, i["name"]):
                data["color"].append(highlight_color)
                data["bar_height"].append(highlight_bar_height)
                data["label"].append(i["name"])
            else:
                if "activated" in i:
                    data["color"].append(systemd_color)
                else:
                    data["color"].append(dmesg_color)
                data["bar_height"].append(standard_bar_height)
                data["label"].append(None)


# Parallel-sort the data structure lists based on start time
(
    sorted_data["start"],
    sorted_data["duration"],
    sorted_data["end"],
    sorted_data["name"],
    sorted_data["label"],
    sorted_data["log_source"],
    sorted_data["color"],
    sorted_data["bar_height"]
) = (
    list(t) for t in zip(*sorted(zip(
        data["start"],
        data["duration"],
        data["end"],
        data["name"],
        data["label"],
        data["log_source"],
        data["color"],
        data["bar_height"],
    )))
)

# Enumerate the log items sequentially after sort
for id, n in enumerate(sorted_data["start"]):
    sorted_data["id"].append(id)

# Convert the data into a ColumnDataSource for Bokeh
source = ColumnDataSource(data=sorted_data)

# Configure the tool-tip display on mouse hover
hover = HoverTool(
    tooltips=[
        ("Source", "@log_source"),
        ("Name", "@name"),
        ("Started", "@start{0.00} ms"),
        ("Ended", "@end{0.00} ms"),
        ("Run Time", "@duration{0.00} ms"),
    ],
    point_policy="follow_mouse",
)

# Build the Bokeh chart
p = figure(
    title=f"Boot Time Measurements -- {len(sorted_data['id'])} Actions -- {source_file}",
    y_axis_label="Boot Action (Sequence ID)",
    x_axis_label="Time Since Start (ms)",
    width=chart_width,
    height=chart_height,
)
p.hbar(
    y="id",
    left="start",
    right="end",
    source=source,
    color="color",
    height="bar_height",
)
p.tools.append(hover)
p.y_range.flipped = True
p.title.text_font_size = '15pt'
p.axis.major_label_text_font_size = "15pt"
p.axis.axis_label_text_font_size = "15pt"

# Label the highlighted items
labels = LabelSet(
    x="start",
    y="id",
    text="label",
    x_offset=5,
    y_offset=5,
    source=source,
    text_color=highlight_color,
    background_fill_color="white",
    border_line_color=highlight_color,
    border_line_width=1,
)
p.add_layout(labels)

output_notebook()
show(p)