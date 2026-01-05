import tkinter as tk
from tkinter import messagebox
import secrets
import string

# ================== KONFIGURASI ==================
BG_COLOR = "#FFFFFF"
PRIMARY_COLOR = "#1976D2"
SUCCESS_COLOR = "#4CAF50"
ERROR_COLOR = "#D32F2F"
FONT_BOLD = ("Arial", 10, "bold")
CODE_TIMEOUT = 30  # detik

# ================== SECURITY ==================
def generate_dynamic_code(length=6):
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

# ================== FORMAT RUPIAH ==================
def format_rupiah(event=None):
    value = entry_jumlah.get().replace("Rp", "").replace(",", "").strip()
    if value.isdigit():
        entry_jumlah.delete(0, tk.END)
        entry_jumlah.insert(0, f"Rp {int(value):,}")

# ================== PROSES AKHIR ==================
def execute_final_process(tujuan, jumlah):
    status_log.config(text=f"[ SUKSES] Data dikirim ke {tujuan}", fg=SUCCESS_COLOR)
    messagebox.showinfo(
        "SUKSES",
        f"Transaksi {jumlah} berhasil dikirim dengan aman."
    )
    entry_tujuan.delete(0, tk.END)
    entry_jumlah.delete(0, tk.END)

# ================== MODAL VERIFIKASI ==================
def start_verification_modal(tujuan, jumlah):
    secret_code = generate_dynamic_code()
    attempts_left = 3
    time_left = CODE_TIMEOUT
    expired = False

    modal = tk.Toplevel(root)
    modal.title("SECURITY CHECKPOINT")
    modal.geometry("400x300")
    modal.config(bg=BG_COLOR)
    modal.resizable(False, False)
    modal.grab_set()

    tk.Label(
        modal,
        text="VERIFIKASI KEAMANAN",
        font=("Arial", 12, "bold"),
        fg=ERROR_COLOR,
        bg=BG_COLOR
    ).pack(pady=10)

    tk.Label(modal, text="Kode Verifikasi:", bg=BG_COLOR).pack()

    tk.Label(
        modal,
        text=secret_code,
        font=("Helvetica", 32, "bold"),
        fg=PRIMARY_COLOR,
        bg="white",
        width=8,
        relief=tk.RIDGE
    ).pack(pady=10)

    countdown_label = tk.Label(
        modal,
        text=f" Sisa waktu: {time_left} detik",
        fg=ERROR_COLOR,
        bg=BG_COLOR,
        font=("Arial", 10, "bold")
    )
    countdown_label.pack()

    entry_kode = tk.Entry(modal, font=("Arial", 14), justify="center", width=10)
    entry_kode.pack(pady=5)
    entry_kode.focus()

    # ================== COUNTDOWN ==================
    def countdown():
        nonlocal time_left, expired
        if expired:
            return
        time_left -= 1
        if time_left <= 0:
            expired = True
            status_log.config(text="[ TIMEOUT] Kode kedaluwarsa", fg=ERROR_COLOR)
            messagebox.showerror("Timeout", "Waktu verifikasi habis.")
            modal.destroy()
        else:
            countdown_label.config(text=f" Sisa waktu: {time_left} detik")
            modal.after(1000, countdown)

    modal.after(1000, countdown)

    # ================== VERIFIKASI ==================
    def verify():
        nonlocal attempts_left, expired
        if expired:
            return

        if entry_kode.get().strip() == secret_code:
            expired = True
            modal.destroy()
            status_log.config(text="[STATUS] Verifikasi berhasil", fg=PRIMARY_COLOR)
            execute_final_process(tujuan, jumlah)
        else:
            attempts_left -= 1
            if attempts_left <= 0:
                expired = True
                status_log.config(text="[ BLOKIR] Percobaan habis", fg=ERROR_COLOR)
                messagebox.showerror("Blokir", "Terlalu banyak percobaan.")
                modal.destroy()
            else:
                messagebox.showwarning(
                    "Kode Salah",
                    f"Kode salah. Sisa percobaan: {attempts_left}"
                )

    tk.Button(
        modal,
        text="VERIFIKASI",
        command=verify,
        bg=SUCCESS_COLOR,
        fg="white",
        font=FONT_BOLD
    ).pack(pady=10)

    modal.bind("<Return>", lambda e: verify())
    root.wait_window(modal)

# ================== TAHAP 1 ==================
def start_transaction():
    tujuan = entry_tujuan.get().strip()
    jumlah_raw = entry_jumlah.get().replace("Rp", "").replace(",", "").strip()

    if not tujuan or not jumlah_raw:
        messagebox.showwarning("Peringatan", "Semua kolom harus diisi.")
        return

    if not jumlah_raw.isdigit() or int(jumlah_raw) <= 0:
        messagebox.showwarning("Peringatan", "Jumlah transaksi tidak valid.")
        return

    jumlah = f"Rp {int(jumlah_raw):,}"

    status_log.config(text="[STATUS] Memulai verifikasi keamanan...", fg=PRIMARY_COLOR)
    start_verification_modal(tujuan, jumlah)

# ================== UI ==================
root = tk.Tk()
root.title("Aplikasi Transaksi Aman - PBL")
root.geometry("500x400")
root.config(bg=BG_COLOR)

header = tk.Frame(root, bg=PRIMARY_COLOR, pady=10)
header.pack(fill="x")

tk.Label(
    header,
    text="SISTEM TRANSAKSI DATA BERLAPIS AMAN",
    fg="white",
    bg=PRIMARY_COLOR,
    font=("Arial", 14, "bold")
).pack()

form = tk.Frame(root, bg="white", padx=20, pady=20, relief=tk.SUNKEN, bd=1)
form.pack(pady=20, padx=20, fill="x")

tk.Label(form, text="Rekening Tujuan:", bg="white", font=FONT_BOLD).grid(row=0, column=0, sticky="w")
entry_tujuan = tk.Entry(form, width=30)
entry_tujuan.grid(row=0, column=1, pady=5)

tk.Label(form, text="Jumlah Transaksi:", bg="white", font=FONT_BOLD).grid(row=1, column=0, sticky="w")
entry_jumlah = tk.Entry(form, width=30)
entry_jumlah.grid(row=1, column=1, pady=5)
entry_jumlah.bind("<KeyRelease>", format_rupiah)

tk.Button(
    root,
    text="Mulai Transaksi",
    command=start_transaction,
    bg=PRIMARY_COLOR,
    fg="white",
    font=("Arial", 12, "bold")
).pack(pady=10)

tk.Label(root, text="LOG STATUS:", bg=BG_COLOR, font=FONT_BOLD).pack()
status_log = tk.Label(root, text="Menunggu input transaksi...", bg=BG_COLOR, fg="grey")
status_log.pack()

root.mainloop()
