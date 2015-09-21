#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Tkinter import *
from ttk import Treeview
from wx import TaskBarIcon, IconFromBitmap, Bitmap, EVT_TASKBAR_LEFT_DOWN, MenuItem, EVT_MENU, App
from wx import Menu as Menu_wx

from datetime import datetime
from subprocess import check_output, Popen
from sqlite3 import connect
from urllib import urlopen
from re import sub, findall
from time import strftime, sleep
from sys import argv
from sys import exit as sys_exit
from os import name, listdir, sep, system
from PencereGoster import PencereGoster
    
from threading import Thread
from tkMessageBox import showinfo, askquestion
#check_output("chcp 1254", shell=True)
from Queue import Queue

if name == "nt":
    from os import startfile
    import bildirim
elif name == "posix":
    import pynotify
    from pynotify import Notification as pynotify_Notification
    from pynotify import init as pynotify_init
    try:
        from ssl import SSLContext, PROTOCOL_TLSv1
    except: pass
    pynotify_init("Test")
    
import pygame
pygame.mixer.init()


class UYGULAMA(object):
    def __init__(self, pencere_):
        self.surum = "1.0"
        self.gizli = 0
        self.calinanlar = []
        self.vt = Veritabani()
        self.sira = Queue()
        self.uyaripen=[]
        self.gizli = 0
        
        self.pencere = pencere_
        
        global pencere_ana_
        pencere_ana_ = self.pencere
        self.Acik = 1
        self.Acik_ = 1
        self.pencereler = []
        self.ayar = []
        self.Arayuz()
        tarih = self.tarihcek()
        
        if not "veriler.vt" in listdir('.'):
            eklenecek = "%s.%s.%s" %(self.gun, self.ay,self.yil)
            self.v = connect("veriler.vt")
            self.v.text_factory = str
            self.im = self.v.cursor()
            self.im.execute("CREATE TABLE sontarih(bilgi)")
            self.im.execute("CREATE TABLE vakitler(imsak, gunes, ogle, ikindi, aksam, yatsi)")
            self.im.execute("CREATE TABLE ayarlar(bilgi)")
            self.im.execute("CREATE TABLE ses(ses_duzeyi)")
            self.im.execute("INSERT INTO ayarlar VALUES (?)", ('bos',))
            if name=="posix":
                cikti_al = system('notify-send "Ezan Vakitleri - Tespit Ediliyor" "Sisteminizin desteklediği bildirim yapısı tespit ediliyor."')
                if cikti_al == 0:
                    self.im.execute("INSERT INTO ayarlar VALUES (?)", ('pysiz_bildirim',))
                else:
                    self.im.execute("INSERT INTO ayarlar VALUES (?)", ('pyli_bildirim',))
            self.im.execute("INSERT INTO sontarih VALUES (?)", (eklenecek,))
            self.im.execute("INSERT INTO ses VALUES (?)", (100,))
            self.v.commit()

            
            veriler = self.im.execute("SELECT * FROM vakitler")
            vericek = self.im.fetchall()
            
            if not vericek:
                vr = self.vakitcek_d()
                """self.liste_temizle()
                self.t.insert("", 0, values=(vr[0], vr[1], vr[2], vr[3], vr[4]))"""
            
            self.im.execute("SELECT * FROM ayarlar")
            vericek=self.im.fetchall()
            if vericek:
                if not vericek[0][0] == 'bos':
                    self.ayarlar = vericek

                else:
                    self.Secenekler()
            else:
                self.ayarlar = vericek
            
        else:
            self.v = connect("veriler.vt", check_same_thread=False)
            self.v.text_factory = str
            self.im = self.v.cursor()
            veriler = self.im.execute("SELECT * FROM sontarih")
            vericek = self.im.fetchall()
            sontarih = vericek[0][0]
            
            veriler = self.im.execute("SELECT * FROM vakitler")
            vericek = self.im.fetchall()
            
            if not vericek:
                vr = self.vakitcek_d()
                """self.liste_temizle()
                self.t.insert("", 0, values=(vr[0], vr[1], vr[2], vr[3], vr[4]))"""
            
            self.im.execute("SELECT * FROM ayarlar")
            vericek=self.im.fetchall()
            if vericek:
                if not vericek[0][0] == 'bos':
                    self.ayarlar = vericek
                else:
                    self.Secenekler()
            else:
                self.ayarlar = vericek
            if sontarih != tarih:
                self.tarihguncelle()
        
        self.im.execute("SELECT * FROM ses")
        self.ses_duzeyi = self.im.fetchall()[0][0]
        pygame.mixer.music.set_volume(float(self.ses_duzeyi)/100)
        
        
        #pencere = win32console.GetConsoleWindow()
        #win32gui.ShowWindow(pencere, 0)
        self.im.execute("SELECT * FROM vakitler")
        self.vakitler = self.im.fetchall()
        self.vakitler = self.vakitler[0]
        
        self.liste_temizle()
        self.t.insert("", 0, values=(self.vakitler[0], self.vakitler[1], self.vakitler[2], self.vakitler[3], self.vakitler[4], self.vakitler[5]))
        
        
        
        
        self.saat = self.saatcek()
        self.vakitdenetle()
        self.baslangic_denetim()
        self.tarih_al = self.tarihcek()
        
        Thread(target=self.saat_yenile).start()
        
        #Thread(target=self.denetim).start()
        #Thread(target=self.uyari, args=("", "")).start()
        
        Thread(target=self.uyaridenetim).start()
        #self.pencere.after(1, lambda: self.sira.put(lambda: Thread(target=self.guncellestirmeDenetim).start()))
        
        ##Thread(target=self.guncellestirmeDenetim).start()
        
        self.sira.put(self.guncellestirmeDenetim)
        self.sira.put(self.surekliGuncelle)
        
        
        #self.sira.put(lambda: Thread(target=self.guncellestirmeDenetim).start())
    
    def surekliGuncelle(self):
        devam = 1
        if self.Acik:
            self.pencere.update_idletasks()
        else:
            devam= 0
        
        if devam:
            self.pencere.after(100, self.surekliGuncelle)
          
    def guncellestirmeDenetim(self, komut=""):
        if komut != "":
            showinfo(u"Güncelleştirmeler Denetleniyor", u"Güncelleştirmeler denetleniyor...")
        
        if name=="posix":
            try:
                sertifika = SSLContext(PROTOCOL_TLSv1)
                dosya = urlopen("https://raw.githubusercontent.com/millipardus/ezanvakitleri/master/surum.txt", context=sertifika).read().strip()
            except: 
                dosya = urlopen("https://raw.githubusercontent.com/millipardus/ezanvakitleri/master/surum.txt").read().strip()
        elif name=="nt":
            dosya = urlopen("https://raw.githubusercontent.com/millipardus/ezanvakitleri/master/surum.txt").read().strip()
            
        if dosya != self.surum and float(dosya) > float(self.surum):
            soru = askquestion(u"Yeni Bir Sürüm Var !", u"Yeni bir sürüm tespit edildi. Sürüm numarası: %s\nYüklemek ister misiniz ?" %dosya)
            if soru == "yes":
                if argv[0].endswith(".py"):
                    if name=="nt":
                        startfile("guncellestir.py")
                    elif name=="posix":
                        system("python guncellestir.py")
                elif argv[0].endswith(".exe"):
                    startfile("guncellestir.exe")
                else:
                    if name=="posix":
                        system("./guncellestir")
                exit()
        elif komut != "":
            showinfo(u"Yeni Sürüm Yok", u"Şu an güncel sürümü kullanıyorsunuz.")
                
                
        if komut == "":
            self.pencere.after(7200000, lambda: self.sira.put(self.guncellestirmeDenetim))
            #self.pencere.after(2000, lambda: self.sira.put(lambda: Thread(target=self.guncellestirmeDenetim).start()))
            
        
    def ortala(self, penc):
        penc.update_idletasks()
        gen= penc.winfo_width()
        yuk = penc.winfo_height()
        
        e_gen = penc.winfo_screenwidth()
        e_yuk = penc.winfo_screenheight()
        
        x = (e_gen / 2) - (gen / 2)
        y = (e_yuk / 2) - (yuk / 2)
        
        penc.geometry("{}x{}+{}+{}".format(gen, yuk, x, y))
            
    def Arayuz(self):
        self.pencereler.append(self.pencere)
        if name == "nt":
            self.pencere.iconbitmap("kaynaklar"+sep+"camii.ico")
        elif name == "posix":
            self.pencere.iconbitmap("@kaynaklar"+sep+"camii.xbm")
        self.pencere.title(u"Ezan Vakitleri")
        #self.pencere.geometry("500x100")
        self.Dizilimlik = Menu(self.pencere)
        self.pencere.config(menu=self.Dizilimlik)
        
        self.Bismillahirrahmanirrahim = Label(text="Esirgeyen ve Bağışlayan ALLAH'ın adıyla", font=("Arial", 20))
        self.Bismillahirrahmanirrahim.pack()
        self.pencere.after(2000, lambda: self.Bismillahirrahmanirrahim.pack_forget())
        
        self.komutlar = Menu(self.Dizilimlik, tearoff=0)
        self.dosya = Menu(self.Dizilimlik, tearoff=0)
        self.ayarlar_ = Menu(self.Dizilimlik, tearoff=0)
        self.yardim_menusu = Menu(self.Dizilimlik, tearoff=0)
        
        self.Dizilimlik.add_cascade(label="Dosya", menu=self.dosya)
        self.Dizilimlik.add_cascade(label="Komutlar", menu=self.komutlar)
        self.Dizilimlik.add_cascade(label=u"Ayarlar", menu=self.ayarlar_)
        self.Dizilimlik.add_cascade(label=u"Yardım", menu=self.yardim_menusu)
        
        self.cerceve = Frame(self.pencere, height=100)
        
        self.komutlar.add_command(label="Vakitleri Çek ve Kaydet", command=self.vakitcek_d)
        self.komutlar.add_command(label="Gizle", command=self.pencere_gizle)
        self.komutlar.add_command(label=u"Güncelleştirmeleri Denetle", command=lambda: Thread(target=self.guncellestirmeDenetim("komut")).start())
        self.komutlar.add_command(label=u"Pencereyi Ortala", command=lambda: self.ortala(self.pencere))
        self.komutlar.add_separator()
        self.komutlar.add_command(label=u"Ezan Oku", command=lambda: Thread(target=self.yonlendir, args=("kaynaklar"+sep+"ezan.mp3",)).start())
        self.komutlar.add_command(label=u"Ezan Oku (Yinelemeli)", command=lambda: Thread(target=self.yonlendir, args=("kaynaklar"+sep+"ezan.mp3","yinele")).start())
        self.komutlar.add_command(label=u"Ezanı Durdur", command=lambda: Thread(target=self.muzik_durdur).start())
        self.komutlar.add_command(label=u"Ezanı Duraklat", command=lambda: Thread(target=self.muzik_duraklat).start())
        self.komutlar.add_command(label=u"Ezana Devam Et", command=lambda: Thread(target=self.muzik_devam).start())
        
        self.yardim_menusu.add_command(label=u"Hakkında", command=self.hakkinda_ac)
        

        self.dosya.add_command(label=u"Çıkış", command=self.cikis)
        self.ayarlar_.add_command(label=u"Seçenekler", command=self.Secenekler)
        self.ayarlar_.add_command(label=u"Ses Düzeyini Ayarla", command=self.SesDuzeyi)
        
        self.etk1 = Label(text=u"Hoşgeldiniz !")
        self.etk2 = Label(text=u"Tarih: %s" %self.tarihcek(), font=("Arial", 15))
        self.etk3 = Label(text=u"Saat: ", font=("Arial", 15))
        self.etk4 = Label(text=u"", font=("Arial", 15))
        self.t = Treeview(self.cerceve)
        self.etk1.pack()
        self.etk2.pack()
        self.etk3.pack()
        self.etk4.pack()
        
        #self.saat_yenile()
        
        self.t["columns"] = ("imsak", "gunes", "ogle", "ikindi", "aksam", "yatsi")
        
        self.t.column("imsak", width=83, anchor="center")
        self.t.column("gunes", width=83, anchor="center")
        self.t.column("ogle", width=83, anchor="center")
        self.t.column("ikindi", width=83, anchor="center")
        self.t.column("aksam", width=83, anchor="center")
        self.t.column("yatsi", width=83, anchor="center")
        
        self.t.heading("imsak", text=u"İmsak")
        self.t.heading("gunes", text=u"Güneş")
        self.t.heading("ogle", text=u"Öğle")
        self.t.heading("ikindi", text=u"İkindi")
        self.t.heading("aksam", text=u"Akşam")
        self.t.heading("yatsi", text=u"Yatsı")
        
        
        self.t["show"] = "headings"
        self.t.pack()
        self.cerceve.pack()
        
        self.pencere.protocol("WM_DELETE_WINDOW", self.cikis)
        self.pencere.after(1000, self.sil)
        self.ortala(self.pencere)
    
    def hakkinda_ac(self):
        self.sira.put(lambda: showinfo(u"Ezan Vakitleri - Hakkında", u"Program Adı: Ezan Vakitleri\nSürüm: %s\nLisans: GNU\\GPL\nEzan: Abdurrahman Al Hindi" %self.surum))
    
    def pencere_gizle(self):
        self.pencere.withdraw()
        self.gizli = 1
        #Thread(target=self.gizle).start()
    
    def gizle(self):
        pass
    
    def dvc(self, veri):
        return int(sub("^0+", "", veri))
    
    def son_vakit_denetim(self):
        imsak = self.vakitler[0].split(':')
        gunes = self.vakitler[1]
        ogle = self.vakitler[2]
        ikindi = self.vakitler[3]
        aksam = self.vakitler[4]
        yatsi = self.vakitler[5]
        
        s_za = datetime.now()
        
        imsak = datetime(s_za.year, s_za.month, s_za.day, imsak[0].split(':')[0], imsak[0].split(':')[1])
        simdi = datetime(s_za.year, s_za.month, s_za.day, s_za.hour, s_za.minute)
        
        if simdi.time() < imsak.time():
            s1 = imsak+  ":00"
            s2 =strftime("%H:%M:%S")
            FMT = '%H:%M:%S'
            zd = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
            m, s = divmod(zd.seconds, 60)
            h,m = divmod(m,60)
            self.etk4["text"] = u"İmsağa kalan zaman: %s" %(str(h)+":"+str(m)+":"+str(s))
        
        
    def bildirimPenceresiGoster(self, baslik, icerik, resim="", aciklama=""):
        if name == "nt":
            bildirim.bildiri(baslik, icerik, resim, aciklama)
        elif name == "posix":
            if ('pyli_bildirim',) in self.ayarlar:
                bildirim_linux = pynotify_Notification(baslik, icerik)
                bildirim_linux.show()
            else:
                Popen(["notify-send", baslik, icerik])
    
    def SesAyarla(self, pencere, sesduzeyi):
        sesduzeyi_al = sesduzeyi.get()
        self.ses_duzeyi = sesduzeyi_al
        pygame.mixer.music.set_volume(float(self.ses_duzeyi)/100)
        print sesduzeyi_al
        self.im.execute("DROP TABLE ses")
        self.im.execute("CREATE TABLE ses(ses_duzeyi)")
        self.im.execute("INSERT INTO ses VALUES (?)", (sesduzeyi_al,))
        self.v.commit()
        
        pencere.destroy()
        showinfo(u"Ses Düzeyi Kaydedildi", u"Ses düzeyi başarıyla kaydedildi.")
        
        
    
    def SesDuzeyi(self):
        pencere = Tk()
        pencere.title("Ses Düzeyini Ayarla")
        pencere.geometry("300x80")
        
        duzeyvekutu = Frame(pencere)
        
        if name == "nt":
            pencere.iconbitmap("kaynaklar"+sep+"camii.ico")
        elif name == "posix":
            pencere.iconbitmap("@kaynaklar"+sep+"camii.xbm")
        
        self.im.execute("SELECT * FROM ses")
        eski_sesduzeyi = self.im.fetchall()[0][0]
        
        
        sesduzeyi = Scale(duzeyvekutu, from_=0, to=100, orient=HORIZONTAL, command=lambda x:self.MevcutSesAyarla(sesduzeyi,"hizli"))
        sesduzeyi.set(eski_sesduzeyi)
        sesduzeyi.grid(row=0, column=0)
        
        sesduzeyi.bind("<ButtonRelease-1>", lambda x: self.MevcutSesAyarla(sesduzeyi))
        sesduzeyi.bind("<Button-1>", self.Sifirla)
        
        kutu = Entry(duzeyvekutu, width=3)
        kutu.grid(row=0, column=1, pady=5)
        
        self.kutu = kutu
        
        kutu.bind("<Return>", lambda x: self.KaydirmaAyarla(kutu, sesduzeyi))
        kutu.bind("<Key>", self.Sifirla_gonder)
        
        #dug = Button(pencere, text=u"Sesi Ayarla", command=lambda: self.SesAyarla(pencere, sesduzeyi))
        #dug.pack()
        
        duzeyvekutu.pack()
        self.kaydediliyor___ = Label(pencere,text="Sağ-sola sürükleyebilir\nya da yandaki kutuya yazabilirsiniz.")
        self.kaydediliyor___.pack()
        
        self.ortala(pencere)
    def MevcutSesAyarla(self, sesduzeyi, komut=""):
        if komut == "":
            pygame.mixer.music.set_volume(float(sesduzeyi.get())/100)
            self.im.execute("DROP TABLE ses")
            self.im.execute("CREATE TABLE ses(ses_duzeyi)")
            self.im.execute("INSERT INTO ses VALUES (?)", (sesduzeyi.get(),))
            self.v.commit()
            self.kutu.delete(0, END)
            self.kutu.insert(0, sesduzeyi.get())
            self.kaydediliyor___["text"] = "Kaydedildi. Pencereyi kapatabilirsiniz."
        elif komut == "hizli":
            pygame.mixer.music.set_volume(float(sesduzeyi.get())/100)
            self.kutu.delete(0, END)
            self.kutu.insert(0, sesduzeyi.get())
    
    def Sifirla(self, olay, komut=""):
        if komut == "":
            self.kaydediliyor___["text"] = ""
        elif komut == "kutu":
            self.kaydediliyor___["text"] = "Kaydetmek için enter'a basınız."

    def Sifirla_gonder(self, o=""):
        self.Sifirla(self.kutu, "kutu")
    
    def KaydirmaAyarla(self, olay, kaydir):
        arac = olay
        kaydir.set(arac.get())
        self.MevcutSesAyarla(kaydir)
    
    def Secenekler(self):
        veriler = self.vt.vtOku("ayarlar", self.im)
        
        
        pencere = Toplevel()
        #pencere.geometry("500x500")
        pencere.title("Seçenekler")
        
        if name == "nt":
            pencere.iconbitmap("kaynaklar"+sep+"camii.ico")
        elif name == "posix":
            pencere.iconbitmap("@kaynaklar"+sep+"camii.xbm")
        
        
        self.pencereler.append(pencere)
        
        
        self.o1 = IntVar()
        self.o2 = IntVar()
        self.o3 = IntVar()
        self.o4 = IntVar()
        self.o5 = IntVar()
        self.o6 = IntVar()
        self.o7 = IntVar()
        self.o8 = IntVar()
        self.o9 = IntVar()
        self.o10 = IntVar()
        self.o11 = IntVar()
        self.o12 = IntVar()
        self.o13 = IntVar()
        
        self.o1.set(0)
        self.o2.set(0)
        self.o3.set(0)
        self.o4.set(0)
        self.o5.set(0)
        self.o6.set(0)
        self.o7.set(0)
        self.o8.set(0)
        self.o9.set(0)
        self.o10.set(0)
        self.o11.set(0)
        self.o12.set(0)
        self.o13.set(0)

        if not veriler:
            pass
        else:
            if veriler[0][0] != "bos":
                if ('ezan',) in veriler:
                    self.o1.set(1)
                if ('bip',) in veriler:
                    self.o2.set(1)
                if ('ezan_sesli_bildirim',) in veriler:
                    self.o3.set(1)
                if ('ezan_bildirim_pencere',) in veriler:
                    self.o4.set(1)
                if ('ezan_bildirim_sag_alt',) in veriler:
                    self.o5.set(1)
                if ('kala_sesli_bildirim',) in veriler:
                    self.o6.set(1)
                if ('kala_bildirim_sag_alt',) in veriler:
                    self.o7.set(1)
                if ('5dk_kala',) in veriler:
                    self.o8.set(1)
                if ('10dk_kala',) in veriler:
                    self.o9.set(1)
                if ('15dk_kala',) in veriler:
                    self.o10.set(1)
                if ('30dk_kala',) in veriler:
                    self.o11.set(1)
                if ('45dk_kala',) in veriler:
                    self.o12.set(1)
                if ('60dk_kala',) in veriler:
                    self.o13.set(1)

        etk = Label(pencere, text="_"*50+"\n"+u"Ezan vakti geldiğinde;\n"+"-"*50)
        
        onay= Checkbutton(pencere, text=u"Ezan oku", variable=self.o1)
        onay2=Checkbutton(pencere, text=u"Bip sesi çıkart", variable=self.o2)
        onay3= Checkbutton(pencere, text=u"Sesli bildirim yap", variable=self.o3)
        onay4= Checkbutton(pencere, text=u"Bildirim penceresi göster", variable=self.o4)
        onay5= Checkbutton(pencere, text=u"Sağ altta bildirim göster", variable=self.o5)
        
        etk2 = Label(pencere, text="_"*50+"\n"+u"Ezana 5-10-15-30-45-60 dakika kala;\n"+"-"*50)
        
        onay6= Checkbutton(pencere, text=u"Sesli bildirim yap", variable=self.o6)
        onay7= Checkbutton(pencere, text=u"Sağ altta bildirim göster", variable=self.o7)
        
        etk3 = Label(pencere, text="_"*50+"\n"+u"Diğer Ayarlar;\n"+"-"*50)
        
        onay8= Checkbutton(pencere, text=u"Ezana 5 dakika kala uyar", variable=self.o8)
        onay9= Checkbutton(pencere, text=u"Ezana 10 dakika kala uyar", variable=self.o9)
        onay10= Checkbutton(pencere, text=u"Ezana 15 dakika kala uyar", variable=self.o10)
        onay11= Checkbutton(pencere, text=u"Ezana 30 dakika kala uyar", variable=self.o11)
        onay12= Checkbutton(pencere, text=u"Ezana 45 dakika kala uyar", variable=self.o12)
        onay13= Checkbutton(pencere, text=u"Ezana 60 dakika kala uyar", variable=self.o13)
        
        
        
        dug = Button(pencere, text=u"Ayarla", command=lambda: self.Ayarla(pencere))
        
        dug2 = Button(pencere, text=u"Ses Ayarları", command=self.SesDuzeyi)
        
        
        etk.pack()
        onay.pack()
        onay2.pack()
        onay3.pack()
        onay4.pack()
        onay5.pack()
        etk2.pack()
        onay6.pack()
        onay7.pack()
        etk3.pack()
        onay8.pack()
        onay9.pack()
        onay10.pack()
        onay11.pack()
        onay12.pack()
        onay13.pack()
        dug.pack()
        dug2.pack()

        self.ortala(pencere)
     
    def Ayarla(self, pencere):
        secenekler = []
        if self.o1.get() == 1:
            secenekler.append("ezan")
        if self.o2.get() == 1:
            secenekler.append("bip")
        if self.o3.get() == 1:
            secenekler.append("ezan_sesli_bildirim")
        if self.o4.get() == 1:
            secenekler.append("ezan_bildirim_pencere")
        if self.o5.get() == 1:
            secenekler.append("ezan_bildirim_sag_alt")
        if self.o6.get() == 1:
            secenekler.append("kala_sesli_bildirim")
        if self.o7.get() == 1:
            secenekler.append("kala_bildirim_sag_alt")
        if self.o8.get() == 1:
            secenekler.append("5dk_kala")
        if self.o9.get() == 1:
            secenekler.append("10dk_kala")
        if self.o10.get() == 1:
            secenekler.append("15dk_kala")
        if self.o11.get() == 1:
            secenekler.append("30dk_kala")
        if self.o12.get() == 1:
            secenekler.append("45dk_kala")
        if self.o13.get() == 1:
            secenekler.append("60dk_kala")
        
        self.im.execute("SELECT * FROM ayarlar")
        ayarlari_al = self.im.fetchall()
        
        
            
        try:
            self.im.execute("DROP TABLE ayarlar")
        except:
            pass
        self.im.execute("CREATE TABLE ayarlar (bilgi)")
        for i in secenekler:
            self.im.execute("INSERT INTO ayarlar VALUES (?)", (i,))
        
        if ('pyli_bildirim',) in ayarlari_al:
	    self.im.execute("INSERT INTO ayarlar VALUES (?)", ('pyli_bildirim',))
	elif ('pysiz_bildirim',) in ayarlari_al:
	    self.im.execute("INSERT INTO ayarlar VALUES (?)", ('pysiz_bildirim',))
	
        self.v.commit()
        
        ayarlar = []
        for i in secenekler:
            ayarlar.append([i])
        
        self.ayarlar = ayarlar
        pencere.destroy()
        showinfo(u"Seçenekler Kaydedildi", u"Seçenekler başarıyla kaydedildi.")
    
    def denetim(self):
        print self.Acik
        if self.Acik:
            print self.saat
            print self.saatcek()
            devam=1
            if self.tarih_al != self.tarihcek():
                self.tarih_al = self.tarihcek()
                tarih = self.tarihcek()
                #print "Tarih güncelleniyor."
                showinfo("Tarih Güncellendi", "Tarih güncellendi: %s" %tarih)
                self.im.execute("UPDATE sontarih SET bilgi =?", (self.tarih_al,))
                self.v.commit()
                #print "Tarih güncellendi: %s" %tarih
                system("cls")
                #print "Bugünün Tarihi: %s" %tarih
                self.vakitler = self.vakitcek_d()
            
            
            if self.saat != self.saatcek():
                self.saat = self.saatcek()
                self.vakitdenetle()
                #print self.saat
            
        else:
            devam=0
            
        if devam:
            print "devam. Şimdi işlev tekrarlanacak."
            self.pencere.after(10, self.denetim)
    
    def saat_yenile(self):
        while 1:
            if self.Acik:
                if self.tarih_al != self.tarihcek():
                    self.tarih_al = self.tarihcek()
                    tarih = self.tarihcek()
                    #print "Tarih güncelleniyor."
                    showinfo("Tarih Güncellendi", "Tarih güncellendi: %s" %tarih)
                    self.im.execute("UPDATE sontarih SET bilgi =?", (self.tarih_al,))
                    self.v.commit()
                    #print "Tarih güncellendi: %s" %tarih
                    system("cls")
                    #print "Bugünün Tarihi: %s" %tarih
                    self.vakitler = self.vakitcek_d()
            
            
                if self.saat != self.saatcek():
                    self.saat = self.saatcek()
                    self.vakitdenetle()
                    #print self.saat
                    
                saat= self.saatcek("tam")
                self.etk3["text"] = "Saat: %s" %saat
                imsak_ = self.vakitler[0].split(':')
                gunes_ = self.vakitler[1].split(':')
                ogle_ = self.vakitler[2].split(':')
                ikindi_ = self.vakitler[3].split(':')
                aksam_ = self.vakitler[4].split(':')
                yatsi_ = self.vakitler[5].split(':')
                
                s_za = datetime.now()
                
                imsak = datetime(s_za.year, s_za.month, s_za.day, int(imsak_[0]), int(imsak_[1]), 0)
                gunes = datetime(s_za.year, s_za.month, s_za.day, int(gunes_[0]), int(gunes_[1]), 0)
                ogle = datetime(s_za.year, s_za.month, s_za.day, int(ogle_[0]), int(ogle_[1]), 0)
                ikindi = datetime(s_za.year, s_za.month, s_za.day, int(ikindi_[0]), int(ikindi_[1]), 0)
                aksam = datetime(s_za.year, s_za.month, s_za.day, int(aksam_[0]), int(aksam_[1]), 0)
                yatsi = datetime(s_za.year, s_za.month, s_za.day, int(yatsi_[0]), int(yatsi_[1]), 0)
                simdi = datetime(s_za.year, s_za.month, s_za.day, s_za.hour, s_za.minute, s_za.second)
                
                s1 = ''

                if simdi < imsak and simdi < gunes and simdi < ogle and simdi < ikindi and simdi < aksam and simdi < yatsi:
                    s1 = self.vakitler[0] + ":00"
                    strvakit = u"İmsak vaktine"
                    strdosya = "imsak"
                
                elif simdi > imsak and simdi < gunes and simdi < ogle and simdi < ikindi and simdi < aksam and simdi < yatsi:
                    s1 = self.vakitler[1] + ":00"
                    strvakit = u"Güneşin doğmasına"
                    strdosya = "gunes"                
                    
                elif simdi > imsak and simdi > gunes and simdi < ogle and simdi < ikindi and simdi < aksam and simdi < yatsi:
                    s1 = self.vakitler[2] + ":00"
                    strvakit = u"Öğle vaktine"
                    strdosya = "ogle"

                elif simdi > imsak and simdi > gunes and simdi > ogle and simdi < ikindi and simdi < aksam and simdi < yatsi:
                    s1 = self.vakitler[3] + ":00"
                    strvakit = u"İkindi vaktine"
                    strdosya = "ikindi"

                elif simdi > imsak and simdi > gunes and simdi > ogle and simdi > ikindi and simdi < aksam and simdi < yatsi:
                    s1 = self.vakitler[4] + ":00"
                    strvakit = u"Akşam vaktine"
                    strdosya = "aksam"

                elif simdi > imsak and simdi > gunes and simdi > ogle and simdi > ikindi and simdi > aksam and simdi < yatsi:
                    s1 = self.vakitler[5] + ":00"
                    strvakit = u"Yatsı vaktine"
                    strdosya = "yatsi"
                
                elif simdi > imsak and simdi > gunes and simdi > ogle and simdi > ikindi and simdi > aksam and simdi > yatsi:
                    s1 = self.vakitler[0] + ":00"
                    strvakit = u"İmsak vaktine"
                    strdosya = "imsak"
                
                
                
                

                s2 =strftime("%H:%M:%S")
                FMT = '%H:%M:%S'
                #try:
                #if datetime.strptime(s1, FMT) > datetime.strptime(s2, FMT):
                try:
                    zd = datetime.strptime(s1, FMT) - datetime.strptime(s2, FMT)
                    #else:
                    #    zd = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
                        
                    kalanzaman = str(zd).replace("-1 day, ", "")
                    
                    if kalanzaman == "0:45:00":
                        if ('kala_bildirim_sag_alt',) in self.ayarlar:
                            self.sira.put(lambda: Thread(target=self.bildirimPenceresiGoster, args=(u"Ezan Vakti - Uyarı", u"%s 45 dakika kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start())
                            """if name == "nt":
                                Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarı", u"%s 30 dakika kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start()
                            elif name == "posix":
                                system("notify-send %s" %(u"Ezan Vakti - Uyarı\n%s 30 dakika kaldı !" %strvakit))"""
                        
                        if ('kala_sesli_bildirim',) in self.ayarlar:
                            self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+sep+strdosya+"45dk.mp3","")).start())
                        #self.sira.put(lambda: self.muzik_cal("kaynaklar"+sep+strdosya+"30dk.mp3"))
                    
                    if kalanzaman.split(':')[1] == "30" and self.dvc(str(datetime.now().hour)) == self.dvc(s1.split(':')[0]) and kalanzaman.split(':')[2] == "00":
                        if ('kala_bildirim_sag_alt',) in self.ayarlar:
                            self.sira.put(lambda: Thread(target=self.bildirimPenceresiGoster, args=(u"Ezan Vakti - Uyarı", u"%s 30 dakika kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start())
                            """if name == "nt":
                                Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarı", u"%s 30 dakika kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start()
                            elif name == "posix":
                                system("notify-send %s" %(u"Ezan Vakti - Uyarı\n%s 30 dakika kaldı !" %strvakit))"""
                        
                        if ('kala_sesli_bildirim',) in self.ayarlar:
                            self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+sep+strdosya+"30dk.mp3","")).start())
                        #self.sira.put(lambda: self.muzik_cal("kaynaklar"+sep+strdosya+"30dk.mp3"))
                        
                    
                    if kalanzaman.split(':')[1] == "15" and self.dvc(str(datetime.now().hour)) == self.dvc(s1.split(':')[0]) and kalanzaman.split(':')[2] == "00":
                        if ('kala_bildirim_sag_alt',) in self.ayarlar:
                            self.sira.put(lambda: Thread(target=self.bildirimPenceresiGoster, args=(u"Ezan Vakti - Uyarı", u"%s 15 dakika kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start())
                            """if name == "nt":
                                Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarı", u"%s 15 dakika kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start()
                            elif name == "posix":
                                system("notify-send %s" %(u"Ezan Vakti - Uyarı\n%s 15 dakika kaldı !" %strvakit))"""
                            
                        
                        #self.sira.put(lambda: self.muzik_cal("kaynaklar"+sep+strdosya+"15dk.mp3"))
                        if ('kala_sesli_bildirim',) in self.ayarlar:
                            self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+sep+strdosya+"15dk.mp3","")).start())
                        
                    
                    if kalanzaman.split(':')[1] == "10" and self.dvc(str(datetime.now().hour)) == self.dvc(s1.split(':')[0]) and kalanzaman.split(':')[2] == "00":
                        if ('kala_bildirim_sag_alt',) in self.ayarlar:
                            self.sira.put(lambda: Thread(target=self.bildirimPenceresiGoster, args=(u"Ezan Vakti - Uyarı", u"%s 10 dakika kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start())
                            """if name == "nt":
                                Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarı", u"%s 10 dakika kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start()
                            elif name == "posix":
                                system("notify-send %s" %(u"Ezan Vakti - Uyarı\n%s 10 dakika kaldı !" %strvakit))"""
                            
                        #self.sira.put(lambda: self.muzik_cal("kaynaklar"+sep+strdosya+"10dk.mp3"))
                        if ('kala_sesli_bildirim',) in self.ayarlar:
                            self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+sep+strdosya+"10dk.mp3","")).start())
                    if kalanzaman == "0:05:00":
                        if ('kala_bildirim_sag_alt',) in self.ayarlar:
                            self.sira.put(lambda: Thread(target=self.bildirimPenceresiGoster, args=(u"Ezan Vakti - Uyarı", u"%s 5 dakika kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start())
                            """if name == "nt":
                                Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarı", u"%s 5 dakika kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start()
                            elif name == "posix":
                                system("notify-send %s" %(u"Ezan Vakti - Uyarı\n%s 5 dakika kaldı !" %strvakit))"""
                        #self.sira.put(lambda: self.muzik_cal("kaynaklar"+sep+strdosya+"5dk.mp3"))
                        if ('kala_sesli_bildirim',) in self.ayarlar:
                            self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+sep+strdosya+"5dk.mp3","")).start())
                    
                    if kalanzaman.split(':')[0] == "1" and kalanzaman.split(':')[1] == "00" and kalanzaman.split(':')[2] == "00":
                        if ('kala_bildirim_sag_alt',) in self.ayarlar:  
                            self.sira.put(lambda: Thread(target=self.bildirimPenceresiGoster, args=(u"Ezan Vakti - Uyarı", u"%s 1 saat kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start())
                            """if name == "nt":
                                Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarı", u"%s 1 saat kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start()
                            elif name == "posix":
                                system("notify-send %s" %(u"Ezan Vakti - Uyarı\n%s 1 saat kaldı !" %strvakit))"""
                        #self.sira.put(lambda: self.muzik_cal("kaynaklar"+sep+strdosya+"60dk.mp3"))
                        if ('kala_sesli_bildirim',) in self.ayarlar:
                            self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+sep+strdosya+"60dk.mp3","")).start())
                    
                    self.etk4["text"] = u"%s kalan zaman: %s" %(strvakit, kalanzaman)
                except: pass
                    
          
                sleep(1)
            else:
                break
    
    def liste_temizle(self):
        for i in self.t.get_children():
            self.t.delete(i)
    
    def sil(self):
    
        self.etk1.pack_forget()
    
    def muzik_durdur(self):
        pygame.mixer.music.stop()
        self.yinele = 0
    
    def muzik_duraklat(self):
        pygame.mixer.music.pause()
    
    def muzik_devam(self):
        pygame.mixer.music.unpause()
    
    def muzik_cal(self, muzik, komut=""):
        if self.calinanlar:
            if not ('ezan.mp3' in self.calinanlar[-1] or 'ezan2.mp3' in self.calinanlar[-1]):
                while pygame.mixer.music.get_busy():
                    self.pencere.after(1)
        if komut == "yinele":
            self.yinele = 1
        else:
            self.yinele = 0
        
        if self.yinele:
            self.calinanlar.append(muzik)
            #pygame.mixer.music.stop()
            pygame.mixer.music.load(muzik)
            pygame.mixer.music.play(-1)
       
        if not self.yinele:
            self.calinanlar.append(muzik)
            pygame.mixer.music.stop()
            pygame.mixer.music.load(muzik)
            pygame.mixer.music.play()
        
    
    def ezan_cal(self):
        self.sira.put(lambda: self.muzik_cal("kaynaklar"+sep+"ezan.mp3"))
        """pygame.mixer.music.load("ezan.mp3")
        pygame.mixer.music.play()
        self.pencere.after(60000, pygame.mixer.music.stop())"""
        #startfile("kaynaklar"+sep+"ezan.mp3")
    
    def yonlendir(self, muzik, komut=""):
        
        if komut == "" or not komut:
            self.sira.put(lambda: self.muzik_cal(muzik))
        else:
            self.sira.put(lambda: self.muzik_cal(muzik, komut))

    def uyaridenetim(self):
        while True:
            if self.Acik_:
                sleep(1)
                devam = 1
                try:
                    al =self.sira.get(block=False)
                    
                except:
                    pass
                else:
                    try:
                        self.pencere.after_idle(al)
                    except: pass

            else:
                devam = 0
                break
        if devam:
            self.pencere.after(300, self.uyaridenetim)
    
    """def PencereGoster(self, baslik, icerik):
        pencere = Toplevel()
        pencere.geometry("300x50")
        if name == "nt":
            pencere.iconbitmap("kaynaklar"+sep+"camii.ico")
        elif name == "posix":
            pencere.iconbitmap("@kaynaklar"+sep+"camii.xbm")
            
        pencere.title(baslik)
        etk = Label(pencere, text=icerik)
        etk.pack(expand=True, padx=20, pady=10)
        dug = Button(pencere, text="Tamam", command=lambda:pencere.destroy())
        dug.pack(side="bottom", fill=X, expand=True)
        self.ortala(pencere)"""
    
    def uyari(self, baslik, icerik, mp3=""):
        Thread(target=self.uyaridenetim).start()
        if ('ezan_sesli_bildirim',) in self.ayarlar:
            self.sira.put(lambda: Thread(target=self.yonlendir, args=(mp3,)).start())
        while pygame.mixer.music.get_busy():
            self.pencere.after(1)
        try:
            if self.ayarlar:
                print "758"
                print mp3
                if ('bip',) in self.ayarlar:
                    self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+sep+"bip.mp3",)).start())
                if ('ezan',) in self.ayarlar and not "gunes.mp3" in mp3:
                    
                    self.sira.put(lambda: Thread(target=self.ezan_cal).start())

                
                    """if name == "nt":
                        winsound.Beep(2500, 1000)
                    elif name=="posix":
                        system("beep -f 2500 -l 1000")"""
                """elif len(self.ayarlar) == 2:
                    self.sira.put(lambda: Thread(target=self.ezan_cal).start())
                    winsound.Beep(2500, 1000)"""
            else:
                pass
        except:pass
        #print self.ayarlar
        if ('ezan_bildirim_pencere',) in self.ayarlar:
            #print "evvvet"
            self.sira.put(lambda: PencereGoster(baslik, icerik))
        
        
        if self.gizli:
            #print "öö"
            self.sira.put(self.pencere.deiconify)
            #Thread(target=self.pencere.deiconify).start()
            self.gizli = 0
        """self.uyaripen = (showinfo(baslik, icerik))
        self.uyaripen = ()
        Thread(target=self.uyar, args=(baslik, icerik)).start()"""
    
    def bildirim_(self, a, b, c, d):
        if name == "nt":
            self.sira.put(lambda: Thread(target=bildirim.bildiri, args=(a, b, c, d)).start())
        elif name == "posix":
            system("notify-send %s" %(a+"\n"+b))
    
    def vakitdenetle(self):
        saat = self.saatcek()
        print self.vakitler
        if saat == self.vakitler[0]:
            #self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+sep+"imsak.mp3",)).start())
            self.sira.put(Thread(target=self.uyari, args=(u"Ezan Vakti - Uyarı", u"İmsak Vakti !","kaynaklar"+sep+"imsak.mp3")).start())
            #self.sira.put(lambda: self.muzik_cal("kaynaklar"+sep+"imsak.mp3"))
            if ('ezan_bildirim_sag_alt',) in self.ayarlar:
                self.sira.put(lambda: Thread(target=self.bildirimPenceresiGoster, args=(u"Ezan Vakti - Uyarı", u"İmsak Vakti !", "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start())
                """if name == "nt":
                    Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarı", u"İmsak Vakti !", "camii2.ico", "Ezan Vakti")).start()
                elif name == "posix":
                    system("notify-send %s" %(u"Ezan Vakti - Uyarı\nİmsak Vakti !"))"""
            
        elif saat == self.vakitler[1]:
            #self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+sep+"ogle.mp3",)).start())
            Thread(target=self.uyari, args=(u"Ezan Vakti - Uyarı", u"Güneş Doğdu !", "kaynaklar"+sep+"gunes.mp3")).start()
            #self.sira.put(lambda: self.muzik_cal("kaynaklar"+sep+"ogle.mp3"))
            if ('ezan_bildirim_sag_alt',) in self.ayarlar:
                self.sira.put(lambda: Thread(target=self.bildirimPenceresiGoster, args=(u"Ezan Vakti - Uyarı", u"Güneş Doğdu !", "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start())
                """if name == "nt":
                    Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarı", u"Güneş Doğdu !", "camii2.ico", "Ezan Vakti")).start()    
                elif name == "posix":
                    system("notify-send %s" %(u"Ezan Vakti - Uyarı\nGüneş Doğdu !"))"""
            
        elif saat == self.vakitler[2]:
            #self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+sep+"ogle.mp3",)).start())
            Thread(target=self.uyari, args=(u"Ezan Vakti - Uyarı", u"Öğle Vakti !", "kaynaklar"+sep+"ogle.mp3")).start()
            #self.sira.put(lambda: self.muzik_cal("kaynaklar"+sep+"ogle.mp3"))
            if ('ezan_bildirim_sag_alt',) in self.ayarlar:
                self.sira.put(lambda: Thread(target=self.bildirimPenceresiGoster, args=(u"Ezan Vakti - Uyarı", u"Öğle Vakti !", "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start())
                """if name == "nt":
                    Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarı", u"Öğle Vakti !", "camii2.ico", "Ezan Vakti")).start()
                elif name == "posix":
                    system("notify-send %s" %(u"Ezan Vakti - Uyarı\nÖğle Vakti !"))"""
            
            
        elif saat == self.vakitler[3]:
            #self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+sep+"ikindi.mp3",)).start())
            Thread(target=self.uyari, args=(u"Ezan Vakti - Uyarı", u"İkindi Vakti !", "kaynaklar"+sep+"ikindi.mp3")).start()
            #self.sira.put(lambda: self.muzik_cal("kaynaklar"+sep+"ikindi.mp3"))
            if ('ezan_bildirim_sag_alt',) in self.ayarlar:
                self.sira.put(lambda: Thread(target=self.bildirimPenceresiGoster, args=(u"Ezan Vakti - Uyarı", u"İkindi Vakti !", "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start())
                """if name == "nt":
                    Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarı", u"İkindi Vakti !", "camii2.ico", "Ezan Vakti")).start()
                elif name == "posix":
                    system("notify-send %s" %(u"Ezan Vakti - Uyarı\nİkindi Vakti !"))"""
            
            

            
        elif saat == self.vakitler[4]:
            #self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+sep+"aksam.mp3",)).start())
            Thread(target=self.uyari, args=(u"Ezan Vakti - Uyarı", u"Akşam Vakti !", "kaynaklar"+sep+"aksam.mp3")).start()
            #self.sira.put(lambda: self.muzik_cal("kaynaklar"+sep+"aksam.mp3"))
            
            if ('ezan_bildirim_sag_alt',) in self.ayarlar:
                self.sira.put(lambda: Thread(target=self.bildirimPenceresiGoster, args=(u"Ezan Vakti - Uyarı", u"Akşam Vakti !", "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start())
                """if name == "nt":
                    Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarı", u"Akşam Vakti !", "camii2.ico", "Ezan Vakti")).start()
                elif name == "posix":
                    system("notify-send %s" %(u"Ezan Vakti - Uyarı\nAkşam Vakti !"))"""
            

            
        elif saat == self.vakitler[5]:
            #self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+sep+"yatsi.mp3",)).start())
            Thread(target=self.uyari, args=(u"Ezan Vakti - Uyarı", u"Yatsı Vakti !", "kaynaklar"+sep+"yatsi.mp3")).start()
            #self.sira.put(lambda: self.muzik_cal("kaynaklar"+sep+"yatsi.mp3"))
            
            if ('ezan_bildirim_sag_alt',) in self.ayarlar:
                self.sira.put(lambda: Thread(target=self.bildirimPenceresiGoster, args=(u"Ezan Vakti - Uyarı", u"Yatsı Vakti !", "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start())
                """if name == "nt":
                    Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarı", u"Yatsı Vakti !", "camii2.ico", "Ezan Vakti")).start()
                elif name == "posix":
                    system("notify-send %s" %(u"Ezan Vakti - Uyarı\nYatsı Vakti !"))"""
            

            
    def baslangic_denetim(self):
        imsak_ = self.vakitler[0].split(':')
        gunes_ = self.vakitler[1].split(':')
        ogle_ = self.vakitler[2].split(':')
        ikindi_ = self.vakitler[3].split(':')
        aksam_ = self.vakitler[4].split(':')
        yatsi_ = self.vakitler[5].split(':')
        
        
        s_za = datetime.now()
                
        imsak = datetime(s_za.year, s_za.month, s_za.day, int(imsak_[0]), int(imsak_[1]), 0)
        gunes = datetime(s_za.year, s_za.month, s_za.day, int(gunes_[0]), int(gunes_[1]), 0)
        ogle = datetime(s_za.year, s_za.month, s_za.day, int(ogle_[0]), int(ogle_[1]), 0)
        ikindi = datetime(s_za.year, s_za.month, s_za.day, int(ikindi_[0]), int(ikindi_[1]), 0)
        aksam = datetime(s_za.year, s_za.month, s_za.day, int(aksam_[0]), int(aksam_[1]), 0)
        yatsi = datetime(s_za.year, s_za.month, s_za.day, int(yatsi_[0]), int(yatsi_[1]), 0)
        simdi = datetime(s_za.year, s_za.month, s_za.day, s_za.hour, s_za.minute, s_za.second)
        
        s1 = ''
        
        if simdi < imsak and simdi < gunes and simdi < ogle and simdi < ikindi and simdi < aksam and simdi < yatsi:
            s1 = self.vakitler[0] + ":00"
            strvakit = u"İmsak vaktine"
            strdosya = "imsak"
        
        elif simdi > imsak and simdi < gunes and simdi < ogle and simdi < ikindi and simdi < aksam and simdi < yatsi:
            s1 = self.vakitler[1] + ":00"
            strvakit = u"Güneşin doğmasına"
            strdosya = "gunes"                
            
        elif simdi > imsak and simdi > gunes and simdi < ogle and simdi < ikindi and simdi < aksam and simdi < yatsi:
            s1 = self.vakitler[2] + ":00"
            strvakit = u"Öğle vaktine"
            strdosya = "ogle"

        elif simdi > imsak and simdi > gunes and simdi > ogle and simdi < ikindi and simdi < aksam and simdi < yatsi:
            s1 = self.vakitler[3] + ":00"
            strvakit = u"İkindi vaktine"
            strdosya = "ikindi"

        elif simdi > imsak and simdi > gunes and simdi > ogle and simdi > ikindi and simdi < aksam and simdi < yatsi:
            s1 = self.vakitler[4] + ":00"
            strvakit = u"Akşam vaktine"
            strdosya = "aksam"

        elif simdi > imsak and simdi > gunes and simdi > ogle and simdi > ikindi and simdi > aksam and simdi < yatsi:
            s1 = self.vakitler[5] + ":00"
            strvakit = u"Yatsı vaktine"
            strdosya = "yatsi"
        
        elif simdi > imsak and simdi > gunes and simdi > ogle and simdi > ikindi and simdi > aksam and simdi > yatsi:
            s1 = self.vakitler[0] + ":00"
            strvakit = u"İmsak vaktine"
            strdosya = "imsak"
        
        

        s2 =strftime("%H:%M:%S")
        FMT = '%H:%M:%S'
        #try:
        #if datetime.strptime(s1, FMT) > datetime.strptime(s2, FMT):
        zd = datetime.strptime(s1, FMT) - datetime.strptime(s2, FMT)
        #else:
        #    zd = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
            
        kalanzaman = str(zd).replace("-1 day, ", "")
        
        if kalanzaman.startswith("0:29"):
        #if (kalanzaman.split(':')[1] == "29") and self.dvc(str(datetime.now().hour)) == self.dvc(s1.split(':')[0]):
            self.sira.put(lambda: Thread(target=self.bildirimPenceresiGoster, args=(u"Ezan Vakti - Uyarı", u"%s 30 dakika kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start())
            """if name == "nt":
                Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarı", u"%s 30 dakika kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start()
            elif name == "posix":
                system("notify-send %s" %(u"Ezan Vakti - Uyarı\n%s 30 dakika kaldı !"%strvakit))"""
            self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+sep+strdosya+"30dk.mp3","")).start())
        
        if kalanzaman.startswith("0:14"):
        #if (kalanzaman.split(':')[1] == "14") and self.dvc(str(datetime.now().hour)) == self.dvc(s1.split(':')[0]):
            self.sira.put(lambda: Thread(target=self.bildirimPenceresiGoster, args=(u"Ezan Vakti - Uyarı", u"%s 15 dakika kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start())
            """if name == "nt":
                Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarı", u"%s 15 dakika kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start()
            elif name == "posix":
                system("notify-send %s" %(u"Ezan Vakti - Uyarı\n%s 15 dakika kaldı !"%strvakit))"""
            self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+sep+strdosya+"15dk.mp3","")).start())
        
        if kalanzaman.startswith("0:09"):
        #if (kalanzaman.split(':')[1] == "09") and self.dvc(str(datetime.now().hour)) == self.dvc(s1.split(':')[0]):
            self.sira.put(lambda: Thread(target=self.bildirimPenceresiGoster, args=(u"Ezan Vakti - Uyarı", u"%s 10 dakika kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start())
            """if name == "nt":
                Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarı", u"%s 10 dakika kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start()
            elif name == "posix":
                system("notify-send %s" %(u"Ezan Vakti - Uyarı\n%s 10 dakika kaldı !"%strvakit))"""
            self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+sep+strdosya+"10dk.mp3","")).start())
        
        if kalanzaman.startswith("0:05"):
        #if (kalanzaman.split(':')[1] == "04") and self.dvc(str(datetime.now().hour)) == self.dvc(s1.split(':')[0]):
            self.sira.put(lambda: Thread(target=self.bildirimPenceresiGoster, args=(u"Ezan Vakti - Uyarı", u"%s 5 dakika kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start())
            """if name == "nt": 
                Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarı", u"%s 5 dakika kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start()
            elif name == "posix":
                system("notify-send %s" %(u"Ezan Vakti - Uyarı\n%s 5 dakika kaldı !"%strvakit))"""
            self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+sep+strdosya+"5dk.mp3","")).start())
        
        
        if kalanzaman.startswith("0:59"):
        #if kalanzaman.split(':')[0] == "0" and kalanzaman.split(':')[1] == "59":
            self.sira.put(lambda: Thread(target=self.bildirimPenceresiGoster, args=(u"Ezan Vakti - Uyarı", u"%s 1 saat kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start())
            """if name == "nt":
                Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarı", u"%s 1 saat kaldı !" %strvakit, "kaynaklar"+sep+"camii2.ico", "Ezan Vakti")).start()
            elif name == "posix":
                system("notify-send %s" %(u"Ezan Vakti - Uyarı\n%s 1 saat kaldı !"%strvakit))"""
            self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+sep+strdosya+"60dk.mp3","")).start())
        
        self.etk4["text"] = u"%s kalan zaman: %s" %(strvakit, kalanzaman)
        

    def saatcek(self, komut=None):
        if not komut:
            return str(datetime.now()).split(' ')[1].split('.')[0].strip()[:-3]
        elif komut == "tam":
            return str(datetime.now()).split(' ')[1].split('.')[0].strip()
    
    def tarihcek(self):
        tarih_ = str(datetime.now()).split(' ')[0].split('-')
        self.yil, self.ay, self.gun = tarih_
        tarih = "%s.%s.%s" %(self.gun, self.ay, self.yil)
        
        return tarih
    
    def tarihguncelle(self):
        tarih = self.tarihcek()
        self.im.execute("update sontarih set bilgi =?", ("%s.%s.%s" %(self.gun, self.ay, self.yil),))
        self.v.commit()
        veriler = self.im.execute("SELECT * FROM sontarih")
        vericek = self.im.fetchall()
        sontarih = vericek[0][0]
        if sontarih == tarih:
            self.vakitcek_d()
        else:
            pass
    
    
    def vakitcek(self, komut=None):
        showinfo(u"Vakitler Ayarlanıyor", u"Vakitler çekiliyor.")

        kodlar = urlopen("http://www.diyanet.gov.tr/tr/namazvakitleri").read()
        
        di_imsak = ".*?<span id=\"spImsak\">(.*?)</span>.*?"
        imsak = findall(di_imsak, kodlar)[0]
        
        di_gunes = ".*?<span id=\"spGunes\">(.*?)</span>.*?"
        gunes = findall(di_gunes, kodlar)[0]
        
        di_ogle = ".*?<span id=\"spOgle\">(.*?)</span>.*?"
        ogle = findall(di_ogle, kodlar)[0]
        
        di_ikindi = ".*?<span id=\"spIkindi\">(.*?)</span>.*?"
        ikindi = findall(di_ikindi, kodlar)[0]
        
        di_aksam = ".*?<span id=\"spAksam\">(.*?)</span>.*?"
        aksam = findall(di_aksam, kodlar)[0]
        
        di_yatsi = ".*?<span id=\"spYatsi\">(.*?)</span>.*?"
        yatsi = findall(di_yatsi, kodlar)[0]
        

        
        if not komut:
            self.im.execute("INSERT INTO vakitler VALUES(?, ?, ?, ?, ?, ?)", (imsak, gunes, ogle, ikindi, aksam, yatsi))
            self.v.commit()
            
        elif komut == "duzenle":
            self.im.execute("DROP TABLE vakitler")
            self.im.execute("CREATE TABLE vakitler(imsak, ogle, gunes, ikindi, aksam, yatsi)")
            self.im.execute("INSERT INTO vakitler VALUES (?, ?, ?, ?, ?, ?)",\
            (imsak, gunes,ogle, ikindi, aksam, yatsi))
            self.v.commit()
            """im.execute("SELECT * FROM vakitler")
            veriler = im.fetchall()
            im.execute("UPDATE vakitler SET imsak =? WHERE imsak =?", (imsak, veriler[0][0]))
            im.execute("UPDATE vakitler SET ogle =? WHERE ogle =?", (ogle, veriler[0][1]))
            im.execute("UPDATE vakitler SET ikindi =? WHERE ikindi =?", (ikindi, veriler[0][2]))
            im.execute("UPDATE vakitler SET aksam =? WHERE aksam =?", (aksam, veriler[0][3]))
            im.execute("UPDATE vakitler SET yatsi =? WHERE yatsi =?", (yatsi, veriler[0][4]))"""
            

        
        return (imsak, gunes, ogle, ikindi, aksam, yatsi)
        
    def vakitcek_d(self):
        veriler = self.vakitcek("duzenle")
        self.liste_temizle()
        self.t.insert("", 0, values=(veriler[0], veriler[1], veriler[2], veriler[3], veriler[4], veriler[5]))
        showinfo(u"Vakitler Ayarlandı", u"Vakitler başarıyla ayarlandı.")
        return veriler
    
    def goster(self):
        self.pencere.deiconify()
    
    def cikis(self):
        self.Acik = 0
        self.Acik_ = 0
        for i in self.pencereler:
            try:
                i.destroy()
            except: pass
        exit()

class Veritabani(object):
    def vtOku(self, tablo, im):
        im.execute("SELECT * FROM %s" %tablo)
        veriler = im.fetchall()
        return veriler

IPUCU = 'wx Sistem Cubugu'
RESIM = "kaynaklar"+sep+'camii.png'
        
class GCResim(TaskBarIcon):
    def __init__(self):
        
        super(GCResim, self).__init__()
        
        resim = IconFromBitmap(Bitmap(RESIM))
        self.SetIcon(resim)

        self.Bind(EVT_TASKBAR_LEFT_DOWN, self.SOL_TIKLAYINCA)
    
    def CreatePopupMenu(self):
        menu = Menu_wx()
        self.olustur(menu, u'Çıkış', self.cikis)
        return menu
    
    def olustur(self, menu, etiket, islev):
        nesne = MenuItem(menu, -1, etiket)
        menu.Bind(EVT_MENU, islev, id=nesne.GetId())
        menu.AppendItem(nesne)
        return nesne
    
    def SOL_TIKLAYINCA(self, olay):
        pass
    def cikis(self, olay):
        sys_exit()
        
        
if __name__ == "__main__":
    global pencere_
    pencere_ = Tk()
    u = UYGULAMA(pencere_)
    
    try:
        uyg = App()
        GCR = GCResim()
    except: pass
    #uyg.MainLoop()
    pencere_.mainloop()
    
