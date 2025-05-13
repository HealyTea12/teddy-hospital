import teddy_hospital


def test_teddy_hospital(tmp_dir):
    assert teddy_hospital.add_one(1) == 2
