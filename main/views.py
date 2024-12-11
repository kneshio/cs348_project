from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import View
from django.contrib.auth.hashers import make_password
from .models import *
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.db import connection
from .forms import UserForm

def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserForm()

    return render(request, 'register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        seller = authenticate(request, username=username, password=password)
        if seller is not None:
            auth_login(request, seller)
            
            UserSession.objects.filter(user=seller).delete()  # Delete old sessions

            # Save the new session in the UserSession model
            user_session = UserSession(
                user=seller,
                session_key=request.session.session_key  # Django assigns a session_key
            )
            user_session.save()
            
            return redirect('main')
        else:
            return render(request, 'login.html', {'message': "Wrong username or password"})

    return render(request, 'login.html')

def main(request):
    return render(request, 'main.html', {'user': request.user})

def catalog(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.product_id, p.name, p.category, p.price, p.quantity, p.description, s.username, s.seller_id FROM main_product p
            left join main_seller s on p.seller_id = s.seller_id
        """)

        products = cursor.fetchall()

    return render(request, 'catalog.html', {'products': products})

def search(request):
    name = request.GET.get('name', '').strip()
    category = request.GET.get('category', '').strip()
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    seller = request.GET.get('seller', '').strip()

    # with connection.cursor() as cursor:
    #     cursor.execute("""
    #         SELECT p.product_id, p.name, p.category, p.price, p.quantity, p.description, s.username FROM main_product p
    #         left join main_seller s on p.seller_id = s.seller_id
    #     """)
    #     categories = [row[0] for row in cursor.fetchall()]
    
    query = """
        SELECT p.product_id, p.name, p.category, p.price, p.quantity, p.description, s.username, s.seller_id FROM main_product p
        left join main_seller s on p.seller_id = s.seller_id
        WHERE 1=1
    """
    params = []

    if name:
        query += " AND p.name LIKE %s"
        params.append(f"%{name}%")
    if category:
        query += " AND p.category = %s"
        params.append(category)
    if min_price:
        try:
            price = float(min_price)
            query += " AND p.price >= %s"
            params.append(min_price)
        except ValueError:
            pass
    if max_price:
        try:
            price = float(max_price)
            query += " AND p.price <= %s"
            params.append(max_price)
        except ValueError:
            pass
    if seller:
        query += " AND s.username = %s"
        params.append(seller)

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        products = cursor.fetchall()

    return render(request, 'catalog.html', {'products': products})

def buy(request, pk):
    product = Product.objects.get(pk=pk)
    
    if request.method == 'POST':
        action_type = request.POST.get('action')

        if action_type == 'buy':
            if product.quantity > 0:
                product.quantity -= 1
                if product.quantity == 0:
                    product.delete()
                else:
                    product.save()
                
                return redirect('catalog')
            else:
                return render(request, 'buy.html', {'product': product, 'message': 'Sorry, this product is out of stock!'})
        
    return render(request, 'buy.html')

def sell_hub(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.product_id, p.name, p.category, p.price, p.quantity, p.description, s.username, s.seller_id FROM main_product p
            left join main_seller s on p.seller_id = s.seller_id
            where s.seller_id = %s
        """, [request.user.seller_id])

        products = cursor.fetchall()
        
    return render(request, 'sell_hub.html', {'products': products})

def add(request):
    if request.method == 'POST':
        action_type = request.POST.get('action')

        item_name = request.POST.get('item_name')
        item_category = request.POST.get('item_category')
        item_price = request.POST.get('item_price')
        item_quantity = request.POST.get('item_quantity')
        item_description = request.POST.get('item_description')

        if action_type == 'create':
            new_product = Product(
                name=item_name,
                category=item_category,
                description=item_description,
                price=item_price,
                quantity=item_quantity,
                seller = request.user
            )
            new_product.save()

        return redirect('catalog')

    return render(request, 'add.html')

def edit(request, pk):
    product = Product.objects.get(pk=pk)

    if request.method == 'POST':
        product.name = request.POST.get('item_name')
        product.category = request.POST.get('item_category')
        product.price = request.POST.get('item_price')
        product.quantity = request.POST.get('item_quantity')
        product.description = request.POST.get('item_description')
        product.save()

        return redirect('catalog')

    return render(request, 'edit.html', {'product': product})

def delete(request, **kwargs):
    product_id = kwargs.get('pk')
    product = get_object_or_404(Product, pk = product_id)

    if request.method == 'POST':
        action_type = request.POST.get('action')

        if action_type == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM main_product WHERE product_id = %s", [product_id])

            return redirect('catalog')

    return render(request, 'delete.html', {'product': product})

def logout_view(request):
    if request.user.is_authenticated:
        CustomSession.objects.filter(user=request.user, session_key=request.session.session_key).delete()

    logout(request)
    return redirect('login')

# class AlbumUpdate(UpdateView):
# 	model = Product
# 	fields = []

class UserFormView(View):
    form_class = UserForm
    template_name = 'register.html'

    def get(self,request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self,request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit = False)

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()

            user = authenticate(username = username, password = password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('main')