
def test_get_week_num():
    from util.utils import get_week_num
    # 1号为周四
    assert get_week_num(2021, 7, 1) == 1
    assert get_week_num(2021, 7, 14) == 2
    # 1号为周日
    assert get_week_num(2021, 8, 1) == 0
    assert get_week_num(2021, 8, 4) == 1
    assert get_week_num(2021, 8, 11) == 2

