import os
import subprocess
import re
import platform
from datetime import datetime

def detect_distro():
    try:
        # Try lsb_release first
        out = subprocess.check_output(['lsb_release', '-is'], text=True).strip().lower()
        return out
    except Exception:
        # Fallback to platform
        return platform.system().lower()

def ask_yes_no(question, default=True):
    choice = "[Y/n]" if default else "[y/N]"
    while True:
        answer = input(f"{question} {choice}: ").strip().lower()
        if answer == "":
            return default
        if answer in ['y', 'yes', 'j', 'ja']:
            return True
        if answer in ['n', 'no', 'nee']:
            return False
        print("Please answer 'y' or 'n'.")

def ask_color_text(question, default):
    color = input(f"{question} (default: {default}): ").strip()
    if color == "":
        return default
    return color

def ask_color_zenity(question, default):
    try:
        color = subprocess.check_output([
            "zenity", "--color-selection", "--show-palette",
            "--title", question,
            "--color", f"#{default}"
        ], stderr=subprocess.DEVNULL).decode().strip()
        if color.startswith("rgb"):
            match = re.match(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", color)
            if match:
                color = "#{:02X}{:02X}{:02X}".format(
                    int(match.group(1)), int(match.group(2)), int(match.group(3))
                )
        if color.startswith("#"):
            return color[1:].upper()
    except Exception:
        pass
    return default

def detect_network_interface():
    try:
        output = subprocess.check_output(
            "ip -o -4 addr show | awk '!/ lo / {print $2}'", shell=True
        ).decode().split()
        if output:
            return output[0]
    except Exception:
        pass
    return "eth0"

def ask_alignment(default="top_right"):
    options = [
        "top_left", "top_right", "bottom_left", "bottom_right",
        "top_middle", "bottom_middle", "middle_left", "middle_right", "middle_middle"
    ]
    print("Where do you want to place Conky on your desktop?")
    for idx, opt in enumerate(options, 1):
        print(f"{idx}. {opt}")
    choice = input(f"Choose alignment by number (default: {default}): ").strip()
    if choice == "":
        return default
    try:
        idx = int(choice)
        if 1 <= idx <= len(options):
            return options[idx - 1]
        else:
            print("Invalid number, using default.")
            return default
    except ValueError:
        print("Invalid input, using default.")
        return default

def ask_int(question, default):
    value = input(f"{question} (default: {default}): ").strip()
    if value == "":
        return default
    try:
        return int(value)
    except ValueError:
        print("Invalid number, using default.")
        return default

def get_conky_filename(base="conky.conf"):
    if not os.path.exists(base):
        return base
    overwrite = ask_yes_no(f"File '{base}' already exists. Overwrite?", default=True)
    if overwrite:
        return base
    # Find next available numbered filename
    i = 2
    while True:
        fname = f"conky{i}.conf"
        if not os.path.exists(fname):
            return fname
        i += 1

import os
import subprocess
import re
import platform
from datetime import datetime

# ... (alle andere functies ongewijzigd: detect_distro, ask_yes_no, ask_color_text, ask_color_zenity, detect_network_interface, ask_alignment, ask_int, get_conky_filename)

def main():
    print("Welcome to the Conky configuration generator!\n")

    net_interface = detect_network_interface()
    print(f"Detected network interface: {net_interface}")

    use_zenity = ask_yes_no("Do you want to use the graphical color picker (zenity)?", default=True)
    color_ask = ask_color_zenity if use_zenity else ask_color_text

    options = {
        "sysinfo": ask_yes_no("Show system info (OS, kernel, uptime, CPU model)?", default=True),
        "cpu": ask_yes_no("Show CPU usage?", default=True),
        "memory": ask_yes_no("Show memory usage?", default=True),
        "disk": ask_yes_no("Show disk usage?", default=True),
        "network": ask_yes_no(f"Show network usage for interface '{net_interface}'?", default=True),
        "processes": ask_yes_no("Show top processes?", default=True),
        "updates": ask_yes_no("Show number of updates?", default=True),
        "time": ask_yes_no("Show date and time?", default=True),
    }

    # Vraag of de Lua achtergrond geladen moet worden
    load_lua_bg = ask_yes_no("Load background image with Lua? (Use only with full Conky!!)", default=False)

    if load_lua_bg:
        own_window_transparent = True
        draw_borders = False
        color_default = "0055ff"
    else:
        draw_borders = ask_yes_no("Draw borders around the window?", default=True)
        own_window_transparent = ask_yes_no("Make the window transparent?", default=False)
        color_default = color_ask("Border color (orange)", "ff981d")

    # Vraag voor font shadow en outline
    draw_shades = ask_yes_no("Draw shadow on the font?", default=False)
    draw_outline = ask_yes_no("Draw outline on the font?", default=False)

    # Vraag voor plaatsing
    alignment = ask_alignment()
    gap_x = ask_int("Horizontal gap from screen edge (gap_x)", 50)
    gap_y = ask_int("Vertical gap from screen edge (gap_y)", 50)

    color1 = color_ask("OS and date & time (orange)", "E7660B")
    color4 = color_ask("Info text (yellow)", "ebd290")
    color2 = color_ask("Bars (blue)", "73a7fc")
    color3 = color_ask("Text (green)", "53e656")
    background_color = color_ask("Background color (dark gray)", "23263a")

    config_options = {
        "alignment": alignment,
        "gap_x": gap_x,
        "gap_y": gap_y,
        "minimum_width": 260,
        "maximum_width": 260,
        "minimum_height": 40,
        "use_xft": True,
        "font": "Dejavu Sans Mono:size=10",
        "override_utf8_locale": True,
        "uppercase": False,
        "short_units": True,
        "top_name_width": 20,
        "no_buffers": True,
        "double_buffer": True,
        "update_interval": 1,
        "total_run_times": 0,
        "cpu_avg_samples": 2,
        "net_avg_samples": 2,
        "background": True,
        "own_window": True,
        "own_window_type": "normal",
        "own_window_class": "Conky",
        "own_window_title": "conky-system",
        "own_window_transparent": own_window_transparent,
        "own_window_argb_visual": True,
        "own_window_argb_value": 210,
        "own_window_colour": background_color,
        "own_window_hints": "undecorated,below,sticky,skip_taskbar,skip_pager",
        "draw_borders": draw_borders,
        "border_width": 8,
        "border_inner_margin": 9,
        "draw_graph_borders": True,
        "default_shade_color": "black",
        "draw_shades": draw_shades,
        "draw_outline": draw_outline,
        "default_color": color_default,
        "color1": color1,
        "color2": color2,
        "color3": color3,
        "color4": color4,
    }

    # Voeg Lua alleen toe als gekozen
    if load_lua_bg:
        config_options["lua_load"] = 'assets/image.lua'
        config_options["lua_draw_hook_pre"] = 'conky_draw_image'

    # Huidige datum en tijd ophalen
    current_time = datetime.now().strftime("%A %d %B %Y at %H:%M")

    # Conky configuratiebestand genereren
    lines = [
        "--[[",
        "    Conky Generator by @wim66",
        "    11 June 2025",
        "    Conky Generated on:",
        f"    {current_time}",
        "    https://github.com/wim66/Conky-Generator",
        "]]",
        "",
        "conky.config = {"
    ]

    for key, value in config_options.items():
        if isinstance(value, bool):
            lines.append(f"    {key} = {str(value).lower()},")
        elif isinstance(value, str):
            lines.append(f"    {key} = '{value}',")
        else:
            lines.append(f"    {key} = {value},")
    lines.append("}\n")
    lines.append("conky.text = [[")

    # Detecteer distributie voor sysinfo
    distro = detect_distro()

    # Layout
    if options["sysinfo"]:
        if distro == "fedora":
            lines.append("${font Dejavu Sans Mono:bold:size=22}${alignc}${color1}${execi 10000 lsb_release -d | awk '{print $2, $3, $4}'}${color}${font}")
        else:
            lines.append("${font Dejavu Sans Mono:bold:size=22}${alignc}${color1}${execi 10000 lsb_release -d | cut -f 2}${color}${font}")
        lines.append("${color4}${voffset 0}${alignc}${sysname} ${kernel}")
        lines.append("${alignc}Uptime: ${uptime}")
        lines.append("${alignc}${execi 6000 cat /proc/cpuinfo | grep -i 'Model name' -m 1 | cut -c14-40}")

    if options["cpu"]:
        lines.append("${color3}${voffset 0}${alignc}${font Dejavu Sans Mono:bold:size=10}CPU: ${execi 5 sensors|grep 'Package'|awk '{print $4}'} ${cpu cpu0}% ${font}")
        lines.append("${alignc}${voffset 0}${color2}${cpubar cpu0 10,230}")
        lines.append("${alignc}${voffset 5}${cpugraph 30,230 5294E2 FF2021}")

    if options["memory"]:
        lines.append("${color3}${voffset 0}${alignc}Memory:")
        lines.append("${voffset -10}${goto 36}Used:${alignr 15}Free:")
        lines.append("${goto 36}${mem}${alignr 15} ${memeasyfree}")
        lines.append("${alignc}${voffset 0}${color2}${membar 10,230}${color}")

    if options["disk"]:
        lines.append("${color3}${voffset 3}${alignc}${font Dejavu Sans Mono:bold:size=10}Disks${font}")
        lines.append("${voffset -10}${color3}${goto 36}Used: ${alignr 15}Free:")
        lines.append("${color3}${goto 36}${fs_used /}${alignc -30}ROOT${alignr 15}${fs_free /}")
        lines.append("${alignc}${voffset 0}${color2}${fs_bar 10,230 /}${color}")
        lines.append("${color3}${goto 36}${fs_used /home/}${alignc -30}Home${alignr 15}${fs_free /home}")
        lines.append("${alignc}${voffset 0}${color2}${fs_bar 10,230 /home}${color}")

    if options["network"]:
        lines.append("${color3}${alignc}${voffset 1}${font Dejavu Sans Mono:bold:size=10}Network speed${font}")
        lines.append(f"${{color3}}${{goto 36}}${{voffset -3}}Up: ${{upspeed {net_interface}}}${{alignr 15}}Down: ${{downspeed {net_interface}}}")
        lines.append(f"${{color2}}${{goto 36}}${{voffset -3}}${{upspeedgraph {net_interface} 30,100 5294E2 42E147 3900}}${{alignr 15}}${{downspeedgraph {net_interface} 30,100 5294E2 42E147 32000}}${{color}}")
        lines.append("${color3}${goto 36}${voffset -8}Total up${alignr 15}Total down")
        lines.append(f"${{color3}}${{goto 36}}${{totalup {net_interface}}}${{alignr 15}}${{totaldown {net_interface}}}")

    if options["processes"]:
        lines.append("${color3}${voffset -5}${alignc}${font Dejavu Sans Mono:bold:size=10}Processes${font}")
        for i in range(1, 7):
            lines.append(f"${{goto 36}}${{top name {i}}}${{alignr 15}}${{top cpu {i}}}%")

    if options["updates"]:
        lines.append("${color4}${voffset 10}${alignc}${font Dejavu Sans Mono:bold:size=10}Updates${font}")
        lines.append("${alignc}${execi 1000 assets/check_updates.sh}")

    if options["time"]:
        lines.append("${voffset 10}${color1}${alignc}${font Dejavu Sans Mono:bold:size=10}Date & Time${font}")
        lines.append("${alignc}${time %A, %d %B, %Y}")
        lines.append("${alignc}${font Dejavu Sans Mono:bold:size=14}${time %H:%M}${font}")
        # Pas voffset aan afhankelijk van load_lua_bg
        if load_lua_bg:
            lines.append("${voffset -5}")
        else:
            lines.append("${voffset -25}")

    lines.append("]]")

    # Ask for filename and handle overwrite/numbering
    filename = get_conky_filename("conky.conf")
    with open(filename, "w") as f:
        f.write('\n'.join(lines))

    print(f"\n{filename} has been generated in this folder! (Re)start Conky to see the changes.")

if __name__ == "__main__":
    main()
