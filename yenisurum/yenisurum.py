#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Tkinter import *
import ttk, bildirim, wx

from datetime import datetime
from subprocess import check_output
import sqlite3, os, re, urllib, time, winsound, sys
from threading import Thread
from tkMessageBox import *
#check_output("chcp 1254", shell=True)
from Queue import Queue
import pygame
pygame.mixer.init()


class UYGULAMA(object):
    def __init__(self, pencere_):
        self.surum = "1.1"
        self.gizli = 0
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
        
        if not "veriler.vt" in os.listdir('.'):
            eklenecek = "%s.%s.%s" %(self.gun, self.ay,self.yil)
            self.v = sqlite3.connect("veriler.vt")
            self.v.text_factory = str
            self.im = self.v.cursor()
            self.im.execute("CREATE TABLE sontarih(bilgi)")
            self.im.execute("CREATE TABLE vakitler(imsak, ogle, ikindi, aksam, yatsi)")
            self.im.execute("CREATE TABLE ayarlar(bilgi)")
            self.im.execute("INSERT INTO ayarlar VALUES (?)", ('bos',))
            self.im.execute("INSERT INTO sontarih VALUES (?)", (eklenecek,))
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
            self.v = sqlite3.connect("veriler.vt")
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
                self.vakitcek_d()
                
        #pencere = win32console.GetConsoleWindow()
        #win32gui.ShowWindow(pencere, 0)
        self.im.execute("SELECT * FROM vakitler")
        self.vakitler = self.im.fetchall()
        self.vakitler = self.vakitler[0]
        
        self.liste_temizle()
        self.t.insert("", 0, values=(self.vakitler[0], self.vakitler[1], self.vakitler[2], self.vakitler[3], self.vakitler[4]))
        
        
        
        
        self.saat = self.saatcek()
        self.vakitdenetle()
        self.baslangic_denetim()
        self.tarih_al = self.tarihcek()
        
        Thread(target=self.saat_yenile).start()
        
        #Thread(target=self.denetim).start()
        #Thread(target=self.uyari, args=("", "")).start()
        
        Thread(target=self.uyaridenetim).start()
        #self.pencere.after(1, lambda: self.sira.put(lambda: Thread(target=self.guncellestirmeDenetim).start()))
        self.sira.put(self.guncellestirmeDenetim)
        
        
        #self.sira.put(lambda: Thread(target=self.guncellestirmeDenetim).start())
        
          
    def guncellestirmeDenetim(self, komut=""):
        print "a"
        if komut != "":
            showinfo(u"Güncelleþtirmeler Denetleniyor", u"Güncelleþtirmeler denetleniyor...")

        dosya = urllib.urlopen("https://raw.githubusercontent.com/millipardus/ezanvakitleri/master/surum.txt").read().strip()
        if dosya != self.surum and float(dosya) > float(self.surum):
            soru = askquestion(u"Yeni Bir Sürüm Var !", u"Yeni bir sürüm tespit edildi. Sürüm numarasý: %s\nYüklemek ister misiniz ?" %dosya)
            if soru == "yes":
                if sys.argv[0].endswith(".py"):
                    os.startfile("guncellestir.py")
                elif sys.argv[0].endswith(".exe"):
                    os.startfile("guncellestir.exe")
                exit()
        elif komut != "":
            showinfo(u"Yeni Sürüm Yok", u"Þu an güncel sürümü kullanýyorsunuz.")
                
                
        if komut == "":
            self.pencere.after(7200000, lambda: self.sira.put(self.guncellestirmeDenetim))
            #self.pencere.after(2000, lambda: self.sira.put(lambda: Thread(target=self.guncellestirmeDenetim).start()))
            
        
        
            
    def Arayuz(self):
        self.pencereler.append(self.pencere)
        self.pencere.iconbitmap("kaynaklar"+os.sep+"camii.ico")
        self.pencere.title(u"Ezan Vakitleri")
        #self.pencere.geometry("500x100")
        self.Dizilimlik = Menu(self.pencere)
        self.pencere.config(menu=self.Dizilimlik)
        
        self.komutlar = Menu(self.Dizilimlik, tearoff=0)
        self.dosya = Menu(self.Dizilimlik, tearoff=0)
        self.ayarlar_ = Menu(self.Dizilimlik, tearoff=0)
        
        self.Dizilimlik.add_cascade(label="Dosya", menu=self.dosya)
        self.Dizilimlik.add_cascade(label="Komutlar", menu=self.komutlar)
        self.Dizilimlik.add_cascade(label=u"Ayarlar", menu=self.ayarlar_)
        
        self.cerceve = Frame(self.pencere, height=100)
        
        self.komutlar.add_command(label="Vakitleri Çek ve Kaydet", command=self.vakitcek_d)
        self.komutlar.add_command(label="Gizle", command=self.pencere_gizle)
        self.komutlar.add_command(label=u"Güncelleþtirmeleri Denetle", command=lambda: Thread(target=self.guncellestirmeDenetim("komut")).start())
        self.dosya.add_command(label=u"Çýkýþ", command=self.cikis)
        self.ayarlar_.add_command(label=u"Seçenekler", command=self.Secenekler)
        
        self.etk1 = Label(text=u"Hoþgeldiniz !")
        self.etk2 = Label(text=u"Tarih: %s" %self.tarihcek(), font=("Arial", 20))
        self.etk3 = Label(text=u"Saat: ", font=("Arial", 20))
        self.etk4 = Label(text=u"", font=("Arial", 20))
        self.t = ttk.Treeview(self.cerceve)
        self.etk1.pack()
        self.etk2.pack()
        self.etk3.pack()
        self.etk4.pack()
        
        #self.saat_yenile()
        
        self.t["columns"] = ("imsak", "ogle", "ikindi", "aksam", "yatsi")
        
        self.t.column("imsak", width=100, anchor="center")
        self.t.column("ogle", width=100, anchor="center")
        self.t.column("ikindi", width=100, anchor="center")
        self.t.column("aksam", width=100, anchor="center")
        self.t.column("yatsi", width=100, anchor="center")
        
        self.t.heading("imsak", text=u"Ýmsak")
        self.t.heading("ogle", text=u"Öðle")
        self.t.heading("ikindi", text=u"Ýkindi")
        self.t.heading("aksam", text=u"Akþam")
        self.t.heading("yatsi", text=u"Yatsý")
        
        
        self.t["show"] = "headings"
        self.t.pack()
        self.cerceve.pack()
        
        self.pencere.protocol("WM_DELETE_WINDOW", self.cikis)
        self.pencere.after(1000, self.sil)
    
    def pencere_gizle(self):
        self.pencere.withdraw()
        self.gizli = 1
        #Thread(target=self.gizle).start()
    
    def gizle(self):
        pass
    
    def dvc(self, veri):
        return int(re.sub("^0+", "", veri))
    
    def son_vakit_denetim(self):
        imsak = self.vakitler[0].split(':')
        ogle = self.vakitler[1]
        ikindi = self.vakitler[2]
        aksam = self.vakitler[3]
        yatsi = self.vakitler[4]
        
        s_za = datetime.now()
        
        imsak = datetime(s_za.year, s_za.month, s_za.day, imsak[0].split(':')[0], imsak[0].split(':')[1])
        simdi = datetime(s_za.year, s_za.month, s_za.day, s_za.hour, s_za.minute)
        
        if simdi.time() < imsak.time():
            s1 = imsak+  ":00"
            s2 =time.strftime("%H:%M:%S")
            FMT = '%H:%M:%S'
            zd = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
            m, s = divmod(zd.seconds, 60)
            h,m = divmod(m,60)
            self.etk4["text"] = u"Ýmsaða kalan zaman: %s" %(str(h)+":"+str(m)+":"+str(s))
        
        
        
        
    def Secenekler(self):
        veriler = self.vt.vtOku("ayarlar", self.im)
        
        
        pencere = Toplevel()
        #pencere.geometry("500x500")
        pencere.title("Seçenekler")
        self.pencereler.append(pencere)
        
        self.o1 = IntVar()
        self.o2 = IntVar()
        

        
        self.o1.set(0)
        self.o2.set(0)

        if not veriler:
            pass
        else:
            if veriler[0][0] != "bos":
                if ('ezan',) in veriler:
                    self.o1.set(1)
                if ('bip',) in veriler:
                    self.o2.set(1)
        
        etk = Label(pencere, text=u"Ezan vakti geldiðinde;")
        
        onay= Checkbutton(pencere, text=u"Ezan oku", variable=self.o1)
        onay2=Checkbutton(pencere, text=u"Bip sesi çýkart", variable=self.o2)
        dug = Button(pencere, text=u"Ayarla", command=lambda: self.Ayarla(pencere))

        
        etk.pack()
        onay.pack()
        onay2.pack()
        dug.pack()

    
     
    def Ayarla(self, pencere):
        secenekler = []
        if self.o1.get() == 1:
            secenekler.append("ezan")
        if self.o2.get() == 1:
            secenekler.append("bip")
            
        try:
            self.im.execute("DROP TABLE ayarlar")
        except:
            pass
        self.im.execute("CREATE TABLE ayarlar (bilgi)")
        for i in secenekler:
            self.im.execute("INSERT INTO ayarlar VALUES (?)", (i,))
        self.v.commit()
        
        ayarlar = []
        for i in secenekler:
            ayarlar.append([i])
        
        self.ayarlar = ayarlar
        pencere.destroy()
        showinfo(u"Seçenekler Kaydedildi", u"Seçenekler baþarýyla kaydedildi.")
    
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
                os.system("cls")
                #print "Bugünün Tarihi: %s" %tarih
                self.vakitler = self.vakitcek_d()
            
            
            if self.saat != self.saatcek():
                self.saat = self.saatcek()
                self.vakitdenetle()
                #print self.saat
            
        else:
            devam=0
            
        if devam:
            print "devam. Þimdi iþlev tekrarlanacak."
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
                    os.system("cls")
                    #print "Bugünün Tarihi: %s" %tarih
                    self.vakitler = self.vakitcek_d()
            
            
                if self.saat != self.saatcek():
                    self.saat = self.saatcek()
                    self.vakitdenetle()
                    #print self.saat
                    
                saat= self.saatcek("tam")
                self.etk3["text"] = "Saat: %s" %saat
                imsak_ = self.vakitler[0].split(':')
                ogle_ = self.vakitler[1].split(':')
                ikindi_ = self.vakitler[2].split(':')
                aksam_ = self.vakitler[3].split(':')
                yatsi_ = self.vakitler[4].split(':')
                
                s_za = datetime.now()
                
                imsak = datetime(s_za.year, s_za.month, s_za.day, int(imsak_[0]), int(imsak_[1]), 0)
                ogle = datetime(s_za.year, s_za.month, s_za.day, int(ogle_[0]), int(ogle_[1]), 0)
                ikindi = datetime(s_za.year, s_za.month, s_za.day, int(ikindi_[0]), int(ikindi_[1]), 0)
                aksam = datetime(s_za.year, s_za.month, s_za.day, int(aksam_[0]), int(aksam_[1]), 0)
                yatsi = datetime(s_za.year, s_za.month, s_za.day, int(yatsi_[0]), int(yatsi_[1]), 0)
                simdi = datetime(s_za.year, s_za.month, s_za.day, s_za.hour, s_za.minute, s_za.second)
                
                s1 = ''

                if simdi < imsak and simdi < ogle and simdi < ikindi and simdi < aksam and simdi < yatsi:
                    s1 = self.vakitler[0] + ":00"
                    strvakit = u"Ýmsaða"
                    strdosya = "imsak"
                    
                    
                elif simdi > imsak and simdi < ogle and simdi < ikindi and simdi < aksam and simdi < yatsi:
                    s1 = self.vakitler[1] + ":00"
                    strvakit = u"Öðleye"
                    strdosya = "ogle"

                elif simdi > imsak and simdi > ogle and simdi < ikindi and simdi < aksam and simdi < yatsi:
                    s1 = self.vakitler[2] + ":00"
                    strvakit = u"Ýkindiye"
                    strdosya = "ikindi"

                elif simdi > imsak and simdi > ogle and simdi > ikindi and simdi < aksam and simdi < yatsi:
                    s1 = self.vakitler[3] + ":00"
                    strvakit = u"Akþama"
                    strdosya = "aksam"

                elif simdi > imsak and simdi > ogle and simdi > ikindi and simdi > aksam and simdi < yatsi:
                    s1 = self.vakitler[4] + ":00"
                    strvakit = u"Yatsýya"
                    strdosya = "yatsi"
                
                elif simdi > imsak and simdi > ogle and simdi > ikindi and simdi > aksam and simdi > yatsi:
                    s1 = self.vakitler[0] + ":00"
                    strvakit = u"Ýmsaða"
                    strdosya = "imsak"
                
                
                
                

                s2 =time.strftime("%H:%M:%S")
                FMT = '%H:%M:%S'
                #try:
                #if datetime.strptime(s1, FMT) > datetime.strptime(s2, FMT):
                try:
                    zd = datetime.strptime(s1, FMT) - datetime.strptime(s2, FMT)
                    #else:
                    #    zd = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
                        
                    kalanzaman = str(zd).replace("-1 day, ", "")
                    
                    if kalanzaman.split(':')[1] == "30" and self.dvc(str(datetime.now().hour)) == self.dvc(s1.split(':')[0]) and kalanzaman.split(':')[2] == "00":
                        Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarý", u"%s 30 dakika kaldý !" %strvakit, "kaynaklar"+os.sep+"camii2.ico", "Ezan Vakti")).start()
                        self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+os.sep+strdosya+"30dk.mp3",)).start())
                        #self.sira.put(lambda: self.muzik_cal("kaynaklar"+os.sep+strdosya+"30dk.mp3"))
                        
                    
                    if kalanzaman.split(':')[1] == "15" and self.dvc(str(datetime.now().hour)) == self.dvc(s1.split(':')[0]) and kalanzaman.split(':')[2] == "00":
                        Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarý", u"%s 15 dakika kaldý !" %strvakit, "kaynaklar"+os.sep+"camii2.ico", "Ezan Vakti")).start()
                        #self.sira.put(lambda: self.muzik_cal("kaynaklar"+os.sep+strdosya+"15dk.mp3"))
                        self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+os.sep+strdosya+"15dk.mp3",)).start())
                        
                    
                    if kalanzaman.split(':')[1] == "10" and self.dvc(str(datetime.now().hour)) == self.dvc(s1.split(':')[0]) and kalanzaman.split(':')[2] == "00":
                        Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarý", u"%s 10 dakika kaldý !" %strvakit, "kaynaklar"+os.sep+"camii2.ico", "Ezan Vakti")).start()
                        #self.sira.put(lambda: self.muzik_cal("kaynaklar"+os.sep+strdosya+"10dk.mp3"))
                        self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+os.sep+strdosya+"10dk.mp3",)).start())
                    if kalanzaman == "0:05:00":
                        Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarý", u"%s 5 dakika kaldý !" %strvakit, "kaynaklar"+os.sep+"camii2.ico", "Ezan Vakti")).start()
                        #self.sira.put(lambda: self.muzik_cal("kaynaklar"+os.sep+strdosya+"5dk.mp3"))
                        self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+os.sep+strdosya+"5dk.mp3",)).start())
                    
                    if kalanzaman.split(':')[0] == "1" and kalanzaman.split(':')[1] == "00" and kalanzaman.split(':')[2] == "00":
                        Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarý", u"%s 1 saat kaldý !" %strvakit, "kaynaklar"+os.sep+"camii2.ico", "Ezan Vakti")).start()
                        #self.sira.put(lambda: self.muzik_cal("kaynaklar"+os.sep+strdosya+"60dk.mp3"))
                        self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+os.sep+strdosya+"60.mp3",)).start())
                    
                    self.etk4["text"] = u"%s kalan zaman: %s" %(strvakit, kalanzaman)
                except: pass
                    
          
                time.sleep(1)
            else:
                break
    
    def liste_temizle(self):
        for i in self.t.get_children():
            self.t.delete(i)
    
    def sil(self):
        self.etk1["text"] = ""
    
    def muzik_cal(self, muzik):
        pygame.mixer.music.stop()
        pygame.mixer.music.load(muzik)
        pygame.mixer.music.play()
    
    def ezan_cal(self):
        self.sira.put(lambda: self.muzik_cal("kaynaklar"+os.sep+"ezan.mp3"))
        """pygame.mixer.music.load("ezan.mp3")
        pygame.mixer.music.play()
        self.pencere.after(60000, pygame.mixer.music.stop())"""
        #os.startfile("kaynaklar"+os.sep+"ezan.mp3")
    
    def yonlendir(self, muzik):
        self.sira.put(lambda: self.muzik_cal(muzik))

    def uyaridenetim(self):
        while True:
            if self.Acik_:
                time.sleep(1)
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
            self.pencere.after(100, self.uyaridenetim)
    
    def uyari(self, baslik, icerik, mp3=""):
        
        try:
            if self.ayarlar:
                if len(self.ayarlar) == 1:
                    if self.ayarlar[0][0] == "ezan":
                        Thread(target=self.uyaridenetim).start()
                        self.sira.put(lambda: Thread(target=self.ezan_cal).start())

                    elif self.ayarlar[0][0] == "bip":
                        winsound.Beep(2500, 1000)
                elif len(self.ayarlar) == 2:
                    self.sira.put(lambda: Thread(target=self.ezan_cal).start())
                    winsound.Beep(2500, 1000)
            else:
                pass
        except:pass
        print mp3
        
        self.sira.put(lambda: showinfo(baslik, icerik))
        
        if self.gizli:
            #print "öö"
            self.sira.put(self.pencere.deiconify)
            #Thread(target=self.pencere.deiconify).start()
            self.gizli = 0
        """self.uyaripen = (showinfo(baslik, icerik))
        self.uyaripen = ()
        Thread(target=self.uyar, args=(baslik, icerik)).start()"""
    
    def bildirim_(self, a, b, c, d):
        self.sira.put(lambda: Thread(target=bildirim.bildiri, args=(a, b, c, d)).start())
    
    def vakitdenetle(self):
        saat = self.saatcek()
        print self.vakitler
        if saat == self.vakitler[0]:
            Thread(target=self.uyari, args=(u"Ezan Vakti - Uyarý", u"Ýmsak Vakti !","kaynaklar"+os.sep+"imsak.mp3")).start()
            #self.sira.put(lambda: self.muzik_cal("kaynaklar"+os.sep+"imsak.mp3"))
            self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+os.sep+"imsak.mp3",)).start())
            Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarý", u"Ýmsak Vakti !", "camii2.ico", "Ezan Vakti")).start()
            
            
            
        elif saat == self.vakitler[1]:
            Thread(target=self.uyari, args=(u"Ezan Vakti - Uyarý", u"Öðle Vakti !", "kaynaklar"+os.sep+"ogle.mp3")).start()
            #self.sira.put(lambda: self.muzik_cal("kaynaklar"+os.sep+"ogle.mp3"))
            self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+os.sep+"ogle.mp3",)).start())
            Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarý", u"Öðle Vakti !", "camii2.ico", "Ezan Vakti")).start()
            
            
        elif saat == self.vakitler[2]:
            Thread(target=self.uyari, args=(u"Ezan Vakti - Uyarý", u"Ýkindi Vakti !", "kaynaklar"+os.sep+"ikindi.mp3")).start()
            #self.sira.put(lambda: self.muzik_cal("kaynaklar"+os.sep+"ikindi.mp3"))
            self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+os.sepa+"ikindi.mp3",)).start())
            Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarý", u"Ýkindi Vakti !", "camii2.ico", "Ezan Vakti")).start()
            
            

            
        elif saat == self.vakitler[3]:
            Thread(target=self.uyari, args=(u"Ezan Vakti - Uyarý", u"Akþam Vakti !", "kaynaklar"+os.sep+"aksam.mp3")).start()
            #self.sira.put(lambda: self.muzik_cal("kaynaklar"+os.sep+"aksam.mp3"))
            self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+os.sep+"aksam.mp3",)).start())
            Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarý", u"Akþam Vakti !", "camii2.ico", "Ezan Vakti")).start()
            

            
        elif saat == self.vakitler[4]:
            Thread(target=self.uyari, args=(u"Ezan Vakti - Uyarý", u"Yatsý Vakti !", "kaynaklar"+os.sep+"yatsi.mp3")).start()
            #self.sira.put(lambda: self.muzik_cal("kaynaklar"+os.sep+"yatsi.mp3"))
            self.sira.put(lambda: Thread(target=self.yonlendir, args=("kaynaklar"+os.sep+"yatsi.mp3",)).start())
            Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarý", u"Yatsý Vakti !", "camii2.ico", "Ezan Vakti")).start()
            

            
    def baslangic_denetim(self):
        imsak_ = self.vakitler[0].split(':')
        ogle_ = self.vakitler[1].split(':')
        ikindi_ = self.vakitler[2].split(':')
        aksam_ = self.vakitler[3].split(':')
        yatsi_ = self.vakitler[4].split(':')
        
        
        s_za = datetime.now()
                
        imsak = datetime(s_za.year, s_za.month, s_za.day, int(imsak_[0]), int(imsak_[1]), 0)
        ogle = datetime(s_za.year, s_za.month, s_za.day, int(ogle_[0]), int(ogle_[1]), 0)
        ikindi = datetime(s_za.year, s_za.month, s_za.day, int(ikindi_[0]), int(ikindi_[1]), 0)
        aksam = datetime(s_za.year, s_za.month, s_za.day, int(aksam_[0]), int(aksam_[1]), 0)
        yatsi = datetime(s_za.year, s_za.month, s_za.day, int(yatsi_[0]), int(yatsi_[1]), 0)
        simdi = datetime(s_za.year, s_za.month, s_za.day, s_za.hour, s_za.minute, s_za.second)
        
        s1 = ''

        if simdi < imsak and simdi < ogle and simdi < ikindi and simdi < aksam and simdi < yatsi:
            s1 = self.vakitler[0] + ":00"
            strvakit = u"Ýmsaða"            
        elif simdi > imsak and simdi < ogle and simdi < ikindi and simdi < aksam and simdi < yatsi:
            s1 = self.vakitler[1] + ":00"
            strvakit = u"Öðleye"

        elif simdi > imsak and simdi > ogle and simdi < ikindi and simdi < aksam and simdi < yatsi:
            s1 = self.vakitler[2] + ":00"
            strvakit = u"Ýindiye"

        elif simdi > imsak and simdi > ogle and simdi > ikindi and simdi < aksam and simdi < yatsi:
            s1 = self.vakitler[3] + ":00"
            strvakit = u"Akþama"

        elif simdi > imsak and simdi > ogle and simdi > ikindi and simdi > aksam and simdi < yatsi:
            s1 = self.vakitler[4] + ":00"
            strvakit = u"Yatsýya"
        
        elif simdi > imsak and simdi > ogle and simdi > ikindi and simdi > aksam and simdi > yatsi:
            s1 = self.vakitler[0] + ":00"
            strvakit = u"Ýmsaða"
        
        
        

        s2 =time.strftime("%H:%M:%S")
        FMT = '%H:%M:%S'
        #try:
        #if datetime.strptime(s1, FMT) > datetime.strptime(s2, FMT):
        zd = datetime.strptime(s1, FMT) - datetime.strptime(s2, FMT)
        #else:
        #    zd = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)
            
        kalanzaman = str(zd).replace("-1 day, ", "")
        
        if (kalanzaman.split(':')[1] == "29") and self.dvc(str(datetime.now().hour)) == self.dvc(s1.split(':')[0]):
            Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarý", u"%s 30 dakika kaldý !" %strvakit, "kaynaklar"+os.sep+"camii2.ico", "Ezan Vakti")).start()
        
        if (kalanzaman.split(':')[1] == "14") and self.dvc(str(datetime.now().hour)) == self.dvc(s1.split(':')[0]):
            Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarý", u"%s 15 dakika kaldý !" %strvakit, "kaynaklar"+os.sep+"camii2.ico", "Ezan Vakti")).start()
        
        if (kalanzaman.split(':')[1] == "09") and self.dvc(str(datetime.now().hour)) == self.dvc(s1.split(':')[0]):
            Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarý", u"%s 10 dakika kaldý !" %strvakit, "kaynaklar"+os.sep+"camii2.ico", "Ezan Vakti")).start()
        
        if (kalanzaman.split(':')[1] == "04") and self.dvc(str(datetime.now().hour)) == self.dvc(s1.split(':')[0]):
            Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarý", u"%s 5 dakika kaldý !" %strvakit, "kaynaklar"+os.sep+"camii2.ico", "Ezan Vakti")).start()
        
        if kalanzaman.split(':')[0] == "0" and kalanzaman.split(':')[1] == "59":
            Thread(target=bildirim.bildiri, args=(u"Ezan Vakti - Uyarý", u"%s 1 saat kaldý !" %strvakit, "kaynaklar"+os.sep+"camii2.ico", "Ezan Vakti")).start()
        
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
            self.vakitcek_d("duzenle")
        else:
            pass
    
    
    def vakitcek(self, komut=None):
        showinfo(u"Vakitler Ayarlanýyor", u"Vakitler çekiliyor.")

        kodlar = urllib.urlopen("http://www.diyanet.gov.tr/tr/namazvakitleri").read()
        
        di_imsak = ".*?<span id=\"spImsak\">(.*?)</span>.*?"
        imsak = re.findall(di_imsak, kodlar)[0]
        
        di_ogle = ".*?<span id=\"spOgle\">(.*?)</span>.*?"
        ogle = re.findall(di_ogle, kodlar)[0]
        
        di_ikindi = ".*?<span id=\"spIkindi\">(.*?)</span>.*?"
        ikindi = re.findall(di_ikindi, kodlar)[0]
        
        di_aksam = ".*?<span id=\"spAksam\">(.*?)</span>.*?"
        aksam = re.findall(di_aksam, kodlar)[0]
        
        di_yatsi = ".*?<span id=\"spYatsi\">(.*?)</span>.*?"
        yatsi = re.findall(di_yatsi, kodlar)[0]
        

        
        if not komut:
            self.im.execute("INSERT INTO vakitler VALUES(?, ?, ?, ?, ?)", (imsak, ogle, ikindi, aksam, yatsi))
            self.v.commit()
            
        elif komut == "duzenle":
            self.im.execute("DROP TABLE vakitler")
            self.im.execute("CREATE TABLE vakitler(imsak, ogle, ikindi, aksam, yatsi)")
            self.im.execute("INSERT INTO vakitler VALUES (?, ?, ?, ?, ?)",\
            (imsak, ogle, ikindi, aksam, yatsi))
            self.v.commit()
            """im.execute("SELECT * FROM vakitler")
            veriler = im.fetchall()
            im.execute("UPDATE vakitler SET imsak =? WHERE imsak =?", (imsak, veriler[0][0]))
            im.execute("UPDATE vakitler SET ogle =? WHERE ogle =?", (ogle, veriler[0][1]))
            im.execute("UPDATE vakitler SET ikindi =? WHERE ikindi =?", (ikindi, veriler[0][2]))
            im.execute("UPDATE vakitler SET aksam =? WHERE aksam =?", (aksam, veriler[0][3]))
            im.execute("UPDATE vakitler SET yatsi =? WHERE yatsi =?", (yatsi, veriler[0][4]))"""
            

        
        return (imsak, ogle, ikindi, aksam, yatsi)
        
    def vakitcek_d(self):
        veriler = self.vakitcek("duzenle")
        self.liste_temizle()
        self.t.insert("", 0, values=(veriler[0], veriler[1], veriler[2], veriler[3], veriler[4]))
        showinfo(u"Vakitler Ayarlandý", u"Vakitler baþarýyla ayarlandý.")
        return veriler
    
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

