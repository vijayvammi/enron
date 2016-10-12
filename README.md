# enron

The expected file structure is:

enron_root_directory
	
	-- edrm-enron-v1
	
	-- edrm-enron-v2
	
	-- lost+found

My program expects enron_root_directory/edrm-enron-v2 as input. It does not require write access to that folder or its contents but only read access. Some of the test cases, create zip files (and delete zip files after test) and will require write access to the directory where the code resides.

Set up:
If you are using a virtualenv, activate virtual envioronment and install the required packages:
	$ pip install -r requirements.txt

Testing: The simplest way to test is $pytest -v (-s to see console output). 
Running : python script.py /path/to/enron/edrm/v2

Example output is provided in the repository. 

Hardware requirements: I had to use t2.small as the memory of t2.micro was not sufficient. [The program consumed more than 90% of 1gb ram at 93% of runtime and swapping was required]. The typical run time on the full dataset is 12-14 mins. I think, unzippping and processing will be much slower than using zipfile module. 

Assumptions:
1). A word in email body is considered as *some_alpha_numeric_content*. The * could be a ',',' ', '.', '*' etc.
2). Every zipfile has one and only one xml file which has the metadata on emails
3). The email body is standard MIME and readily parsable by any of the MIME parsers.
4). An email address should have @ in it to be considered valid and I remove any special characters in the word containing @. 
	

