from django.shortcuts import render,redirect
from .models import Cweather,User
from .forms import UserForm,RegisterForm
from django.forms.models import model_to_dict
from django.db.models import Q
# Create your views here.
import json

def index(request):
    context = {
        'name':'songzi'
    }
    return render(request,'index.html',context=context)

# 登录函数
def login(request):
    if request.session.get('is_login', None):
        return redirect('/#/')

    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user =User.objects.get(name=username)
                if user.password == password:
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('myapp:index')
                else:
                    message = "密码不正确！"
            except:
                message = "用户不存在！"
                return render(request, 'login.html', locals())

    login_form = UserForm()
    return render(request, 'login.html', locals())

# 注册函数
def register(request):

    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/index/")
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'register.html', locals())
            else:
                same_name_user = User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'register.html', locals())
                same_email_user = User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'register.html', locals())

                # 当一切都OK的情况下，创建新用户

                new_user = User.objects.create()
                new_user.name = username
                new_user.password = password1
                new_user.email = email
                new_user.sex = sex
                new_user.save()
                return redirect('/login/')  # 自动跳转到登录页面

    register_form = RegisterForm()
    return render(request, 'register.html', locals())


#登出函数
def logout(request):
    if not request.session.get("is_login" ,None):
        return redirect("/#/")

    request.session.flush()
    return redirect("/#/")

# 地区数据的函数
def area(request,id):
    if request.method == 'POST':
        # 因为前端获取的日期是05-07等格式的，所以需要将前面的0去掉
        date = request.POST.get('date')
        date_list = [str(int(i)) for i in date.split('-')]
        search_date = '-'.join(date_list)
        area_id = id
        # 在数据库查询 地区为传进来的地区并且日期为传进来的日期的数据
        search_info = Cweather.objects.filter(Q(area=area_id) & Q(get_time=search_date))
        # 查询当前地区的省，并且进行distinct去重，转化为json格式
        set_area = json.dumps(list(search_info.values('province').distinct()))
        get_area = json.loads(set_area) #将查询的数据集转化为列表

        city_info = []
        # 循环的去查询每个省的前十个城市数据，分别存入city_info列表
        for city in get_area:
            city_list = []
            max_tp_list = []
            min_tp_list = []
            search_city = search_info.filter(province=city['province'])[:10]
            for s in search_city:
                city_list.append(s.city)    #从每个省的数据中获取城市的字段，存入city_list列表
                max_tp_list.append(s.max_tp)    #从每个省的数据中获取最高温的字段，存入max_tp_list列表
                min_tp_list.append(s.min_tp)    #从每个省的数据中获取最低温的字段，存入min_tp_list列表

            context = {
                'city_list':city_list,
                'max_tp':max_tp_list,
                'min_tp': min_tp_list,
                'pro':city
            }
            city_info.append(context)   #context代表一个省中的数据，有多少个省，列表就有多少条数据
        if not search_info:
            message = '此地区暂无{}日期的数据。'.format(search_date)

        return render(request,'area.html',locals())


# 全国最高温、最低温的函数
def national(request,level):
    if request.method == 'POST':
        # 因为前端获取的日期是05-07等格式的，所以需要将前面的0去掉
        date = request.POST.get('date')
        date_list = [str(int(i)) for i in date.split('-')]
        search_date = '-'.join(date_list)

        # 在数据库查询 地区为传进来的地区并且日期为传进来的日期的数据
        date_info = Cweather.objects.filter(Q(get_time=search_date))
        # 如果查询出来的数据为空，那么在页面显示暂无的提示
        if not date_info:
            message = '暂无{}日期的数据。'.format(search_date)

        city = []
        tp = []
        # 如果用户是从高温排序点击来的，那么从数据库拿出max_tp字段(高温数据的那一列)
        if level == 'max':
            # 从数据库取出高温的数据，并且按照降序进行排序
            max_city_info = date_info.extra(select={'max_tp':'max_tp+0'}).extra(order_by=["-max_tp"])[:10]
            date_type = '全国{}最高气温表'.format(search_date)
            for info in max_city_info:
                city.append(info.city)  #拿出城市的字段，添加到city列表
                tp.append(info.max_tp)  #拿出高温的字段，添加进tp列表
        # 如果用户是从低温排序点击来的，那么从数据库拿出min_tp字段(低温数据的那一列)
        elif level == 'min':
            # 从数据库取出低温的数据，并且按照升序进行排序
            max_city_info = date_info.extra(select={'min_tp':'min_tp+0'}).extra(order_by=["min_tp"])[:10]
            date_type = '全国{}最低气温升序表'.format(search_date)
            for info in max_city_info:
                city.append(info.city)  #同上逻辑一样
                tp.append(info.min_tp)  #同上逻辑一样

        return render(request,'national.html',locals())




