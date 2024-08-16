from FaseBulan_back import *
import datetime
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.widgets import DateEntry

#===== COMMAND FUNCTION =====#
def update_command(time):
    time_str.set(value = time)
    
    time_label.configure(text = time_str.get()[0:10]+"\n"+time_str.get()[11:16]+" UTC+0")
    
    Year    = int(time_str.get()[6:10])
    Month   = int(time_str.get()[3:5])
    Day     = int(time_str.get()[0:2])
    Hour    = int(time_str.get()[11:13])
    Minute  = int(time_str.get()[-2])

    JD = DtoJD(Day, Month, Year, Hour, Minute)
    R0, _alpha0, _delta0, _lambda0, _beta0 = SolarPos(JD)
    _Delta, _alpha, _delta, _lambda, _beta = LunarPos(JD)

    _alpha_inhours = [int(_alpha/15), int((_alpha/15-int(_alpha/15))*60),(((_alpha/15-int(_alpha/15))*60)-int((_alpha/15-int(_alpha/15))*60))*60]
    _delta_inhours = [int(_delta), int((_delta-int(_delta))*60),(((_delta-int(_delta))*60)-int((_delta-int(_delta))*60))*60]

    lunarillum = LunarIllum(JD)*100         #dalam persen

    YearFrac = (Year + (Month-1+(Day-1)/30.5)/12)
    k = (YearFrac - 2000)*12.3685
    p = int(abs(k-int(k))/0.25)*0.25        #round down desimal k ke kelipatan 0.25

    ki = []
    for i in np.arange(-1, 1.25, 0.25):
        ki.append(int(k)+p+i)

    JDi = []
    for i in ki:
        JDi.append(JDLunarPhase(i))

    JDki = []
    for i in JDi:
        JDki.append(i-JD)

    j = 0
    while True:
        if JDki[j] > 0:
            JDNext = JDi[j]
            JDNext2 = JDi[j+1]
            JDPrev = JDi[j-1]
            JDPrev2 = JDi[j-2]

            StateNext  = CheckState(ki[j])
            StateNext2 = CheckState(ki[j+1])
            StatePrev  = CheckState(ki[j-1])
            StatePrev2 = CheckState(ki[j-2])
            break
        else:
            j = j + 1

    if StatePrev == "New Moon":
        lunarphase = "Waxing Crescent"
    elif StatePrev == "First Quarter":
        lunarphase = "Waxing Gibbous"
    elif StatePrev == "Full Moon":
        lunarphase = "Waning Gibbous"
    elif StatePrev == "Third Quarter":
        lunarphase = "Waning Crescent"

    knew = int(k)+2
    JDnew = JDLunarPhase(knew)
    while JDnew > JD:
        knew = knew -1
        JDnew = JDLunarPhase(knew)
    dJD = JD - JDnew


    JD_label.configure(text="{:.2f}".format(JD))
    Illum_label.configure(text=f"{lunarillum:.2f}"+"%")
    Distance_label.configure(text="{:.2f} km".format(_Delta))
    RA_label.configure(text="{}h {}m {:.2f}s".format(_alpha_inhours[0], _alpha_inhours[1], _alpha_inhours[2]))
    Declin_label.configure(text=str(_delta_inhours[0])+u"\N{DEGREE SIGN}"+''' {}' {}" '''.format(_delta_inhours[1], round(_delta_inhours[2])))
        
    mooncode_p2, mooncode_p, mooncode_n, mooncode_n2 = state_mooncode(StatePrev)
    p2_img = ImageTk.PhotoImage(Image.open('MoonGallery/moon.'+ mooncode_p2 +'.jpg').resize((140, 140)))
    p2_moon.configure(image=p2_img)
    p2_moon.image = p2_img
    p_img = ImageTk.PhotoImage(Image.open('MoonGallery/moon.'+ mooncode_p +'.jpg').resize((140, 140)))
    p_moon.configure(image=p_img)
    p_moon.image = p_img
    n_img = ImageTk.PhotoImage(Image.open('MoonGallery/moon.'+ mooncode_n +'.jpg').resize((140, 140)))
    n_moon.configure(image=n_img)
    n_moon.image = n_img
    n2_img = ImageTk.PhotoImage(Image.open('MoonGallery/moon.'+ mooncode_n2 +'.jpg').resize((140, 140)))
    n2_moon.configure(image=n2_img)
    n2_moon.image = n2_img

    p2_label.configure(text=StatePrev2)
    p_label.configure(text=StatePrev)
    n_label.configure(text=StateNext)
    n2_label.configure(text=StateNext2)

    p2_date = "{}/{}/{} {}:{}".format(str(JDtoD(JDPrev2)[0]), str(JDtoD(JDPrev2)[1]), str(JDtoD(JDPrev2)[2]), str(JDtoD(JDPrev2)[3]), 
                                  str(JDtoD(JDPrev2)[4]), str(JDtoD(JDPrev2)[0]))
    p_date = "{}/{}/{} {}:{}".format(str(JDtoD(JDPrev)[0]), str(JDtoD(JDPrev)[1]), str(JDtoD(JDPrev)[2]), str(JDtoD(JDPrev)[3]), 
                                    str(JDtoD(JDPrev)[4]), str(JDtoD(JDPrev)[0]))
    n_date = "{}/{}/{} {}:{}".format(str(JDtoD(JDNext)[0]), str(JDtoD(JDNext)[1]), str(JDtoD(JDNext)[2]), str(JDtoD(JDNext)[3]), 
                                    str(JDtoD(JDNext)[4]), str(JDtoD(JDNext)[0]))
    n2_date = "{}/{}/{} {}:{}".format(str(JDtoD(JDNext2)[0]), str(JDtoD(JDNext2)[1]), str(JDtoD(JDNext2)[2]), str(JDtoD(JDNext2)[3]), 
                                    str(JDtoD(JDNext2)[4]), str(JDtoD(JDNext2)[0]))

    p2_date_label.configure(text=p2_date)
    p_date_label.configure(text=p_date)
    n_date_label.configure(text=n_date)
    n2_date_label.configure(text=n2_date)

    mooncode = phase_mooncode(lunarphase, lunarillum)
    moon_img = ImageTk.PhotoImage(Image.open('MoonGallery/moon.'+ mooncode +'.jpg').resize((310,310)))
    main_moon.configure(image=moon_img)
    main_moon.image = moon_img

    phase_label.configure(text=lunarphase)
    newmoon_label.configure(text="{:.2f} days from the last new moon".format(dJD))

