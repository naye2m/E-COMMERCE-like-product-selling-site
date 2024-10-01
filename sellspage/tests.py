from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import SellsPageUser, Product, PhotoModel, Contracts, Promo, Location, KeyFeatureOfProduct, DescriptionPhoto, Order, Comment, Wishlist
from .forms import UserRegistrationForm, ProductForm ,UserLoginForm
from .utils import choiceListGen, timestampFormatter, recDir, recKeys, recAny

SellsPageUser = get_user_model()

# $ python manage.py test sellspage

class UserModelTest(TestCase):

    def setUp(self):
        self.user = SellsPageUser.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            is_seller=True,
            date_of_birth='1990-01-01',
            email='john.doe@example.com'
        )

    def test_user_full_name(self):
        self.assertEqual(self.user.full_name, 'John Doe')

    def test_user_promo_from(self):
        promo = Promo.objects.create(holder=self.user, promo_code='PROMO123', interest_share_percent=10)
        self.assertEqual(self.user.promo_from, promo)

    def test_user_pagination(self):
        for i in range(15):
            Product.objects.create(
                title=f'Product {i}',
                main_image=PhotoModel.objects.create(drive_photo_id=f'drive_photo_{i}'),
                price=100.0 + i,
                listed_by=self.user
            )

        page1 = self.user.get_page(page_no=1)
        page2 = self.user.get_page(page_no=2)

        self.assertEqual(len(page1['posts']), 10)
        self.assertEqual(len(page2['posts']), 5)
        self.assertTrue(page1['nextPage'])
        self.assertFalse(page2['nextPage'])


class ListingProductModelTest(TestCase):

    def setUp(self):
        self.user = SellsPageUser.objects.create_user(username='seller', password='password')
        self.product = Product.objects.create(
            title='Test Product',
            main_image=PhotoModel.objects.create(drive_photo_id='drive_photo_1'),
            price=99.99,
            listed_by=self.user
        )

    def test_listing_product_str(self):
        self.assertEqual(str(self.product), 'Test Product by seller')

    def test_listing_product_absolute_url(self):
        self.assertEqual(self.product.get_absolute_url(), reverse('listing_detail', args=[str(self.product.id)]))


class UserRegistrationFormTest(TestCase):

    def test_valid_form(self):
        form_data = {
            'username': 'newuser',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane.doe@example.com',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'username': 'newuser',
            'password1': 'TestPass123!',
            'password2': 'DifferentPass123!',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane.doe@example.com',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())


class ProductFormTest(TestCase):

    def setUp(self):
        self.user = SellsPageUser.objects.create_user(username='seller', password='password')
        self.photo = PhotoModel.objects.create(drive_photo_id='drive_photo_1')

    def test_valid_form(self):
        form_data = {
            'title': 'Test Product',
            'main_image': self.photo.id,
            'price': 99.99,
            'listed_by': self.user.id,
            'description': 'A great product!',
        }
        form = ProductForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'title': '',
            'main_image': '',
            'price': '',
            'listed_by': self.user.id,
            'description': '',
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())


class PhotoModelTest(TestCase):

    def test_upload_photo(self):
        with self.assertRaises(ValueError):
            PhotoModel.upload_photo('invalid_photo')


class ViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = SellsPageUser.objects.create_user(username='user', password='password')
        self.seller = SellsPageUser.objects.create_user(username='seller', password='password', is_seller=True)
        self.product = Product.objects.create(
            title='Test Product',
            main_image=PhotoModel.objects.create(drive_photo_id='drive_photo_1'),
            price=99.99,
            listed_by=self.seller
        )

    def test_login_view(self):
        response = self.client.post(reverse('login'), {'username': 'user', 'password': 'password'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))

    def test_register_view(self):
        form_data = {
            'username': 'newuser',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane.doe@example.com',
        }
        response = self.client.post(reverse('register'), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))

    def test_add_listing_product_view(self):
        self.client.login(username='seller', password='password')
        form_data = {
            'title': 'New Product',
            'main_image': PhotoModel.objects.create(drive_photo_id='drive_photo_2').id,
            'price': 100.0,
            'description': 'A new product description',
            'listed_by': self.seller.id,
        }
        response = self.client.post(reverse('add_listing_product'), data=form_data)
        self.assertEqual(response.status_code, 302)
        product = Product.objects.get(title='New Product')
        self.assertRedirects(response, product.get_absolute_url())

    def test_profile_view(self):
        response = self.client.get(reverse('profile', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')

    def test_listing_detail_view(self):
        response = self.client.get(reverse('listing_detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product_detail.html')

    def test_logout_view(self):
        self.client.login(username='user', password='password')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))


class UtilsTest(TestCase):

    def test_choice_list_gen(self):
        choices = choiceListGen(['Option1', 'Option2'])
        self.assertEqual(choices, [('Option1', 'Option1'), ('Option2', 'Option2')])

    def test_timestamp_formatter(self):
        now = timezone.now()
        formatted = timestampFormatter(now)
        self.assertEqual(formatted, now.strftime("%b %d %Y, %I:%M %p"))

    def test_rec_dir(self):
        result = recDir(self)
        self.assertIn('test_rec_dir', result)

    def test_rec_keys(self):
        result = recKeys({'key1': 'value1'})
        self.assertEqual(result['key1'], ['<class \'str\'>', 'value1'])

    def test_rec_any(self):
        result = recAny({'key1': 'value1'})
        self.assertEqual(result['key1'][1], 'value1')

# sellspage/tests/test_forms.py


SellsPageUser = get_user_model()

class UserLoginFormTest(TestCase):
    
    def setUp(self):
        """Create a user for login testing."""
        self.username = 'testuser'
        self.password = 'securepassword'
        self.user = SellsPageUser.objects.create_user(username=self.username, password=self.password)
    
    def test_valid_login_form(self):
        """Test valid login form submission."""
        form_data = {
            'username': self.username,
            'password': self.password,
        }
        form = UserLoginForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username'], self.username)
        self.assertEqual(form.cleaned_data['password'], self.password)
    
    def test_invalid_login_form(self):
        """Test login form with invalid data."""
        form_data = {
            'username': '',
            'password': '',
        }
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)
    
    def test_inactive_user_login(self):
        """Test login form with an inactive user."""
        self.user.is_active = False
        self.user.save()
        form_data = {
            'username': self.username,
            'password': self.password,
        }
        form = UserLoginForm(data=form_data)
        with self.assertRaises(ValidationError):
            form.confirm_login_allowed(self.user)
    
    def test_username_field(self):
        """Test the username field."""
        form = UserLoginForm(data={'username': self.username})
        self.assertIn('username', form.fields)
        self.assertEqual(form.fields['username'].widget.attrs['autofocus'], True)
    
    def test_password_field(self):
        """Test the password field."""
        form = UserLoginForm(data={'password': self.password})
        self.assertIn('password', form.fields)
        self.assertEqual(form.fields['password'].widget.attrs['autocomplete'], 'current-password')
    
    def test_blank_username(self):
        """Test the form with a blank username."""
        form_data = {
            'username': '',
            'password': self.password,
        }
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
    
    def test_blank_password(self):
        """Test the form with a blank password."""
        form_data = {
            'username': self.username,
            'password': '',
        }
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
    
    def test_login_with_wrong_password(self):
        """Test login with correct username but wrong password."""
        form_data = {
            'username': self.username,
            'password': 'wrongpassword',
        }
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)




if __name__ == "__main__":
    import unittest
    unittest.main()
