import boto3
from botocore.client import Config
import io
import zipfile
import mimetypes


def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:436348450747:deployLateRoundPick-Topic')
    try:
        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
        portfolio_bucket = s3.Bucket('portfolio.lateroundpick.io')
        build_bucket = s3.Bucket('build.lateroundpick.io')
    
        build_bucket.download_file('build.zip', '/tmp/build.zip')
    
        portfolio_zip = io.BytesIO()
    
        build_bucket.download_fileobj('build.zip', portfolio_zip)
    
        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
        topic.publish(Subject="LateRoundPick code build deploy", Message="Late Round Pick has been deployed successfully")
        print('Late Round Pick Deplot function completed with no errors')
    except:
        topic.publish(Subject="LateRoundPick code build deploy failed", Message="Late Round Pick deploy has failed")
        raise