def input_command():
    raw_time = datetime.datetime.strptime(calendar.entry.get(), '%m/%d/%Y')
    input_time = raw_time.strftime("%d/%m/%Y") +" "+hour_str.get()+':'+minute_str.get()
    current_bool.set(value=False)
    current_rb.configure(variable=current_bool)
    update_command(input_time)

def current_command():    
    current_time = datetime.datetime.now(datetime.timezone.utc).strftime("%d/%m/%Y %H:%M")
    update_command(current_time)
    
    # while current_bool.get() == True:
    #     window.after(60000, current_command)

def show_info():
    messagebox.showinfo('About This App', "This application was developed as a project assignment for Computational Astronomy course.\n"+ 
                        "Department of Physics, Brawijaya University, 2023.\n"+
                        "\nAlgorithm Reference:\n"+
                        "   Duffett-Smith, P. (1988). Practical Astronomy with Your Calculator,\n"+
                        "       3rd ed.\n"+
                        "   Meeus, J.H. (1998). Astronomical Algorithms, 2nd ed.\n"+
                        "\nMoon Image Source:\n"+
                        "   NASA Scientific Visualization Studio (File ID 4874)" +
                        "   https://svs.gsfc.nasa.gov/vis/a000000/a004800/a004874/frames/730x730_1x1_30p/\n"+
                        "\nProgrammer: Christopher Limuel\nSupervisor: Dr.rer.nat. Abdurrouf, S.Si, M.Si.\n"
                        "\nThe lunar phases generated here are based on geocentric coordinates (as observed from the center of the Earth).\n"+
                        "All times are indicated in the UTC+0 time zone.")


