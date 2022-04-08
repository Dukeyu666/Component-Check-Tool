import tkinter as tk
from tkinter import Scrollbar, messagebox,filedialog
from tkinter.font import Font
import tkinter.ttk as ttk
import re
from dbconnect import Dbconnect
import os
from datetime import datetime
import read_pml,threading


def do_query(func,component=None,server=None):
    try:
        connector=Dbconnect(server)
        connector.connector()
    except Exception as e:
        messagebox.showerror("error",e.args[1])
        return
    for i in treeview.get_children():
        #print(i)
        treeview.delete(i)
    current_time=datetime.now().strftime("%Y%m%d%H%M%S")
    if func == 'skunumber':
        result=connector.ready_chk(component)
        #print(result)
        if result == None:
            messagebox.showinfo("Info","{0} is being synchronized.".format(component))
            return
        elif result[0] == 'EOL':
            messagebox.showinfo("Info","{0} is EOL.".format(component))
            return
        elif 'not' not in result[0]:
            treeview.insert("",text=result[0],index="end",values=[result[0],result[1],result[2].strftime("%Y-%m-%d %H:%M:%S"),result[3].strftime("%Y-%m-%d %H:%M:%S")])
            messagebox.showinfo("Info","{0} Ready to DASH.".format(component))
            return
        else:
            messagebox.showinfo("Info","{0} not exist in the server.".format(component))
            return

    elif func == 'ML':
        result=connector.ML_chk(component)
        if result != None:
            with open(file=".//Results//{0}//{1}_{2}_{3}.txt".format(server,component,server,current_time),\
                mode='w',encoding='utf-8') as f:
                for r in result:
                    if 'active' not in r[1] and 'waiting' not in r[1] and 'usable' in r[1]:
                        f.write(f"{r[0]:20s}{r[1][9:12]:8s}{r[1][-7:-1]}.\n")
                    else:
                        f.write(f"{r[0]:28s}Not usable.\n")
            for r in result:
                if 'active' not in r[1] and 'waiting' not in r[1] and 'usable' in r[1]:
                    treeview.insert("",text=r[0],index="end",values=[r[0],r[1][9:12],r[1][-7:-1]])
                else:
                    treeview.insert("",text=r[0],index="end",values=[r[0]," ","Unavailable."])
        else:
            messagebox.showinfo("Info","Not Found {0} , please choose [SKU Ready] to check it.".format(component))
    elif func == 'PML':
        if selectedfile != None and var_entry.get() :
            components_list=read_pml.readout(selectedfile)
            result=connector.PML_chk(components_list)
            with open(file=".//Results//{0}//{1}_{2}_{3}.txt".format(server,os.path.basename(selectedfile),server,current_time),\
                mode='w',encoding='utf-8') as f:
                for r in result:
                    if r[1] == 'Syncronizing' :
                        f.write(f"{r[0]:28s} Syncronizing.\n")
                    elif r[1] == 'EOL':
                        f.write(f"{r[0]:28s} EOL.\n")
                    elif r[1] == 'Not exist':
                        f.write(f"{r[0]:28s} Not exist.\n")  
                    else:
                        f.write(f"{r[0]:20s}{str(r[1]):8s} Ready.\n")
                        pass
            for r in result:
                if r[1] == 'Syncronizing' :
                    treeview.insert("",text=r[0],index="end",values=[r[0],' ',r[1]])
                elif r[1] == 'EOL':
                    treeview.insert("",text=r[0],index="end",values=[r[0],' ',r[1]])
                elif r[1] == 'Not exist':
                    treeview.insert("",text=r[0],index="end",values=[r[0],' ',r[1]])  
                else:
                    treeview.insert("",text=r[0],index="end",values=[r[0],r[1],r[2].strftime("%Y-%m-%d %H:%M:%S"),r[3].strftime("%Y-%m-%d %H:%M:%S")])
            messagebox.showinfo("Show","[{0}] [{1}] show in the table ".format(os.path.basename(selectedfile),len(result)))
        else:
            messagebox.showwarning("Warning","Please click OpenPML to choose PML file first.")
        entry1.config(state='disabled')

def run():
    if item_chk() == 1:
        btn_run.config(state="normal")
        return
    else:
        if var.get() != 'PML':
            do_query(var.get(),var_entry.get().strip(),combobox1.get())
        else:
            do_query(var.get(),server=combobox1.get())
    btn_run.config(state="normal")

def item_chk():
    if var.get() == "0" :
        messagebox.showwarning("Warning","Please choose an item.")
        return 1
    elif var.get() == "skunumber" :
        treeview.heading("2",text="ReadyTime")
        if var_entry.get() == "" :
            messagebox.showerror("Warning","Not found component string.")
            return 1
        else:
            if not(re.match("^(\w{6}\-\w{3}$)",var_entry.get().strip()) or re.match("^(\w{14})$",var_entry.get().strip())) :
                messagebox.showwarning("Warning","Please check for the spelling of P/N or ML.")
                return 1
    elif var.get() == "ML":
        treeview.heading("2",text="Usable or Not")
        if var_entry.get() == "" :
            messagebox.showerror("Warning","Not found component string.")
            return 1
        else:
            if not(re.match("^(\w{14})$",var_entry.get().strip())) :
                messagebox.showwarning("Warning","Please check for the spelling of ML.")
                return 1
    if combobox1.get() == "Server Name":
        messagebox.showerror("Error","Please choose one of servers to query.")
        return 1
    return 0
    
def ctrl_entry():
    if var.get() == "PML":
        treeview.heading("2",text="ReadyTime")
        entry1.delete(0,'end')
        entry1.config(state="disabled")
    else:
        entry1.config(state="normal")

