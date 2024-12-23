import os
import boto3
from dotenv import load_dotenv
from urllib.parse import unquote
from flask import Flask, request, render_template, redirect, url_for, flash

app = Flask(__name__)
app.secret_key="sampleproject"

load_dotenv()

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
)

@app.route('/')
def index():
    buckets = s3_client.list_buckets().get('Buckets')
    return render_template('index.html', buckets=buckets)

@app.route('/bucket/<bucket_name>')
def bucket_content(bucket_name):
    objects = s3_client.list_objects_v2(Bucket=bucket_name).get('Contents', [])
    buckets = s3_client.list_buckets().get('Buckets')
    return render_template('index.html', bucket_name=bucket_name, objects=objects, buckets=buckets)

@app.route('/create_bucket', methods=['POST'])
def create_bucket():
    bucket_name = request.form['bucket_name']
    s3_client.create_bucket(Bucket=bucket_name)
    return redirect(url_for('index'))

@app.route('/delete_bucket/<bucket_name>', methods=['POST'])
def delete_bucket(bucket_name):
    s3_client.delete_bucket(Bucket=bucket_name)
    return redirect(url_for('index'))

@app.route('/upload_file/<bucket_name>', methods=['POST'])
def upload_file(bucket_name):
    file = request.files['file']
    if file:
        s3_client.upload_fileobj(file, bucket_name, file.filename)
    return redirect(url_for('bucket_content', bucket_name=bucket_name))

@app.route('/delete_file/<bucket_name>/<file_key>', methods=['POST'])
def delete_file(bucket_name, file_key):
    s3_client.delete_object(Bucket=bucket_name, Key=file_key)
    return redirect(url_for('bucket_content', bucket_name=bucket_name))

@app.route('/create_folder/<bucket_name>', methods=['POST'])
def create_folder(bucket_name):
    folder_name = request.form['folder_name']
    if not folder_name.endswith('/'):
        folder_name += '/'
    s3_client.put_object(Bucket=bucket_name, Key=folder_name)
    return redirect(url_for('bucket_content', bucket_name=bucket_name))

@app.route('/delete_folder/<bucket_name>/<path:folder_key>', methods=['POST'])
def delete_folder(bucket_name, folder_key):
    folder_key = unquote(folder_key)
    s3_client.delete_object(Bucket=bucket_name, Key=folder_key)
    return redirect(url_for('bucket_content', bucket_name=bucket_name))

@app.route('/copy_file/<source_bucket>/<source_key>/<target_bucket>', methods=['POST'])
def copy_file(source_bucket, source_key, target_bucket):
    target_bucket = request.form['target_bucket']
    copy_source = {'Bucket': source_bucket, 'Key': source_key}
    s3_client.copy(copy_source, target_bucket, source_key)
    return redirect(url_for('bucket_content', bucket_name=source_bucket))

@app.route('/move_file/<source_bucket>/<source_key>/<target_bucket>', methods=['POST'])
def move_file(source_bucket, source_key, target_bucket):
    target_bucket = request.form['target_bucket']
    copy_source = {'Bucket': source_bucket, 'Key': source_key}
    s3_client.copy(copy_source, target_bucket, source_key)
    s3_client.delete_object(Bucket=source_bucket, Key=source_key)
    return redirect(url_for('bucket_content', bucket_name=source_bucket))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