#===== WINDOW =====#
window = ttk.Window(themename = 'superhero')
window.title('Fase Bulan')
window.geometry('1080x720')
window.resizable(0,0)

#===== MAIN FRAME =====#
visual_frame = ttk.Frame(window)
input_frame  = ttk.Frame(window)

visual_frame.place(relx=0, rely=0, relwidth=1, relheight=0.8)
input_frame.place(relx = 0, rely=0.78, relwidth=1, relheight=0.2)

ttk.Label(visual_frame, background='black').pack(expand=True, fill="both")

#===== INPUT FRAME =====#
#----- TIME INPUT -----#
calendar = DateEntry(input_frame)

hour_list = ["%.0f" % i for i in np.arange(24)]
for i in range(len(hour_list)):
    if len(hour_list[i]) < 2:
        hour_list[i] = '0' + hour_list[i]
hour_str = tk.StringVar(value = hour_list[0])
hour_cmb = ttk.Combobox(input_frame, textvariable = hour_str, width=2)
hour_cmb['values'] = hour_list

minute_list = ["%.0f" % i for i in np.arange(60)]
for i in range(len(minute_list)):
    if len(minute_list[i]) < 2:
        minute_list[i] = '0' + minute_list[i]
minute_str = tk.StringVar(value = minute_list[0])
minute_cmb = ttk.Combobox(input_frame, textvariable = minute_str, width=2)
minute_cmb['values'] = minute_list

raw_time = datetime.datetime.strptime(calendar.entry.get(), '%m/%d/%Y')
input_time = raw_time.strftime("%d/%m/%Y") +" "+hour_str.get()+':'+minute_str.get()
time_str = tk.StringVar(value = input_time)

main_button = ttk.Button(input_frame, command = input_command, text = "Set Time")
time_label = ttk.Label(input_frame, text = time_str.get()[0:10]+"\n"+time_str.get()[11:16] + " UTC+0",
                       font=("Montserrat Bold", 22))
info_frame=ttk.Frame(input_frame)
info_frame.columnconfigure(0)
info_frame.rowconfigure(0)
info_frame.place(relx=0.98, rely=0.85, anchor='e')
info_button=ttk.Button(info_frame, command=show_info, text='i').grid(row=0, column=0,ipady=0.01, ipadx=0.01)

time_label.place(relx=0.02, rely=0.5, anchor='w')
calendar.place(relx=0.86, rely=0.26, anchor='e')
hour_cmb.place(relx=0.92, rely=0.26, anchor='e')
ttk.Label(input_frame, text=":").place(relx=0.9315, rely=0.26, anchor='e')
minute_cmb.place(relx=0.98, rely=0.26, anchor='e')
main_button.place(relx=0.98, rely=0.60, relwidth=0.313, anchor='e')

#----- CURRENT TIME -----#
current_time = datetime.datetime.now(datetime.timezone.utc).strftime("%d/%m/%Y %H:%M")

current_bool = tk.BooleanVar()
current_rb = ttk.Radiobutton(input_frame, variable=current_bool, text="Current Time", command=current_command)

current_rb.place(relx=0.667, rely=0.8)

#===== CALCULATION =====#
Year    = int(time_str.get()[6:10])
Month   = int(time_str.get()[3:5])
Day     = int(time_str.get()[0:2])
Hour    = int(time_str.get()[11:13])
Minute  = int(time_str.get()[-2])

JD = DtoJD(Day, Month, Year, Hour, Minute)
R0, _alpha0, _delta0, _lambda0, _beta0 = SolarPos(JD)
_Delta, _alpha, _delta, _lambda, _beta = LunarPos(JD)

