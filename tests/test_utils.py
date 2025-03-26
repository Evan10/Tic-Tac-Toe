import pytest

from common.utils import is_id, create_id



#TODO:
# write pytests

def test_is_id():
    
    assert not is_id("00000000-0000-0000-00000000000000000") 
    assert not is_id("00000000-0000-0000-0000-00000000000") 
    assert not is_id("00000000-0000-0000-0000-00000000000-")
    assert not is_id("00000000-0000-0000-0000-00000000_000")
    assert not is_id("000000000-000-0000-0000-000000000000")
    assert     is_id("00000000-0000-0000-0000-000000000000") 
    assert     is_id("abcdefgh-ijkl-mnop-qrst-uvwxyz012345")

    for x in range(10):
        assert is_id(create_id())
    
    with pytest.raises(ValueError):
        is_id(1)
        is_id({"abcdefgh-ijkl-mnop-qrst-uvwxyz012345"})
        is_id(3.3)
