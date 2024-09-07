
# by Fláv


import tkinter as tk
from tkinter import filedialog, messagebox
import PyPDF2
from gtts import gTTS
import os
import pygame
import threading

class PDFReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Leitor de PDF em Voz Alta")
        self.root.geometry("400x300")

        self.language_var = tk.StringVar(value='en')  # Idioma padrão: Inglês
        self.file_path = None  # Inicializa o caminho do arquivo como None
        self.text = ""  # Armazena o texto extraído do PDF

        # Inicializa o mixer do pygame
        pygame.mixer.init(frequency=22050, size=-16, channels=2)  # Frequência e canais padrão
        pygame.mixer.music.set_volume(1.0)  # Define o volume máximo

        # Criação dos elementos da interface
        self.label = tk.Label(root, text="Selecione um arquivo PDF:")
        self.label.pack(pady=10)

        self.select_button = tk.Button(root, text="Selecionar PDF", command=self.load_pdf)
        self.select_button.pack(pady=10)

        self.status_label = tk.Label(root, text="", fg="blue")
        self.status_label.pack(pady=10)

        self.language_label = tk.Label(root, text="Selecione o idioma:")
        self.language_label.pack(pady=10)

        self.language_menu = tk.OptionMenu(root, self.language_var, 'pt', 'en', 'fr', 'de')
        self.language_menu.pack(pady=10)

        self.read_button = tk.Button(root, text="Ler PDF", command=self.read_pdf, state=tk.DISABLED)
        self.read_button.pack(pady=10)

        self.start_button = tk.Button(root, text="Iniciar Leitura", command=self.start_speech, state=tk.DISABLED)
        self.start_button.pack(pady=10)

    def load_pdf(self):
        """Carrega um arquivo PDF."""
        self.file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not self.file_path:
            messagebox.showwarning("Aviso", "Nenhum arquivo selecionado.")
        else:
            self.status_label.config(text=f"Arquivo carregado: {os.path.basename(self.file_path)}")
            self.read_button.config(state=tk.NORMAL)  # Habilita o botão de ler PDF
            self.start_button.config(state=tk.NORMAL)  # Habilita o botão de iniciar leitura

    def read_pdf(self):
        """Lê o conteúdo do PDF e armazena em texto."""
        if not self.file_path:
            messagebox.showwarning("Aviso", "Por favor, selecione um arquivo PDF primeiro.")
            return

        try:
            with open(self.file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                self.text = ""
                for page in reader.pages:
                    extracted_text = page.extract_text()
                    if extracted_text:  # Verifica se o texto foi extraído
                        self.text += extracted_text + "\n"

            if self.text.strip():  # Verifica se o texto não está vazio
                print("Texto extraído com sucesso:")
                print(self.text)  # Mostra o texto extraído no console
                messagebox.showinfo("Texto Extraído", "Texto extraído com sucesso!")
            else:
                messagebox.showwarning("Aviso", "O PDF não contém texto legível.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def start_speech(self):
        """Inicia a leitura em uma thread separada."""
        if not self.text:
            messagebox.showwarning("Aviso", "Por favor, leia o PDF primeiro.")
            return

        # Desabilita o botão de iniciar leitura enquanto o áudio está sendo reproduzido
        self.start_button.config(state=tk.DISABLED)
        threading.Thread(target=self.text_to_speech, args=(self.text,)).start()

    def text_to_speech(self, text):
        """Converte texto em fala e reproduz usando pygame."""
        language = self.language_var.get()
        try:
            tts = gTTS(text=text, lang=language)
            audio_file = "temp_audio.mp3"
            tts.save(audio_file)

            # Verifica se o arquivo de áudio foi criado
            if not os.path.exists(audio_file):
                messagebox.showerror("Erro", "Arquivo de áudio não foi criado.")
                return

            # Carrega o arquivo de áudio
            pygame.mixer.music.load(audio_file)
            print(f"Reproduzindo o áudio: {audio_file}")
            pygame.mixer.music.play()  # Reproduz o áudio

            # Aguarda até que a reprodução termine
            while pygame.mixer.music.get_busy():
                self.root.update()  # Atualiza a interface para evitar travamentos

            os.remove(audio_file)  # Remove o arquivo de áudio temporário
            print("Arquivo de áudio removido.")
        except pygame.error as e:
            messagebox.showerror("Erro", f"Erro ao reproduzir áudio: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")
        finally:
            self.start_button.config(state=tk.NORMAL)  # Reabilita o botão após a reprodução

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFReaderApp(root)
    root.mainloop()