_alpha_inhours = [int(_alpha/15), int((_alpha/15-int(_alpha/15))*60),(((_alpha/15-int(_alpha/15))*60)-int((_alpha/15-int(_alpha/15))*60))*60]
_delta_inhours = [int(_delta), int((_delta-int(_delta))*60),(((_delta-int(_delta))*60)-int((_delta-int(_delta))*60))*60]

lunarillum = LunarIllum(JD)*100         #dalam persen

YearFrac = (Year + (Month-1+(Day-1)/30.5)/12)
k = (YearFrac - 2000)*12.3685
p = int(abs(k-int(k))/0.25)*0.25        #round down desimal k ke kelipatan 0.25

# JD fase sebelumnya
def CheckState(k):
    if abs(k-int(k)) == 0:
        State = "New Moon"
    elif abs(k-int(k)) == 0.25:
        State = "First Quarter"
    elif abs(k-int(k)) == 0.5:
        State = "Full Moon"
    elif abs(k-int(k)) == 0.75:
        State = "Third Quarter"
    return State

ki = []
for i in np.arange(-1, 1.25, 0.25):
  ki.append(int(k)+p+i)

JDi = []
for i in ki:
  JDi.append(JDLunarPhase(i))

JDki = []
for i in JDi:
  JDki.append(i-JD)

j = 0
while True:
  if JDki[j] > 0:
    JDNext = JDi[j]
    JDNext2 = JDi[j+1]
    JDPrev = JDi[j-1]
    JDPrev2 = JDi[j-2]

    StateNext  = CheckState(ki[j])
    StateNext2 = CheckState(ki[j+1])
    StatePrev  = CheckState(ki[j-1])
    StatePrev2 = CheckState(ki[j-2])
    break
  else:
    j = j + 1

if StatePrev == "New Moon":
    lunarphase = "Waxing Crescent"
elif StatePrev == "First Quarter":
    lunarphase = "Waxing Gibbous"
elif StatePrev == "Full Moon":
    lunarphase = "Waning Gibbous"
elif StatePrev == "Third Quarter":
    lunarphase = "Waning Crescent"

knew = int(k)+2
JDnew = JDLunarPhase(knew)
while JDnew > JD:
    knew = knew -1
    JDnew = JDLunarPhase(knew)
dJD = JD - JDnew

#----- DETAILS -----#
left_frame = ttk.Frame(visual_frame)
left_frame.place(relx=0.02, rely=0.7, relheight=0.24, relwidth=0.25)
left_frame.rowconfigure((0, 1, 2, 3, 4), weight=1)
left_frame.columnconfigure(0, weight=1)
left_frame.columnconfigure(1, weight=7)

ttk.Label(left_frame, background='black').grid(row=0, column=0, rowspan=5, columnspan=2, sticky='nswe')

JD_title = ttk.Label(left_frame, text="JD", font=("Montserrat Semibold",10), background='black')
Illum_title = ttk.Label(left_frame, text="Illumination", font=("Montserrat Semibold",10), background='black')
Distance_title = ttk.Label(left_frame, text="Distance", font=("Montserrat Semibold",10), background='black')
RA_title = ttk.Label(left_frame, text="Right Asc.",font=("Montserrat Semibold",10), background='black')
Declin_title = ttk.Label(left_frame, text="Declination",font=("Montserrat Semibold",10), background='black')

JD_label = ttk.Label(left_frame, text="{:.2f}".format(JD), font=("Biko",10), background='black')
Illum_label = ttk.Label(left_frame, text=f"{lunarillum:.2f}"+"%", font=("Biko",10), background='black')
Distance_label = ttk.Label(left_frame, text="{:.2f} km".format(_Delta), font=("Biko",10), background='black')
RA_label = ttk.Label(left_frame, text="{}h {}m {:.2f}s".format(_alpha_inhours[0], _alpha_inhours[1], _alpha_inhours[2]),
                      font=("Biko",10), background='black')
