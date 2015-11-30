#this script creates all the files that have to do with versioning automatically
#you don't need it, this is just for myself to prepare an update.
#Shared it with you so you can improve, or use this method for your own program :)

#used by the updater, to check which files are changed and thus creating a "pratial" update
import hashlib
#using time to create the version
import time
#used to list all the files in the current directory
import os

#creating a dictionary to store the MD5 hashes in
md5s = {}
exclude_list = ["votes.txt","config.txt"]

files = os.listdir("build/exe.win-amd64-3.3/")
#calculating the hash value of all the files
for filee in files:
	if filee not in exclude_list:
		#calculating the MD5 of files and storing them in the list
		md5s[filee] = hashlib.md5(open("build/exe.win-amd64-3.3/{filename}".format(filename=filee).replace("\\","/"),"rb").read()).hexdigest()

#creating the format for the hashfile (filename = hashvalue)
formatt = ""
for md5 in md5s:
	formatt += "{filename} = {md5}\n".format(filename=md5,md5=md5s[md5])

#writing the MD5s to a file, so the remote client can compare the hashes to the local files
with open("build/exe.win-amd64-3.3/hashes","w") as hashfile:
	hashfile.write(formatt)

#Tought that this version format would be quite nice, you'll know when the version they use was made.
#this makes it easy to tell if a version they use is old, or quite new.
#It is also easy to compare via scripting/programming language, as it is just a float.
version_number = time.strftime("%Y%m%d.%H%M%S", time.gmtime())

with open("build/exe.win-amd64-3.3/version","w") as version_file:
	version_file.write(version_number)

print("successfully ran Update prepare!")