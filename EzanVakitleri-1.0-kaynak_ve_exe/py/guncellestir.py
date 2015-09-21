#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib import urlretrieve
from urllib2 import urlopen
from Tkinter import *
import sys, os, codecs
from threading import Thread

class UYG(object):
    def __init__(self):
        if sys.argv[0].endswith(".py"):
            if not "vakit_gorsel.py.yedek" in os.listdir('.'):
                    #os.rename("vakit_gorsel.py", "vakit_gorsel.py.yedek")
                    dosya = "vakit_gorsel.py.yedek"
            else:
                dosya = "vakit_gorsel.py.yedek"
                sayac = 0
                while dosya in os.listdir('.'):
                    sayac+=1
                    dosya = "vakit_gorsel.py.yedek"+str(sayac)
            try:
                os.rename("vakit_gorsel.py", dosya)
            except: pass
            
            #Thread(target=HataMesaji, args=(u"Dosya İndiriliyor", u"Lütfen dosya indirilirken sabırlı olun.")).start()
            HataMesaji(u"Dosya İndiriliyor", u"Lütfen dosya indirilirken sabırlı olun.")
            
            try:
                kodlar = urlopen("https://raw.githubusercontent.com/millipardus/ezanvakitleri/master/yenisurum/yenisurum.py").read()
                
                dosya_olustur = codecs.open("yenisurum.py", "w", "utf-8")
                
                dosya_olustur.write(kodlar.decode("cp1254"))
                dosya_olustur.close()
                
                #self.yenidosya = urlretrieve("https://raw.githubusercontent.com/millipardus/ezanvakitleri/master/yenisurum/yenisurum.py", "yenisurum.py")
                #urlopen("https://raw.githubusercontent.com/millipardus/ezanvakitleri/master/yenisurum/yenisurum.py")
                
            except:
                #Thread(target=HataMesaji, args=("Hata 00001 !", "Dosya indirilemedi ! Lütfen geliştiriciye başvurun.")).start()
                hata = HataMesaji("Hata 00001 !", "Dosya indirilemedi ! Lütfen geliştiriciye başvurun.")
                try:
                    os.rename(dosya, "vakit_gorsel.py")
                    os.remove("yenisurum.py")
                except: pass
                #showerror("Hata 00001 !", "Dosya indirilemedi ! Lütfen geliştiriciye başvurun.")
            else:
                #Thread(target=HataMesaji, args=(u"Dosya İndirildi !", u"Dosya Başarıyla İndirildi !")).start()
                HataMesaji(u"Dosya İndirildi !", u"Dosya Başarıyla İndirildi !")
                try:
                    fazladan_al = urlopen("https://raw.githubusercontent.com/millipardus/ezanvakitleri/master/yenisurum/icerik.txt", timeout=2).read()
                    
                except: fazladan = 0
                else:
                    fazladan = 1
                if fazladan:
                    listeolustur =fazladan_al.strip().splitlines()
                    
                    for i in listeolustur:
                        urlretrieve("https://raw.githubusercontent.com/millipardus/ezanvakitleri/master/yenisurum/"+i, i.replace('/', os.sep))
                
                
                #try:
                os.rename("yenisurum.py", "vakit_gorsel.py")
                os.startfile("vakit_gorsel.py")
                """except:
                    try:
                        os.rename(dosya, "vakit_gorsel.py")
                        os.remove("yenisurum.py")
                    except: pass"""
                exit()
        elif sys.argv[0].endswith(".exe"):
            #Thread(target=HataMesaji, args=(u"Dosya İndiriliyor", u"Lütfen dosya indirilirken sabırlı olun.")).start()
            HataMesaji(u"Dosya İndiriliyor", u"Lütfen dosya indirilirken sabırlı olun.")
            try:
                self.yenidosya = urlretrieve("https://raw.githubusercontent.com/millipardus/ezanvakitleri/master/yenisurum/yenisurum.exe", "yenisurum.exe")
                urlopen("https://raw.githubusercontent.com/millipardus/ezanvakitleri/master/yenisurum/yenisurum.exe")
            except:
                hata = HataMesaji("Hata 00001 !", "Dosya indirilemedi ! Lütfen geliştiriciye başvurun.")
                #showerror("Hata 00001 !", "Dosya indirilemedi ! Lütfen geliştiriciye başvurun.")
            else:
                HataMesaji(u"Dosya İndirildi !", u"Dosya Başarıyla İndirildi !")
                try:
                    fazladan_al = urlopen("https://raw.githubusercontent.com/millipardus/ezanvakitleri/master/yenisurum/icerikexe.txt", timeout=2).read()
                    
                except: fazladan = 0
                else:
                    fazladan = 1
                if fazladan:
                    listeolustur =fazladan_al.strip().splitlines()
                    
                    for i in listeolustur:
                        urlretrieve("https://raw.githubusercontent.com/millipardus/ezanvakitleri/master/yenisurum/"+i, i.replace('/', os.sep))
                if not "vakit_gorsel.exe.yedek" in os.listdir('.'):
                    #os.rename("vakit_gorsel.exe", "vakit_gorsel.exe.yedek")
                    dosya = "vakit_gorsel.exe.yedek"
                else:
                    dosya = "vakit_gorsel.exe.yedek"
                    sayac = 0
                    while dosya in os.listdir('.'):
                        sayac+=1
                        dosya = "vakit_gorsel.exe.yedek"+str(sayac)
                
                os.rename("vakit_gorsel.exe", dosya)
                os.rename("yenisurum.exe", "vakit_gorsel.exe")
                os.startfile("vakit_gorsel.exe")
                exit()

                
class HataMesaji(Tk):
    def __init__(self, baslik, yazi):
        Tk.__init__(self)
        self.iconbitmap("kaynaklar"+os.sep+"camii.ico")
        self.title(baslik)
        self.geometry("300x100")
        etk = Label(text=yazi)
        etk.pack()
        mainloop()

def ana():
    uyg = UYG()

    
if __name__ == "__main__":
    ana()