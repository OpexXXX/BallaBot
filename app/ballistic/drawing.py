# -*- coding: utf-8 -*-
import cairo
import math
from app.ballistic.file_parser  import BallisticData


def printShootingConditions(bldat:BallisticData,cntx, x_pos,y_pos,font_Size=3.0*2.834):
    
    label = TextBox(bldat.cartrige,fontSize=4*2.834,anchor='LT')
    label.draw(cntx,[x_pos,y_pos])
    y_pos+=font_Size*1.5

    printList = [
    bldat.rifle_name,
    "Нач. скорость скорректированная по температуре, м/с  "+str(bldat.cartrige_velocity),
    bldat.cartrige_bk,
    "Дистанция пристрелки, м:  " + str(round(bldat.rifle_shoot_distance)),
    bldat.temperature,
    bldat.humidity,
    bldat.pressure]

    for row in printList:
        label = TextBox(str(row),fontSize=font_Size,anchor='LT')
        label.draw(cntx,[x_pos,y_pos])
        y_pos+=font_Size*1.2
    return y_pos


def print_signature(cntx, x_pos,y_pos,font_Size=2.0*2.834):
    label = TextBox("Generated by Telegram bot @opex618_bot" ,fontSize=font_Size,anchor='LT')
    label.draw(cntx,[x_pos,y_pos])


class Triangle(object):
    """
   x1y1 ------ x2y2
        \    /
         \  /
          \/
         x0y0
    """
    def __init__(self, coords, height, width, fill=True):
        """[summary]
        Args:
            coords (turpla): (x0y0)
            height (float): [description]
            width (float): [description]
            fill (bool, optional): [description]. Defaults to True.
        """
        self.coords = coords
        self.width = width
        self.height = height
        self.fill = fill

    def get_coords(self, coords):

        x0 = self.coords[0]+coords[0]
        y0 = self.coords[1]+coords[1]
        
        x1 = x0-self.width/2
        y1 = y0-self.height

        x2 = x0+self.width/2
        y2 = y0-self.height
        return x0,y0,x1,y1, x2, y2

    def draw(self,ctx, coords):
        (x0,y0,x1,y1,x2,y2) = self.get_coords(coords)

        ctx.set_source_rgba(0, 0, 0, 1)
        ctx.set_line_width(0.01)
        #context.set_line_cap(cairo.LINE_CAP_BUTT)
        ctx.set_line_join(cairo.LINE_JOIN_MITER)
        ctx.move_to(x0, y0)
        ctx.line_to(x1, y1)
        ctx.line_to(x2, y2)
        ctx.fill()
        ctx.stroke()

class Circle(object):
    def __init__(self, coords, diametr, fill=True):
        self.coords = coords
        self.diametr = diametr
        self.fill = fill
    
    def draw(self,ctx, coords):
        x_c = self.coords[0]+coords[0]
        y_c = self.coords[1]+coords[1]

        ctx.set_source_rgba(0, 0, 0, 1)
        ctx.arc(x_c, y_c, self.diametr/2 , 0, 2*math.pi)
        ctx.fill()
        ctx.stroke()

class TextBox(object):
    def __init__(self,text, coords = (0,0), anchor='CB', fontSize=2.0, rotation=0):
        """
        Args:
            text (str): текст
            coords ([x0,y0]): Координаты
            anchor (str): Отрисовка относительно Top Centr Right Left Bottom  TC = TopCentr. Defaults to 'TC'.
            fontSize (float, optional): [description]. Defaults to 8.0.
        """
        self.coords = coords
        self.txt = str((text))
        self.anchor = anchor
        self.font_size = fontSize
        self.rotation=rotation

    def draw(self,ctx, coords,  fontName="Arial",  verticalPadding=0):

        
        rotation =self.rotation * math.pi / 180
        ctx.select_font_face(fontName, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(self.font_size)
        fascent, fdescent, fheight, fxadvance, fyadvance = ctx.font_extents()

        (x, y, width, height, dx, dy) = ctx.text_extents(self.txt)
        x = self.coords[0]+coords[0]
        y = self.coords[1]+coords[1]

        if rotation == 0:
            if self.anchor=='CB':
                y-=height/2
            if self.anchor=='LT':
                x+=(width/2)
                y+=height/2
            if self.anchor=='LC':
                x+=(width/2)
                
            if self.anchor=='RC':
                x-=(width/2)

        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(rotation)
        lines = self.txt.split("\n")

        for i in range(len(lines)):
            line = lines[i]
            xoff, yoff, textWidth, textHeight = ctx.text_extents(line)[:4]
            offx = -textWidth / 2.0
            offy = (fheight/4 ) + (fheight + verticalPadding) * i
            ctx.move_to(offx, offy)
            ctx.show_text(line)
        ctx.restore()

        """def draw(self,ctx,coords=(0,0)):
        x_c = self.coords[0]+coords[0]
        y_c = self.coords[1]+coords[1]
        ctx.select_font_face("Calibri", cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(self.font_size)
        (x, y, width, height, dx, dy) = ctx.text_extents(self.txt)
        if self.anchor=='CB':
            x_c-=(width/2)
        if self.anchor=='LT':
            y_c+=height
        if self.anchor=='LC':
            y_c+=height/2
        if self.anchor=='RC':
            y_c+=height/2
            x_c-=width
        ctx.set_source_rgb(0, 0, 0)
        ctx.move_to(x_c, y_c)
        ctx.show_text(self.txt)"""

class Line(object):

    def __init__(self,coords,width):
        self.coords = coords
        self.width = width

    def get_coords(self, coords):
        x0 = self.coords[0]+coords[0]
        y0 = self.coords[1]+coords[1]
        x1 = self.coords[2]+coords[0]
        y1 = self.coords[3]+coords[1]
        return x0,y0,x1,y1

    def draw(self,ctx, coords):
        (x0,y0,x1,y1) = self.get_coords(coords)

        ctx.set_source_rgba(0, 0, 0, 1)
        ctx.set_line_width(self.width)
        #context.set_line_cap(cairo.LINE_CAP_BUTT)
        ctx.move_to(x0, y0)
        ctx.line_to(x1, y1)
        ctx.stroke()

class Sticker(object):
    def __init__(self,  cntx, ballistic_data:BallisticData, height, coords=(0,0)):
        self.draw_objects = []
        self.ballistic_data = ballistic_data
        self.cntx = cntx
        self.height = height
        self.coords = coords
    def draw(self,cntx, coords = [0,0]):
        for x in self.draw_objects:
            x.draw(cntx,coords)
