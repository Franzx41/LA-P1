#!/usr/bin/env python
# coding: utf-8

'''
 Analisor léxico baseado em busca por regex
 Autor: Francisco Ferreira

 Os executáveis desse código estão na pasta "linux_executavel/" e "windows_executavel/"

 Etapas para rodar esse script:

 1) Instalar a dependência tkinter:
	sudo apt-get install python3-tk
		ou
	pip install tk

 2) Finalmente executando o analisador léxico:
	python analyzer.py 
'''

import re
import tkinter as tk
from tkinter import filedialog

class Analyzer:
    def __init__(self):
        # Lista de regexes
        self.regex_list = [
            ('LINE_COMMENT', r'//(.)*\n'),
            ('BLOCK_COMMENT', r'/\*[\s\S]*?\*/'),
            ('STRING', r'\"([^\"\'])*\"'), # Exclui os caracteres (ASCII 34 aspas simples, ASCII 39 aspas simples) 
            ('CHARACTER', r'\'([^\"\'])\''), # Exclui os caracteres (ASCII 34 aspas simples, ASCII 39 aspas simples) 
            ('KEY_WORD', r'(variables|methods|constants|class|return|empty|main|if|then|else|while|for|read|write|integer|float|boolean|string|true|false|extends)'),
            ('IDENTIFIER', r'[a-zA-Z]+[a-zA-Z0-9_]*'),
            ('NUMBER', r'-?\d+(\.\d+)?'),
            ('OPERATOR', r'(\+\+)|(--)|(\+)|(-)|(\*)|(\/)|(==)|(>=)|(<=)|(>)|(<)|(=)|(!)|(&&)|(\|\|)|(!)'),
            ('DELIMITER', r';|,|\(|\)|\{|\}|\[|\]'),
            ('SYMBOL', r'[\x20-\x21\x23-\x26\x28-\x7E]'), # Usando range para excluir aspas simples e aspas duplas
            ('ERRO_LEXICO', r'.') # Regex para determinar erros léxicos (ou seja, match qualquer outra coisa fora do nosso dicionário)
        ]
        # Agrupa a a lista de regex em um único named capturing groups
        self.final_regex = '|'.join('(?P<%s>%s)' % p for p in self.regex_list)

    '''
        Dado um text, faz análise léxica e retorna:
        - results: lista de tokens e suas respectivas posições no arquivo de texto
        - stats: um dicionário com contadores de ocorrência para cada token
    '''
    def analyze(self, source_code_str):
        results = []
        stats = {}
        for item in self.regex_list: 
            stats[item[0]] = 0

        # Ref: https://docs.python.org/3/library/re.html#re.finditer
        # Faz match das regexes e retorna uma list de grupos encontrados
        for m in re.finditer(self.final_regex, source_code_str):
            lex_label = m.lastgroup
            lex_value = m.group(lex_label)
            counter = stats[lex_label]
            stats[lex_label] = counter + 1
            
            start = m.start()
            end = m.end()

            # Linha de início do lexema e seu offset
            start_line = source_code_str.count('\n', 0, start) + 1
            start_offset = start - source_code_str.rfind('\n', 0, start) - 1

            # Linha de término do lexema e seu offset
            end_line = source_code_str.count('\n', 0, end) + 1
            end_offset = end - source_code_str.rfind('\n', 0, end) - 1
            
            results.append(dict(
                start_line=start_line, start_offset=start_offset, 
                end_line=end_line, end_offset=end_offset, 
                label=lex_label, value=lex_value
            ))

        return results, stats

# --- Fim de Analyzer --------------------------------------------------------------------

