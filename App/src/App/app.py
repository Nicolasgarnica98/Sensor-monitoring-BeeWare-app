"""
Aplicacion_proyecto
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import socket
import pickle
import datetime as dt


class App(toga.App):
    def startup(self):

        button_conectar = toga.Button('Conectar', on_press=self.conectar)
        button_desconetcar = toga.Button('Desconectar', on_press=self.desconectar)

        main_box = toga.Box(style=Pack(direction=COLUMN))
        self.is_conectado = toga.Label('DESCONECTADO')
        self.aire = toga.Label('          Calidad del aire: BUENA')
        self.ruido = toga.Label('          Niveles de ruido: NORMAL')
        self.sensor = toga.Label('          Colocar dedo para medir BPM')
        self.bpm = toga.Label('          BPM: Sin medir')
        
        main_box.add(button_conectar)
        main_box.add(button_desconetcar)
        main_box.add(self.is_conectado)
        main_box.add(self.aire)
        main_box.add(self.ruido)
        main_box.add(self.sensor)
        main_box.add(self.bpm)

        self.main_window = toga.MainWindow(title='Aplicación de control de parametros medicos')
        self.main_window.content = main_box
        self.main_window.show()


    def conectar(self,widget):
        self.main_window.info_dialog('Atención ','Oprima aceptar para comenzar la medición')
        print('BOMBORRIN')
        TCP_IP = '192.168.0.11'
        TCP_PORT = 5005
        self.BUFFER_SIZE = 1024
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((TCP_IP, TCP_PORT))
        self.is_conectado.text = 'CONECTADO'

        self.fil = open('data.txt', 'at')
        date = dt.datetime.now()
        self.fil.write('Inicio adquisición\n')
        self.fil.write(date.strftime('%d-%m-%Y %H:%M:%S'))
        self.fil.write('\n')
        self.fil.flush()

        
        while 1:
            i = 0
            data_Rec = self.s.recv(self.BUFFER_SIZE)
            if len(data_Rec) == 0:
                break
            content = data_Rec.decode("utf-8")
            content = content.split(",")
            calidad_aire = content[0]
            cantidad_ruido = content[1]
                      
            self.sensor.text = '          {}'.format(str(content[2]))

            self.bpm.text = '          BPM: {}'.format(str(content[3]))

            print('Valores')
            print(content[0])
            print(content[1])
            print(content[2])
            print(content[3])

            if float(calidad_aire) > 6000:
                self.aire.text = '           Calidad del aire: MALA'
                self.main_window.info_dialog('Alerta ','Calidad del aire: MALA')
                break
            
            elif i>30 and str(content[2])=='Tomando pulso...' and float(content[3])>=130:
                self.main_window.info_dialog('Precaución ','Frecuencia cardiaca excesiva' + str(content[3]))
                break
            elif i>=6 and str(content[2])=='          No se encuentra medición':
                self.bpm.text = ('          Por favor acercar el dedo')
                break
            if float(cantidad_ruido) >= 2200:
                self.ruido.text = '          Niveles de ruido: DEMASIADO ALTOS'
                self.main_window.info_dialog('Alerta ','Niveles de ruido: DEMASIADO ALTOS')
                break

            i = i +1

            date = dt.datetime.now()
            self.fil.write(date.strftime('%d-%m-%Y %H:%M:%S'))
            self.fil.write(': ')

            self.fil.write(content[0])
            self.fil.write(', ')

            self.fil.write(content[1])
            self.fil.write(', ')

            self.fil.write(content[2])
            self.fil.write('\n')
            self.fil.flush()




    def desconectar(self, widget):
        self.fil.close()
        self.s.close()
        self.aire.text = ('          Calidad del aire: BUENA')
        self.ruido.text= ('          Niveles de ruido: NORMAL')
        self.sensor.text = ('          Colocar dedo para medir BPM')
        self.bpm.text = ('          BPM: Sin medir')
        self.is_conectado.text = 'DESCONECTADO'


def main():
    return App()
