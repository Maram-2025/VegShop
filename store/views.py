from django.shortcuts import render, redirect, get_object_or_404#عشان لما يجلب البيانات من قاعده البيانات  اذا كانت مش موجوده مايخرب التطبيق
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
import requests 

# Create your views here.
def admin_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        return redirect('index')
    return wrapper
# ----------------------------------------


def index(request):
    product = Product.objects.all()
    category = Category.objects.all()
    return render(request, 'store/index.html', {'Products': product, 'Categories': category})


@login_required
def about(request):
    return render(request, 'store/about.html')


@login_required
def cart(request):
    customer = get_object_or_404(Customer, user=request.user)

    order = Order.objects.filter(
        customer=customer,
        status='cart'
    ).first()

    items = order.items.all() if order else []

    total = sum(item.price * item.quantity for item in items)

    return render(request, 'store/cart.html', {
        'order': order,
        'items': items,
        'total': total
    })


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    customer, created = Customer.objects.get_or_create(
        user=request.user,
        defaults={
            'name': request.user.username,
            'email': request.user.email
        }
    )

    order, created = Order.objects.get_or_create(
        customer=customer,
        status='cart'
    )

    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        product=product,
        defaults={
            'quantity': 1,
            'price': product.price
        }
    )

    if not created:
        order_item.quantity += 1
        order_item.save()

    return redirect('cart')


@login_required
def remove_item(request, item_id):
    item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__customer__user=request.user
    )
    item.delete()
    return redirect('cart')


