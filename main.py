from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.io import output_notebook
import json
import re

f = open("dblack_test_09_14_2023_19_25_18.json")

boot_time_data = json.load(f)

action_id = []
action_start_time = []
action_duration = []
action_end_time = []
action_name = []
log_source = []
color = []
width = []

min_duration = 0
max_duration = 100000
max_index = 10000

std_color = "red"
high_color = "yellow"
std_width = 1
high_width = 10
high_pattern = ("multi-user.target")

n = 1

for item in boot_time_data:
    for i in item["timing_details"]:
        if (i["time"] / 1000 >= min_duration and i["time"] / 1000 <= max_duration and i[
            "activating"] / 1000 < max_index) or re.search(high_pattern, i["name"]):
            action_id.append(n)
            action_start_time.append(round(i["activating"] / 1000, 3))
            action_duration.append(round(i["time"] / 1000, 3))
            action_end_time.append(round((i["activating"] + i["time"]) / 1000, 3))
            action_name.append(i["name"])
            if re.search(high_pattern, i["name"]):
                print(i["name"])
                color.append(high_color)
                width.append(high_width)
            else:
                color.append(std_color)
                width.append(std_width)
            if "activated" in i:
                log_source.append("systemd")
            else:
                log_source.append("dmesg")
            n += 1

data = {
    "id": action_id,
    "start": action_start_time,
    "duration": action_duration,
    "end": action_end_time,
    "name": action_name,
    "log_source": log_source,
    "color": color,
    "width": width
}

source = ColumnDataSource(data=data)

hover = HoverTool(
    tooltips=[
        ("Source", "@log_source"),
        ("Name", "@name"),
        ("Started", "@start ms"),
        ("Ended", "@end ms"),
        ("Run Time", "@duration ms"),
    ],
    point_policy="follow_mouse",
)

output_notebook()

p = figure(title=f"Boot Time Measurements -- {len(action_id)} Actions", y_axis_label="Boot Action (Sequence ID)",
           x_axis_label="Time Since Start (ms)", width=1000, height=700)
p.hbar(y="id", left="start", right="end", source=source, legend_label="Action Duration", color="color", width="width")
p.tools.append(hover)
p.y_range.flipped = True
p.title.text_font_size = '20pt'
p.axis.major_label_text_font_size = "15pt"
p.axis.axis_label_text_font_size = "15pt"

show(p)