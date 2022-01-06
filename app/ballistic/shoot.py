# -*- coding: utf-8 -*-

import cairo
from app.ballistic.file_parser  import BallisticData
from app.ballistic.turret import TurretSticker
from app.ballistic.reticle import ReticleSticker
from app.ballistic.drawing import print_signature
from app.ballistic.drawing import printShootingConditions

def main(csvFilePath, htmFilePath, pdfOutFilePath, round_to_click = False, sticker_len_mm = 75, stickerHeight_mm = 9, click_on_turn=15):
    warning_list = []
    surface = cairo.PDFSurface(pdfOutFilePath, 597, 842)
    #surface = cairo.SVGSurface(pdfOutFilePath, 210, 900)
    context = cairo.Context(surface)
    dat = BallisticData()
    dat.load_data_file(csvFilePath,htmFilePath)
    warning_list+=dat.warning_list
    tur = TurretSticker((0,0),context,dat,len = sticker_len_mm*2.834,height=stickerHeight_mm*2.834,fontSize=3*2.834,round_to_click=round_to_click,click_on_turn=click_on_turn)

    

    y_pos = 30
    x_pos = 30
    y_pos = printShootingConditions(dat,context,x_pos,y_pos)
    y_pos+=  5*2.834
    #y_pos = tur.print_sticker_size(x_pos,y_pos)
    tur.set_font_size(3.3*2.834)
    tur.prepare_angular_turret()
    tur.draw(context,[x_pos,y_pos])
    tur.set_font_size(3*2.834)
    y_pos+=tur.height+20
    for xx in range(1,3):
        tur.prepare_option_1()
        tur.draw(context,[x_pos,y_pos])
        y_pos+=tur.height
    y_pos=tur.print_cartride(x_pos,y_pos)
    y_pos+=10
    tur_h=tur.height
    if tur.height<8*2.834:
        tur.set_sticker_height(8*2.834)
    for xx in range(1,3):
        tur.prepare_option_2()
        tur.draw(context,[x_pos,y_pos])
        y_pos+=tur.height
    tur.set_sticker_height(tur_h)
    y_pos=tur.print_cartride(x_pos,y_pos)
    y_pos+=10
    for xx in range(1,3):
        tur.prepare_option_3()
        tur.draw(context,[x_pos,y_pos])
        y_pos+=tur.height
    y_pos=tur.print_cartride(x_pos,y_pos)
    y_pos+=10
    for xx in range(1,3):
        tur.prepare_option_4()
        tur.draw(context,[x_pos,y_pos])
        y_pos+=tur.height
    y_pos=tur.print_cartride(x_pos,y_pos)
    y_pos+=10    

    tur_h=tur.height
    if tur.height<8*2.834:
        tur.set_sticker_height(8*2.834)
    for xx in range(1,3):
        tur.prepare_one_turn()
        tur.draw(context,[x_pos,y_pos])
        y_pos+=tur.height
    y_pos=tur.print_cartride(x_pos,y_pos)
    y_pos+=10    
    for xx in range(1,3):
        tur.prepare_two_turn()
        tur.draw(context,[x_pos,y_pos])
        y_pos+=tur.height
    y_pos=tur.print_cartride(x_pos,y_pos)
    y_pos+=15
    print_signature(context, 10*2.834, 5*2.834)
    
    mildot = ReticleSticker(context,dat)
    mildot.prepare_mildot(38*2.834)
    mildot.draw(context,(25*2.834,y_pos))
    mildot.draw(context,(50*2.834,y_pos))

    mildot.prepare_moa(55*2.834)
    mildot.draw(context,(73*2.834,y_pos))
    mildot.draw(context,(100*2.834,y_pos))
    
    context.show_page()

    return warning_list,"".join(xi for xi in dat.cartrige if xi.isalnum())
    
        #context.show_page()
        #y_pos=10
if __name__=='__main__':
    main('test/2.csv','test/2.htm','test/out.pdf')

        
        
   