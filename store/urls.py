from django.urls import path
from . import views
from .views import pagessignin
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('cart/remove/<int:item_id>/', views.remove_item, name='remove_item'),
    path('cart/update/<int:item_id>/',
         views.update_quantity, name='update_quantity'),

    path('confirm-order/', views.confirm_order, name='confirm_order'),

    path('contact/', views.contact, name='contact'),
    path('product-single/<int:prud_id>/',
         views.productsingle, name='product-single'),
    path('shop/', views.shop, name='shop'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:prud_id>/',
         views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:item_id>/',
         views.remove_from_wishlist, name='remove_from_wishlist'),
    # dashboard
    path('indexDash/', views.indexDash, name='indexDash'),
    
    path('logout/', views.logout_view, name='logout'),

    path('pages-sign-in/', pagessignin.as_view(), name='pages-sign-in'),
    path('register/', views.register, name='register'),
    path('Category-list/', views.Categorylist, name='Category-list'),
    path('add-a-category/', views.addacategory, name='add-a-category'),
    path('edit-a-category/<int:cate_id>',
         views.editacategory, name='edit-a-category'),
    path('Delete-a-category/<int:cate_id>',
         views.Deleteacategory, name='Delete-a-category'),
    path('listProdect/', views.listProdect, name='listProdect'),
    path('add-a-prodect/', views.addaprodect, name='add-a-prodect'),
    path('edit-a-prodect/ <int:prud_id>',
         views.editaprodect, name='edit-a-prodect'),
    path('Delete-prodect/ <int:prud_id>',
         views.Deleteprodect, name='Delete-prodect'),
    path('ListOrder/', views.ListOrder, name='ListOrder'),
    path('AddAnOrder/', views.AddAnOrder, name='AddAnOrder'),
    path('EditOrder/<int:order_id>/', views.EditOrder, name='EditOrder'),
    path('DeleteOrder/<int:order_id>/', views.DeleteOrder, name='DeleteOrder'),
    path('listCustomers/', views.listCustomers, name='listCustomers'),
    path('AddACustomer/', views.AddACustomer, name='AddACustomer'),
    path('EditACustomer/<int:customer_id>/',
         views.EditACustomer, name='EditACustomer'),
    path('DeleteACustomer/<int:customer_id>/',
         views.DeleteACustomer, name='DeleteACustomer'),
    path('scan/', views.ssrf_test),

]
