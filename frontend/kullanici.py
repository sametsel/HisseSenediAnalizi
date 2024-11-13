import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from mysql.connector import Error, connect
import os
import subprocess

def create_db_connection():
    try:
        conn = connect(
            host="localhost",
            user="root",
            password="123456",
            database="userdb"
        )
        return conn
    except Error as e:
        messagebox.showerror("Veritabanı Hatası", f"Veritabanı bağlantısı kurulamadı: {e}")
        return None

def kayit_ol():
    username = kullanici_adi_girisi.get()
    password = sifre_girisi.get()

    if not username or not password:
        messagebox.showerror("Hata", "Kullanıcı adı ve şifre boş bırakılamaz.")
        return

    conn = create_db_connection()
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            messagebox.showinfo("Başarılı", "Kayıt başarılı.")
        except Error as e:
            messagebox.showerror("Hata", f"Kayıt sırasında bir hata oluştu: {e}")
        finally:
            cursor.close()
            conn.close()

def giris_yap():
    username = kullanici_adi_girisi.get()
    password = sifre_girisi.get()

    if not username or not password:
        messagebox.showerror("Hata", "Kullanıcı adı ve şifre boş bırakılamaz.")
        return

    conn = create_db_connection()
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            result = cursor.fetchone()
            if result:
                messagebox.showinfo("Başarılı", "Giriş başarılı.")
                pencere.destroy()  # Mevcut pencereyi kapat
                subprocess.Popen(["python", "D://HisseSenediAnalizi//frontend//aa.py"])  # aa.py dosyasını çalıştır
            else:
                messagebox.showerror("Hata", "Kullanıcı adı veya şifre yanlış.")
        except Error as e:
            messagebox.showerror("Hata", f"Giriş sırasında bir hata oluştu: {e}")
        finally:
            cursor.close()
            conn.close()

def update_background(event):
    global background_image, original_image
    new_width = event.width
    new_height = event.height
    resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)
    background_image = ImageTk.PhotoImage(resized_image)
    background_label.config(image=background_image)
    background_label.image = background_image  # Arka plan resmini güncellemek için referansı koruma
    center_widgets()

def center_widgets():
    frame.place(relx=0.5, rely=0.5, anchor='center')

def main():
    global original_image, background_label, background_image, kullanici_adi_girisi, sifre_girisi, frame, pencere

    pencere = tk.Tk()
    pencere.title("Dinamik Arka Plan Resmi")
    pencere.geometry("800x600")

    original_image = Image.open("D://HisseSenediAnalizi//frontend//arkaplan.jpeg")
    background_image = ImageTk.PhotoImage(original_image.resize((800, 600), Image.LANCZOS))
        
    background_label = tk.Label(pencere, image=background_image)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    pencere.bind("<Configure>", update_background)
    
    frame = tk.Frame(pencere, bg="white")
    center_widgets()
    
    kullanici_adi_etiketi = tk.Label(frame, text="Kullanıcı Adı:", bg="white")
    kullanici_adi_etiketi.grid(row=0, column=0, padx=10, pady=10)

    kullanici_adi_girisi = tk.Entry(frame)
    kullanici_adi_girisi.grid(row=0, column=1, padx=10)
    
    sifre_etiketi = tk.Label(frame, text="Şifre:", bg="white")
    sifre_etiketi.grid(row=1, column=0, padx=10, pady=10)

    sifre_girisi = tk.Entry(frame, show="*")
    sifre_girisi.grid(row=1, column=1, padx=10)

    giris_yap_butonu = tk.Button(frame, text="Giriş Yap", command=giris_yap)
    giris_yap_butonu.grid(row=2, column=0, padx=5, pady=10)
    
    kayit_ol_butonu = tk.Button(frame, text="Kayıt Ol", command=kayit_ol)
    kayit_ol_butonu.grid(row=2, column=1, padx=5, pady=10)

    pencere.mainloop()

if __name__ == "__main__":
    main()
