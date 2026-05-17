import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import customtkinter as ctk


# ==========================================================
# PALETA DE COLORES
# ==========================================================
BG_APP        = "#1a1a1a"
BG_SURFACE    = "#222222"
BG_SURFACE2   = "#1e1e1e"
BG_CHIP       = "#222222"
BG_CHIP_ON    = "#2e2e2e"
BG_BTN        = "#2c2c2c"
BG_BTN_HOV    = "#333333"
BG_RESIZE_BTN = "#333333"
BG_LOG        = "#181818"

BORDER        = "#2e2e2e"
BORDER2       = "#333333"
BORDER3       = "#3a3a3a"

TXT_PRIMARY   = "#e8e8e8"
TXT_SECONDARY = "#bbbbbb"
TXT_MUTED     = "#666666"
TXT_HINT      = "#444444"
TXT_LABEL     = "#555555"
TXT_LOG_OK    = "#6a6a6a"
TXT_LOG_SKIP  = "#505050"
TXT_FOOTER    = "#383838"


# ==========================================================
# TAMAÑOS PREDEFINIDOS
# ==========================================================
PRESET_SIZES = [
    ("120 × 120 px", (120, 120)),
    ("320 × 320 px", (320, 320)),
    ("100 × 100 px", (100, 100)),
    ("Custom",        None),
]

