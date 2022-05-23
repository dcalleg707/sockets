import tkinter
from traceback import FrameSummary


ventana = tkinter.Tk()
ventana.geometry("1280x720")


bg = tkinter.PhotoImage(file="sockets/img/Wallpaper.png")
fondo = tkinter.Label(ventana,image=bg)
fondo.place(x=0,y=0)



carpetaCreada = tkinter.PhotoImage(file="sockets/img/carpetaCreada.png")
carpetaImg = tkinter.PhotoImage(file="sockets/img/carpeta.png")
blocImg = tkinter.PhotoImage(file="sockets/img/bloc.png")
apagarImg = tkinter.PhotoImage(file="sockets/img/shutdown.png")

row = 3
column = 0
nombreCarpeta = tkinter.Entry(ventana)

def crearCarpeta():
    nombreCarpeta.grid(row=0,column=4)
    botonCarpeta = tkinter.Button(ventana, text="Crear carpeta", command= lambda: crearIconoCarpeta(nombreCarpeta.get(),botonCarpeta))
    botonCarpeta.grid(row=1, column=4)
    

def crearIconoCarpeta(nombre,botonCarpeta):
    botonCarpeta.grid_remove()
    nombreCarpeta.grid_remove()
    global row, column
    print(nombre)
    carpetaNueva = tkinter.Button(ventana, image=carpetaCreada, text=nombre,command=borrarCarpeta, compound="top")
    carpetaNueva.grid(row=row,column=column,padx=10,pady=20)
    row = row + 1
    if row == 7:
        row = 0
        column = column + 1
    print(row)

def borrarCarpeta():
    global row, column
    list = ventana.grid_slaves(row=row-1,column=column)
    for l in list:
        row-=1
        l.grid_remove()
        

def cerrar():
    ventana.destroy()


boton1 = tkinter.Button(ventana, image=carpetaImg, text="Crear carpeta", command= crearCarpeta)
boton2 = tkinter.Button(ventana, image=blocImg, text="Abrir bloc")
boton3 = tkinter.Button(ventana, image= apagarImg, text="Apagar",command=cerrar)

boton1.grid(row=0,column=0,padx=10,pady=20)
boton2.grid(row=1,column=0,padx=10,pady=20)
boton3.grid(row=2,column=0,padx=10,pady=20)

ventana.mainloop()
