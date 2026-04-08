import customtkinter as ctk
import tkinter as tk
from can_handler import RealCANBus as CANSim  

ctk.set_appearance_mode("dark")

class CircularGauge(ctk.CTkFrame):
    def __init__(self, master, radius, min_val, max_val, units, title, color, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.min_val = min_val
        self.max_val = max_val
        self.color = color
        
        self.title_lbl = ctk.CTkLabel(self, text=title, text_color="#AAAAAA", font=("Montserrat", 14))
        self.title_lbl.pack(pady=(0, 5))
        
        self.canvas = tk.Canvas(self, width=radius*2, height=radius*2, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack()
        
        # Upward curving arcs
        self.canvas.create_arc(10, 10, radius*2-10, radius*2-10, start=-45, extent=270, style=tk.ARC, width=10, outline="#333333")
        self.arc_id = self.canvas.create_arc(10, 10, radius*2-10, radius*2-10, start=225, extent=0, style=tk.ARC, width=10, outline=color)
        
        self.val_lbl = ctk.CTkLabel(self, text="0", text_color=color, font=("Montserrat", 36, "bold"))
        self.val_lbl.place(relx=0.5, rely=0.5, anchor="center")
        
        self.unit_lbl = ctk.CTkLabel(self, text=units, text_color="#FFFFFF", font=("Montserrat", 16))
        self.unit_lbl.place(relx=0.5, rely=0.75, anchor="center")

    def set_value(self, val):
        val = max(self.min_val, min(self.max_val, val))
        self.val_lbl.configure(text=str(int(val)))
        percent = (val - self.min_val) / (self.max_val - self.min_val)
        angle = int(270 * percent)  
        self.canvas.itemconfigure(self.arc_id, extent=-angle)

class GoKartDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Senior Design Dashboard")
        self.geometry("800x480") 
        self.configure(fg_color="#1a1a1a")
        
        self.can_bus = CANSim()
        self.sim_running = False

        self.setup_ui()
        self.reset_dashboard()

    def setup_ui(self):
        # 1. Gauges
        self.gauge_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.gauge_frame.pack(pady=20, fill="x")
        
        self.speed_gauge = CircularGauge(self.gauge_frame, radius=70, min_val=0, max_val=140, units="km/h", title="SPEED", color="#00DD00")
        self.speed_gauge.pack(side="left", expand=True)

        self.rpm_gauge = CircularGauge(self.gauge_frame, radius=70, min_val=0, max_val=8000, units="RPM", title="ENGINE", color="#FF5555")
        self.rpm_gauge.pack(side="left", expand=True)

        self.battery_gauge = CircularGauge(self.gauge_frame, radius=70, min_val=0, max_val=100, units="%", title="BATTERY", color="#00AADD")
        self.battery_gauge.pack(side="left", expand=True)

        # 2. Main Info (Gear & Temp)
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.pack(fill="x", pady=5)

        self.gear_lbl = ctk.CTkLabel(self.info_frame, text="GEAR: N", font=("Montserrat", 36, "bold"))
        self.gear_lbl.pack(side="left", expand=True)

        self.temp_lbl = ctk.CTkLabel(self.info_frame, text="TEMP: -- °C", font=("Montserrat", 32, "bold"))
        self.temp_lbl.pack(side="right", expand=True)

        # 3. DIAGNOSTIC CENTER (New)
        self.diag_frame = ctk.CTkFrame(self, fg_color="#222222", border_width=2, border_color="#444444", corner_radius=10)
        self.diag_frame.pack(pady=15, padx=50, fill="x")
        
        # Check Engine Light (Drawn on a small canvas)
        self.cel_canvas = tk.Canvas(self.diag_frame, width=40, height=40, bg="#222222", highlightthickness=0)
        self.cel_canvas.pack(side="left", padx=20, pady=10)
        self.cel_light = self.cel_canvas.create_oval(5, 5, 35, 35, fill="#330000", outline="#550000", width=2)
        
        # Warning Message Text
        self.warning_lbl = ctk.CTkLabel(self.diag_frame, text="SYSTEM NOMINAL", font=("Montserrat", 20, "bold"), text_color="#00DD00")
        self.warning_lbl.pack(side="left", pady=10)

        # 4. Controls
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.pack(pady=10)

        self.start_btn = ctk.CTkButton(self.controls_frame, text="START SIM", fg_color="#00DD00", hover_color="#00AA00", text_color="black", command=self.toggle_sim)
        self.start_btn.pack(side="left", padx=10)

        self.reset_btn = ctk.CTkButton(self.controls_frame, text="RESET", fg_color="#555555", hover_color="#777777", text_color="white", command=self.reset_dashboard)
        self.reset_btn.pack(side="left", padx=10)

    def set_diagnostics(self, temp, battery):
        """Evaluates SAE parameters and triggers warnings"""
        high_temp = temp > 90
        low_bat = battery < 20
        
        if high_temp and low_bat:
            self.cel_canvas.itemconfigure(self.cel_light, fill="#FF0000", outline="#FFAA00")
            self.warning_lbl.configure(text="CRITICAL: TEMP & BATTERY", text_color="#FF0000")
            self.diag_frame.configure(border_color="#FF0000")
        elif high_temp:
            self.cel_canvas.itemconfigure(self.cel_light, fill="#FF0000", outline="#FFAA00")
            self.warning_lbl.configure(text="CRITICAL: HIGH TEMP", text_color="#FF0000")
            self.diag_frame.configure(border_color="#FF0000")
        elif low_bat:
            self.cel_canvas.itemconfigure(self.cel_light, fill="#FFAA00", outline="#FFFF00") # Yellow for battery
            self.warning_lbl.configure(text="WARNING: LOW BATTERY", text_color="#FFAA00")
            self.diag_frame.configure(border_color="#FFAA00")
        else:
            self.cel_canvas.itemconfigure(self.cel_light, fill="#330000", outline="#550000")
            self.warning_lbl.configure(text="SYSTEM NOMINAL", text_color="#00DD00")
            self.diag_frame.configure(border_color="#444444")

    def toggle_sim(self):
        self.sim_running = not self.sim_running
        if self.sim_running:
            self.start_btn.configure(text="STOP SIM", fg_color="#FF5555", hover_color="#AA0000", text_color="white")
            self.update_loop() 
        else:
            self.start_btn.configure(text="START SIM", fg_color="#00DD00", hover_color="#00AA00", text_color="black")

    def reset_dashboard(self):
        if self.sim_running:
            self.toggle_sim()
            
        self.speed_gauge.set_value(0)
        self.rpm_gauge.set_value(3000)
        self.battery_gauge.set_value(75)
        self.gear_lbl.configure(text="GEAR: N")
        self.temp_lbl.configure(text="TEMP: 70.0 °C", text_color="#FFFFFF")
        self.set_diagnostics(70, 75) # Reset to nominal

    def update_loop(self):
        if self.sim_running:
            data = self.can_bus.read()
            
            self.speed_gauge.set_value(data["speed"])
            self.rpm_gauge.set_value(data["rpm"])
            self.battery_gauge.set_value(data["battery"])
            self.gear_lbl.configure(text=f"GEAR: {data['gear']}")
            self.temp_lbl.configure(text=f"TEMP: {data['temp']:.1f} °C")
            
            # Call the new diagnostic evaluator
            self.set_diagnostics(data["temp"], data["battery"])

            self.after(33, self.update_loop)

if __name__ == "__main__":
    app = GoKartDashboard()
    app.mainloop()