def openfile():
    global selectedfile
    selectedfile=None
    selectedfile=filedialog.askopenfilename(initialdir='.\PML',title="Choose one ini file",filetypes=[('ini files','*.ini')])
    filename=os.path.basename(selectedfile)
    entry1.config(state='normal')
    entry1.delete(0,'end')
    entry1.insert('insert',filename)
    return filename

def copy_clipboard(e):
    if treeview.get_children() == ():
        return
    sel=treeview.selection()
    root.clipboard_clear()
    for s in sel:
        root.clipboard_append(treeview.item(s,'text')+"\n")
def threading_run():
    thread = threading.Thread(target=run)
    thread.start() 
    root.update_idletasks()
    btn_run.config(state="disabled")

bg_color="#FFFAF0"    

root=tk.Tk()
root.title("Component Check Tool")
root.resizable(width=0, height=0)
root.config(background=bg_color)
#root.iconbitmap('.\search2.ico')
screen_width=root.winfo_screenwidth()
screen_height=root.winfo_screenheight()
app_width=480
app_height=420

x=(screen_width/2)-(app_width/2)
y=(screen_height/2)-(app_height/2)
root.geometry(f"{app_width}x{app_height}+{int(x)}+{int(y)}")

root_Font=Font(family="Consolas",size=13,weight="bold",slant="italic")
var=tk.StringVar()
var.set("skunumber")
var_entry=tk.StringVar()

frame1=tk.Frame(root,width=140,height=120,background=bg_color)
frame1.grid(row=0,column=0,pady=15)
frame1.grid_propagate(False)
frame2=tk.Frame(root,width=200,height=120,background=bg_color)
frame2.grid(row=0,column=1,sticky="W")
frame2.grid_propagate(True)
frame3=tk.Frame(root,width=474,height=265,background=bg_color)
frame3.grid(row=1,column=0,columnspan=3,padx=3)
frame3.grid_propagate(False)
frame4=tk.Frame(root,width=110,height=120,background=bg_color)
frame4.grid(row=0,column=2,padx=3)
frame4.grid_propagate(False)

radio_btn1=tk.Radiobutton(frame1,bg=bg_color,activebackground=bg_color,text="SKU Ready",variable=var,value="skunumber",font=root_Font,command=ctrl_entry)
radio_btn1.grid(row=0,column=0,pady=2,sticky="W")
radio_btn2=tk.Radiobutton(frame1,bg=bg_color,activebackground=bg_color,text="ML",variable=var,value="ML",font=root_Font,command=ctrl_entry)
radio_btn2.grid(row=1,column=0,pady=2,sticky="W")
radio_btn3=tk.Radiobutton(frame1,bg=bg_color,activebackground=bg_color,text="PML",variable=var,value="PML",font=root_Font,command=ctrl_entry)
radio_btn3.grid(row=2,column=0,pady=2,sticky="W")

entry1=tk.Entry(frame2,textvariable=var_entry,font=Font(family="Consolas",size=13,weight="bold"),width=20,foreground="#000080",border=2,highlightthickness=1,highlightcolor="#fffafa",)
entry1.insert(0,"ML or P/N")
entry1.bind("<Button-3>",lambda arg:entry1.delete(0,'end'))
entry1.grid(column=0,row=0,pady=10,ipady=2.5,sticky="W")

combobox1=ttk.Combobox(frame2,width=17,height=25,font=root_Font,state='readonly',value=["TAIWISDIV01","TAIWISDIV02","TAIWISDIV03","CHOWISDIV01"])
combobox1.grid(row=1,column=0,columnspan=2,pady=10,ipady=2.5,ipadx=5)
combobox1.set("Server Name")

scrollbar=Scrollbar(frame3,jump=1,orient="vertical")
scrollbar.grid(row=0,column=1,pady=1,sticky="NS")

treeview=ttk.Treeview(frame3,columns=["0","1","2","3"],show="headings",yscrollcommand=scrollbar.set,selectmode="extended",height=12)
treeview.column("0",width=130)
treeview.column("1",width=40,anchor="center")
treeview.column("2",width=135,anchor="center")
treeview.column("3",width=135,anchor="center")
treeview.heading("0",text="Component")
treeview.heading("1",text="Rev")
treeview.heading("2",text="ReadyTime")
treeview.heading("3",text="EndofLife")
treeview.bind("<Control-c>",copy_clipboard)
treeview.grid(row=0,column=0,pady=1,ipadx=7)

scrollbar.config(command=treeview.yview)
style=ttk.Style()
style.configure("Treeview",rowheight=20,font=('Arial',10))

btn_run=tk.Button(frame4,text="RUN",font=Font(family="Consolas",size=14,weight="bold",underline=True),command=threading_run,activeforeground="red",border=3,width=5)
btn_run.grid(row=1,column=0,padx=15,pady=5,sticky="W")

filedialog_btn=tk.Button(frame4,text="OpenPML",font=Font(family="Consolas",size=12,weight="bold",underline=True),command=lambda:openfile(),bg=bg_color,border=0,activeforeground='white')
filedialog_btn.grid(row=0,column=0,padx=10,pady=10,sticky='W')

selectedfile=None  


if not os.path.exists(".//Results") :
    os.mkdir('.//Results')
    os.mkdir('.//Results//TAIWISDIV01')
    os.mkdir('.//Results//TAIWISDIV02')
    os.mkdir('.//Results//TAIWISDIV03')
    os.mkdir('.//Results//CHOWISDIV01')

if __name__ == '__main__':
    root.mainloop()