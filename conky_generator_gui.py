import os
import subprocess
import platform
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from datetime import datetime


class ConkyGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Conky Configuration Generator")
        self.root.configure(bg='#001225')

        # Configureer de stijl voor de GUI
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#001225')
        style.configure('TLabel', background='#001225', foreground='#E0E0E0', font=('Helvetica', 11))
        style.configure('Title.TLabel', background='#001225', foreground='#63b8ff', font=('Helvetica', 16, 'bold'))
        style.configure('TButton', background='#293346', foreground='white', font=('Helvetica', 11, 'bold'), padding=10, bordercolor='#4682B4', borderwidth=2, relief='solid')
        style.map('TButton', background=[('active', '#5A9BD4'), ('disabled', '#3A3A3A')], foreground=[('active', 'white'), ('disabled', '#A0A0A0')], bordercolor=[('active', '#5A9BD4'), ('disabled', '#3A3A3A')])
        style.configure('TLabelframe', background='#001225', foreground='#E0E0E0', bordercolor='#4682B4', borderwidth=2, relief='solid')
        style.configure('TLabelframe.Label', background='#001225', foreground='#63b8ff')
        style.configure('TCheckbutton', background='#001225', foreground='#E0E0E0', font=('Helvetica', 10))
        style.map('TCheckbutton', background=[('active', '#001225'), ('selected', '#001225')], foreground=[('active', '#5A9BD4'), ('selected', '#E0E0E0')], indicatorbackground=[('selected', '#5A9BD4'), ('!selected', '#293346'), ('active', '#5A9BD4')])
        style.configure('TOptionMenu', background='#001225', foreground='#E0E0E0', font=('Helvetica', 10))
        style.configure('TEntry', fieldbackground='#293346', foreground='#E0E0E0', insertcolor='white', bordercolor='#4682B4', borderwidth=2, relief='solid')
        style.map('TEntry', bordercolor=[('focus', '#5A9BD4'), ('disabled', '#3A3A3A')], fieldbackground=[('focus', '#293346'), ('disabled', '#3A3A3A')])
        style.configure('TSeparator', background='#4682B4')
        style.configure('TMenubutton', background='#293346', foreground='#E0E0E0', font=('Helvetica', 10), padding=8, bordercolor='#4682B4', borderwidth=1, relief='solid')
        style.map('TMenubutton', background=[('active', '#5A9BD4'), ('disabled', '#3A3A3A')], foreground=[('active', 'white'), ('disabled', '#A0A0A0')])

        self.root.option_add("*Menu.Background", '#293346')
        self.root.option_add("*Menu.Foreground", '#E0E0E0')
        self.root.option_add("*Menu.activeBackground", '#5A9BD4')
        self.root.option_add("*Menu.activeForeground", 'white')
        self.root.option_add("*Menu.borderWidth", 0)
        self.root.option_add("*Menu.relief", 'flat')

        # Variabelen om gebruikersinvoer op te slaan
        self.options = {}
        self.config_options = {}
        self.net_interface = self.detect_network_interface()
        self.distro = self.detect_distro()

        # Hoofdframe
        self.main_frame = ttk.Frame(self.root, padding="15", style='TFrame')
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Zorg dat kolommen gelijk verdeeld zijn
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

        # Titel (over beide kolommen)
        ttk.Label(self.main_frame, text="Conky Configuration Generator", style='Title.TLabel').grid(row=0, column=0, columnspan=2, pady=10)

        # Scheidingslijn
        ttk.Separator(self.main_frame, orient='horizontal').grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Netwerkinterface weergeven (over beide kolommen)
        ttk.Label(self.main_frame, text=f"Detected network interface: {self.net_interface}").grid(row=2, column=0, columnspan=2, pady=5)

        # Twee kolommen: links voor opties en uitlijning, rechts voor kleuren, gaps en borders
        self.create_option_checkboxes()  # Kolom 0
        self.create_alignment_menu()     # Kolom 0
        self.create_color_pickers()      # Kolom 1
        self.create_gap_inputs()         # Kolom 1
        self.create_lua_background_option()  # Kolom 1
        self.create_border_options()     # Kolom 1

        # Statuslabel voor feedback
        self.status_label = ttk.Label(self.main_frame, text="", background='#001225', foreground='#E0E0E0')
        self.status_label.grid(row=9, column=0, columnspan=2, pady=5)

        # Frame voor knoppen (horizontale lay-out)
        button_frame = ttk.Frame(self.main_frame, style='TFrame')
        button_frame.grid(row=10, column=0, columnspan=2, pady=20)

        # Knop om configuratie te genereren
        self.generate_button = ttk.Button(button_frame, text="Generate Conky Config", command=self.generate_config)
        self.generate_button.grid(row=0, column=0, padx=5)

        # Knop om Conky te herstarten
        self.restart_button = ttk.Button(button_frame, text="(Re)start Conky", command=self.restart_conky)
        self.restart_button.grid(row=0, column=1, padx=5)

    def detect_distro(self):
        try:
            out = subprocess.check_output(['lsb_release', '-is'], text=True).strip().lower()
            return out
        except Exception:
            return platform.system().lower()

    def detect_network_interface(self):
        try:
            output = subprocess.check_output(
                "ip -o -4 addr show | awk '!/ lo / {print $2}'", shell=True
            ).decode().split()
            return output[0] if output else "eth0"
        except Exception:
            return "eth0"

    def restart_conky(self):
        """Herstart Conky door bestaande instanties te stoppen en conky.conf te starten."""
        self.status_label.config(text="Restarting Conky...")
        self.restart_button.configure(state='disabled')
        self.root.update()

        try:
            # Controleer of conky.conf bestaat
            if not os.path.exists("conky.conf"):
                raise FileNotFoundError("conky.conf not found. Generate a config first.")

            # Stop alle Conky-processen
            subprocess.run(["killall", "conky"], check=False)

            # Wacht 1 seconde
            subprocess.run(["sleep", "1"], check=True)

            # Start Conky met conky.conf in de achtergrond
            subprocess.Popen(["conky", "-c", "conky.conf"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        except FileNotFoundError as e:
            self.status_label.config(text="Error: conky.conf not found")
            messagebox.showerror("Error", str(e))
        except subprocess.CalledProcessError as e:
            self.status_label.config(text="Error restarting Conky")
            messagebox.showerror("Error", f"Failed to restart Conky: {e}")
        finally:
            self.restart_button.configure(state='normal')
            self.root.update()

    def create_option_checkboxes(self):
        options_frame = ttk.LabelFrame(self.main_frame, text="Display Options", padding="10")
        options_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N), pady=10, padx=5)

        option_labels = [
            ("Show system info (OS, kernel, uptime, CPU model)?", "sysinfo"),
            ("Show CPU usage?", "cpu"),
            ("Show memory usage?", "memory"),
            ("Show disk usage?", "disk"),
            (f"Show network usage for interface '{self.net_interface}'?", "network"),
            ("Show top processes?", "processes"),
            ("Show number of updates?", "updates"),
            ("Show date and time?", "time")
        ]

        self.options = {key: tk.BooleanVar(value=True) for _, key in option_labels}

        for idx, (label, key) in enumerate(option_labels):
            ttk.Checkbutton(options_frame, text=label, variable=self.options[key]).grid(row=idx, column=0, sticky=tk.W, pady=3)

    def create_color_pickers(self):
        colors_frame = ttk.LabelFrame(self.main_frame, text="Color Options", padding="10")
        colors_frame.grid(row=3, column=1, sticky=(tk.W, tk.E, tk.N), pady=10, padx=5)

        self.colors = {
            "color1": tk.StringVar(value="E7660B"),
            "color2": tk.StringVar(value="73a7fc"),
            "color3": tk.StringVar(value="53e656"),
            "color4": tk.StringVar(value="ebd290"),
            "background_color": tk.StringVar(value="23263a"),
            "border_color": tk.StringVar(value="ff981d")
        }

        color_labels = [
            ("OS and date & time color:", "color1"),
            ("Bars color:", "color2"),
            ("Text color:", "color3"),
            ("Info text color:", "color4"),
            ("Background color:", "background_color"),
            ("Border color:", "border_color")
        ]

        for idx, (label, key) in enumerate(color_labels):
            ttk.Label(colors_frame, text=label).grid(row=idx, column=0, sticky=tk.W, pady=3)
            ttk.Button(colors_frame, text="Pick Color", command=lambda k=key: self.pick_color(k)).grid(row=idx, column=1, padx=5, pady=3)

    def pick_color(self, key):
        color = colorchooser.askcolor(title=f"Choose {key} color", initialcolor=f"#{self.colors[key].get()}")[1]
        if color:
            self.colors[key].set(color[1:].upper())

    def create_alignment_menu(self):
        align_frame = ttk.LabelFrame(self.main_frame, text="Alignment", padding="10")
        align_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=10, padx=5)

        ttk.Label(align_frame, text="Desktop alignment:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.alignment = tk.StringVar(value="top_right")
        options = [
            "top_left", "top_right", "bottom_left", "bottom_right",
            "top_middle", "bottom_middle", "middle_left", "middle_right", "middle_middle"
        ]
        ttk.OptionMenu(align_frame, self.alignment, "top_right", *options).grid(row=0, column=1, padx=5, pady=3)

    def create_gap_inputs(self):
        gap_frame = ttk.LabelFrame(self.main_frame, text="Position Gaps", padding="10")
        gap_frame.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=10, padx=5)

        self.gap_x = tk.StringVar(value="50")
        self.gap_y = tk.StringVar(value="70")

        ttk.Label(gap_frame, text="Horizontal gap (gap_x):").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(gap_frame, textvariable=self.gap_x, width=5).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(gap_frame, text="Vertical gap (gap_y):").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(gap_frame, textvariable=self.gap_y, width=5).grid(row=1, column=1, padx=5, pady=5)

    def create_lua_background_option(self):
        self.load_lua_bg = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self.main_frame,
            text="Load background image with Lua? (Use only with full Conky!!)",
            variable=self.load_lua_bg
        ).grid(row=5, column=1, sticky=tk.W, pady=10, padx=5)

    def create_border_options(self):
        border_frame = ttk.LabelFrame(self.main_frame, text="Border Options", padding="10")
        border_frame.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=10, padx=5)

        self.draw_borders = tk.BooleanVar(value=False)
        self.own_window_transparent = tk.BooleanVar(value=False)
        self.draw_shades = tk.BooleanVar(value=False)
        self.draw_outline = tk.BooleanVar(value=False)

        ttk.Checkbutton(border_frame, text="Draw borders around the window?", variable=self.draw_borders).grid(row=0, column=0, sticky=tk.W, pady=3)
        ttk.Checkbutton(border_frame, text="Make the window transparent?", variable=self.own_window_transparent).grid(row=1, column=0, sticky=tk.W, pady=3)
        ttk.Checkbutton(border_frame, text="Draw shadow on the font?", variable=self.draw_shades).grid(row=2, column=0, sticky=tk.W, pady=3)
        ttk.Checkbutton(border_frame, text="Draw outline on the font?", variable=self.draw_outline).grid(row=3, column=0, sticky=tk.W, pady=3)

    def get_conky_filename(self, base="conky.conf"):
        if not os.path.exists(base):
            return base
        if messagebox.askyesno("File Exists", f"File '{base}' already exists. Overwrite?"):
            return base
        i = 2
        while True:
            fname = f"conky{i}.conf"
            if not os.path.exists(fname):
                return fname
            i += 1

    def generate_config(self):
        self.status_label.config(text="Generating...")
        self.generate_button.configure(state='disabled')
        self.root.update()

        self.config_options = {
            "alignment": self.alignment.get(),
            "gap_x": int(self.gap_x.get()) if self.gap_x.get().isdigit() else 50,
            "gap_y": int(self.gap_y.get()) if self.gap_y.get().isdigit() else 70,
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
            "own_window_transparent": self.own_window_transparent.get(),
            "own_window_argb_visual": True,
            "own_window_argb_value": 210,
            "own_window_colour": self.colors["background_color"].get(),
            "own_window_hints": "undecorated,below,sticky,skip_taskbar,skip_pager",
            "draw_borders": self.draw_borders.get(),
            "border_width": 8,
            "border_inner_margin": 9,
            "draw_graph_borders": True,
            "default_shade_color": "black",
            "draw_shades": self.draw_shades.get(),
            "draw_outline": self.draw_outline.get(),
            "default_color": self.colors["border_color"].get(),
            "color1": self.colors["color1"].get(),
            "color2": self.colors["color2"].get(),
            "color3": self.colors["color3"].get(),
            "color4": self.colors["color4"].get(),
        }

        if self.load_lua_bg.get():
            self.config_options["lua_load"] = 'assets/image.lua'
            self.config_options["lua_draw_hook_pre"] = 'conky_draw_image'

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
        for key, value in self.config_options.items():
            if isinstance(value, bool):
                lines.append(f"    {key} = {str(value).lower()},")
            elif isinstance(value, str):
                lines.append(f"    {key} = '{value}',")
            else:
                lines.append(f"    {key} = {value},")
        lines.append("}\n")
        lines.append("conky.text = [[")

        if self.options["sysinfo"].get():
            if self.distro == "fedora":
                lines.append("${font Dejavu Sans Mono:bold:size=22}${alignc}${color1}${execi 10000 lsb_release -d | awk '{print $2, $3, $4}'}${color}${font}")
            else:
                lines.append("${font Dejavu Sans Mono:bold:size=22}${alignc}${color1}${execi 10000 lsb_release -d | cut -f 2}${color}${font}")
            lines.append("${color4}${voffset 0}${alignc}${sysname} ${kernel}")
            lines.append("${alignc}Uptime: ${uptime}")
            lines.append("${alignc}${execi 6000 cat /proc/cpuinfo | grep -i 'Model name' -m 1 | cut -c14-40}")

        if self.options["cpu"].get():
            lines.append("${color3}${voffset 0}${alignc}${font Dejavu Sans Mono:bold:size=10}CPU: ${execi 5 sensors|grep 'Package'|awk '{print $4}'} ${cpu cpu0}% ${font}")
            lines.append("${alignc}${voffset 0}${color2}${cpubar cpu0 10,230}")
            lines.append("${alignc}${voffset 5}${cpugraph 30,230 5294E2 FF2021}")

        if self.options["memory"].get():
            lines.append("${color3}${voffset 0}${alignc}Memory:")
            lines.append("${voffset -10}${goto 36}Used:${alignr 15}Free:")
            lines.append("${goto 36}${mem}${alignr 15} ${memeasyfree}")
            lines.append("${alignc}${voffset 0}${color2}${membar 10,230}${color}")

        if self.options["disk"].get():
            lines.append("${color3}${voffset 3}${alignc}${font Dejavu Sans Mono:bold:size=10}Disks${font}")
            lines.append("${voffset -10}${color3}${goto 36}Used: ${alignr 15}Free:")
            lines.append("${color3}${goto 36}${fs_used /}${alignc -30}ROOT${alignr 15}${fs_free /}")
            lines.append("${alignc}${voffset 0}${color2}${fs_bar 10,230 /}${color}")
            lines.append("${color3}${goto 36}${fs_used /home/}${alignc -30}Home${alignr 15}${fs_free /home}")
            lines.append("${alignc}${voffset 0}${color2}${fs_bar 10,230 /home}${color}")

        if self.options["network"].get():
            lines.append("${color3}${alignc}${voffset 1}${font Dejavu Sans Mono:bold:size=10}Network speed${font}")
            lines.append(f"${{color3}}${{goto 36}}${{voffset -3}}Up: ${{upspeed {self.net_interface}}}${{alignr 15}}Down: ${{downspeed {self.net_interface}}}")
            lines.append(f"${{color2}}${{goto 36}}${{voffset -3}}${{upspeedgraph {self.net_interface} 30,100 5294E2 42E147 3900}}${{alignr 15}}${{downspeedgraph {self.net_interface} 30,100 5294E2 42E147 32000}}${{color}}")
            lines.append("${color3}${goto 36}${voffset -8}Total up${alignr 15}Total down")
            lines.append(f"${{color3}}${{goto 36}}${{totalup {self.net_interface}}}${{alignr 15}}${{totaldown {self.net_interface}}}")

        if self.options["processes"].get():
            lines.append("${color3}${voffset -5}${alignc}${font Dejavu Sans Mono:bold:size=10}Processes${font}")
            for i in range(1, 7):
                lines.append(f"${{goto 36}}${{top name {i}}}${{alignr 15}}${{top cpu {i}}}%")

        if self.options["updates"].get():
            lines.append("${color4}${voffset 10}${alignc}${font Dejavu Sans Mono:bold:size=10}Updates${font}")
            lines.append("${alignc}${execi 1000 assets/check_updates.sh}")

        if self.options["time"].get():
            lines.append("${voffset 10}${color1}${alignc}${font Dejavu Sans Mono:bold:size=10}Date & Time${font}")
            lines.append("${alignc}${time %A, %d %B}")
            lines.append("${alignc}${font Dejavu Sans Mono:bold:size=11}${time %H:%M}${font}")
            if self.load_lua_bg.get():
                lines.append("${voffset -5}")
            else:
                lines.append("${voffset -25}")

        lines.append("]]")

        filename = self.get_conky_filename("conky.conf")
        with open(filename, "w") as f:
            f.write('\n'.join(lines))

        self.status_label.config(text="")
        self.generate_button.configure(state='normal')
        messagebox.showinfo("Success", f"{filename} has been generated in this folder! (Re)start Conky to see the changes.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ConkyGeneratorApp(root)
    root.mainloop()