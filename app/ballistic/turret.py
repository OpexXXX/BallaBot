# -*- coding: utf-8 -*-
import math
from app.ballistic.drawing import Sticker
from app.ballistic.drawing import Line
from app.ballistic.drawing import Triangle
from app.ballistic.drawing import Circle
from app.ballistic.drawing import TextBox
from app.ballistic.file_parser  import BallisticData
import cairo

class TurretSticker(Sticker):
    
    def __init__(self, coords, cntx,  ballistic_data:BallisticData,click_on_turn = 60, len=75*2.834, height=9*2.834, fontSize=3.0*2.834, round_to_click = False):
        super(TurretSticker,self).__init__(cntx, ballistic_data, height, coords)
        self.click_on_turn  = click_on_turn
        self.length = len
        #self.diametr = 04
        self.correction_units = ballistic_data.correction_units
        self.correction_on_click = ballistic_data.correction_on_сlick
        self.correction_on_turn =  15
        self.set_correction_on_turn()
        self.round_to_click = round_to_click
        self.font_size = fontSize
   
    def print_sticker_size(self,x_pos,y_pos,font_Size=3*2.834): 
        txtList = ["Длинна наклейки, мм:" ,  "{:0.1f}".format(round((self.length/2.834),2))+';',
        "Высота, мм:" ,  "{:0.1f}".format(round((self.height/2.834),2))+';',
        "Клик:" ,  "{:0.2f}".format(round((self.correction_on_click),2)),self.correction_units+';',
        " на 1 оборот" ,str(self.correction_on_turn),self.correction_units,]
        strrow =  ' '.join(txtList)
        label = TextBox(strrow,fontSize=font_Size,anchor='LT')

        label.draw(self.cntx,[x_pos,y_pos])
        y_pos+=font_Size*1.2
        return y_pos

    def print_cartride(self,x_pos,y_pos,font_Size=2.5*2.834):
        txt = self.ballistic_data.cartrige + ", " + "{:0.0f}".format(round((self.ballistic_data.cartrige_velocity))) + " м/с, пристрелка " + "{:0.0f}".format(round((self.ballistic_data.rifle_shoot_distance))) + "м., " + self.ballistic_data.temperature 
        label = TextBox(txt,fontSize=font_Size,anchor='LT')
        label.draw(self.cntx,[x_pos,y_pos])
        y_pos+=(font_Size*1.2)/2.834
        return y_pos
    def prepare_option_1(self, step=100, autoStep=False, roundStep=True, autoFilling=False):
        """Подготавливает объекты для отрисовки option 1 
        Args:
            step (float): Шаг разметки. Defaults to 100.0.
            fontSize (float): Автоматическое вычисление шага. Defaults to 8.0.
            autoStep (bool): [description]. Defaults to True.
            roundStep (bool): Привидение последовательности  к счету кратно сотни. Defaults to True.
            roundStep = True      165 200 250 300 350
            roundStep = False     165 215 265 315 365
            autoFilling (bool): Автоуменьшение шага. Defaults to True."""
        
        self.draw_objects = []
        self._add_border()
        turn = 0
        #if autoStep:step = self.get_option_3_min_step()
        current_x_pos = self.length   
        current_distance = self.ballistic_data.rifle_shoot_distance #Начинаем с дистанции пристрелки
        i=1
        big_font_size = self.font_size * 1.7 
        small_font_size = self.font_size * 1.3

        triangle_height  =2.5*2.834 
        zero_triangle_height = 3.0*2.834
        
        if self.height<=5*2.834:
            big_font_size = self.font_size * 1.1
            small_font_size = self.font_size 
            zero_triangle_height =  (self.height - big_font_size)*1.5     
            triangle_height  = (self.height - big_font_size)
           
        elif self.height<=7*2.834:
            big_font_size -=(7*2.834-self.height)
            small_font_size -= (7*2.834-self.height)
            triangle_height  = (self.height - big_font_size)
            zero_triangle_height =  (self.height-2.2*2.834)
        else:

            label = TextBox("M",[current_x_pos,3.9*2.834],fontSize= 1.7*2.834)
            self.draw_objects.append(label) 
            marking = Line([current_x_pos,self.height-zero_triangle_height,current_x_pos,4.0*2.834],1*2.834)
            self.draw_objects.append(marking)
            pass
        step=100

        
        trian = Triangle((current_x_pos,self.height),zero_triangle_height,1*2.834)
        self.draw_objects.append(trian)
        

        label = TextBox("{:0.0f}".format(round((current_distance))),[current_x_pos,2.2*2.834],fontSize= 1.7*2.834)
        self.draw_objects.append(label)
        

        if roundStep:
                
                current_distance += (10-current_distance%10)
                if current_distance%50==0:
                    current_distance+=10
        else:
            current_distance+=(step)

        current_correction = self.get_correction_from_distance(current_distance,self.round_to_click)

        while turn<1 and current_distance<self.ballistic_data.maxDistance:

            current_x_pos = self.length-current_correction*(self.length/self.correction_on_turn)
            d = 0.5

            line_height = 2.0*2.834
            line_w = 0.25*2.834

            if (current_distance%(100))==0:
                trian = Triangle((current_x_pos,self.height),triangle_height,1.4*2.834)
                self.draw_objects.append(trian)
                label = TextBox("{:0.0f}".format(round((current_distance/100))),[current_x_pos,self.height-triangle_height],fontSize= big_font_size)
                self.draw_objects.append(label)
            elif (current_distance%(50)==0):
                trian = Triangle((current_x_pos,self.height),triangle_height,1.4*2.834)
                self.draw_objects.append(trian)
                label = TextBox("{:0.1f}".format(round((current_distance/100),2)),[current_x_pos,self.height-triangle_height],fontSize= small_font_size)
                self.draw_objects.append(label)
            else:
                marking = Line([current_x_pos,self.height,current_x_pos,self.height-line_height],line_w)
                self.draw_objects.append(marking)

            #print("i=",i,"  ",self.ballistic_data.cartrige)
            #print('step=',step,'  current_x_pos=', current_x_pos, '  current_correction=',  current_correction, '  current_distance=', current_distance)
            current_distance+=(10)
            i+=1
            current_correction = self.get_correction_from_distance(current_distance,self.round_to_click)
            turn =  math.floor(current_correction/self.correction_on_turn)
    def prepare_option_2(self, step=25.0, autoStep=True, roundStep=True, autoFilling=False):
        """Подготавливает объекты для отрисовки option 2 
        Args:
            step (float): Шаг разметки. Defaults to 100.0.
            fontSize (float): Автоматическое вычисление шага. Defaults to 8.0.
            autoStep (bool): [description]. Defaults to True.
            roundStep (bool): Привидение последовательности  к счету кратно сотни. Defaults to True.
            roundStep = True      165 200 250 300 350
            roundStep = False     165 215 265 315 365
            autoFilling (bool): Автоуменьшение шага. Defaults to True."""
        self.draw_objects = []
        self._add_border()
        current_distance = self.ballistic_data.rifle_shoot_distance #Начинаем с дистанции пристрелки
        i=1
        sticker_height = self.height
        turn = 0
        if sticker_height < 8*2.834: 
            sticker_height = 8*2.834
        
        if autoStep:step = self._get_option_2_min_step()
        current_x_pos = self.length   

        trian = Triangle((current_x_pos,sticker_height),3.0*2.834,1*2.834)
        self.draw_objects.append(trian)
        marking = Line([current_x_pos,sticker_height-3.0*2.834,current_x_pos,4.0*2.834],1*2.834)
        self.draw_objects.append(marking)

        label = TextBox("{:0.0f}".format(round((current_distance))),[current_x_pos,3.9*2.834],fontSize= 1.7*2.834)
        self.draw_objects.append(label)
        label = TextBox("M",[current_x_pos,2.2*2.834],fontSize= 1.7*2.834)
        self.draw_objects.append(label)

        if current_distance%step and roundStep :
                current_distance += (step-current_distance%step)
                if (current_distance%(step*2))==0:
                    current_distance+=step
                roundStep=False
        else:
            current_distance+=(step)

        current_correction = self._get_round_click(self.get_correction_from_distance(current_distance,self.round_to_click))

        while turn<1 and current_distance<self.ballistic_data.maxDistance:
            current_x_pos = self.length-current_correction*(self.length/self.correction_on_turn)
            d = 0.5

            line_height = 4.5*2.834
            line_w = 0.25*2.834

            if (current_distance%(step*2))==0:
                trian = Triangle((current_x_pos,sticker_height),2.5*2.834,1.4*2.834)
                self.draw_objects.append(trian)
                label = TextBox("{:0.0f}".format(round((current_distance))),[current_x_pos,(sticker_height-1.5*2.834)/2],fontSize= 3*2.834,rotation=270)
                self.draw_objects.append(label)
            else:
                marking = Line([current_x_pos,sticker_height,current_x_pos,sticker_height-line_height],line_w)
                self.draw_objects.append(marking)

            #print("i=",i,"  ",self.ballistic_data.cartrige)
            #print('step=',step,'  current_x_pos=', current_x_pos, '  current_correction=',  current_correction, '  current_distance=', current_distance)
            if autoFilling:
                if self._check_fill(current_distance+step/2,step/2,3):
                    step/=2
            current_distance+=(step)
            i+=1
            current_correction = self._get_round_click(self.get_correction_from_distance(current_distance,self.round_to_click))
            turn =  math.floor(current_correction/self.correction_on_turn)
    def prepare_option_3(self, step=25.0, autoStep=True, roundStep=True, autoFilling=False):
        """Подготавливает объекты для отрисовки option 3 
        Args:
            step (float): Шаг разметки. Defaults to 100.0.
            fontSize (float): Автоматическое вычисление шага. Defaults to 8.0.
            autoStep (bool): [description]. Defaults to True.
            roundStep (bool): Привидение последовательности  к счету кратно сотни. Defaults to True.
            roundStep = True      165 200 250 300 350
            roundStep = False     165 215 265 315 365
            autoFilling (bool): Автоуменьшение шага. Defaults to True."""
        self.draw_objects = []
        self._add_border()
        turn = 0
        if autoStep:step = self._get_option_3_min_step()
        current_x_pos = self.length   
        current_distance = self.ballistic_data.rifle_shoot_distance #Начинаем с дистанции пристрелки
        i=1
        big_font_size = self.font_size * 1.5

        triangle_height  =2.5*2.834 
        zero_triangle_height = 3.0*2.834
        sticker_height = self.height

        if sticker_height<=5*2.834:
            big_font_size = self.font_size*0.85
            zero_triangle_height =  (sticker_height - big_font_size)*1.1     
            triangle_height  = (sticker_height - big_font_size)
        elif sticker_height<=7*2.834:
            big_font_size -=(7*2.834-sticker_height)
            triangle_height  = (sticker_height - big_font_size)
            zero_triangle_height =  (sticker_height-2.2*2.834)
        else:
            label = TextBox("M",[current_x_pos,3.9*2.834],fontSize= 1.7*2.834)
            self.draw_objects.append(label) 
            marking = Line([current_x_pos,sticker_height-zero_triangle_height,current_x_pos,4.0*2.834],1*2.834)
            self.draw_objects.append(marking)
            pass
        

        
        trian = Triangle((current_x_pos,sticker_height),zero_triangle_height,1*2.834)
        self.draw_objects.append(trian)
        

        label = TextBox("{:0.0f}".format(round((current_distance))),[current_x_pos,2.2*2.834],fontSize= 1.7*2.834)
        self.draw_objects.append(label)

        if current_distance%step and roundStep:
                current_distance += (step-current_distance%step)
                if (current_distance%(step*2))==0:
                    current_distance+=step
                roundStep=False
        else:
            current_distance+=(step)

        current_correction = self._get_round_click(self.get_correction_from_distance(current_distance,self.round_to_click))

        while turn<1 and current_distance<self.ballistic_data.maxDistance:
            current_x_pos = self.length-current_correction*(self.length/self.correction_on_turn)
            d = 0.5

            line_height = 4.0*2.834
            line_w = 0.25*2.834

            if (current_distance%(step*2))==0:
                trian = Triangle((current_x_pos,sticker_height),triangle_height,1.4*2.834)
                self.draw_objects.append(trian)
                label = TextBox("{:0.0f}".format(round((current_distance)))[:-1],[current_x_pos,sticker_height-triangle_height],fontSize= big_font_size)
                self.draw_objects.append(label)
            else:
                marking = Line([current_x_pos,sticker_height,current_x_pos,sticker_height-triangle_height-big_font_size/2],line_w)
                self.draw_objects.append(marking)

            #print("i=",i,"  ",self.ballistic_data.cartrige)
            #print('step=',step,'  current_x_pos=', current_x_pos, '  current_correction=',  current_correction, '  current_distance=', current_distance)
            current_distance+=(step)
            i+=1
            current_correction = self._get_round_click(self.get_correction_from_distance(current_distance,self.round_to_click))
            turn =  math.floor(current_correction/self.correction_on_turn)
    def prepare_option_4(self, step=100, autoStep=False, roundStep=True, autoFilling=False):
        """Подготавливает объекты для отрисовки option 4 
                Args:
            step (float): Шаг разметки. Defaults to 100.0.
            fontSize (float): Автоматическое вычисление шага. Defaults to 8.0.
            autoStep (bool): [description]. Defaults to True.
            roundStep (bool): Привидение последовательности  к счету кратно сотни. Defaults to True.
            roundStep = True      165 200 250 300 350
            roundStep = False     165 215 265 315 365
            autoFilling (bool): Автоуменьшение шага. Defaults to True."""
        
        self.draw_objects = []
        self._add_border()
        turn = 0
        #if autoStep:step = self.get_option_3_min_step()
        current_x_pos = self.length   
        current_distance = self.ballistic_data.rifle_shoot_distance #Начинаем с дистанции пристрелки
        i=1

        big_font_size = self.font_size * 1.7 
        triangle_height  =2.5*2.834 
        zero_triangle_height = 3.0*2.834
        
        if self.height<=5*2.834:
            big_font_size = self.font_size * 1.1
            zero_triangle_height =  (self.height - big_font_size)*1.5     
            triangle_height  = (self.height - big_font_size)
        elif self.height<=7*2.834:
            big_font_size -=(7*2.834-self.height)
            triangle_height  = (self.height - big_font_size)
            zero_triangle_height =  (self.height-2.2*2.834)
        else:
            label = TextBox("M",[current_x_pos,3.9*2.834],fontSize= 1.7*2.834)
            self.draw_objects.append(label) 
            marking = Line([current_x_pos,self.height-zero_triangle_height,current_x_pos,4.0*2.834],1*2.834)
            self.draw_objects.append(marking)
            pass
        step=100

        
        trian = Triangle((current_x_pos,self.height),zero_triangle_height,1*2.834)
        self.draw_objects.append(trian)
        

        label = TextBox("{:0.0f}".format(round((current_distance))),[current_x_pos,2.2*2.834],fontSize= 1.7*2.834)
        self.draw_objects.append(label)
        
        if roundStep:
            current_distance += (25-current_distance%25)
            if (current_distance%100)==0:
                    current_distance+=25
        else:
            current_distance+=(step)

        

        current_correction = self.get_correction_from_distance(current_distance,self.round_to_click)


        while turn<1 and current_distance<self.ballistic_data.maxDistance:

            current_x_pos = self.length-current_correction*(self.length/self.correction_on_turn)
            d = 0.5

            line_height = 2.0*2.834
            line_w = 0.25*2.834

            if (current_distance%(100))==0:
                trian = Triangle((current_x_pos,self.height),triangle_height,1.4*2.834)
                self.draw_objects.append(trian)
                label = TextBox("{:0.0f}".format(round((current_distance/100))),[current_x_pos,self.height-triangle_height],fontSize= big_font_size)
                self.draw_objects.append(label)
            elif (current_distance%(50)==0):
                marking = Line([current_x_pos,self.height,current_x_pos,self.height-triangle_height-big_font_size/2],line_w)
                self.draw_objects.append(marking)
            elif (current_distance%(25)==0):
                marking = Line([current_x_pos,self.height,current_x_pos,self.height-triangle_height],line_w)
                self.draw_objects.append(marking)

            #print("i=",i,"  ",self.ballistic_data.cartrige)
            #print('step=',step,'  current_x_pos=', current_x_pos, '  current_correction=',  current_correction, '  current_distance=', current_distance)
            current_distance+=(25)
            i+=1
            current_correction = self.get_correction_from_distance(current_distance,self.round_to_click)
            turn =  math.floor(current_correction/self.correction_on_turn)
    def prepare_angular_turret(self):
        self._add_border()
        self.draw_objects = []
        self._add_border()
   

        label = TextBox("{:0.1f}мм".format(round((self.length/2.834))),[self.length/2,self.height + self.font_size*1.1], fontSize= self.font_size*0.8)
        self.draw_objects.append(label)

        
        label = TextBox("{:0.1f}мм".format(round((self.height/2.834))),[self.length+ self.font_size*1.1*2,self.height/2 ],rotation=270, fontSize= self.font_size*0.8)
        self.draw_objects.append(label)

        label = TextBox(self.correction_units,[self.length,self.font_size], fontSize= self.font_size)
        self.draw_objects.append(label)
        for correction in range(0,self.correction_on_turn+1):
            current_x_pos = (self.length-correction*(self.length/self.correction_on_turn))
            marking = Line([current_x_pos,self.font_size*1.2,current_x_pos,self.height],0.5*2.834)
            self.draw_objects.append(marking)

            label = TextBox("{:0.0f}".format(round((correction))),[current_x_pos,self.font_size],fontSize= self.font_size)
            if correction>0:
                self.draw_objects.append(label)
            if correction>=1:
                click_on_turn = self.correction_on_turn/self.correction_on_click
                click_on_one_unit = int(1/self.correction_on_click)
                for j in range(1,click_on_one_unit):
                    x_p = current_x_pos+j*(self.length/click_on_turn)

                    marking = Line([x_p,self.font_size*1.4,x_p,self.height],0.25*2.834)
                    self.draw_objects.append(marking)
        
    def set_sticker_height(self,height):
        self.height = height
    def set_correction_on_turn(self):
        self.correction_on_turn = int(self.correction_on_click * self.click_on_turn)
    def set_correction_on_click(self, correction):
        self.correction_on_click = correction
    def set_diametr(self,diametr):
        self.diametr = diametr
        self.length = math.pi * diametr
    def get_correction_from_distance(self,distance,round_to_click=False):
        if self.ballistic_data.correction_units == "MOA":
            correction = self.ballistic_data.get_MOA_from_distance(distance)
        else:
            correction = self.ballistic_data.get_MRAD_from_distance(distance)
        if round_to_click:
            return self._get_round_click(correction)
        else:
            return correction
    def _get_option_3_min_step(self):
          #Вычисление минимального шага
        for x in [5,10,25,50,100]:
            next_step_moa = self.get_correction_from_distance(x+self.ballistic_data.rifle_shoot_distance)
            size_mm = next_step_moa*(self.length/self.correction_on_turn)
            self.cntx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL)
            self.cntx.set_font_size(self.font_size*2.5)
            height, width  = self._get_text_box_size("{:0.0f}".format(round((self.ballistic_data.rifle_shoot_distance)))[:-1])
            if size_mm>(width/2):
                return x
        return 100
    def _get_option_2_min_step(self):
          #Вычисление минимального шага
        for x in [5,10,25,50,100]:
            next_step_moa = self.get_correction_from_distance(x+self.ballistic_data.rifle_shoot_distance)
            size_mm = next_step_moa*(self.length/self.correction_on_turn)
            self.cntx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL)
            self.cntx.set_font_size(self.font_size*1.5)
            fascent, fdescent, fheight, fxadvance, fyadvance = self.cntx.font_extents()

            height, width  = self._get_text_box_size("{:0.0f}".format(round((self.ballistic_data.rifle_shoot_distance))))
            if size_mm>(fheight/4):
                return x
        return 100
    def _get_min_step(self):
          #Вычисление минимального шага
        for x in [5,10,12.5,25,50,100]:
            next_step_moa = self.get_correction_from_distance(x+self.ballistic_data.rifle_shoot_distance)
            size_mm = next_step_moa*(self.length/self.correction_on_turn)

            self.cntx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL)
            self.cntx.set_font_size(self.font_size)
            height, width  = self._get_text_box_size("{:0.0f}".format(round((self.ballistic_data.rifle_shoot_distance))))
            if size_mm>(width/2):
                return x
        return 100
    def _check_fill(self,distance,step,count_step):
        result = False
        for x in range(1,count_step+1):
            if self._get_filling(distance+(step*x),step):
                result = True
            else:
                break
        return result
    def _get_filling(self,distance,step):

        next_distance = distance + step
        prev_distance = distance - step

        prev_moa = self._get_round_click(self.get_correction_from_distance(prev_distance))
        moa = self._get_round_click(self.get_correction_from_distance(distance))
        next_moa = self._get_round_click(self.get_correction_from_distance(next_distance))

        prev_x_pos = self._get_round_click(prev_moa)*(self.length/self.correction_on_turn)
        x_pos =  self._get_round_click(moa)*(self.length/self.correction_on_turn)
        next_x_pos = self._get_round_click(next_moa)*(self.length/self.correction_on_turn)

        font_h, font_w = self._get_text_box_size("{:0.0f}".format(round((distance))))
        font_w+=self.font_size+1
        delta_to_prev = x_pos-prev_x_pos
        delta_to_next = next_x_pos-x_pos

        if (delta_to_prev)> (font_w/2) and (delta_to_next)> (font_w/2) and delta_to_prev!=0 and delta_to_next!=0:
            return True
        else:
            return False
    def _add_border(self):
        """Рисует границы стикера
        """
        marking = Line([0,0,self.length,0],0.1)
        self.draw_objects.append(marking)
        marking = Line([0,self.height,self.length,self.height],0.1)
        self.draw_objects.append(marking)
    def draw(self,cntx, coords = [0,0]):
        for x in self.draw_objects:
            x.draw(cntx,coords)
    def _get_text_box_size(self,strText):
        self.cntx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL)
        self.cntx.set_font_size(self.font_size)
        (xx, y, width, height, dx, dy) = self.cntx.text_extents(strText)
        return  height, width
    def set_font_size(self,font_size):
        self.font_size = font_size
    def prepare_two_turn(self, step=100.0, autoStep=True, roundStep=True, autoFilling=True):
        """Подготавливает объекты для отрисовки на два оборота
        Args:
            step (float): Шаг разметки. Defaults to 100.0.
            fontSize (float): Автоматическое вычисление шага. Defaults to 8.0.
            autoStep (bool): [description]. Defaults to True.
            roundStep (bool): Привидение последовательности  к счету кратно сотни. Defaults to True.
            roundStep = True      165 200 250 300 350
            roundStep = False     165 215 265 315 365
            autoFilling (bool): Автоуменьшение шага. Defaults to True."""
        self.draw_objects = []
        self._add_border()
        current_distance = self.ballistic_data.rifle_shoot_distance #Начинаем с дистанции пристрелки
        i=1
        current_correction = self._get_round_click(self.get_correction_from_distance(current_distance))
        turn = 0
        if autoStep:step = self._get_min_step()

        while turn<2 and current_distance<self.ballistic_data.maxDistance:
            current_x_pos = (self.length-current_correction*(self.length/self.correction_on_turn))+self.length*turn
            d = self.height*0.05
            line_height = self.height-self.font_size-d
            font_y_pos = self.height-self.font_size*2

            line_w = 0.5*2.834
            if (i%2)==0 :
                line_height += self.font_size
                line_w = 0.25*2.834
                if turn<1:
                    marking = Line([current_x_pos,self.height,current_x_pos,self.height-font_y_pos-self.font_size+2*d],line_w)
                    self.draw_objects.append(marking)
                else:
                    marking = Line([current_x_pos,self.height,current_x_pos,self.height-font_y_pos+d+turn*self.height*0.07],line_w)
                    self.draw_objects.append(marking)
                    marking = Line([current_x_pos,self.height-font_y_pos-self.font_size,current_x_pos,0],line_w)
                    self.draw_objects.append(marking)
            else:
                marking = Line([current_x_pos,self.height,current_x_pos,self.height-font_y_pos+d+turn*self.height*0.07],line_w)
                self.draw_objects.append(marking)

                label = TextBox("{:0.0f}".format(round((current_distance))),[current_x_pos,self.height-font_y_pos-self.font_size*turn],fontSize= self.font_size)
                self.draw_objects.append(label)

            
            
            #print("i=",i,"  ",self.ballistic_data.cartrige)
            #print('step=',step,'  current_x_pos=', current_x_pos, '  current_correction=',  current_correction, '  current_distance=', current_distance)
            if current_distance%step and roundStep:
                current_distance += (step-current_distance%step)
                roundStep=False
            else:
                current_distance+=(step)
            if autoFilling:
                if self._check_fill(current_distance+step/2,step/2,3):
                    step/=2
            i+=1
            current_correction = self._get_round_click(self.get_correction_from_distance(current_distance))
            turn =  math.floor(current_correction/self.correction_on_turn)
    def prepare_one_turn(self, step=100.0, autoStep=True, roundStep=True, autoFilling=True):
        """Подготавливает объекты для отрисовки option 5 
        Args:
            step (float): Шаг разметки. Defaults to 100.0.
            fontSize (float): Автоматическое вычисление шага. Defaults to 8.0.
            autoStep (bool): [description]. Defaults to True.
            roundStep (bool): Привидение последовательности  к счету кратно сотни. Defaults to True.
            roundStep = True      165 200 250 300 350
            roundStep = False     165 215 265 315 365
            autoFilling (bool): Автоуменьшение шага. Defaults to True."""
        self.draw_objects = []
        self._add_border()
        current_distance = self.ballistic_data.rifle_shoot_distance #Начинаем с дистанции пристрелки
        i=1
        current_correction = self._get_round_click(self.get_correction_from_distance(current_distance))
        turn = 0
        if autoStep:step = self._get_min_step()
        while turn<1 and current_distance<self.ballistic_data.maxDistance:
            current_x_pos = self.length-current_correction*(self.length/self.correction_on_turn)
            d = 0.5
            line_height = self.height-self.font_size-d
            line_w = 0.5*2.834
            if (i%2)!=0:
                line_height -= self.font_size
            label = TextBox("{:0.0f}".format(round((current_distance))),[current_x_pos,self.height-line_height-d],fontSize= self.font_size)
            self.draw_objects.append(label)
            if i==2 and roundStep==False:
                height, width = self._get_text_box_size("{:0.0f}".format(round((self.ballistic_data.rifle_shoot_distance))))
                if current_correction*(self.length/self.correction_on_turn)<(width/2+0.8):
                    line_height-=self.font_size
            marking = Line([current_x_pos,self.height,current_x_pos,self.height-line_height],line_w)
            self.draw_objects.append(marking)
            #print("i=",i,"  ",self.ballistic_data.cartrige)
            #print('step=',step,'  current_x_pos=', current_x_pos, '  current_correction=',  current_correction, '  current_distance=', current_distance)
            if current_distance%step and roundStep:
                
                current_distance += (step-current_distance%step)
                current_distance +=step
                roundStep=False
            else:
                current_distance+=(step)
            if autoFilling:
                if self._check_fill(current_distance+step/2,step/2,3):
                    step/=2
            i+=1
            current_correction = self._get_round_click(self.get_correction_from_distance(current_distance))
            turn =  math.floor(current_correction/self.correction_on_turn)
    
    def _get_round_click(self, x):
        """Округляет поправку до цены клика
        Args:
            x (float): Поправка
        Returns:float
        """
        return round(x*(1/self.correction_on_click))/(1/self.correction_on_click)
