from __future__ import division
import zipfile
import xmltodict
import os, re
from email.parser import Parser
from tqdm import tqdm


parser = Parser()

standard_disclaimer = '''***********
EDRM Enron Email Data Set has been produced in EML, PST and NSF format by ZL Technologies, Inc. This Data Set is licensed under a Creative Commons Attribution 3.0 United States License <http://creativecommons.org/licenses/by/3.0/us/> . To provide attribution, please cite to "ZL Technologies, Inc. (http://www.zlti.com)."
***********'''

class Document:
	def __init__(self):
		self.doc_id = ''
		self.sent_to = []
		self.cc = []
		self.email_body_count = 0

'''
Assumption is a word is *word*
Basically, a word is surrounded by spaces, special characters (@,.,,)
or anything. 
'''
def get_email_body_count(body):
	return len(re.sub('\W+',' ', body ).split(' '))


'''
Assuming every zipfile has only xml file which has the information required
'''
def get_xml_file(zf):
	namelist = zf.namelist()
	for file in namelist:
		if file.endswith('.xml'):
			return file
	return None

'''
Method only returns the raw text file, does not do any processing.
'''
def get_email_txt(zf, filename):
	return zf.open(filename).read()

'''
In the text format, I could have used sensible signals to get the body
but I relied upon the email.parser to be more accurate and standard.

Similar argument can be made for email['To'] and email['CC'] but I assumed the xml file to be more reliable. 
'''
def get_email_body(txt):
	email = parser.parsestr(txt)
	body = ''
	if email.is_multipart():
    		for part in email.get_payload():
        		body = body +  part.get_payload()
	else:
    		body = email.get_payload()
	return body

'''
From the existing list get only the ones which are xml format. Assumption all the files end with xml.zip
'''
def get_only_xml_zips(filelist):
	xml_zips = []
	for filename in filelist:
		if filename.endswith('xml.zip'):
			xml_zips.append(filename)
	return xml_zips

'''
Assumptions on how sent to of the XML file are stored are present here
if the sent_to is empty: return empty
if sent to, does not have any portions with @, sent empty
'''
def parse_sent_to(sent_to):
	sent_to = sent_to.strip()
	if sent_to == '':
		return []
	collected = []
	sent_list = re.compile('\s+').split(sent_to)
	for sent in sent_list:
		sent = sent.strip()
		if sent.find('@') == -1:
			continue
		sent = re.sub('[<>,]', '', sent)
		collected.append(sent.lower())
	return collected

'''
Dicti: is a dictionary which contains multi leveled key value pairs
keys: is a list of hierarchy of keys
if the key does not exist, it sends a empty string out
Avoids KeyError and exception handling
'''
def safe_dict(dicti, keys):
	if not isinstance(dicti, dict):
		return ''
	if len(keys) == 1:
		if keys[0] in dicti:
			return dicti[keys[0]]
		else:
			return ''
	if keys[0] in dicti:
		return safe_dict(dicti[keys[0]], keys[1:])
	else:
		return ''

'''
Returns a list of structure document objects for processing
'''
def get_documents(zf, xmlfile):
	lines = zf.open(xmlfile).read()
	dict_of = xmltodict.parse(lines)
	documents = []
	for document in safe_dict(dict_of,['Root','Batch','Documents','Document']):
		doc = Document()
		doc.doc_id = safe_dict(document,['@DocID'])
		for tag in safe_dict(document, ['Tags','Tag']):
			if safe_dict(tag, ['@TagName']) == '#To':
				sent_to = safe_dict(tag, ['@TagValue'])
				doc.sent_to = parse_sent_to(sent_to)
                        if safe_dict(tag, ['@TagName']) == '#CC':
                                cc = safe_dict(tag, ['@TagValue'])
                                doc.cc = parse_sent_to(cc)			
		for ftype in safe_dict(document,['Files','File']):
			if safe_dict(ftype, ['@FileType']) == 'Text':
				file_path = safe_dict(ftype, ['ExternalFile','@FilePath'])
				file_name = safe_dict(ftype, ['ExternalFile','@FileName'])
				email_txt = get_email_txt(zf, file_path+'/'+file_name)
				doc.email_body_count = get_email_body_count(get_email_body(email_txt))	
		documents.append(doc)
	return documents


'''
Updates the dictionry with the appropriate values
'''
def update_scores(alist, adict, value):
	for person in alist:
		if person in adict:
			adict[person] += value
		else:
			adict[person] = value

'''
the driver program
expects : edrm-endron-v2 format
'''
def main(indir):
	if not indir.endswith('/'):
		indir = indir + '/'
	dirlist = os.listdir(indir)
	xml_zips = get_only_xml_zips(dirlist)
	total_email_body_count = 0
	num_emails = 0
	sent_to = {}
	for xmlzip in tqdm(xml_zips):
		try:
			zf = zipfile.ZipFile(indir + xmlzip)
			xmlfile = get_xml_file(zf)
			if not xmlfile:
				continue
			documents = get_documents(zf, xmlfile)
			for doc in documents:
				num_emails += 1
				total_email_body_count += doc.email_body_count
				update_scores(doc.sent_to, sent_to, 1)
				update_scores(doc.cc, sent_to, 0.5)
		except:
			print xmlzip + ' has a problem'
			continue
	avg_email_body = 0
	if  num_emails and total_email_body_count:
		avg_email_body = total_email_body_count/num_emails
	print 'the average number of words with disclaimer ' + str(avg_email_body)
	disclaimer_count = get_email_body_count(standard_disclaimer)
	print 'the average number of works removing the disclaimer ' + str(avg_email_body - disclaimer_count)
	sorted_sent_to = sorted(sent_to, key=sent_to.get, reverse=True)
	for i, sent in enumerate(sorted_sent_to):
		if i >= 100:
			break
		print 'sent to ' + sent + ' count: ' + str(sent_to[sent])


if  __name__ == "__main__":
	import sys
	if len(sys.argv) < 2:
		print 'Please give the enron edrm v2 folder location'
	dirname = sys.argv[1]
	if os.path.isdir(dirname):
		main(dirname)
	else:
		print 'The given folder does not exist'
