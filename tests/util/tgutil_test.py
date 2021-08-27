
def test_split_msg_4096():
    from util.tgutil import split_msg
    msg = ''
    for i in range(0,4096):
        msg += '0'
    msgs = split_msg(msg)
    assert len(msgs) == 1


def test_split_msg_4099():
    from util.tgutil import split_msg
    msg = ''
    for i in range(0,4099):
        msg += f'{i%10}'
    msgs = split_msg(msg)
    assert len(msgs) == 2
    assert len(msgs[0]) == 4096
    assert len(msgs[1]) == 3


def test_split_msg_12289():
    from util.tgutil import split_msg
    msg = ''
    for i in range(0,12289):
        msg += f'{i%10}'
    msgs = split_msg(msg)
    assert len(msgs) == 4
    assert len(msgs[0]) == 4096
    assert len(msgs[3]) == 1