Declin_label = ttk.Label(left_frame, text=str(_delta_inhours[0])+u"\N{DEGREE SIGN}"+''' {}' {}"'''.format(_delta_inhours[1], round(_delta_inhours[2])),
                         font=("Biko",10), background='black')

JD_title.grid(row=0, column=0, sticky='w')
JD_label.grid(row=0, column=1, sticky='w')
Illum_title.grid(row=1, column=0, sticky='w')
Illum_label.grid(row=1, column=1, sticky='w')
Distance_title.grid(row=2, column=0, sticky='w')
Distance_label.grid(row=2, column=1, sticky='w')
RA_title.grid(row=3, column=0, sticky='w')
RA_label.grid(row=3, column=1, sticky='w')
Declin_title.grid(row=4, column=0, sticky='w')
Declin_label.grid(row=4, column=1, sticky='w')
#----- PREV/NEXT STATE -----#

state_frame=tk.Frame(visual_frame)
state_frame.place(relx = 0, rely=0.15, relheight=0.4, relwidth=1)
state_frame.columnconfigure((0, 1, 3, 4), weight=2)
state_frame.columnconfigure(2, weight=17)
state_frame.rowconfigure(0, weight=3)
state_frame.rowconfigure((1, 2), weight=3)

ttk.Label(state_frame, background='black').grid(row=0, column=0, rowspan=3, columnspan=5, sticky='nswe')

def state_mooncode(StatePrev):
    if StatePrev == "New Moon":
        mooncode_p2 = '0835'
        mooncode_p = '1004'
        mooncode_n = '1195'
        mooncode_n2 = '0668'
    elif StatePrev == "First Quarter":
        mooncode_p2 = '1004'
        mooncode_p = '1195'
        mooncode_n = '0668'
        mooncode_n2 = '0835'
    elif StatePrev == "Full Moon":
        mooncode_p2 = '1195'
        mooncode_p = '0668'
        mooncode_n = '0835'
        mooncode_n2 = '1004'
    elif StatePrev == "Third Quarter":
        mooncode_p2 = '0668'
        mooncode_p = '0835'
        mooncode_n = '1004'
        mooncode_n2 = '1195'
    return mooncode_p2, mooncode_p, mooncode_n, mooncode_n2

mooncode_p2, mooncode_p, mooncode_n, mooncode_n2 = state_mooncode(StatePrev)
p2_img = ImageTk.PhotoImage(Image.open('MoonGallery/moon.'+ mooncode_p2 +'.jpg').resize((140, 140)))
p2_moon = ttk.Label(state_frame, image=p2_img, borderwidth=0)
p_img = ImageTk.PhotoImage(Image.open('MoonGallery/moon.'+ mooncode_p +'.jpg').resize((140, 140)))
p_moon = ttk.Label(state_frame, image=p_img, borderwidth=0)
n_img = ImageTk.PhotoImage(Image.open('MoonGallery/moon.'+ mooncode_n +'.jpg').resize((140, 140)))
n_moon = ttk.Label(state_frame, image=n_img, borderwidth=0)
n2_img = ImageTk.PhotoImage(Image.open('MoonGallery/moon.'+ mooncode_n2 +'.jpg').resize((140, 140)))
n2_moon = ttk.Label(state_frame, image=n2_img, borderwidth=0)

p2_moon.grid(row=0, column=0)
p_moon.grid(row=0, column=1)
n_moon.grid(row=0, column=3)
n2_moon.grid(row=0, column=4)

p2_label = ttk.Label(state_frame, text=StatePrev2, font=('Montserrat',14), background='black')
p_label = ttk.Label(state_frame, text=StatePrev, font=('Montserrat',14), background='black')
n_label = ttk.Label(state_frame, text=StateNext, font=('Montserrat',14), background='black')
n2_label = ttk.Label(state_frame, text=StateNext2, font=('Montserrat',14), background='black')

