from django.shortcuts import render, get_object_or_404
from django.http import Http404, QueryDict
from .models import Person
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from .forms import UserForm
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
from django.core.exceptions import FieldDoesNotExist, FieldError
import json, base64, datetime

def stripdate(date):
    ''' removes microseconds and timezone from datetime object'''
    d = date.replace(microsecond=0, tzinfo=None)
    return d

def http_basic_auth(func):
    ''' creates a basic authentication decorator to login users'''
    @wraps(func)
    def _decorator(request, *args, **kwargs):
        from django.contrib.auth import authenticate, login
        if 'HTTP_AUTHORIZATION' in request.META:
            authmeth, auth = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
            if authmeth.lower() == 'basic':
                auth = base64.b64decode(auth).decode("utf-8")               
                username, password = auth.split(':')
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
                else:
                    objdiction = {"message":"invalid login details"}
                    objson = JsonResponse(objdiction, status=401)
                    return objson
        else:
            objdiction = {"message":"Authentication required"}
            objson = JsonResponse(objdiction, status=401)
            return objson

        return func(request, *args, **kwargs)
    return _decorator

@http_basic_auth
@csrf_exempt
def  view_user(request):
    if request.method == 'GET' and len(request.GET) > 0 and any(k not in ('sort_field','sort_order_mode','filter_field','filter_value') for k in request.GET):        
        objdiction = {"message":"invalid parameters"}
        objson = JsonResponse(objdiction, status=400)

    elif request.method == 'GET' and 'sort_field' in request.GET and 'sort_order_mode' in request.GET :
        sort_field = request.GET.get('sort_field')
        sort_order_mode = request.GET.get('sort_order_mode')
        if sort_order_mode == "desc":
            sort_field = f"-{sort_field}"
        elif sort_order_mode == "asc":
            pass
        else:
            objdiction = {"message":"invalid sort_order_mode value"}
            objson = JsonResponse(objdiction, status=400)
            return objson
        try:
            obj = Person.objects.all().order_by(sort_field)
        except FieldError :
            objdiction = {"message":"invalid sort_field value"}
            objson = JsonResponse(objdiction, status=400)
            return objson
        
        if obj.exists():
            objdiction = []
            for i in obj:
                objdiction.append({"id":i.id, "firstname":i.firstname, \
                    "lastname": i.lastname, "gender":i.gender, "date_of_birth":i.date_of_birth, \
                        "date_created":stripdate(i.date_created), "date_updated":stripdate(i.date_updated)}) 
                objson = JsonResponse(objdiction, safe=False)
        else:
            objdiction = {"message":"no user has been created yet"}
            objson = JsonResponse(objdiction, status=404)
    
    elif request.method == 'GET' and 'filter_field' in request.GET and 'filter_value' in request.GET:
        filter_field = request.GET.get('filter_field')
        filter_value = request.GET.get('filter_value')
        try:
            obj = Person.objects.filter(**{filter_field : filter_value})
        except FieldError:
            objdiction = {"message":"invalid filter_field value"}
            objson = JsonResponse(objdiction, status=400)
            return objson
        
        if obj.exists():
            objdiction = []
            for i in obj:
                objdiction.append({"id":i.id, "firstname":i.firstname, \
                    "lastname": i.lastname, "gender":i.gender, "date_of_birth":i.date_of_birth, \
                        "date_created":stripdate(i.date_created), "date_updated":stripdate(i.date_updated)}) 
                objson = JsonResponse(objdiction)
        else:
            objdiction = {"status":"0","message":"user with search criteria does not exist"}
            objson = JsonResponse(objdiction, status=404)
    
    elif request.method == 'GET' and all(k in request.GET for k in ('sort_field','sort_order_mode','filter_field','filter_value')):
        sort_field = request.GET.get('sort_field')
        sort_order_mode = request.GET.get('sort_order_mode')
        filter_field = request.GET.get('filter_field')
        filter_value = request.GET.get('filter_value')

        if sort_order_mode == "desc":
            sort_field = f"-{sort_field}"

        obj = Person.objects.filter(**{filter_field : filter_value}).order_by(sort_field)        
        if obj.exists():
            objdiction = []
            for i in obj:
                objdiction.append({"id":i.id, "firstname":i.firstname, \
                    "lastname": i.lastname, "gender":i.gender, "date_of_birth":i.date_of_birth, \
                        "date_created":stripdate(i.date_created), "date_updated":stripdate(i.date_updated)}) 
                objson = JsonResponse(objdiction)
        else:
            objdiction = {"status":"0","message":"user with search criteria does not exist"}
            objson = JsonResponse(objdiction, status=404)

    elif request.method == 'GET' and len(request.GET) > 0 and all(k not in request.GET for k in ('sort_field','sort_order_mode','filter_field','filter_value')):        
        objdiction = {"message":"invalid parameters"}
        objson = JsonResponse(objdiction, status=400)

    elif request.method == 'GET' and len(request.GET) == 0:        
        obj = Person.objects.all()
        if obj.exists():
            objdiction = []
            for i in obj:
                objdiction.append({"id":i.id, "firstname":i.firstname, \
                    "lastname": i.lastname, "gender":i.gender, "date_of_birth":i.date_of_birth, \
                        "date_created":stripdate(i.date_created), "date_updated":stripdate(i.date_updated)} )
                objson = JsonResponse(objdiction, safe=False)
        else:
            objdiction = {"message":"no user has been created yet"}
            objson = JsonResponse(objdiction)

    elif request.method == "POST":
        if request.content_type == "application/json":
            response = json.loads(request.body.decode('utf-8'))
            form = UserForm(response)
        else:
            form = UserForm(request.POST)
        if form.is_valid():
            fo = form.save()
            id = fo.id
            if id:
                obj = Person.objects.get(id=id)
                objdiction = {"id":obj.id, "firstname":obj.firstname, "lastname": obj.lastname, \
                    "gender":obj.gender, "date_of_birth":obj.date_of_birth, "date_created":stripdate(obj.date_created), \
                        "date_updated":stripdate(obj.date_updated)} 
                objson = JsonResponse(objdiction, status=201)
            else:
                objdiction = {"message":"an error occurred while submitting"}
                objson = JsonResponse(objdiction)
        else:
            objdiction = {"message":"bad request"}
            objson = JsonResponse(objdiction, status=400)

    else:
        objdiction = {"status":"0","message":"method not allowed"}
        objson = JsonResponse(objdiction, status=405)
    
    return objson