@login_required
def update_quantity(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(
            OrderItem,
            id=item_id,
            order__customer__user=request.user
        )
        item.quantity = int(request.POST.get('quantity', 1))
        item.save()
    return redirect('cart')


@login_required
def confirm_order(request):
    customer = get_object_or_404(Customer, user=request.user)

    order = Order.objects.filter(
        customer=customer,
        status='cart'
    ).first()

    if not order:
        messages.error(request, 'there is no items in the cart')
        return redirect('cart')

    order.status = 'processing'

    total = sum(item.total_price for item in order.items.all())
    order.total_price = total
    order.save()

    messages.success(request, 'order is confirmed')
    return redirect('cart')


@login_required
def contact(request):
    return render(request, 'store/contact.html')


@login_required
def productsingle(request, prud_id):
    product = get_object_or_404(Product, id=prud_id)

    related_products = Product.objects.filter(
        category_id=product.category_id
    ).exclude(id=product.id)

    return render(
        request,
        'store/product-single.html',
        {
            'product': product,
            'products': related_products
        }
    )


@login_required
def shop(request):
    category_id = request.GET.get('category')

    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()

    categories = Category.objects.all()

    return render(request, 'store/shop.html', {
        'products': products,
        'Categories': categories
    })


@login_required
def wishlist(request):
    customer = get_object_or_404(Customer, user=request.user)
    wishlist_items = Wishlist.objects.filter(customer=customer)

    return render(request, 'store/wishlist.html', {
        'wishlist_items': wishlist_items
    })


@login_required
def add_to_wishlist(request, prud_id):
    product = get_object_or_404(Product, id=prud_id)

    customer, created = Customer.objects.get_or_create(
        user=request.user,
        defaults={
            'name': request.user.username,
            'email': request.user.email
        }
    )

    Wishlist.objects.get_or_create(
        customer=customer,
        product=product
    )

    return redirect('wishlist')


@login_required
def remove_from_wishlist(request, item_id):
    item = get_object_or_404(Wishlist, id=item_id, customer__user=request.user)
    item.delete()
    return redirect('wishlist')


# dashboard


@admin_required
def indexDash(request):
    return render(request, 'dashboard/indexDash.html')


class pagessignin(LoginView):
    template_name = 'dashboard/pages-sign-in.html'
    authentication_form = CustomLoginForm

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return reverse_lazy('indexDash')
        else:
            return reverse_lazy('index')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            Customer.objects.create(
                user=user,
                name=user.username,
                email=user.email
            )

            login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()

    return render(request, 'dashboard/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('pages-sign-in')


@admin_required
def Categorylist(request):
    cate = Category.objects.all()
    return render(request, 'dashboard/Category-list.html', {'categories': cate})


@admin_required
def addacategory(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'added successfully')
            return redirect('Category-list')
        else:
            print(form.errors)
    else:
        form = CategoryForm()

    return render(request, 'dashboard/add-a-category.html', {'form': form})


@admin_required
def editacategory(request, cate_id):
    form = get_object_or_404(Category, id=cate_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=form)
        if form.is_valid():
            form.save()
            messages.success(request, 'edit successfully')
            return redirect('Category-list')
        else:
            print(form.errors)
    else:
        form = CategoryForm(instance=form)

    return render(request, 'dashboard/edit-a-category.html', {'form': form})


@admin_required
def Deleteacategory(request, cate_id):
    category = get_object_or_404(Category, id=cate_id)

    if request.method == 'POST':
        category.delete()
        return redirect('Category-list')

    return render(request, 'dashboard/Delete-a-category.html', {'category': category})


@admin_required
def listProdect(request):
    Prod = Product.objects.all()
    return render(request, 'dashboard/listProdect.html', {'Prodects': Prod})


@admin_required
def addaprodect(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'added successfully')
            return redirect('listProdect')
        else:
            print(form.errors)
    else:
        form = ProductForm()

    return render(request, 'dashboard/add-a-prodect.html', {'form': form})


@admin_required
def editaprodect(request, prud_id):
    prud = get_object_or_404(Product, id=prud_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=prud)
        if form.is_valid():
            form.save()
            messages.success(request, 'edit successfully')
            return redirect('listProdect')
        else:
            print(form.errors)
    else:
        form = ProductForm(instance=prud)

    return render(request, 'dashboard/edit-a-prodect.html', {'form': form})


@admin_required
def Deleteprodect(request, prud_id):
    prud = get_object_or_404(Product, id=prud_id)
    if request.method == 'POST':
        prud.delete()
        return redirect('listProdect')
    return render(request, 'dashboard/Delete-prodect.html', {'prud': prud})


@admin_required
def ListOrder(request):
    orders = Order.objects.all()
    return render(request, 'dashboard/ListOrder.html', {'orders': orders})


@admin_required
def AddAnOrder(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Order added successfully')
            return redirect('ListOrder')
    else:
        form = OrderForm()

    return render(request, 'dashboard/AddAnOrder.html', {'form': form})


@admin_required
def EditOrder(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Order updated successfully')
            return redirect('ListOrder')
    else:
        form = OrderForm(instance=order)

    return render(request, 'dashboard/EditOrder.html', {
        'form': form,
        'order': order
    })


@admin_required
def DeleteOrder(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Order deleted successfully')
        return redirect('ListOrder')

    return render(request, 'dashboard/DeleteOrder.html', {
        'order': order
    })


@admin_required
def listCustomers(request):
    customers = Customer.objects.all()
    return render(request, 'dashboard/listCustomers.html', {
        'customers': customers
    })


@admin_required
def AddACustomer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']

            if User.objects.filter(username=email).exists():
                messages.error(request, 'This email is already used')
            else:

                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password='12345678'
                )

                customer = form.save(commit=False)
                customer.user = user
                customer.save()

                messages.success(request, 'Customer added successfully')
                return redirect('listCustomers')

    else:
        form = CustomerForm()

    return render(request, 'dashboard/AddACustomer.html', {
        'form': form
    })


@admin_required
def EditACustomer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully')
            return redirect('listCustomers')
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'dashboard/EditACustomer.html', {
        'form': form,
        'customer': customer
    })


@admin_required
def DeleteACustomer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully')
        return redirect('listCustomers')

    return render(request, 'dashboard/DeleteACustomer.html', {
        'customer': customer
    })


   
from django.http import HttpResponse


def ssrf_test(request):
    target = request.GET.get('url')
    if target:
        try:
            # السيرفر يروح يجيب الصفحة اللي تطلبيها
            response = requests.get(target, timeout=5)
            # يعرضها لك بنفس شكلها وألوانها (هنا الخدعة)
            return HttpResponse(response.content)
        except:
            return HttpResponse("تعذر الوصول!")
    return HttpResponse("اكتبي الرابط في الـ URL فوق")