from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import IntegrityError
from .models import User,Uploads,Send_Data
from django.views.decorators.csrf import csrf_exempt
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import aes
from django.http import FileResponse, JsonResponse, HttpResponse
import json
import threading
import time
from pathlib import Path


def home(request):
    return render(request, "index.html")  

def login(request):
    return render(request, "login.html")  

def signup(request):
    return render(request, "signup.html") 
def dash(request):
    return render(request, "dash.html") 

@csrf_exempt
def signup_view(request):
    if request.method == "POST":
        name = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confpassw")

        print(f"Received signup data: Username={name}, Email={email}, Password={password}, Confirm Password={confirm_password}")

        if password != confirm_password:
            return JsonResponse({"error": "Passwords do not match"}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already registered"}, status=400)

        try:
            user = User(name=name, email=email, password=password) 
            user.save()


            return JsonResponse({"success": "User registered successfully"})
        except IntegrityError:
            return JsonResponse({"error": "User already exists"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        print(f"Received login data: Email={email}, Password={password}")

        try:
            user = User.objects.get(email=email, password=password)  
        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid email or password"}, status=400)

        request.session['user_id'] = user.id
        request.session['user_email'] = user.email

        return JsonResponse({"success": "Login successful"})

    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def logout(request):
    request.session.flush()  
    return redirect('/login')

@csrf_exempt
def get_user_files(request):

    if request.method == "GET":
        user_email = request.session.get("user_email")

        if not user_email:
            return JsonResponse({"success": False, "error": "User not authenticated."}, status=401)

        try:
            files = Uploads.objects.filter(name=user_email).values("name", "filename")
            
            files_data = list(files)

            return JsonResponse({
                "success": True,
                "files": files_data
            })
        
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=500)

    return JsonResponse({
        "success": False,
        "error": "Invalid request method."
    }, status=405)  

@csrf_exempt
def upload_image(request):
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]
        key = request.POST.get("key")  
        static_dir = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else os.path.join(settings.BASE_DIR, "static")
        upload_dir = os.path.join(static_dir, "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, image.name)
        with open(file_path, "wb") as f:
            for chunk in image.chunks():
                f.write(chunk)
        aes.encrypt_file(file_path,key=str(key))
        Uploads(name=request.session.get("user_email"),filename=file_path).save()
        

        return JsonResponse({
            "success": True,
            "file_path": f"/static/uploads/{image.name}",
            "key": key
        })

    return JsonResponse({"success": False, "error": "No image uploaded."})


def remove(file_path):
    time.sleep(5)
    os.remove(file_path)


def download_url(request):
    
    file_path=request.session.get("download")
    response = FileResponse(open(file_path, 'rb'))
    filename=os.path.basename(file_path)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    threading.Thread(target=remove,args=(file_path,)).start()
    try:
        s=Send_Data.objects.get(receiver=request.session.get('user_email'),done="1")
        s.delete()
    except:
        pass
    return response

@csrf_exempt
def pass_data(request):
    try:
        user_email = request.session.get("user_email")
        if not user_email:
            return JsonResponse({"error": "User not logged in"}, status=401)
        s = Send_Data.objects.filter(receiver=user_email)
        data = list(s.values())
        return JsonResponse({"data": data}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def request_key(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        password = data.get('password')
        filename= data.get("filename")
        normal=filename
        if not  str(filename).endswith(".enc"):
            filename=filename+".enc"
        receiver= data.get("receiver")
        file_path=aes.decrypt_file(filename,key=str(password))
        s = Send_Data.objects.filter(receiver=receiver, filename=normal).first()

        s.filename=file_path
        s.request="0"
        s.done="1"
        s.save()

        return JsonResponse({'message': 'Key requested successfully'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid password'}, status=400)

@csrf_exempt
def get_my_send(request):
    try:
        s=Send_Data.objects.get(receiver=request.session.get("user_email"),done="1")

        request.session["download"]=s.filename

        return JsonResponse({"status":"ok"})
    except:
        return JsonResponse({'status':'nope'})

@csrf_exempt
def check_for(request):
    s = Send_Data.objects.filter(request="1",name=request.session.get("user_email"))
    
    data = [
        {
            "filename": obj.filename, 
            "receiver": obj.receiver
        } for obj in s
    ]

    return JsonResponse({"data": data}, status=200)


@csrf_exempt
def get_file(request):
    if request.method == "POST":
        data = json.loads(request.body)
        filename = data.get("filename")
        email = data.get("email")
        print(email)
        static_dir = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else os.path.join(settings.BASE_DIR, "static")
        upload_dir = os.path.join(static_dir, "uploads")
        upload_dir = os.path.join(upload_dir, filename)
        upload_dir = os.path.normpath(upload_dir)  
        print(upload_dir)
        s=Send_Data.objects.get(name=email,filename=upload_dir)
        s.request="1"
        s.save()
        return JsonResponse({"status":"ok"})



@csrf_exempt
def send_data(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            filename = data.get("filename")+".enc"
            email = data.get("key")
            static_dir = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else os.path.join(settings.BASE_DIR, "static")
            upload_dir = os.path.join(static_dir, "uploads")
            upload_dir = os.path.join(upload_dir, filename)


            path = Path(upload_dir)

            if path.exists():
                Send_Data(name=request.session["user_email"],filename = upload_dir ,receiver=email).save()
                return JsonResponse({"status": "ok"},status=200)
            else:
                return JsonResponse({"status": "Doesnt exists"},status=400)

        except Exception as e:
            print(str(e))
            return JsonResponse({"status": "ok"},status=400)
            

@csrf_exempt
def download_image(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            filename = data.get("filename")+".enc"
            key = data.get("key") 
            static_dir = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else os.path.join(settings.BASE_DIR, "static")
            upload_dir = os.path.join(static_dir, "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, filename)
            file_path=aes.decrypt_file(file_path,key=str(key))
            if file_path==None:
                return JsonResponse({"status": "invalid key"},status=400)

            request.session['download']=file_path
            return JsonResponse({"status": "ok"})



        except Exception as e:
            return JsonResponse({"status": "ok"},status=400)
            