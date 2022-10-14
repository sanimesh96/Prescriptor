from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Prescription
import json


import boto3
from .utils import convert
from decouple import config
ACCESS_KEY_ID = config('ACCESS_KEY_ID')
ACCESS_SECRET_KEY = config('ACCESS_SECRET_KEY')
s3 = boto3.client('s3',aws_access_key_id = ACCESS_KEY_ID,aws_secret_access_key = ACCESS_SECRET_KEY)
s3 = boto3.client('s3',aws_access_key_id=ACCESS_KEY_ID,aws_secret_access_key= ACCESS_SECRET_KEY,)
textract = boto3.client('textract',aws_access_key_id=ACCESS_KEY_ID,aws_secret_access_key = ACCESS_SECRET_KEY, region_name='us-west-2')
BUCKET_NAME = config('BUCKET_NAME')

# Create your views here.
def homepage(request):
    if request.user.is_authenticated:
        return render(request, 'pages/homepage.html')
    else:
        return redirect('login')


def uploadPrescription(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'pages/uploadPrescription.html')
        elif request.method == 'POST':
            image = request.FILES['prescription_image']
            obj = Prescription(uploaded_by=request.user, image=image)
            obj.save()
            predictPrescription(request, obj.id)
            return redirect('singleViewPres', prescription_id=obj.id)
    else:
        return redirect('login')

def viewPrescription(request):

    if request.user.is_authenticated:
        context = {
            'prescriptions' : Prescription.objects.all(),
        }
        return render(request, 'pages/viewPrescription.html', context=context)
    else:
        return redirect('login')

def Prescriptions(request):

    if request.user.is_authenticated:
        return render(request, 'pages/prescriptions.html')
    else:
        return redirect('login')

def Dashboard(request):

    if request.user.is_authenticated:
        return render(request, 'pages/dashboard.html')
    else:
        return redirect('login')


def singleView(request, prescription_id):
    if request.user.is_authenticated:
        if Prescription.objects.get(id=prescription_id).medication:
            p=True
        else:
          p=False
        context = {
            'prescription': Prescription.objects.get(id=prescription_id),
            'predicted':p,
        }
        return render(request, 'pages/singleView.html', context=context)
    else:
        return redirect('login')

def annotatePrescription(request, prescription_id):
    if request.user.is_authenticated:
        context = {
            'prescription': Prescription.objects.get(id=prescription_id),
        }
        return render(request, 'annotator/via.html', context=context)
    else:
        return redirect("login")

def medication(result):
    res = ''
    for word in result:
        res += word[1]+ ' '
    print(res)
    comprehendmedical = boto3.client('comprehendmedical', aws_access_key_id=ACCESS_KEY_ID,
                        aws_secret_access_key = ACCESS_SECRET_KEY, region_name='us-west-2')
    result = comprehendmedical.detect_entities(Text= res)
    entities = result['Entities']
    for entity in entities:
        print(entity)

def predictPrescription(request, prescription_id):
    if request.user.is_authenticated:
        image_data = Prescription.objects.get(id=prescription_id).image
        img = str(image_data)
        if img:
            response = s3.upload_file( 
                Bucket = BUCKET_NAME,
                Filename=img,
                Key = img
            )
        objs = s3.list_objects_v2(Bucket=BUCKET_NAME)['Contents']
        objs.sort(key=lambda e: e['LastModified'], reverse=True)
        first_item = list(objs[0].items())[0]
        documentName = str(first_item[1])
        # Call Amazon Textract
        with open(documentName, "rb") as document:
            response = textract.analyze_document(
                Document={
                    'Bytes': document.read(),
                },
                FeatureTypes=["FORMS"])
        preds = convert(response,img,img.split('/')[-1])
        prescription = Prescription.objects.get(id=prescription_id)
        prescription.annotation= preds
        prescription.save()
    else:
        return redirect("login")

def addAnnotation(request, prescription_id):
    prescription = Prescription.objects.get(id=prescription_id)
    print(request.POST)
    annotations = request.POST['annotation']
    annotations = json.loads(annotations)
    prescription.annotation = annotations
    prescription.save()
    return JsonResponse({"abc":"dad"})