EXT_MAP = {
    "All formats": [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"],
    "PNG":         [".png"],
    "JPG":         [".jpg", ".jpeg"],
    "WEBP":        [".webp"],
    "BMP":         [".bmp"],
    "TIFF":        [".tiff", ".tif"],
}


# ==========================================================
# FUNCIÓN DE REDIMENSIONADO
# ==========================================================
def redimensionar_imagenes(entradas, carpeta_salida, ancho, alto,
                            callback_progreso, callback_log, callback_fin,
                            ignorar_menores=False):
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    total    = len(entradas)
    ok       = 0
    errores  = 0
    omitidas = 0

    for i, ruta_entrada in enumerate(entradas):
        nombre_archivo = os.path.basename(ruta_entrada)
        nombre_base, ext = os.path.splitext(nombre_archivo)
        ruta_salida = os.path.join(carpeta_salida, nombre_base + ext)

        try:
            img = Image.open(ruta_entrada)

            if ignorar_menores and img.width <= ancho and img.height <= alto:
                omitidas += 1
                callback_log(
                    f"⏭  Skipped ({img.width}×{img.height}px ≤ {ancho}×{alto}px): {nombre_archivo}\n",
                    "skip"
                )
                callback_progreso((i + 1) / total, i + 1, total)
                continue

            img = img.convert("RGBA")
            ratio   = min(ancho / img.width, alto / img.height)
            nuevo_w = round(img.width  * ratio)
            nuevo_h = round(img.height * ratio)
            img = img.resize((nuevo_w, nuevo_h), Image.LANCZOS)

            lienzo   = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
            offset_x = (ancho - nuevo_w) // 2
            offset_y = (alto  - nuevo_h) // 2
            lienzo.paste(img, (offset_x, offset_y), img)

            ext_lower = ext.lower()
            if ext_lower in (".jpg", ".jpeg"):
                fondo = Image.new("RGB", (ancho, alto), (255, 255, 255))
                fondo.paste(lienzo, mask=lienzo.split()[3])
                fondo.save(ruta_salida, "JPEG", quality=95)
            elif ext_lower == ".bmp":
                fondo = Image.new("RGB", (ancho, alto), (255, 255, 255))
                fondo.paste(lienzo, mask=lienzo.split()[3])
                fondo.save(ruta_salida, "BMP")
            elif ext_lower == ".webp":
                lienzo.save(ruta_salida, "WEBP", quality=95)
            elif ext_lower in (".tiff", ".tif"):
                lienzo.save(ruta_salida, "TIFF")
            else:
                lienzo.save(ruta_salida, "PNG")

            ok += 1
            callback_log(f"✓  {nombre_archivo}  →  {ancho}×{alto}px\n", "ok")

        except Exception as e:
            errores += 1
            callback_log(f"✗  Error: {nombre_archivo}: {e}\n", "error")

        callback_progreso((i + 1) / total, i + 1, total)

    callback_fin(ok, errores, omitidas)


# ==========================================================
# WIDGETS PERSONALIZADOS
# ==========================================================
class DarkEntry(ctk.CTkEntry):
    def __init__(self, master, S, **kwargs):
        super().__init__(
            master,
            fg_color=BG_SURFACE,
            border_color=BORDER2,
            border_width=1,
            text_color=TXT_SECONDARY,
            placeholder_text_color=TXT_MUTED,
            corner_radius=S(7),
            font=("Segoe UI", S(12)),
            height=S(36),
            **kwargs
        )


class DarkButton(ctk.CTkButton):
    def __init__(self, master, S, **kwargs):
        super().__init__(
            master,
            fg_color=BG_BTN,
            hover_color=BG_BTN_HOV,
            border_color=BORDER3,
            border_width=1,
            text_color=TXT_SECONDARY,
            corner_radius=S(7),
            font=("Segoe UI", S(12)),
            height=S(36),
            **kwargs
        )


class SectionLabel(ctk.CTkLabel):
    def __init__(self, master, text, S, **kwargs):
        super().__init__(
            master,
            text=text.upper(),
            font=("Segoe UI", S(10)),
            text_color=TXT_LABEL,
            **kwargs
        )


class Divider(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, height=1, fg_color=BORDER, **kwargs)


# ==========================================================
# INTERFAZ PRINCIPAL
# ==========================================================
class AteneaResizer(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=BG_APP)

        # ── Escala DPI ──────────────────────────────────────
        # Obtenemos el DPI real del monitor y calculamos un factor
        # relativo a 96 dpi (referencia 1080p estándar).
        self.update_idletasks()
        dpi    = self.winfo_fpixels("1i")          # píxeles por pulgada reales
        self._sf = dpi / 96.0                      # scale factor

        # Tamaño de ventana: 38% del ancho de pantalla, máx 700 lógicos
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        win_w = min(int(sw * 0.38), int(700 * self._sf))
        win_h = int(sh * 0.64)
        x = (sw - win_w) // 2
        y = (sh - win_h) // 2

        self.title("Atenea Image Resizer")
        self.geometry(f"{win_w}x{win_h}+{x}+{y}")
        self.resizable(False, False)
        self._win_w = win_w

        self.selected_files  = []
        self.selected_preset = 1
        self._set_icon()
        self._build_ui()

    # Función de escala: convierte unidades "base 96dpi" a píxeles reales
    def S(self, value):
        return max(1, int(round(value * self._sf)))

    # ----------------------------------------------------------
    def _set_icon(self):
        ico_path = self._resource("logo.ico")
        png_path = self._resource("logo.png")
        if os.path.exists(ico_path):
            try:
                self.iconbitmap(ico_path)
            except Exception:
                pass
        if os.path.exists(png_path):
            try:
                logo_tk = ImageTk.PhotoImage(Image.open(png_path))
                self.iconphoto(True, logo_tk)
            except Exception:
                pass

    # ----------------------------------------------------------
    def _build_ui(self):
        S   = self.S
        pad = {"padx": S(28)}
        inner_w = self._win_w - S(56)   # ancho disponible descontando padx×2

        # ── HEADER ──────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=S(28), pady=(S(24), 0))

        logo_path = self._resource("logo.png")
        if os.path.exists(logo_path):
            try:
                logo_img = ctk.CTkImage(Image.open(logo_path), size=(S(36), S(36)))
                ctk.CTkLabel(hdr, image=logo_img, text="").pack(side="left", padx=(0, S(12)))
            except Exception:
                pass

        title_col = ctk.CTkFrame(hdr, fg_color="transparent")
        title_col.pack(side="left")
        ctk.CTkLabel(
            title_col, text="Atenea Image Resizer",
            font=("Segoe UI", S(15), "bold"), text_color=TXT_PRIMARY
        ).pack(anchor="w")
        ctk.CTkLabel(
            title_col, text="Atenea Store Tools  ·  V2026",
            font=("Segoe UI", S(9)), text_color=TXT_MUTED
        ).pack(anchor="w")

        Divider(self).pack(fill="x", padx=S(28), pady=(S(18), 0))

        # ── INPUT ────────────────────────────────────────────
        ctk.CTkFrame(self, fg_color="transparent", height=S(16)).pack()
        SectionLabel(self, "Input", S).pack(anchor="w", **pad)
        ctk.CTkFrame(self, fg_color="transparent", height=S(6)).pack()

        self.entry_in = DarkEntry(self, S, width=inner_w, placeholder_text="Select a folder or files…")
        self.entry_in.pack(**pad)
        ctk.CTkFrame(self, fg_color="transparent", height=S(6)).pack()

        btn_row1 = ctk.CTkFrame(self, fg_color="transparent")
        btn_row1.pack(**pad, fill="x")
        half = (inner_w - S(8)) // 2
        DarkButton(btn_row1, S, text="  Folder", width=half, command=self.select_folder).pack(side="left", padx=(0, S(8)))
        DarkButton(btn_row1, S, text="  Files",  width=half, command=self.select_files).pack(side="left")

        # ── FORMAT FILTER ────────────────────────────────────
        ctk.CTkFrame(self, fg_color="transparent", height=S(14)).pack()
        SectionLabel(self, "Filter by format", S).pack(anchor="w", **pad)
        ctk.CTkFrame(self, fg_color="transparent", height=S(6)).pack()

        self.fmt_menu = ctk.CTkOptionMenu(
            self, values=list(EXT_MAP.keys()),
            width=inner_w, height=S(36),
            fg_color=BG_SURFACE, button_color=BG_BTN, button_hover_color=BG_BTN_HOV,
            dropdown_fg_color=BG_SURFACE2, dropdown_hover_color=BG_BTN,
            text_color=TXT_SECONDARY, dropdown_text_color=TXT_SECONDARY,
            corner_radius=S(7), font=("Segoe UI", S(12))
        )
        self.fmt_menu.set("All formats")
        self.fmt_menu.pack(**pad)

        Divider(self).pack(fill="x", padx=S(28), pady=(S(18), 0))

        # ── OUTPUT ───────────────────────────────────────────
        ctk.CTkFrame(self, fg_color="transparent", height=S(16)).pack()
        SectionLabel(self, "Output folder", S).pack(anchor="w", **pad)
        ctk.CTkFrame(self, fg_color="transparent", height=S(6)).pack()

        out_row = ctk.CTkFrame(self, fg_color="transparent")
        out_row.pack(**pad, fill="x")
        btn_small = S(40)
        self.entry_out = DarkEntry(out_row, S, width=inner_w - btn_small - S(8), placeholder_text="Output folder…")
        self.entry_out.insert(0, "resized")
        self.entry_out.pack(side="left", padx=(0, S(8)))
        DarkButton(out_row, S, text="…", width=btn_small, command=self.select_out).pack(side="left")

        Divider(self).pack(fill="x", padx=S(28), pady=(S(18), 0))

        # ── TARGET SIZE ──────────────────────────────────────
        ctk.CTkFrame(self, fg_color="transparent", height=S(16)).pack()
        SectionLabel(self, "Target size", S).pack(anchor="w", **pad)
        ctk.CTkFrame(self, fg_color="transparent", height=S(6)).pack()

        chips_frame = ctk.CTkFrame(self, fg_color="transparent")
        chips_frame.pack(**pad, fill="x")
        self.chip_btns = []
        chip_w = (inner_w - S(8) * 3) // 4
        for col, (label, _) in enumerate(PRESET_SIZES):
            btn = ctk.CTkButton(
                chips_frame, text=label, height=S(34), width=chip_w,
                fg_color=BG_CHIP, hover_color=BG_CHIP_ON,
                border_color=BORDER2, border_width=1,
                text_color=TXT_MUTED, corner_radius=S(7),
                font=("Segoe UI", S(11)),
                command=lambda i=col: self._select_preset(i)
            )
            btn.grid(row=0, column=col, padx=(0, S(8)) if col < 3 else 0, sticky="ew")
            chips_frame.grid_columnconfigure(col, weight=1)
            self.chip_btns.append(btn)

        ctk.CTkFrame(self, fg_color="transparent", height=S(8)).pack()
        self.custom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.custom_frame.pack(**pad, fill="x")

        cw = (inner_w - S(8)) // 2
        self.entry_w = DarkEntry(self.custom_frame, S, width=cw, placeholder_text="Width px")
        self.entry_w.pack(side="left", padx=(0, S(8)))
        self.entry_h = DarkEntry(self.custom_frame, S, width=cw, placeholder_text="Height px")
        self.entry_h.pack(side="left")
        self.custom_frame.pack_forget()

        self._select_preset(1)

        Divider(self).pack(fill="x", padx=S(28), pady=(S(18), 0))

        # ── TOGGLE: SKIP SMALL ───────────────────────────────
        ctk.CTkFrame(self, fg_color="transparent", height=S(16)).pack()

        toggle_bg = ctk.CTkFrame(self, fg_color=BG_SURFACE2, corner_radius=S(8),
                                  border_color=BORDER, border_width=1)
        toggle_bg.pack(**pad, fill="x")

        toggle_inner = ctk.CTkFrame(toggle_bg, fg_color="transparent")
        toggle_inner.pack(fill="x", padx=S(14), pady=S(12))

        self.ignorar_var = ctk.BooleanVar(value=False)
        self.toggle_btn = ctk.CTkSwitch(
            toggle_inner, text="",
            variable=self.ignorar_var,
            onvalue=True, offvalue=False,
            switch_width=S(34), switch_height=S(20),
            button_color="#888888", button_hover_color="#aaaaaa",
            progress_color="#555555", fg_color="#2e2e2e",
            command=self._on_toggle
        )
        self.toggle_btn.pack(side="left", padx=(0, S(12)))

        txt_col = ctk.CTkFrame(toggle_inner, fg_color="transparent")
        txt_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            txt_col, text="Skip images at or below target resolution",
            font=("Segoe UI", S(12)), text_color=TXT_SECONDARY, anchor="w"
        ).pack(anchor="w")
        ctk.CTkLabel(
            txt_col, text="Images ≤ selected size will be ignored",
            font=("Segoe UI", S(10)), text_color=TXT_MUTED, anchor="w"
        ).pack(anchor="w")

        Divider(self).pack(fill="x", padx=S(28), pady=(S(18), 0))

        # ── PROGRESS ─────────────────────────────────────────
        ctk.CTkFrame(self, fg_color="transparent", height=S(16)).pack()

        prog_wrap = ctk.CTkFrame(self, fg_color="transparent")
        prog_wrap.pack(**pad, fill="x")
        self.progress_bar = ctk.CTkProgressBar(
            prog_wrap, height=S(3), corner_radius=S(2),
            fg_color=BG_SURFACE, progress_color="#5a5a5a"
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x")

        prog_info = ctk.CTkFrame(self, fg_color="transparent")
        prog_info.pack(**pad, fill="x", pady=(S(5), 0))
        self.lbl_status = ctk.CTkLabel(
            prog_info, text="Ready",
            font=("Segoe UI", S(10)), text_color=TXT_HINT, anchor="w"
        )
        self.lbl_status.pack(side="left")
        self.lbl_count = ctk.CTkLabel(
            prog_info, text="0 / 0",
            font=("Segoe UI", S(10)), text_color=TXT_HINT, anchor="e"
        )
        self.lbl_count.pack(side="right")

        # ── LOG ──────────────────────────────────────────────
        ctk.CTkFrame(self, fg_color="transparent", height=S(10)).pack()
        self.log_box = ctk.CTkTextbox(
            self, width=inner_w, height=S(80),
            fg_color=BG_LOG, border_color=BORDER, border_width=1,
            text_color=TXT_LOG_OK, font=("Consolas", S(11)),
            corner_radius=S(7)
        )
        self.log_box.pack(**pad)
        self.log_box.insert("end", "—  Waiting for input…")
        self.log_box.configure(state="disabled")

        # ── RESIZE BUTTON ────────────────────────────────────
        ctk.CTkFrame(self, fg_color="transparent", height=S(20)).pack()
        self.btn_resize = ctk.CTkButton(
            self, text="Resize images",
            fg_color=BG_RESIZE_BTN, hover_color="#404040",
            border_color="#444444", border_width=1,
            text_color=TXT_PRIMARY, corner_radius=S(8),
            font=("Segoe UI", S(13), "bold"),
            height=S(44), width=inner_w,
            command=self.start_resize
        )
        self.btn_resize.pack(**pad)

        # ── FOOTER ───────────────────────────────────────────
        ctk.CTkLabel(
            self, text="© 2026 Atenea Store Tools",
            font=("Segoe UI", S(9)), text_color=TXT_FOOTER
        ).pack(pady=(S(14), S(20)))

    # ----------------------------------------------------------
    def _select_preset(self, index):
        self.selected_preset = index
        for i, btn in enumerate(self.chip_btns):
            if i == index:
                btn.configure(fg_color=BG_CHIP_ON, border_color="#555555", text_color=TXT_PRIMARY)
            else:
                btn.configure(fg_color=BG_CHIP,    border_color=BORDER2,   text_color=TXT_MUTED)

        if PRESET_SIZES[index][1] is None:
            self.custom_frame.pack(padx=self.S(28), fill="x")
        else:
            self.custom_frame.pack_forget()

    def _on_toggle(self):
        pass

    # ----------------------------------------------------------
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_files = []
            self.entry_in.delete(0, tk.END)
            self.entry_in.insert(0, folder)

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select images",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp *.tiff *.tif"), ("All", "*.*")]
        )
        if files:
            self.selected_files = list(files)
            self.entry_in.delete(0, tk.END)
            self.entry_in.insert(0, f"{len(files)} files selected")

    def select_out(self):
        folder = filedialog.askdirectory()
        if folder:
            self.entry_out.delete(0, tk.END)
            self.entry_out.insert(0, folder)

    # ----------------------------------------------------------
    def _get_entradas(self):
        extensiones = EXT_MAP[self.fmt_menu.get()]
        if self.selected_files:
            return [f for f in self.selected_files if os.path.splitext(f)[1].lower() in extensiones]
        carpeta = self.entry_in.get().strip()
        if not carpeta or not os.path.isdir(carpeta):
            return []
        return [
            os.path.join(carpeta, f)
            for f in os.listdir(carpeta)
            if os.path.splitext(f)[1].lower() in extensiones
        ]

    def _get_size(self):
        _, size = PRESET_SIZES[self.selected_preset]
        if size is not None:
            return size
        try:
            w = int(self.entry_w.get())
            h = int(self.entry_h.get())
            if w > 0 and h > 0:
                return (w, h)
        except ValueError:
            pass
        return None

    # ----------------------------------------------------------
    def start_resize(self):
        entradas       = self._get_entradas()
        carpeta_salida = self.entry_out.get().strip()
        size           = self._get_size()

        if not entradas:
            messagebox.showerror("Error", "No images found with the selected format.")
            return
        if not carpeta_salida:
            messagebox.showerror("Error", "Please select an output folder.")
            return
        if size is None:
            messagebox.showerror("Error", "Please enter a valid width and height.")
            return

        ancho, alto = size
        ignorar     = self.ignorar_var.get()

        self.progress_bar.set(0)
        self.lbl_status.configure(text="Processing…")
        self.lbl_count.configure(text=f"0 / {len(entradas)}")
        self._log_clear()
        self.btn_resize.configure(state="disabled", text="Resizing…")

        threading.Thread(
            target=redimensionar_imagenes,
            args=(entradas, carpeta_salida, ancho, alto,
                  self._cb_progreso, self._cb_log, self._cb_fin),
            kwargs={"ignorar_menores": ignorar},
            daemon=True
        ).start()

    # ----------------------------------------------------------
    def _cb_progreso(self, valor, done, total):
        self.after(0, lambda: self.progress_bar.set(valor))
        self.after(0, lambda: self.lbl_count.configure(text=f"{done} / {total}"))

    def _cb_log(self, texto, kind="ok"):
        def _write():
            self.log_box.configure(state="normal")
            self.log_box.insert("end", texto)
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        self.after(0, _write)

    def _cb_fin(self, ok, errores, omitidas):
        def _done():
            self.btn_resize.configure(state="normal", text="Resize images")
            self.lbl_status.configure(text="Done")
            msg = f"Completed:  {ok} resized"
            if omitidas:
                msg += f"   ·   {omitidas} skipped"
            if errores:
                msg += f"   ·   {errores} errors"
            messagebox.showinfo("Done", msg)
        self.after(0, _done)

    def _log_clear(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    # ----------------------------------------------------------
    def _resource(self, path):
        try:
            base = sys._MEIPASS
        except Exception:
            base = os.path.abspath(".")
        return os.path.join(base, path)


# ==========================================================
# EJECUCIÓN
# ==========================================================
if __name__ == "__main__":
    app = AteneaResizer()
    app.mainloop()