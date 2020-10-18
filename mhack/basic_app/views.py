from django.shortcuts import render
from basic_app.forms import UserForm
from basic_app.models import UserProfileInfo
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from . import subscribe
from django.core.urlresolvers import reverse


from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages


def index(request):
    return render(request,'basic_app/index.html')

def show(request):

    listo = subscribe.extra(str(request.user))
    print(listo)
    return render(request,'basic_app/list.html',{'listo':listo})

def remove(request):
    if request.method == 'POST':
        searched = request.POST.get('sub')
        subscribe.unsubChannel(str(request.user),searched)
    return HttpResponseRedirect(reverse('basic_app:show'))


def add(request):

    if request.method == 'POST':
        searched = request.POST.get('add')
        subscribe.subChannel(str(request.user),searched)
    return HttpResponseRedirect(reverse('basic_app:show'))


def process(request):
    p=''
    if request.method == 'POST':
        searched = request.POST.get('inputurl')
        #do processing over
        p,q,r,s=subscribe.summary(searched)
        print(p)
        print(q)
        print(r)
        summ=""
        for i in s:
            summ+=i
        if searched.isspace() or not searched:
            searched = "Please go back and enter something"
    return render(request,'basic_app/summary.html',{'p':p,'r':r,'summ':summ})


@login_required
def fire(request,id):
    print("hello")
    users = User.objects.all()
    #return HttpResponse(id)
    #form = Add()
    src = []
    head = []
    desc = []
    image = []
    #print(request.path)
    ct=0
    count=[]
    for i in range(len(users)):
        print(users[i],id)
        if(str(users[i]) == id):
            li=subscribe.generate_feed(id)
            print(li)
            for i in li.keys():
                print(i)
                for el in li[i]:
                    head.append(el[1])
                    image.append(el[3])
                    ct+=1
                    count.append(ct)
                    #f=len(el[1])
                    #s="-"*(200-f)
                    #el[1]+=s
                    #len(el[1])
                    summ=""
                    for ele in el[4]:
                        summ+=ele
                    src.append([i,el[0],el[1],el[3],summ])
                    #desc.append(summ)
            print(len(src))

            print(count)
            print(head)
            print(image)
            print(desc)

            return render(request,'basic_app/user_page.html',{'src':src})
        #return render(request,'basic_app/user_page.html',{'src':src})
    return render(request,'basic_app/user_page.html',{'src':src})

def featured(request):
    source=''
    src = []
    head = []
    desc = []
    image = []
    ct=0
    count=[]
    print(request.user)
    li=subscribe.show_saved('test2')
    print(li)
    for el in li:
        head.append(el[1])
        image.append(el[3])
        ct+=1
        count.append(ct)
        summ=""
        for ele in el[4]:
            summ+=ele
        src.append([source,el[0],el[1],el[3],summ])
    print(len(src))
    print(count)
    print(head)
    print(image)
    print(desc)
    #return render(request,'basic_app/bookmarks.html',{'src':src})

    return render(request,'basic_app/featured.html',{'src':src})
        #return render(request,'basic_app/user_page.html',{'src':src}

def index2(request):
    return render(request,'basic_app/index2.html',{})

def browse(request):
    if request.method == 'POST':
        source=request.POST.get('inputurl2')
    src = []
    head = []
    desc = []
    image = []
    ct=0
    count=[]
    print(source)
    li=subscribe.browser(source)
    for el in li:
        head.append(el[1])
        image.append(el[3])
        ct+=1
        count.append(ct)
        summ=""
        for ele in el[4]:
            summ+=ele
        src.append([source,el[0],el[1],el[3],summ])
    print(len(src))
    print(count)
    print(head)
    print(image)
    print(desc)
    return render(request,'basic_app/browse.html',{'src':src})
    #return render(request,'basic_app/user_page.html',{'src':src})
    #return render(request,'basic_app/user_page.html',{'src':src})

def bookadd(request):
    print("hello")
    if request.method == 'POST':
        searched = request.POST.get('add')
        subscribe.pinChannel(str(request.user),searched)
        #print(searched)
        #print(searched)
    return HttpResponse("done")
    #return HttpResponseRedirect(reverse('basic_app:show'))

def bookremove(request):
    print("hello3")
    if request.method == 'POST':
        searched = request.POST.get('add')
        print(searched)
        subscribe.unpinChannel(str(request.user),searched)
        #print(searched)
        #print(searched)
    return HttpResponseRedirect(reverse('basic_app:bookmarks'))

def bookmarks(request,id):
    source=''
    src = []
    head = []
    desc = []
    image = []
    ct=0
    count=[]
    print(request.user)
    li=subscribe.show_saved(str(request.user))
    print(li)
    for el in li:
        head.append(el[1])
        image.append(el[3])
        ct+=1
        count.append(ct)
        summ=""
        for ele in el[4]:
            summ+=ele
        src.append([source,el[0],el[1],el[3],summ])
    print(len(src))
    print(count)
    print(head)
    print(image)
    print(desc)
    return render(request,'basic_app/bookmarks.html',{'src':src})


def reg(request):
    return HttpResponse("hello")

@login_required
def user_logout(request):
    # Log out the user.
    logout(request)
    # Return to homepage.
    return HttpResponseRedirect(reverse('index'))

def register(request):

    registered = False

    if request.method == 'POST':


        user_form = UserForm(data=request.POST)

        if user_form.is_valid():

            user = user_form.save()

            user.set_password(user.password)

            user.save()



            # Registration Successful
            registered = True
            # u = reverse('basic_app:user_login')
            # return HttpResponseRedirect(u)
            hashcode = 0
            name = user.username
            size = len(name)
            temp = size
            for i in name:
                hashcode += ord(i)*(10**temp)
                temp-=1
            #print(hashcode)
            subscribe.addUser(str(hashcode),name)

        else:
            # One of the forms was invalid if this else gets called.
            print(user_form.errors)

    else:
        # Was not an HTTP post so we just render the forms as blank.
        user_form = UserForm()

    return render(request,'basic_app/registration.html',
                          {'user_form':user_form,
                           'registered':registered})

def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')



        user = authenticate(username=username, password=password)


        if user:

            if user.is_active:

                login(request,user)
                print(user)
                u = reverse('basic_app:fire',kwargs={'id':user})
                return HttpResponseRedirect(u)
            else:
                return HttpResponse("Your account is not active.")
        else:
            return HttpResponse("Invalid login details supplied.")

    else:
        return render(request, 'basic_app/login.html', {})
