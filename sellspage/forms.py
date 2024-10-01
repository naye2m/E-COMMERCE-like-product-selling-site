from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import SellsPageUser, Product, Contracts, Order, Comment, Wishlist

from .utils import choiceListGen, productTypes

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = SellsPageUser
        fields = ['username', 'first_name', 'last_name', 'email', 'date_of_birth', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if SellsPageUser.objects.filter(email=email).exists():
            raise ValidationError(_("A user with that email already exists."))
        return email

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError("Username is required.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise ValidationError("Password is required.")
        return password

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError("This account is inactive.")
        # Add any other custom checks here if needed

class ProductForm(forms.ModelForm):
    price = forms.FloatField(validators=[MinValueValidator(0.01)], widget=forms.NumberInput(attrs={'placeholder': 'Price'}))
    title = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'Title'}))
    description = forms.CharField(max_length=750, required=False, widget=forms.Textarea(attrs={'placeholder': 'Short Description'}))
    long_description = forms.CharField(max_length=1500, required=False, widget=forms.Textarea(attrs={'placeholder': 'Long Description'}))
    # print(Product._meta.get_field('product_type').choices) # This works
    product_type = forms.ChoiceField(choices=Product._meta.get_field('product_type').choices, required=True)
    # product_type = forms.ChoiceField(choices=choiceListGen(productTypes), required=True)

    class Meta:
        model = Product
        fields = ['title', 'main_image', 'price', 'description', 'long_description', 'product_type']

class ContractsForm(forms.ModelForm):
    whatsapp_phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': 'Whatsapp Phone'}))
    whatsapp_link = forms.URLField(max_length=200, required=False, widget=forms.URLInput(attrs={'placeholder': 'Whatsapp Link'}))
    imo_phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': 'IMO Phone'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': 'Personal Phone'}))
    bkash_phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': 'Bkash Phone'}))
    nagad_phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': 'Nagad Phone'}))
    facebook_username = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'placeholder': 'Facebook Username'}))
    messenger_username = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'placeholder': 'Messenger Username'}))
    facebook_link = forms.URLField(max_length=200, required=False, widget=forms.URLInput(attrs={'placeholder': 'Facebook Link'}))
    messenger_link = forms.URLField(max_length=200, required=False, widget=forms.URLInput(attrs={'placeholder': 'Messenger Link'}))

    class Meta:
        model = Contracts
        fields = ['whatsapp_phone', 'whatsapp_link', 'imo_phone', 'phone', 'bkash_phone', 'nagad_phone', 'facebook_username', 'messenger_username', 'facebook_link', 'messenger_link']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['product'].queryset = user.listed_products.filter(is_available=True)

class CommentForm(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Add your comment here...'}), max_length=500, required=True)

    class Meta:
        model = Comment
        fields = ['comment']

class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = ['product']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['product'].queryset = Product.objects.exclude(wishlists__user=user)
