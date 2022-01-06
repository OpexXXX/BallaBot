# -*- coding: utf-8 -*-
import csv
from logging import error
from os import truncate
from bs4 import BeautifulSoup


class BallisticDataException(Exception):
    pass

class HeaderNotFound(BallisticDataException):
    def __init__(self):
        super().__init__(
            "Столбцы 'Верт. поправка, MOA' или 'Верт. поправка, MRAD' отсутствуют в таблице.\nДобавте в настройках таблицы."
        )
class RifleDistanceLessOfTable(BallisticDataException):
    def __init__(self):
        super().__init__(
            "'Начало дистанции, м' больше, чем дистанция пристрелки.\nУстановите значение 'Начало дистанции, м' меньше, чем дистанция пристрелки в настройках таблицы."
        )
class RifleDistanceMoreOfTable(BallisticDataException):
    def __init__(self):
        super().__init__(
            "Дистанция пристрелки больше, чем значения в таблице.\nУстановите значения 'Начало дистанции, м' и 'Конец дистанции, м' в настройках таблицы."
        )

class BallisticData(object):
    def __init__(self):
        self.correction_units = 'MRAD'      #MOA/MRAD
        self.correction_on_сlick = 0.25   #Цена 1 клика
        self.cartrige = ""        #2 Патрон
        self.cartrige_velocity = 0#4 Скорость
        self.cartrige_bk = 0      #5 Коэффициент
        self.rifle_name = ""      #11 Винтовка
        self.rifle_shoot_distance = 0 #вычесленное из таблицы с учетоп поправок Пристрелка 
        self.rifle_reference_shoot_distance = 0 #Указанная пристрелка без поправок
        self.temperature = 0      #21 Температура
        self.humidity = 0         #22 Влажность
        self.pressure = 0         #23 Давление
        self.zero_temperature = 0      #21 Температура пристрелки
        self.zero_humidity = 0         #22 Влажность
        self.zero_pressure = 0         #23 Давление
        self.zero_atmos = False         #Учет атмосферы пристрелки
        self.shift_zero = False         #Смещение пристрелки
        self.dataList = list()         #List с данными csv [{'distance': 100.0, 'MOA': 7.4},   {'distance': 110.0, 'MOA': 9.7}]
        self.warning_list = list()      #List с ворнингами по содержимому csv htm

    def load_htm_file(self,htmFilePath):
        self.dataList = list()
        with open(htmFilePath,encoding="utf8") as f:
            htm_sourse = f.read()
            parsed_html = BeautifulSoup(htm_sourse,features="html.parser")
            htm_p_tags = parsed_html.find_all('p')
        i=0
        self.zero_atmos = False
        zero_atmos_row_num = 0
        atmos_parse = False
        for tag in htm_p_tags:

            text = tag.text.strip()
            text = text.replace("\n"," ")
            if "Патрон:" in text:  
                text = text[text.find(":") + 1 : ]
                self.cartrige = text     #2 Патрон
            if "корость" in text and " м/с:" in text and "ветра" not in text:
                text = text[text.find(":") + 1 :text.find(":") + 5 ]
                self.cartrige_velocity =float(text.replace(",",".")) #4 Скорость
            if "Баллистический коэффициент:" in text: 
                text = text[text.find(":") + 1 : ] 
                self.cartrige_bk ="Баллистический коэффициент: "+text      #5 Баллистический коэффициент
            if "Винтовка:" in text: 
                self.rifle_name = text      #11 Винтовка
            if "Дистанция пристрелки, м:" in text:
                text = text[text.find(":") + 1 : ]
                self.rifle_reference_shoot_distance = float(text.replace(",",".")) #12 Пристрелка
                

            if "Смещение пристрелки" in text:
                text = text[text.find(":") + 2 : ]
                self.v_offset =  float(text[ :text.find("/") ].replace(",","."))
                self.h_offset =  float(text[text.find("/")+1 :text.find(" ") ].replace(",","."))
                if(self.v_offset>0):
                    self.shift_zero=True
                    self.warning_list.append(f"Вертикальное смещение пристрелки {str(self.v_offset)} в настройках патрона.")
                if(self.h_offset>0):
                    self.warning_list.append(f"Горизонтальное смещение пристрелки {str(self.h_offset)} в настройках патрона.")
            if "Верт. клик," in text:
                if 'MRAD' in text:
                    self.correction_units = 'MRAD'
                    text = text[ :text.find("(")]
                else:
                    self.correction_units = 'MOA'
                text = text[text.find(":") + 1 : ]
                self.correction_on_сlick = float(text.replace(",",".")) #15 Цена клика
            
            
            if "Атм. пристрелки." in text:
                if "Учет включен" in text:
                    self.zero_atmos = True
                    atmos_parse=True
                    zero_atmos_row_num = i
                    self.warning_list.append("Включен учет атмосферы пристрелки.")
            if "Атмосфера" in text:
                atmos_parse =False
            if atmos_parse:
                if "Температура, °C:" in text :
                    temp_text = text[text.find("°C:") + 4 :text.find("°C:")+8] 
                    self.zero_temperature = temp_text #21 Температура
                if "Влажность, %:" in text: 
                    hum_text = text[text.find("%:") + 3 :text.find("%:")+7]
                    self.zero_humidity = hum_text    #22 Влажность
                if "Давление, мм.рт.ст.:" in text: 
                    press_text = text[text.find("ст.:") + 5 :text.find("ст.:")+10]
                    self.zero_pressure = press_text    #23 Давление
            else:
                if "Температура, °C:" in text : 
                    self.temperature = text      #21 Температура
                if "Влажность, %:" in text: 
                    self.humidity = text         #22 Влажность
                if "Давление, мм.рт.ст.:" in text: 
                    self.pressure = text         #23 Давление
            i+=1
    def load_csv_file(self,csvFilePath):
       
        header_found = False
        with open(csvFilePath,encoding="utf8") as f:
            header_row_number=0
            for line in f:
                if "Верт. поправка, MOA" in line or "Верт. поправка, MRAD"in line:
                    header_found = True
                    if "Верт. поправка, MOA" in line:
                        self.correction_units_in_table = "MOA"
                    else:
                        self.correction_units_in_table = "MRAD"
                        self.warning_list.append("Желательно включить столбец 'Верт. поправка, MOA'  ")
                    break
                header_row_number+=1 
        if not header_found:
            raise HeaderNotFound()       
        with open(csvFilePath,encoding="utf8") as f:
            for row in range(header_row_number): 
                next(f, None)
           
            reader = csv.DictReader(f,delimiter=';')

            for row in list(reader):
                dist_m = float(row["Дистанция, метры"].replace(",","."))
                if self.correction_units_in_table == "MOA":
                    moa = float(row["Верт. поправка, MOA"].replace(",","."))
                    self.dataList.append({'Distance': dist_m, 'MOA': moa})
                else:
                    mrad = float(row["Верт. поправка, MRAD"].replace(",","."))
                    self.dataList.append({'Distance': dist_m, 'MRAD': mrad})      
            step = 0

            
            
            #Срез дистанций меньше дистанции пристрелки
            '''for i in range (1, len(self.dataList)):
                if float(self.dataList[i-1]['Distance']) <= self.rifle_shoot_distance and float(self.dataList[i]['Distance'])>=self.rifle_shoot_distance:
                    step = self.dataList[i]['Distance']-self.dataList[i-1]['Distance']  
                    
                    if(i>2):
                        self.dataList = self.dataList[i-2:]
                    break'''
            if step>5.0:
                self.warning_list.append(f"'Шаг дистанции, м' {str(step)}. \n Установите шаг 2.5 или меньше в настройках таблицы.")
            
    def load_data_file(self,csvFilePath,htmFilePath):
        """Загрузка данных из файлов сгенерированных мобильным приложением Стрелок
        Args:
            csvFilePath (str): путь к csv файлу
            htmFilePath (str): путь к htm файлу
        """
        self.warning_list = []
        self.correction_units_in_table =""
        self.load_htm_file(htmFilePath)
        self.load_csv_file(csvFilePath)
        self.maxDistance = self.dataList[-1]['Distance']
        self.rifle_shoot_distance=self.get_distance_from_correction(0)
        if self.zero_atmos or self.shift_zero:
            warn_text = "Дистанция пристрелки с учетом"
            if self.zero_atmos:
                warn_text+=", атмосферы пристрелки"
            if self.shift_zero:
                warn_text+= ", смещения пристрелки"
            warn_text+=": "
            warn_text+= "{:0.0f}".format(round((self.rifle_shoot_distance)))
            warn_text+=" метров."
            
            self.warning_list.append(warn_text)
            pass
        if self.rifle_shoot_distance<self.dataList[0]['Distance']:
            raise RifleDistanceLessOfTable()
        elif self.rifle_shoot_distance>self.dataList[-1]['Distance']:
            raise RifleDistanceMoreOfTable()

    def get_correction_from_distance(self, distance):
        result_correction=0
        for i in range(len(self.dataList)-1,0,-1):
            r = self.dataList[i]
            if (r['Distance'] <= distance or i==(0)) and i<len(self.dataList)-1:
                next_distance = self.dataList[i+1]['Distance']
                next_correction = self.dataList[i+1][self.correction_units_in_table]
                delta_correction = next_correction- r[self.correction_units_in_table]
                delta_distance = next_distance- r['Distance'] 
                step = next_distance-distance
                koef = 1-step / delta_distance
                result_correction = r[self.correction_units_in_table]+delta_correction*koef
                return result_correction
        return result_correction

    def get_MOA_from_distance(self, distance):
        if self.correction_units_in_table == "MOA":
            return  self.get_correction_from_distance(distance)
        else:
            correction = self.get_correction_from_distance(distance)    
            return correction*3.4377
                      
    def get_MRAD_from_distance(self, distance):
        if self.correction_units_in_table == "MRAD":
            return  self.get_correction_from_distance(distance)
        else:
            correction = self.get_correction_from_distance(distance)    
            return correction/3.4377

        
    
    def get_distance_from_correction(self, correction):
        result_distance=0
        for i in range(len(self.dataList)-1,0,-1):
            r = self.dataList[i]
            if (r[self.correction_units_in_table] <= correction or i==(0))and i<len(self.dataList)-1:
                next_distance = self.dataList[i+1]['Distance']
                next_correction = self.dataList[i+1][self.correction_units_in_table]
                delta_correction = next_correction- r[self.correction_units_in_table]
                delta_distance = next_distance- r['Distance'] 
                step = next_correction-correction
                koef = 1-step / delta_correction
                result_distance = r['Distance']+delta_distance*koef
                return result_distance
        return result_distance

        
    def get_distance_from_MOA(self, correction):
        if self.correction_units_in_table == "MOA":
            return  self.get_distance_from_correction(correction)
        else:
            distance = self.get_distance_from_correction(correction/3.4377)    
            return distance

    def get_distance_from_MRAD(self, correction):

        if self.correction_units_in_table == "MRAD":
            return  self.get_distance_from_correction(correction)
        else:
            distance = self.get_distance_from_correction(correction*3.4377)    
            return distance
  