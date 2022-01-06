# -*- coding: utf-8 -*-
from app.ballistic.drawing import Sticker
from app.ballistic.drawing import Line
from app.ballistic.drawing import Circle
from app.ballistic.drawing import TextBox
from app.ballistic.drawing import Triangle
from app.ballistic.file_parser  import BallisticData
class ReticleSticker(Sticker):

    def __init__(self,  cntx, ballistic_data:BallisticData, coords=(0,0), height=9*2.834, font_size=2.0*2.834):
        super(ReticleSticker,self).__init__(cntx, ballistic_data, height, coords)
        self.font_size = font_size

    def prepare_moa(self,height = 54*2.834):
        scale = height/27 #Значение масштаба
        font_size  = self.font_size * scale/2.834

        self.draw_objects = []
        self.draw_objects.append(Line([0,0,0,25*scale],0.15*scale))
        self.draw_objects.append(Line([-(1.69/2)*scale,0,(1.69/2)*scale,0],0.15*scale))
        self.draw_objects.append(Line([0,25*scale,0,26*scale],0.75*scale))
        #Горизонтальная разметка
        for x in range(1,25):
            if (x%5==0):
                self.draw_objects.append(Line([-(1.69/2)*scale,x*scale,(1.69/2)*scale,x*scale],0.15*scale))
            else:
                self.draw_objects.append(Line([-(0.84/2)*scale,x*scale,(0.84/2)*scale,x*scale],0.15*scale))
        #Подписи
        distance = self.ballistic_data.rifle_shoot_distance
        label = TextBox("{:0.0f}".format(distance),[(1.69/2+0.15)*scale, 0],fontSize= font_size,anchor='LC')
        self.draw_objects.append(label)
        for moa in range(1,26):
            distance = self.ballistic_data.get_distance_from_MOA(moa)
            if (moa%5==0):
                label = TextBox("{:0.0f}".format(distance),[(1.69/2+0.15)*scale, moa*scale],fontSize= font_size,anchor='LC')
                self.draw_objects.append(label)
            else:
                x_0 = 0
                y_0 = moa*scale
                anchor = "RC"

                if moa%10 in [1,4,6,9]:
                    x_0 = -(0.15+(0.84/2))*scale
                    anchor = "RC"
                elif moa%10 in [2,7]:
                    x_0 = (0.15+(0.84/2))*scale
                    y_0 = moa*scale-(0.2*scale)
                    anchor = "LC"
                elif moa%10 in [3,8]:
                    x_0 =(0.15+(0.84/2))*scale
                    y_0 = moa*scale+(0.2*scale)
                    anchor = "LC"
                label = TextBox("{:0.0f}".format(distance),[x_0, y_0],fontSize= font_size*0.7,anchor=anchor)
                self.draw_objects.append(label)
        label = TextBox(self.ballistic_data.cartrige,[-4.2*scale, 12.5*scale], fontSize= font_size*0.65,rotation=90)
        self.draw_objects.append(label)

    
    def prepare_mildot(self,height = 23*2.834):
         #Значение масштаба
        
        scale = height/5.75

        font_size= self.font_size * height*0.04/2.834
        self.draw_objects = []
        # Линии
        self.draw_objects.append(Line([0,0,0,4.7*scale],0.05*scale))
        self.draw_objects.append(Line([-0.125*scale,0,0.125*scale,0],0.05*scale))
        self.draw_objects.append(Line([0,5*scale,0,5.5*scale],0.25*scale))
        for x in range(1,5):    #Точки
            self.draw_objects.append(Circle((0, x*scale), 0.25*scale))
        distance = self.ballistic_data.rifle_shoot_distance
        label = TextBox("{:0.0f}".format(distance),[0.20*scale, 0],fontSize= font_size,anchor='LC')
        self.draw_objects.append(label)
        for x in range(1,11):
            mrad = x/2
            distance = self.ballistic_data.get_distance_from_MRAD(mrad)
            if x%2==0:
                label = TextBox("{:0.0f}".format(distance),[0.20*scale, mrad*scale],fontSize= font_size,anchor='LC')
                self.draw_objects.append(label)
            else:
                label = TextBox("{:0.0f}".format(distance),[-0.15*scale, mrad*scale],fontSize= font_size*0.85,anchor='RC')
                self.draw_objects.append(label)
        self.ballistic_data.cartrige


        label = TextBox(self.ballistic_data.cartrige,[-1.1*scale, 2.5*scale], fontSize= font_size*0.8,rotation=90)
        self.draw_objects.append(label)