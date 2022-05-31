import tkinter
from traceback import FrameSummary


ventana = tkinter.Tk()
ventana.geometry("1280x720")


bg = tkinter.PhotoImage(file="img/Wallpaper.png")
fondo = tkinter.Label(ventana,image=bg)
fondo.place(x=0,y=0)



carpetaCreada = tkinter.PhotoImage(file="img/carpetaCreada.png")
carpetaImg = tkinter.PhotoImage(file="img/carpeta.png")
blocImg = tkinter.PhotoImage(file="img/bloc.png")
apagarImg = tkinter.PhotoImage(file="img/shutdown.png")

row = 3
column = 0
nombreCarpeta = tkinter.Entry(ventana)
botones = []

def crearCarpeta():
    nombreCarpeta.grid(row=0,column=4)
    botonCarpeta = tkinter.Button(ventana, text="Crear carpeta", command= lambda: crearIconoCarpeta(nombreCarpeta.get(),botonCarpeta))
    botonCarpeta.grid(row=1, column=4)


def crearIconoCarpeta(nombre,botonCarpeta):
    botonCarpeta.grid_remove()
    nombreCarpeta.grid_remove()
    global row, column
    carpetaNueva = tkinter.Button(ventana, image=carpetaCreada, text=nombre, command=lambda:borrarCarpeta(carpetaNueva), compound="top")
    carpetaNueva.grid(row=row,column=column,padx=10,pady=20)
    row = row + 1
    if row == 7:
        row = 0
        column = column + 1

def borrarCarpeta(carpetaNueva):
    global row,column
    carpetaNueva.destroy()
    if row > 0:
        row-=1
    elif row==0 and column==1:
        row = 6
        column = 0
    elif row==0 and column>0:
        row = 7
        column-=1
    print(row,column)
        


def cerrar():
    ventana.destroy()


boton1 = tkinter.Button(ventana, image=carpetaImg, text="Crear carpeta", command= crearCarpeta)
boton2 = tkinter.Button(ventana, image=blocImg, text="Abrir bloc")
boton3 = tkinter.Button(ventana, image= apagarImg, text="Apagar",command=cerrar)

boton1.grid(row=0,column=0,padx=10,pady=20)
boton2.grid(row=1,column=0,padx=10,pady=20)
boton3.grid(row=2,column=0,padx=10,pady=20)

ventana.mainloop()