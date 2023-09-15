from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.io import output_notebook

import json
import re

f = open("dblack_test_09_14_2023_19_25_18.json")

boot_time_data = json.load(f)

data = {
    "id": [],
    "start": [],
    "duration": [],
    "end": [],
    "name": [],
    "log_source": [],
    "color": [],
    "bar_height": [],
}

min_duration = 0
max_duration = 100000
max_index = 20000

dmesg_color = "blue"
systemd_color = "red"
highlight_color = "green"
standard_height = 1
highlight_height = 20
highlight_pattern = "multi-user.target"

n = 1

for item in boot_time_data:
    for i in item["timing_details"]:
        if (min_duration <= i["time"] / 1000 <= max_duration and i["activating"] / 1000 < max_index) or re.search(
                highlight_pattern, i["name"]):
            data["id"].append(n)
            data["start"].append(round(i["activating"] / 1000, 3))
            data["duration"].append(round(i["time"] / 1000, 3))
            data["end"].append(round((i["activating"] + i["time"]) / 1000, 3))
            data["name"].append(i["name"])
            if "activated" in i:
                data["log_source"].append("systemd")
            else:
                data["log_source"].append("dmesg")
            if re.search(highlight_pattern, i["name"]):
                data["color"].append(highlight_color)
                data["bar_height"].append(highlight_height)
            else:
                if "activated" in i:
                    data["color"].append(systemd_color)
                else:
                    data["color"].append(dmesg_color)
                data["bar_height"].append(standard_height)
            n += 1

# z = zip(
#         data["start"],
#         data["duration"],
#         data["end"],
#         data["name"],
#         data["log_source"],
#         data["color"],
#         data["bar_height"],
#     )


# for id, n in enumerate(Z["start"]):
#     data["id"].append(id)
#
# print(data)

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

p = figure(title=f"Boot Time Measurements -- {len(data['id'])} Actions", y_axis_label="Boot Action (Sequence ID)",
           x_axis_label="Time Since Start (ms)", width=1000, height=700)
p.hbar(y="id", left="start", right="end", source=source, color="color", height="bar_height")
p.tools.append(hover)
p.y_range.flipped = True
p.title.text_font_size = '20pt'
p.axis.major_label_text_font_size = "15pt"
p.axis.axis_label_text_font_size = "15pt"

show(p)