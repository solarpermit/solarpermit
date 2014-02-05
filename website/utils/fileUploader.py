import time
import os
import string
import pprint
class qqFileUploader(object):

    def __init__(self, allowedExtensions = [], sizeLimit = 1024):

        self.allowedExtensions = allowedExtensions
        self.sizeLimit = sizeLimit


    def handleUpload(self, djangoRequest, uploadDirectory):

        #read file info from stream
        uploaded = djangoRequest.read
        #get file size
        fileSize = int(uploaded.im_self.META["CONTENT_LENGTH"])
        #get file name
        #fileName = uploaded.im_self.META["HTTP_X_FILE_NAME"]        
        try:
            asize = djangoRequest.FILES['qqfile'].size
            isHtx = False
        except:
            isHtx = True
        fileName = djangoRequest.REQUEST.get('qqfile')
        if len(fileName) > 65:
            fileName = fileName[0:20]+fileName[(len(fileName) -30):len(fileName)]
        #if fileName == None:
        #    fileName = djangoRequest.FILES['qqfile'].name
        #    isHtx = False
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        file_store_name = str(time.time())+'_'+''.join(c for c in fileName if c in valid_chars)
        #print len(file_store_name)
        #check first for allowed file extensions
        if self._getExtensionFromFileName(fileName).lower() in self.allowedExtensions:
            #check file size
            if fileSize > self.sizeLimit:
                return {"success": False, "filename": fileName, "json": '{"error": "File is too large."}'}
            file = open(uploadDirectory + file_store_name,"wb")
 
            #file_store_name = uploadDirectory+ "_" + file_store_name
            if isHtx:
                #upload file
                #write file
                file.write(djangoRequest.read(fileSize))
                file.close()
            else:
                f = djangoRequest.FILES['qqfile']
                for chunk in f.chunks():
                    file.write(chunk)
                file.close()
            return {"success": True, "filename": fileName,  "store_name":file_store_name,  "json": '{"success": true,"store_name":"'+file_store_name+'", "fileName":"'+fileName+'"}'}


                

        else:
            return {"success": False, "filename": fileName, "json": '{"error": "File has an invalid extension."}'}


    def _getExtensionFromFileName(self,fileName):
        
        filename, extension = os.path.splitext(fileName)
        return extension
    def _getFileNameNoExtension(self,fileName):
        filename, extension = os.path.splitext(fileName)
        return filename        
