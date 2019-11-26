#importing required modules
try:
	import time
	import sys
	import os
	import boto3
	import csv
	import datetime as dt
	import datefinder as df
except ImportError:
	print('the import statement has troubles trying to load a module')
	sys.exit()
except ModuleNotFoundError:
	print(' Module not founded in your python engine. Install them and try again')
	sys.exit()

start_time=time.time() #used to calculate the running time of this program


#Folder Location 
basepath="Receipts/"

totalBills=0	#this variable is to calculate the files in the given folder
datedBills=0	#this variable is to calculate how many of them contains dates

now = dt.datetime.now()	#Storing the current date

db=[]#store the dated bills
eb=[]#stroing the  undated bills

#the credentials.csv file contains access_key and secret_key to connect the aws rekognition
try:
	with open('credentials.csv','r') as input:	
		next(input)
		reader=csv.reader(input)
	
		for line in reader:
			access_key=line[2]
			secret_key=line[3]
except FileNotFoundError:
	print('The given credentials file is not located. Give the correct path and try again')
	sys.exit()


try:
	for entry in os.listdir(basepath):	#accessing all the file from a given path
		if os.path.isfile(os.path.join(basepath,entry)):
			with open(os.path.join(basepath,entry),'rb') as source_img:	#opening the file to convert that into binary form 
				source_byte=source_img.read()
				totalBills+=1
		
			print('Image ',entry,' is processing')	#this is for reference to identify with is file is currently in progress
			client=boto3.client('rekognition',aws_access_key_id=access_key,aws_secret_access_key=secret_key,region_name='us-east-1')	#accessing aws rekognition
	
			response=client.detect_text(Image={'Bytes':source_byte})	#storing the response which it get from AWS api
			
			sdate=dt.datetime(2019,1,1)	#Store the some date to avoid the unnecessary dates from files
		
			text_detection=response['TextDetections']#storing the detected text from the response to avoid unnecessary data
			
			date=[] #list to store the dates
			ele=0
			
			#creating a temp files to store the detected text
			with open ('temp.txt','w') as temp:
				for text in text_detection:
					temp.write(text['DetectedText'])#storing the detect text
					temp.write(' ')
				temp.close()
			
			#reading the temp file
			with open ('temp.txt','r') as temp:
				content=temp.readlines()	#To form the list from the file
				content=content[0].split() #Spliting every words by ,(comma)
				content=list(dict.fromkeys(content)) #removing dublicates
			
				try:
					for line in content: #accessing word by word
						matches=df.find_dates(line)	#finding the date
						for match in matches:
							if now>match and match>sdate: #applying conditions to check the dates
								date.append(str(match)) #adding the date into the date list which already created
								ele=1
				except OverflowError:
					pass
		
				temp.close()	
		
		print('Process is done') #This is also for reference to know the image process is done
		
		if ele==1:
			datedBills+=1
			db.append({entry:date})
		else:
			eb.append(entry)
except Exception as ex:
    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
    message = template.format(type(ex).__name__, ex.args)
    print (message)
	

print()
#printing file names
print('Files that contains dates which api recognized')
print()
for text in db:
	print(text,'\n')
print()

print('Files that is not contails any which api recognized')
print()
for text in eb:
	print(text,'\n')
print()

acy=(datedBills/totalBills)*100
print('Dated Bills= ',datedBills)	#dated bill count
print('Total Bills= ',totalBills)	#total bill count
print('Accuracy= ',acy)	#accurancy of the progress

print("--- %s seconds ---" % (time.time() - start_time)) #printing the execution time of the program