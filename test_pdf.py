from app.ballistic.shoot import main as make_sticker

if __name__=='__main__':
    make_sticker( 'test/table.csv','test/table.htm','test/out.pdf',sticker_len_mm=75,round_to_click=False,click_on_turn=80)