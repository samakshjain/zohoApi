from flask import Flask, request, jsonify
import urlparse
import urllib2
import requests

app = Flask(__name__)
app.debug = True

@app.route("/upload", methods=["POST"])
def uploadPdf():
    # Get upload Url from body
    uploadURL = request.json["uploadURL"]
    # Make the URL parse-able
    pos_of_fslash = uploadURL.rfind('/')
    parseableURL = uploadURL[:pos_of_fslash+1] + '?' + uploadURL[pos_of_fslash+1:]
    # Parse the URL to get the query params
    par = urlparse.parse_qs(urlparse.urlparse(parseableURL).query)

    # form-data for make_record request
    record_payload = {
        'scope'     : 'creatorapi',
        'authtoken' : '4e4cac8f91b9eb6098b51666619b4d96',
        'confrecid' : par['confrecid'][0]
    }

    # make_record request
    make_record = requests.post('https://creator.zoho.com/api/ali.pichvai/json/karbone/form/Confirmation_Files/record/add/', data=record_payload)
    record_Id = make_record.json()['formname'][1]['operation'][1]['values']['ID']
    print record_Id

    # download_file function which downloads pdf located at download_url
    def download_file(download_url):
        response = urllib2.urlopen(download_url)
        file = open("document.pdf", 'wb')
        file.write(response.read())
        file.close()
        print("Completed")

    # download the pdf
    download_file(uploadURL)

    # form-data for upload_pdf
    upload_payload = {
        'filename'      : par['zc_FileName'][0]+'.pdf',
        'applinkname'   : 'karbone',
        'formname'      : 'Confirmation_Files',
        'fieldname'     : 'Upload_Confirmation', 
        'recordId'      : record_Id 
    }

    files = {'file': open('document.pdf', 'rb')}

    upload_pdf = requests.post('https://creator.zoho.com/api/xml/fileupload/scope=creatorapi&authtoken=4e4cac8f91b9eb6098b51666619b4d96', 
        data=upload_payload, files=files)

    response = jsonify({
        "uploadURL" : parseableURL
        })
    
    return response

if __name__ == "__main__":
    app.run()