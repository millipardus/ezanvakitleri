from Tkinter import *
from os import name, sep

class PencereGoster(Tk):
    def __init__(self, baslik, icerik):
        Tk.__init__(self)
        #self.geometry("300x50")
        self.geometry("300x100")
        self.baslik = baslik

        self.resizable(0, 0)
        if name == "nt":
            self.iconbitmap("kaynaklar"+sep+"camii.ico")
        elif name == "posix":
            self.iconbitmap("@kaynaklar"+sep+"camii.xbm")
            
        self.title(baslik)
        etk = Label(self, text=icerik)
        etk.pack(expand=True)
        dug = Button(self, text="Tamam", command=lambda:self.destroy())
        dug.pack(side="bottom", expand=True)
        self.ortala(self)
        
        
    def ortala(self, penc):
        penc.update_idletasks()
        gen= penc.winfo_width()
        yuk = penc.winfo_height()
        
        e_gen = penc.winfo_screenwidth()
        e_yuk = penc.winfo_screenheight()
        
        x = (e_gen / 2) - (gen / 2)
        y = (e_yuk / 2) - (yuk / 2)
        
        penc.geometry("{}x{}+{}+{}".format(gen, yuk, x, y))

def baslat():
    pencere = PencereGoster("Pencere","Deneme Penceresi")
    mainloop()

if __name__ == "__main__":
    baslat()
    