IPUCU = u'Ezan Vakitleri'
RESIM = "kaynaklar"+os.sep+'camii.png'
        
class GCResim(wx.TaskBarIcon):
    def __init__(self):
        
        super(GCResim, self).__init__()
        
        resim = wx.IconFromBitmap(wx.Bitmap(RESIM))
        self.SetIcon(resim)

        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.SOL_TIKLAYINCA)
    
    def CreatePopupMenu(self):
        menu = wx.Menu()
        self.olustur(menu, u'Çýkýþ', self.cikis)
        return menu
    
    def olustur(self, menu, etiket, islev):
        nesne = wx.MenuItem(menu, -1, etiket)
        menu.Bind(wx.EVT_MENU, islev, id=nesne.GetId())
        menu.AppendItem(nesne)
        return nesne
    
    def SOL_TIKLAYINCA(self, olay):
        print "ae"
        global pencere_ana_
        #if self.gizli:
        #    print "evet"
        pencere_ana_.deiconify()
    def cikis(self, olay):
        sys.exit()
        
        
if __name__ == "__main__":
    global pencere_
    pencere_ = Tk()
    u = UYGULAMA(pencere_)
    
    uyg = wx.App()
    GCR = GCResim()
    #uyg.MainLoop()
    pencere_.mainloop()
    