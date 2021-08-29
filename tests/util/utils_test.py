from datetime import datetime

def test_get_date_list():
    from util.utils import get_date_list
    ds = get_date_list(datetime(2021, 7, 1), datetime(2021, 8, 20))
    assert len(ds) == 2
    print(ds)
    assert len(ds['xmm']) == 7
    assert ds['xmm'][0] == datetime(2021,7,7)
    assert ds['xmm'][1] == datetime(2021,7,14)
    assert ds['xmm'][2] == datetime(2021,7,21)
    assert ds['xmm'][3] == datetime(2021,7,28)
    assert ds['xmm'][4] == datetime(2021,8,4)
    assert ds['xmm'][5] == datetime(2021,8,11)
    assert ds['xmm'][6] == datetime(2021,8,18)
    assert len(ds['dmm']) == 2
    assert ds['dmm'][0] == datetime(2021,7,14)
    assert ds['dmm'][1] == datetime(2021,8,11)

def test_get_target_date():
    from util.utils import get_target_date
    ds = get_target_date(datetime(2021, 7, 1), datetime(2021, 8, 20))
    assert len(ds) == 2
    print(ds)
    assert len(ds['xmm']) == 7
    assert ds['xmm'][0] == datetime(2021,7,7)
    assert ds['xmm'][1] == datetime(2021,7,14)
    assert ds['xmm'][2] == datetime(2021,7,21)
    assert ds['xmm'][3] == datetime(2021,7,28)
    assert ds['xmm'][4] == datetime(2021,8,4)
    assert ds['xmm'][5] == datetime(2021,8,11)
    assert ds['xmm'][6] == datetime(2021,8,18)
    assert len(ds['dmm']) == 2
    assert ds['dmm'][0] == datetime(2021,7,14)
    assert ds['dmm'][1] == datetime(2021,8,11)

def test_get_week_num():
    from util.utils import get_week_num
    # 1号为周一
    assert get_week_num(2021, 6, 1) == 0
    assert get_week_num(2021, 6, 16) == 2
    # 1号为周四
    assert get_week_num(2021, 7, 1) == 0
    assert get_week_num(2021, 7, 14) == 2
    # 1号为周日
    assert get_week_num(2021, 8, 1) == 0
    assert get_week_num(2021, 8, 4) == 1
    assert get_week_num(2021, 8, 11) == 2


def test_get_xmm_maxtry():
    from util.utils import get_xmm_maxtry
    # 周三
    assert get_xmm_maxtry(datetime(2021, 8, 4)) == 3
    # 周日
    assert get_xmm_maxtry(datetime(2021, 8, 1)) == -1
    # 周五
    assert get_xmm_maxtry(datetime(2021, 8, 6)) == 1


def test_get_dmm_maxtry():
    from util.utils import get_dmm_maxtry
    # 31日月
    assert get_dmm_maxtry(datetime(2021, 8, 1)) == 30
    # 28日月
    assert get_dmm_maxtry(datetime(2021, 2, 1)) == 27
    # 29日月
    assert get_dmm_maxtry(datetime(2024, 2, 1)) == 28