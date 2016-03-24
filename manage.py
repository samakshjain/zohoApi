from config import Config
from flask import Flask, request, jsonify
import urlparse
import urllib2
import os
import requests

app = Flask(__name__)
app.config.from_object(Config)

path = os.getenv('ZC_CONFIG_PATH')

if path:
    app.config.from_envvar('ZC_CONFIG_PATH')


@app.route("/upload", methods=["POST"])
def upload_pdf():

    auth_token = app.config.get("AUTH_TOKEN")
    # Get upload Url from body
    upload_url = request.json["pdf_url"]

    if not auth_token and "auth_token" in request.json:
        auth_token = request.json["auth_token"]

    if not auth_token:
        response = jsonify({"error": "missing auth token"})
        response.status_code = 400
        return response

    # Make the URL parse-able
    pos_of_fslash = upload_url.rfind('/')
    parseable_url = upload_url[:pos_of_fslash + 1] + '?' + upload_url[pos_of_fslash + 1:]
    # Parse the URL to get the query params
    par = urlparse.parse_qs(urlparse.urlparse(parseable_url).query)

    # form-data for make_record request
    record_payload = {
        'scope': 'creatorapi',
        'authtoken': auth_token,
        'confrecid': par['confrecid'][0]
    }

    # make_record request
    make_record = requests.post(
        'https://creator.zoho.com/api/ali.pichvai/json/karbone/form/Confirmation_Files/record/add/',
        data=record_payload)
    record_id = make_record.json()['formname'][1]['operation'][1]['values']['ID']

    file_name = par['zc_FileName'][0] + '.pdf'

    # download_file function which downloads pdf located at download_url
    def download_file(download_url):
        res = urllib2.urlopen(download_url)
        f = open(file_name, 'wb')
        f.write(res.read())
        f.close()
        print("Completed")

    # download the pdf
    download_file(upload_url)

    # form-data for upload_pdf
    upload_payload = {
        'filename': file_name,
        'applinkname': 'karbone',
        'formname': 'Confirmation_Files',
        'fieldname': 'Upload_Confirmation',
        'recordId': record_id
    }

    f = open(file_name, 'rb')
    files = {'file': f}

    requests.post(
        'https://creator.zoho.com/api/xml/fileupload/scope=creatorapi&authtoken=' + auth_token,
        data=upload_payload, files=files)

    f.close()
    response = jsonify({})

    os.remove(file_name)
    return response


if __name__ == "__main__":
    app.run(
        host=app.config.get("HOST"),
        port=app.config.get("PORT")
    )
