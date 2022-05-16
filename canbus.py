import pandas as pd
import datetime
import matplotlib.pyplot as plt



# Get CAN log file
def getlog(filename):
	with open(filename) as f:
		lines = f.read().splitlines()
	return lines


# Parse CAN log file into List
def parselog(d):
	r = []
	firstdt = datetime.datetime.fromtimestamp(float(d[0][1:18]))
	for i in d:
		time = float(i[1:18])
		dt = datetime.datetime.fromtimestamp(time)
		elasped = dt - firstdt
		int = i[20:24]
		data = i[25:]
		#canid = i[25:28]
		canid = data.split("#")[0]
		#code = i[29:]
		code = data.split("#")[1]
		c1 = code[0:2]
		c2 = code[2:4]
		c3 = code[4:6]
		c4 = code[6:8]
		c5 = code[8:10]
		c6 = code[10:12]
		c7 = code[12:14]
		c8 = code[14:16]
		r.append([dt,elasped,int,canid,code,c1,c2,c3,c4,c5,c6,c7,c8])
	return r


# Return Unique CAN IDs
def uniquecanid(df):
	l = df.CanID.unique().tolist()
	l.sort()
	return l


# Count number of CAN IDs
def countcanid(df):
	return df['CanID'].value_counts()



# Return signed int
def signedint(h):
	x = int(h,16)
	if x > 0x7FFFFFFF:
		x-=0x100000000
	return x



# Unpack CAN data in DataFrame to all possible values
def unpack(df):
	cols = ["C1","C2","C3","C4","C5","C6","C7","C8"]

	# 8-Bit
	counter=1
	for c in cols:
		df['8bit-unsigned-'+str(counter)] = df[c].apply(lambda x: int(x,16))
		df['8bit-signed-'+str(counter)] = df[c].apply(lambda x: signedint(x))
		counter+=1

	# 16-Bit
	counter=1
	max = 8

	for c in cols:
		if counter == max:
			break
		df['16bit-unsigned-'+str(counter)] = (df[cols[counter-1]]+df[cols[counter]]).apply(lambda x: int(x,16))
		df['16bit-signed-'+str(counter)] = (df[cols[counter-1]]+df[cols[counter]]).apply(lambda x: signedint(x))
		counter+=1

	# 32-Bit
	counter=1
	max = 6
	for c in cols:
		if counter == max:
			break
		df['32bit-unsigned-'+str(counter)] = (df[cols[counter-1]]+df[cols[counter]]+df[cols[counter+1]]+df[cols[counter+2]]).apply(lambda x: int(x,16))
		df['32bit-signed-'+str(counter)] = (df[cols[counter-1]]+df[cols[counter]]+df[cols[counter+1]]+df[cols[counter+2]]).apply(lambda x: signedint(x))
		counter+=1

	return df



# Search Function
def search(df,s,e):

	cols = ['8bit-signed-1','8bit-signed-2','8bit-signed-3','8bit-signed-4','8bit-signed-5','8bit-signed-6','8bit-signed-7','8bit-signed-8',
		'8bit-unsigned-1','8bit-unsigned-2','8bit-unsigned-3','8bit-unsigned-4','8bit-unsigned-5','8bit-unsigned-6','8bit-unsigned-7','8bit-unsigned-8',
		'16bit-signed-1','16bit-signed-2','16bit-signed-3','16bit-signed-4','16bit-signed-5','16bit-signed-6','16bit-signed-7',
		'16bit-unsigned-1','16bit-unsigned-2','16bit-unsigned-3','16bit-unsigned-4','16bit-unsigned-5','16bit-unsigned-6','16bit-unsigned-7',
		'32bit-signed-1','32bit-signed-2','32bit-signed-3','32bit-signed-4','32bit-signed-5',
		'32bit-unsigned-1','32bit-unsigned-2','32bit-unsigned-3','32bit-unsigned-4','32bit-unsigned-5',
		]

	df = df[df['32bit-signed-3'].between(s, e, inclusive=True)]
	return df



# Extract Stats from DataFrame
def analysis(df):
	analysis_data = {}
	analysis_data['canids'] = uniquecanid(df)
	for id in analysis_data['canids']:
		df_canid = df.loc[df['CanID']==id]
		analysis_data['canid'] = {str(id): {'count_c1': df_canid['C1'].value_counts().count() }}
	
	return analysis_data


# Export data to HTML/Images for review
def export(df, canid):

	f = open("out/data_" + str(canid) + ".html", "a")
	f.write("<html>")


	cols = ['8bit-signed-1','8bit-signed-2','8bit-signed-3','8bit-signed-4','8bit-signed-5','8bit-signed-6','8bit-signed-7','8bit-signed-8',
		'8bit-unsigned-1','8bit-unsigned-2','8bit-unsigned-3','8bit-unsigned-4','8bit-unsigned-5','8bit-unsigned-6','8bit-unsigned-7','8bit-unsigned-8',
		'16bit-signed-1','16bit-signed-2','16bit-signed-3','16bit-signed-4','16bit-signed-5','16bit-signed-6','16bit-signed-7',
		'16bit-unsigned-1','16bit-unsigned-2','16bit-unsigned-3','16bit-unsigned-4','16bit-unsigned-5','16bit-unsigned-6','16bit-unsigned-7',
		'32bit-signed-1','32bit-signed-2','32bit-signed-3','32bit-signed-4','32bit-signed-5',
		'32bit-unsigned-1','32bit-unsigned-2','32bit-unsigned-3','32bit-unsigned-4','32bit-unsigned-5',
		]

	df_canid = df.loc[df['CanID']==canid]

	for i in cols:
		fig = plt.figure()
		df_canid[i].plot()
		filename = "output_" + str(canid) + "_" + i + ".png"
		filenamesv = "out/output_" + str(canid) + "_" + i + ".png"
		fig.savefig(filenamesv)
		plt.clf()
		plt.close()
		f.write("CANID: " + str(canid) + ", Data: " + str(i) + "<img src=\"" + filename + "\"><BR>")

	f.write("</html>")
	f.close()



if __name__ == "__main__":

	# Load data from log file
	f = input("Log Filename: ")
	data = getlog(f)
	data = parselog(data)
	

	# Generate Dataframe
	headers = ["Time","Elasped","Interface","CanID","Code","C1","C2","C3","C4","C5","C6","C7","C8"]
	df = pd.DataFrame(data, columns=headers)

	df = df.set_index('Elasped')
	del df['Time']

	df = df.replace('', '0')
	df = unpack(df)


	# Get Stats
	analysis_data = analysis(df)
	print("Number of CAN IDs found: " + str(len(analysis_data['canids'])))

	
	# Export Data
	for canid in analysis_data['canids']:
		export(df,canid)



	### Below are example uses to search data


	# Example - Search Time and Values
	start = '00:00:03.000000'
	end = '00:00:09.000000'
	valuelow = 400
	valuehigh = 2000
	
	sdf = df.loc[start:end]
	rdata = search(sdf,valuehigh,valuelow)


	# Example - Find Unique values in specific CAN ID in 8bit-signed-2
	df_canid = df.loc[df['CanID']=='0A0']
	print (df_canid['8bit-signed-2'].unique())









