import requests
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import threading
import time

# API_KEY = yourapikey

CURRENCIES = [
    'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'SEK', 'NZD',
    'MXN', 'SGD', 'HKD', 'NOK', 'KRW', 'TRY', 'INR', 'RON', 'RUB', 'BRL', 'ZAR'
]

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class AnimatedButton(ctk.CTkButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_fg_color = self.cget("fg_color")
        self.hover_fg_color = self.cget("hover_color")
        
    def animate_click(self):
        original_text = self.cget("text")
        self.configure(text="...", fg_color="#444444")
        self.update()
        time.sleep(0.3)
        self.configure(text=original_text, fg_color=self.default_fg_color)

class CurrencyConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("💱 Currency Converter")
        self.geometry("500x650")
        self.resizable(False, False)
        
        try:
            self.iconbitmap("currency_icon.ico")
        except:
            pass

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=20)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="CURRENCY CONVERTER",
            font=("Roboto", 20, "bold"),
            text_color="#4fc3f7"
        )
        self.title_label.pack()
        
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Real-time Exchange Rates",
            font=("Roboto", 12),
            text_color="#b0bec5"
        )
        self.subtitle_label.pack()

        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.amount_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.amount_frame.pack(pady=(20, 10), padx=20, fill="x")
        
        self.label_amount = ctk.CTkLabel(
            self.amount_frame,
            text="Amount:",
            font=("Roboto", 14),
            anchor="w"
        )
        self.label_amount.pack(fill="x")
        
        self.entry_amount = ctk.CTkEntry(
            self.amount_frame,
            placeholder_text="Enter amount",
            font=("Roboto", 16),
            height=45,
            border_width=2,
            corner_radius=10
        )
        self.entry_amount.pack(fill="x", pady=(5, 0))

        self.currency_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.currency_frame.pack(pady=10, padx=20, fill="x")
        
        self.from_frame = ctk.CTkFrame(self.currency_frame, fg_color="transparent")
        self.from_frame.pack(fill="x", pady=5)
        
        self.label_from = ctk.CTkLabel(
            self.from_frame,
            text="From Currency:",
            font=("Roboto", 14),
            anchor="w"
        )
        self.label_from.pack(fill="x")
        
        self.dropdown_from = ctk.CTkComboBox(
            self.from_frame,
            values=CURRENCIES,
            font=("Roboto", 14),
            height=45,
            dropdown_font=("Roboto", 14),
            corner_radius=10,
            button_color="#1976d2",
            border_width=2
        )
        self.dropdown_from.set("USD")
        self.dropdown_from.pack(fill="x", pady=(5, 0))

        self.to_frame = ctk.CTkFrame(self.currency_frame, fg_color="transparent")
        self.to_frame.pack(fill="x", pady=5)
        
        self.label_to = ctk.CTkLabel(
            self.to_frame,
            text="To Currency:",
            font=("Roboto", 14),
            anchor="w"
        )
        self.label_to.pack(fill="x")
        
        self.dropdown_to = ctk.CTkComboBox(
            self.to_frame,
            values=CURRENCIES,
            font=("Roboto", 14),
            height=45,
            dropdown_font=("Roboto", 14),
            corner_radius=10,
            button_color="#1976d2",
            border_width=2
        )
        self.dropdown_to.set("EUR")
        self.dropdown_to.pack(fill="x", pady=(5, 0))

        self.btn_convert = AnimatedButton(
            self.main_frame,
            text="CONVERT",
            font=("Roboto", 16, "bold"),
            height=50,
            corner_radius=10,
            fg_color="#1976d2",
            hover_color="#1565c0",
            command=self.convert
        )
        self.btn_convert.pack(pady=20, padx=20, fill="x")

        self.result_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=10,
            fg_color="#1e1e1e",
            border_width=2,
            border_color="#333333"
        )
        self.result_frame.pack(pady=(0, 20), padx=20, fill="x")
        
        self.label_result = ctk.CTkLabel(
            self.result_frame,
            text="",
            font=("Roboto", 18, "bold"),
            text_color="#4caf50",
            wraplength=400
        )
        self.label_result.pack(pady=15, padx=15)

        self.status_bar = ctk.CTkLabel(
            self,
            text="Ready",
            font=("Roboto", 10),
            text_color="#757575"
        )
        self.status_bar.pack(side="bottom", fill="x", pady=(0, 10))

    def update_status(self, message):
        self.status_bar.configure(text=message)
        self.update()

    def convert(self):
        amount_text = self.entry_amount.get()
        from_cur = self.dropdown_from.get()
        to_cur = self.dropdown_to.get()

        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive number for amount.")
            return

        self.btn_convert.animate_click()
        self.label_result.configure(text="Converting...")
        self.update_status("Contacting exchange rate API...")

        threading.Thread(target=self.perform_conversion, args=(amount, from_cur, to_cur), daemon=True).start()

    def perform_conversion(self, amount, from_cur, to_cur):
        try:
            converted, error = convert_currency(amount, from_cur, to_cur)
            
            if error:
                self.after(0, lambda: messagebox.showerror("Conversion Error", error))
                self.after(0, lambda: self.label_result.configure(text=""))
                self.after(0, lambda: self.update_status(f"Error: {error}"))
            else:
                result_text = f"{amount:,.2f} {from_cur} = {converted:,.2f} {to_cur}"
                self.after(0, lambda: self.label_result.configure(text=result_text))
                self.after(0, lambda: self.update_status(f"Successfully converted {from_cur} to {to_cur}"))
                
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}"))
            self.after(0, lambda: self.update_status("Error occurred during conversion"))

def convert_currency(amount, from_currency, to_currency):
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_currency}"
    try:
        response = requests.get(url)
        data = response.json()
        if data['result'] == 'success':
            rates = data['conversion_rates']
            if to_currency in rates:
                converted_amount = amount * rates[to_currency]
                return converted_amount, None
            else:
                return None, f"Currency '{to_currency}' not found."
        else:
            return None, f"API error: {data.get('error-type', 'unknown error')}"
    except Exception as e:
        return None, f"Network error: {str(e)}"

if __name__ == "__main__":
    app = CurrencyConverterApp()
    app.mainloop()