from django.shortcuts import render

def index(request):
    return render(request,'index.html')
    #return HttpResponse("HELLO FROM PRAKHAR..!!")

def about(request):
    return render(request,'about.html')

