import script as sc

def test_get_xml_file(monkeypatch):
	class zipfile:
		def namelist(self):
			return ['a.xml','b']
	zf = zipfile()
	file = sc.get_xml_file(zf)
	assert file == 'a.xml'

def testt_get_xml_file_none(monkeypatch):
        class zipfile:
                def namelist(self):
                        return ['a','b']
        zf = zipfile()
        file = sc.get_xml_file(zf)
        assert file == None


