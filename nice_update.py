#used by the updater, to check which files are changed and thus creating a pratial update
import hashlib
#used to show the progress of the downloader
import sys
#used to open the bat file
import subprocess

#remote location for the update
remote_location = "http://rikels.info/share/nicevoting/"
#the filename with the remote hashes
remote_hashfile = "hashes"
exclude_list = ["votes.txt","config.txt"]

def download_file(url,headers=None,local_filename=None,path=None):
	#paths have to end with a slash, else the path to a file will be: c:/folderFile.txt instead of c:/folder/file.txt
	if not path.endswith("/"):
		path = path + "/"
	# stream=True is needed if we want to be able to save the file
	r = requests.get(url, stream=True, headers=headers)
	if local_filename == None:
		try:
			local_filename = r.headers["content-disposition"].split("filename=")[1].strip("\"")
		except:
			local_filename = url.split("/")[-1]
	print(local_filename)
	total_length = r.headers.get('content-length')
	with open(path+local_filename, 'wb') as local_file:
		if total_length is None:
				for chunk in r.iter_content(chunk_size=1024): 
					if chunk: # filter out keep-alive new chunks
						local_file.write(chunk)
						local_file.flush()
		else:
			dl = 0
			total_length = int(total_length)
			for chunk in r.iter_content(chunk_size=1024): 
				dl += len(chunk)
				if chunk: # filter out keep-alive new chunks
						local_file.write(chunk)
						local_file.flush()
				done = int(50 * dl / total_length)
				#showing the progress via a ASCII progress bar
				sys.stdout.write("\r[{done}{todo}]	{downloaded}/{todownload}".format(done=('='*done),todo=(' '*(50-done)),downloaded=dl,todownload=total_length))
				sys.stdout.flush()
	return (local_filename)

def update():
	remote_version = float(requests.get("{url}/version".format(url=remote_location)).content)
	#getting the local version
	try:
		version_file_path = os.path.dirname(os.path.abspath("__file__"))+"\\version"
		if os.path.exists(version_file_path):
			with open(version_file_path,"r") as version_file:
				local_version = version_file.read()
		else:
			print("Version file not found, setting it to version 0.0 ;)")
			local_version = "0.0"
	except:
		pass
	if remote_version > local_version:
	#getting the local files hash values
		#creating a dictionary to store the MD5 hashes in
		md5s = {}
		#calculating the hash value of all the files
		files = os.listdir(".")
		for filee in files:
			if filee not in exclude_list:
				#calculating the MD5 of files and storing them in the list
				md5s[filee] = hashlib.md5(open("{filename}".format(filename=filee).replace("\\","/"),"rb").read()).hexdigest()



	#getting the remote file with MD5 hashes and convert it to a list
		remote_hashes = requests.get("{remote_location}{remote_hashes}".format(remote_location=remote_location,remote_hashfile=remote_hashfile)).content
		remote_hashes = remote_hashes.split("\n")
		compare_hashes = {}
		for pair in remote_hashes[:-1]:
			pair = pair.split("=")
			compare_hashes[pair[0].strip()] = pair[1].strip()


		grab = []
		#comparing the remote with the local hashes, we use the remote list in the for loop, so we get new files too,
		#as new files aren't stored in the local md5s list, it will throw a KeryError, which we catch and add to the grab list
		for md5 in compare_hashes:
			try:
				if md5s[md5] != compare_hashes[md5]:
					grab += [md5]
			except KeyError:
				grab += [md5]

	#downloading all updated and new files
		#first creating a temporary folder to download everything to
		os.mkdir("update")
		#downloading all necessary files to the temporary folder
		for get in grab:
			download_store("{remote_location}/{file}".format(remote_location=remote_location,file=get),local_path="./update")
		#calling the bat files to move everything and overwrite previous versions
		subprocess.Popen("update.bat")