@http_basic_auth
@csrf_exempt
def user_detail_view(request, id):
    if id.isdigit() == False:
        objdiction = {"message":"invalid parameters"}
        objson = JsonResponse(objdiction, status=400)
        return objson

    elif request.method == "GET":
        try:
            obj = get_object_or_404(Person, id=id)
        except Http404 :
            objdiction = {"message":"user not found"}
            objson = JsonResponse(objdiction, status=404)
            return objson
        
        objdiction = {"id":obj.id,"firstname":obj.firstname, "lastname": obj.lastname, \
            "gender":obj.gender, "date_of_birth":obj.date_of_birth, \
                "date_created":stripdate(obj.date_created), \
                    "date_updated":stripdate(obj.date_updated)} 
        objson = JsonResponse(objdiction)

    elif request.method == "PUT":
        
            try:
                response = json.loads(request.body.decode('utf-8'))
            except Exception:
                objdiction = {"message":"invalid content type"}
                objson = JsonResponse(objdiction, status=400)
                return objson

            try:
                obj = get_object_or_404(Person, id=id)
            except Http404:
                objdiction = {"message":"user not found"}
                objson = JsonResponse(objdiction, status=404)
                return objson

            try:
                Person.objects.filter(id=id).update(**response, date_updated = datetime.datetime.now())
            except FieldDoesNotExist as e:
                message = e.__str__()
                message = message.replace('Person', 'User')
                objdiction = {"message":message}
                objson = JsonResponse(objdiction, status=400)
                return objson

            obj = get_object_or_404(Person, id=id)
            objdiction = {"id":obj.id, "firstname":obj.firstname, \
                "lastname": obj.lastname, "gender":obj.gender, "date_of_birth":obj.date_of_birth, \
                    "date_created":stripdate(obj.date_created), "date_updated":stripdate(obj.date_updated)}
            objson = JsonResponse(objdiction, status=201)
            
        # else:
        #     response = request.__dict__
            
        #     # print(request.body)     
        #     # print(response)
        #     print(dir(request))    
        #     print(request._set_post('put'))   
        #     try:
        #         obj = get_object_or_404(Person, id=id)
        #     except Http404:
        #         objdiction = {"message":"user not found"}
        #         objson = JsonResponse(objdiction, status=404)
        #         return objson

        #     form = UserForm(response, instance=obj)

        #     if form.is_valid():
        #         form.save()
        #         obj = get_object_or_404(Person, id=id)
        #         objdiction = {"id":obj.id, "firstname":obj.firstname, \
        #             "lastname": obj.lastname, "gender":obj.gender, "date_of_birth":obj.date_of_birth, \
        #                 "date_created":stripdate(obj.date_created), "date_updated":stripdate(obj.date_updated)}
        #         objson = JsonResponse(objdiction, status=201)            
        #     else:
        #         objdiction = {"message":"update failed"}
        #         objson = JsonResponse(objdiction, status=400)

    elif request.method == 'DELETE':
        Person.objects.filter(id=id).delete()
        try:
            obj = get_object_or_404(Person, id=id)
        except Http404:
            data = ''
            objson =JsonResponse(data, status=204, safe=False)
            return objson
        
        objson = {"message":"delete failed"}
        objson = JsonResponse(objson, status=404)
    else :
        objson = {"message":"method not allowed"}
        objson = JsonResponse(objson, status=405)
    return objson
    
    
    
