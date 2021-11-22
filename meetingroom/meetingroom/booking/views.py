from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib.auth import authenticate, login,logout
from .models import Room, Booking, UserInfo
from datetime import datetime, timedelta, date
from django.db.models import Q
import json
from django.contrib.auth.decorators import login_required

# Create your views here.


def log_in_page(request):
    return render(request, 'booking/login.html')

def log_in(request):
    if request.method != 'POST':
        return render(request, 'booking/login.html',{'message':'Please input user name and password!'})

    username = request.POST.get('username')
    password = request.POST.get('password')
    if not username or not password:
        return render(request, 'booking/login.html',{'message':'Please input user name and password!'})

    user = authenticate(request, username=username, password=password)


    if user is not None:
        login(request, user)
        return redirect('index')
    else:
        return render(request, 'booking/login.html',{'message':'User does not exist!'})

def log_out(request):
    logout(request)
    return redirect("index")

@login_required(login_url='/login_page')
def indexlq(request):
    time_ids = Booking.time_choice
    today = datetime.today().strftime('%Y-%m-%d')

    date_ = request.GET.get('date', today)  # default today does not work
    if not date_:
        date_ = today

    today = datetime.strptime(today, '%Y-%m-%d').date()
    date = datetime.strptime(date_, '%Y-%m-%d').date()
    print("Today is: ", datetime.now())
    if date < today or date > today + timedelta(days=7, hours=0):
        return render(request, 'booking/index.html', {'msg': '* Only select the date from today to the future 7 days!'+str(today + timedelta(days=7, hours=0))})

    book_list = Booking.objects.filter(date=date_)
    rooms = Room.objects.all().order_by('roomname')
    current_user = UserInfo.objects.get(username=request.user)
    htmls = ''

    for room in rooms:
        htmls += '<tr><td>' + room.roomname + '('+ str(room.num) + ')' + '</td>'
        for time in time_ids:
            is_book = False
            for book in book_list:
                if book.room.pk == room.pk and time[0]== book.time_id:  # can use like this in iterator
                    is_book = True
                    break

            if is_book:
                if book.user.pk == current_user.pk:
                    htmls += '<td class="active item" id="' + str(time[0]) + '" data-room="'+ str(room.pk) + '">' + str(book.user.username) + '</td>'
                else:
                    htmls += '<td class="another_active item" id="' + str(time[0]) + '" data-room="'+ str(room.pk) + '">' + str(book.user.username) + '</td>'
            else:
                htmls += '<td class="item" id="' + str(time[0]) + '" data-room="'+ str(room.pk) + '"></td>'

        htmls += '</tr>'

    contex = dict()
    contex['time_ids'] = time_ids
    contex['htmls'] = htmls
    return render(request, 'booking/index.html',contex)

@login_required(login_url='/login_page')
def booklq(request):
    """https://www.pluralsight.com/guides/work-with-ajax-django"""

    if request.is_ajax and request.method == "POST":

        book_date = request.POST.get('choose_date')
        post_data = json.loads(request.POST.get('post_data'))
        # print(post_data, book_date)

        user = UserInfo.objects.get(username=request.user)  # login required
        try:
            # to book
            booking_items = []
            for room, time_ids in post_data["add"].items():

                for time_id in time_ids:
                    room_ = Room.objects.get(id=room)
                    book_item = Booking(user=user, date=book_date, room=room_, time_id=time_id)
                    booking_items.append(book_item)
            Booking.objects.bulk_create(booking_items)

            # to cancel booking https://www.cnblogs.com/huchong/p/8027962.html
            q = Q()
            for room, time_ids in post_data["del"].items():
                cancel_item = Q()
                cancel_item.connector = "AND"
                for time_id in time_ids:
                    room_ = Room.objects.get(id=room)
                    cancel_item.children.append(('user',user))
                    cancel_item.children.append(('date',book_date))
                    cancel_item.children.append(('room',room_))
                    cancel_item.children.append(('time_id',time_id))
                    q.add(cancel_item, "OR")
            if q:
                Booking.objects.filter(q).delete()

            return JsonResponse({'state': 1})
        except Exception as e:
            return JsonResponse({'state': 2, 'msg': str(e)})

    else:
        return JsonResponse({'state': 0})

@login_required(login_url='/login_page')
def my_booking(request):
    today = date.today()
    books = Booking.objects.filter(user=request.user, date__gte=today)  # .values()
    time_ids = Booking.time_choice
    book_list = dict()
    booking_date_list = set()

    for book in books:
        date_of_book = book.date.strftime('%Y-%m-%d')
        booking_date_list.add(date_of_book)
        if date_of_book not in book_list.keys():
            book_list[date_of_book] = dict()
        if book.room not in book_list[date_of_book]:
            book_list[date_of_book][book.room] = [book.time_id]
        else:
            book_list[date_of_book][book.room].append(book.time_id)

    # print("***",book_list)
    html_to_front = []
    for dateb, bookings in book_list.items():
        htmls = ''
        for room, booked_time_ids in bookings.items():
            htmls += '<tr><td>' + room.roomname + '('+ str(room.num) + ')' + '</td>'
            for time in time_ids:
                if time[0] in booked_time_ids:
                    htmls += '<td class="active item" id="' + str(time[0]) + '" data-room="'+ str(room.pk) + '">' + str(request.user) + '</td>'
                else:
                    htmls += '<td class="item" id="' + str(time[0]) + '" data-room="'+ str(room.pk) + '"></td>'
            htmls += '</tr>'
        html_to_front.append((dateb,htmls))

    my_booking_date = request.GET.get('date', '')
    for item in html_to_front:
        if item[0] == my_booking_date:
            html_to_front = [item]

    context = dict()
    context['time_ids'] = time_ids
    context['html_to_front'] = html_to_front
    context['booking_date_list'] = list(booking_date_list)

    return render(request, 'booking/mybooking.html', context)



