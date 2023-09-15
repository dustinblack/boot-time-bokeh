from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.io import output_notebook
import json

f = open("dblack_test_09_14_2023_19_25_18.json")

boot_time_data = json.load(f)

action_id = []
action_start_time = []
action_duration = []
action_end_time = []
action_name = []
log_source = []

min_duration = 0
max_duration = 100000
max_index = 10000

n = 1

for item in boot_time_data:
    for i in item["timing_details"]:
        if i["time"] / 1000 > min_duration and i["time"] / 1000 < max_duration and i["activating"] / 1000 < max_index:
            action_id.append(n)
            action_start_time.append(round(i["activating"] / 1000, 3))
            action_duration.append(round(i["time"] / 1000, 3))
            action_end_time.append(round((i["activating"] + i["time"]) / 1000, 3))
            action_name.append(i["name"])
            if "activated" in i:
                log_source.append("systemd")
            else:
                log_source.append("dmesg")
            n += 1

# del boot_time_index[100:]
# del action_duration[100:]

data = {"id": action_id, "start": action_start_time, "duration": action_duration, "end": action_end_time,
        "name": action_name, "log_source": log_source}
source = ColumnDataSource(data=data)

hover = HoverTool(tooltips=[
    ("Source", "@log_source"),
    ("Name", "@name"),
    ("Started", "@start ms"),
    ("Ended", "@end ms"),
    ("Run Time", "@duration ms"),
])

output_notebook()

p = figure(title=f"Boot Time Measurements -- {len(action_id)} Actions", y_axis_label="Time Since Start (ms)",
           x_axis_label="Boot Action (Sequence ID)", width=2500, height=3500)
p.vbar(x="id", bottom="start", top="end", source=source, legend_label="Action Duration", color="red", width=1)
# p.y_range.flipped = True
p.tools.append(hover)
p.title.text_font_size = '30pt'
p.axis.major_label_text_font_size = "20pt"
p.axis.axis_label_text_font_size = "20pt"

show(p)