p2_label.grid(row=1, column=0, sticky='n')
p_label.grid(row=1, column=1, sticky='n')
n_label.grid(row=1, column=3, sticky='n')
n2_label.grid(row=1, column=4, sticky='n')

p2_date = "{}/{}/{} {}:{}".format(str(JDtoD(JDPrev2)[0]), str(JDtoD(JDPrev2)[1]), str(JDtoD(JDPrev2)[2]), str(JDtoD(JDPrev2)[3]), 
                                  str(JDtoD(JDPrev2)[4]), str(JDtoD(JDPrev2)[0]))
p_date = "{}/{}/{} {}:{}".format(str(JDtoD(JDPrev)[0]), str(JDtoD(JDPrev)[1]), str(JDtoD(JDPrev)[2]), str(JDtoD(JDPrev)[3]), 
                                 str(JDtoD(JDPrev)[4]), str(JDtoD(JDPrev)[0]))
n_date = "{}/{}/{} {}:{}".format(str(JDtoD(JDNext)[0]), str(JDtoD(JDNext)[1]), str(JDtoD(JDNext)[2]), str(JDtoD(JDNext)[3]), 
                                 str(JDtoD(JDNext)[4]), str(JDtoD(JDNext)[0]))
n2_date = "{}/{}/{} {}:{}".format(str(JDtoD(JDNext2)[0]), str(JDtoD(JDNext2)[1]), str(JDtoD(JDNext2)[2]), str(JDtoD(JDNext2)[3]), 
                                  str(JDtoD(JDNext2)[4]), str(JDtoD(JDNext2)[0]))

p2_date_label = ttk.Label(state_frame, text=p2_date, font=("Biko",12), background='black')
p_date_label = ttk.Label(state_frame, text=p_date, font=("Biko",12), background='black')
n_date_label = ttk.Label(state_frame, text=n_date, font=("Biko",12), background='black')
n2_date_label = ttk.Label(state_frame, text=n2_date, font=("Biko",12), background='black')

p2_date_label.grid(row=2, column=0, sticky='n')
p_date_label.grid(row=2, column=1, sticky='n')
n_date_label.grid(row=2, column=3, sticky='n')
n2_date_label.grid(row=2, column=4, sticky='n')

#----- MAIN IMAGE -----#
def phase_mooncode(lunarphase, lunarillum):
    if lunarillum < 50:
        if lunarphase == "Waxing Crescent":
            mooncode = str(round((1195-1004)/50*(lunarillum-0))+1004)
        elif lunarphase =="Waning Crescent":
            mooncode = str(round((1004-835)/50*(50-lunarillum))+835)
    elif lunarillum >=50:
        if lunarphase == "Waxing Gibbous":
            mooncode = str(round((1376-1195)/50*(lunarillum-50))+1195)
        elif lunarphase == "Waning Gibbous":
            mooncode = str(round((835-668)/50*(100-lunarillum))+668)
    if len(mooncode) < 4:
        mooncode = '0' + mooncode
    return mooncode
mooncode = phase_mooncode(lunarphase, lunarillum)
moon_img = ImageTk.PhotoImage(Image.open('MoonGallery/moon.'+ mooncode +'.jpg').resize((310,310)))
main_moon = ttk.Label(visual_frame, image=moon_img, borderwidth=0)
main_moon.place(relx = 0.5, rely = 0.62, anchor='s')

phase_label = ttk.Label(visual_frame, text=lunarphase, font=('Montserrat Extrabold', 26), background='black')
phase_label.place(relx=0.5, rely=0.73, anchor='n')
ttk.Label(visual_frame, text="Current Phase", font=('Biko', 18), background='black').place(relx=0.5, rely=0.68, anchor='n')
newmoon_label = ttk.Label(visual_frame, text="{:.2f} days from the last new moon".format(dJD),
                        background='black', font=('Biko', 14))
newmoon_label.place(relx=0.5, rely=0.85, anchor='n')

#===== RUN =====#
window.iconbitmap("FaseBulan_logo.ico")
window.mainloop()