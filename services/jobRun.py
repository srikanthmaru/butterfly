import requests
import json
import os
import sys

def getJobConfig():
    try:
        url = 'http://127.0.0.1:5000/jobs/1'
        getData = requests.get(url)
        if getData.status_code != 200:
            print('Status:', getData.status_code, 'Problem with the request. Exiting.')
            exit()
        getJsonData = getData.json()
        #scriptValue = getJsonData[0]['name']
    except requests.exceptions.RequestException as e:
        print e
    return getJsonData

def createScript(scriptValue,scriptAbsPath):
    try:
        with open(scriptAbsPath, "w") as scriptPath:
            scriptPath.write("{0}".format(scriptValue))
        os.chmod(scriptAbsPath, 0777)   
    except:
        e = sys.exc_info()[0]
        print "failed while creating script: " + str(e)
        raise
    return "Done"    

if __name__ == "__main__":

    getJsonData = getJobConfig()
    
    scriptValue = getJsonData[0]['name']
    scriptAbsPath = 'Output.hql'
    createScript(scriptValue,scriptAbsPath)

