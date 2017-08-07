import aaps

def test_kattis_result():
    result = aaps.KattisResult()
    result.add_AC('helloworld', '01-01-2017 08:00')
    result.add_WA('helloworld', '01-01-2017 07:00')
    assert len(result.AC) == 1
    assert len(result.WA) == 1
    assert result.AC[0].id == 'helloworld'
    assert result.WA[0].id == 'helloworld'
