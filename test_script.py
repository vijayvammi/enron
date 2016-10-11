import script as sc
import zipfile, os

zipfilename = 'test_enron.xml.zip'

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def create_zipfile(xml=True):
    zf = zipfile.ZipFile(zipfilename, mode='w')
    try:
        if xml:
            zf.write('test.xml')
        zf.write('text_000')
        zipdir('text_000/', zf)
    except:
        raise    
    finally:
        zf.close()

def delete_zipfile():
    if os.path.isfile(zipfilename):
        os.remove(zipfilename)                


def test_get_xml_file():
	create_zipfile()
	zf = zipfile.ZipFile(zipfilename, 'r')
	xmlfile = sc.get_xml_file(zf)
	try:
		assert xmlfile == 'test.xml'
	finally:
		delete_zipfile()

def test_get_xml_file_none():
	create_zipfile(False)
	zf = zipfile.ZipFile(zipfilename, 'r')
	xmlfile = sc.get_xml_file(zf)
	try:
		assert xmlfile == None
	finally:
		delete_zipfile()    

def test_get_only_xml_zips():
	filelist = ['a.xml.zip','b']
	xml_zips = sc.get_only_xml_zips(filelist)
	assert len(xml_zips) == 1

def test_get_only_xml_zips_none():
	filelist = ['b']
	xml_zips = sc.get_only_xml_zips(filelist)
	assert len(xml_zips) == 0

def test_safe_dict_one_level():
	dicti = {'a':1, 'b':2}
	assert sc.safe_dict(dicti, ['a']) == 1
	assert sc.safe_dict(dicti, ['b']) == 2

def test_safe_dict_one_level_none():
	dicti = {'a':1, 'b':2}
	assert sc.safe_dict(dicti, ['c']) == ''

def test_safe_dict_two_level():
	dicti = {'a':{'a1':1}, 'b':{'b1':2}}
	assert sc.safe_dict(dicti, ['a', 'a1']) == 1
	assert sc.safe_dict(dicti, ['b', 'b1']) == 2

def test_safe_dict_two_level_none():
	dicti = {'a': 1, 'b': 2}
	assert sc.safe_dict(dicti, ['a', 'a1']) == ''

def test_get_email_txt():
	create_zipfile()
	zf = zipfile.ZipFile(zipfilename, 'r')
	filename = 'text_000/test_file.txt'
	try:
		assert sc.get_email_txt(zf, filename).strip() == 'I have 4 words'
	finally:
		delete_zipfile()

def test_get_email_body():
	txt = open('text_000/test_email.txt').read()
	body = sc.get_email_body(txt)
	assert body.strip() == 'I have 4 words.'

def test_parse_sent_to():
	sent_to = 'a <a@web.com>, b <b@web.com>'
	assert len(sc.parse_sent_to(sent_to)) == 2
	sent_to = 'a a@web.com, b <b@web.com>'
	assert len(sc.parse_sent_to(sent_to)) == 2
	sent_to = 'a, b'
	assert len(sc.parse_sent_to(sent_to)) == 0
	sent_to = 'a a@web.com, b'
	assert len(sc.parse_sent_to(sent_to)) == 1
	sent_to = 'a@web.com'
	assert len(sc.parse_sent_to(sent_to)) == 1

def test_get_documents(monkeypatch):
	class mockzf:
		def open(self, file):
			return mockzf()
		def read(self):
			return ['a','b']

	def safe_dict(dicti, keys):
		if keys[0] == '@TagValue':
			return 'a <a@web.com>, b <b@web.com>'
		if keys[0] == '@TagName':
			return '#To'
		if keys[0] == '@FileType':
			return 'Text'
		if keys[0] == 'ExternalFile':
			return 'file'
		return ['a <a@web.com>', 'b <b@web.com>']
	def get_email_txt(zf, path):
		return 'I have 4 words'
	def get_email_body(txt):
		return 'I have 4 words'
	monkeypatch.setattr(sc, 'get_email_txt', get_email_txt)
	monkeypatch.setattr(sc, 'get_email_body', get_email_body)  
	monkeypatch.setattr(sc, 'safe_dict', safe_dict)
	monkeypatch.setattr(sc.xmltodict, 'parse', get_email_body)
	zf = mockzf()
	docs = sc.get_documents(zf, 'xmlfile')
	assert len(docs) == 2
	for doc in docs:
		assert len(doc.sent_to) == 2
		assert doc.email_body.strip() == 'I have 4 words'


def test_get_documents_integration():
	create_zipfile()
	zf = zipfile.ZipFile(zipfilename, 'r')
	xmlfile = 'test.xml'
	try:
		docs = sc.get_documents(zf, xmlfile)
	finally:
		delete_zipfile()
	assert len(docs) == 2

def test_update_scores():
	alist = ['a', 'b']
	adict = {'a':2}
	sc.update_scores(alist, adict, 1)
	assert adict['a'] == 3
	assert adict['b'] == 1
	 
def test_main():
	create_zipfile()
	sc.main('.')
	delete_zipfile()	