class GUI:
    def __init__(self):
        self.lex_color_map = {
            'LINE_COMMENT': r'#1F77B4', #Blue
            'BLOCK_COMMENT': r'#90764b', #Brown
            'STRING': r'#2CA02C', #Green
            'CHARACTER': r'#E377C2', #Pink
            'KEY_WORD': r'#9467BD', #Purple
            'IDENTIFIER': r'#FF7F0E', #Orange
            'NUMBER': r'#FFFF00', #Yelloqw
            'OPERATOR': r'#7F7F7F', #Gray
            'DELIMITER': r'#BCBD22', #Olive
            'SYMBOL': r'#17BECF', #Cyan
            'ERRO_LEXICO': r'#FF0000' #Red
        }
        self.checkbox_map = {}
        self.root = tk.Tk()
        self.analyzer = Analyzer()
        self.init()

    def init(self):
        self.root.title("Analisador léxico (Francisco Ferreira)")
        self.root.geometry("900x500")
        self.root.config(bg="#EEEEEE")

        # Create title labels
        title1 = tk.Label(self.root, text="Texto de entrada:", bg="#EEEEEE")
        title2 = tk.Label(self.root, text="Resultado da análise léxica:", bg="#EEEEEE")
        title3 = tk.Label(self.root, text="Tokens e ocorrências:", bg="#EEEEEE")
        title1.grid(row=0, column=0, sticky=(tk.W), padx=5, pady=(10, 0))
        title2.grid(row=0, column=1, sticky=(tk.W), padx=5, pady=(10, 0))
        title3.grid(row=0, column=2, sticky=(tk.W), padx=0, pady=(10, 0))

        # Cria formulários de text
        self.text_area1 = tk.Text(self.root, height=10, width=30)
        self.text_area2 = tk.Text(self.root, height=10, width=30)
        self.text_area1.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5, pady=(0, 10))
        self.text_area2.grid(row=1, column=1, sticky=(tk.N, tk.S, tk.E, tk.W), padx=5, pady=(0, 10))
        self.text_area1.bind("<<Modified>>", self.on_text_change)

        # Cria a legenda de tokens
        checkbox_frame = tk.Frame(self.root, borderwidth=1, relief="solid")
        checkbox_frame.grid(row=1, column=2, rowspan=2, padx=(0,10), pady=0, sticky="n")
        cb_pos = 0
        for key, value in self.lex_color_map.items(): 
            checkbox = tk.Checkbutton(checkbox_frame, text="{} (0)".format(key), bg=value)
            self.checkbox_map[key] = checkbox
            checkbox.grid(row=cb_pos, column=0, padx=(0, 15), pady=2, sticky="w")
            cb_pos += 1

            #Configura tags para fazer highlight dos tokens
            self.text_area2.tag_config(key, background=value, foreground="black")

        self.status_label = tk.Label(self.root, text="Abra um arquivo pelo menu ou cole o texto diretamente no formulário de texto de entrada")
        self.status_label.grid(row=2, column=0, columnspan=3, padx=0, pady=0, sticky=tk.W)

        # Cria menu
        menubar = tk.Menu()
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Abrir arquivo...", command=self.open_file)
        filemenu.add_command(label="Apagar tudo", command=self.clear_all_texts)
        filemenu.add_separator()
        filemenu.add_command(label="Sair", command=self.root.quit)
        menubar.add_cascade(label="Menu", menu=filemenu)
        self.root.config(menu=menubar)

        # Configura os componetes para serem redimensionáveis
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)

        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=0)

        # Inicia o GUI
        self.root.mainloop()

    def on_text_change(self, event):
        if self.text_area1.edit_modified():
            # Reset a flag do evento corrente
            self.text_area1.edit_modified(False)
            text = self.text_area1.get('1.0', tk.END)
            self.lex_analyze(text)

    def lex_analyze(self, text):
        result, stats = self.analyzer.analyze(text)
        self.text_area2.config(state=tk.NORMAL) # Habilita text de resultado
        self.text_area2.delete('1.0', tk.END)
        self.text_area2.insert('1.0', self.text_area1.get('1.0', tk.END))

        print("-- Resultados ----------------------------")

        self.clear_all_tags()
        for i in range(len(result)):
            lex = result[i]
            print(lex)
            label = lex['label']
            start_pos = "{}.{}".format(lex['start_line'], lex['start_offset'])
            end_pos = "{}.{}".format(lex['end_line'], lex['end_offset'])
            self.text_area2.tag_add(label, start_pos, end_pos)

        for key, value in stats.items(): 
            self.checkbox_map[key].config(text="{} ({})".format(key, value))

        error_counter = stats['ERRO_LEXICO']
        print("Resultado da análise: {} erro(s)".format(error_counter))
        if (error_counter > 0):
            self.status_label.config(text="Resultado da análise: {} erro(s) foram encontrados".format(error_counter), fg="red")
        else:
            self.status_label.config(text="Resultado da análise: nenhum erro foi encontrado", fg="green")

        # Desabilita text de resultado
        self.text_area2.config(state=tk.DISABLED)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.text_area1.delete('1.0', tk.END)
                self.text_area1.insert('1.0', content)

    def clear_all_texts(self):
        self.status_label.config(text="", fg="black")
        self.text_area2.config(state=tk.NORMAL)
        self.text_area1.delete('1.0', tk.END)
        self.text_area2.delete('1.0', tk.END)

    def clear_all_tags(self):
        tags = self.text_area2.tag_names()
        for tag in tags:
            self.text_area2.tag_remove(tag, "1.0", tk.END)        

# --- Fim de GUI --------------------------------------------------------------------

def main():
    analyzer = Analyzer()
    gui = GUI()

if __name__ == '__main__':
    main()    
