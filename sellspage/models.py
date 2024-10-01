from django.db import models
from django.contrib.auth.models import AbstractUser,User
from django.core.paginator import Paginator
from django.urls import reverse
from PIL import Image
import requests
import json as JSON
from django.utils.translation import gettext_lazy as _

from .utils import filter_dict,choiceListGen, productTypes, getFromPromoCode ,timestampFormatter

__all__:list = [
    "AbstractUser",
    "Comment",
    "Contracts",
    "DescriptionPhoto",
    "KeyFeatureOfProduct",
    "Like",
    "Location",
    "Order",
    "PhotoModel",
    "Product",
    "Promo",
    "SellsPageUser",
    "User",
    "Wishlist",
]

class PhotoModel(models.Model):
    drive_photo_id = models.CharField(max_length=256, blank=True, null=True)

    def as_image_object(self) -> Image:
        # Placeholder for implementation to return the image object
        pass
    
    def get_url(self):
        # todo
        return "blabla"
    
    @classmethod
    def upload_photo(cls, photo) -> "PhotoModel":
        # Upload photo to Google Drive and save the drive ID
        url = "your_google_script_url_here"  # Replace with your actual Google Apps Script URL
        json_data = JSON.dumps({"photo_data": photo.read()})
        response = requests.post(url, data=json_data)
        data = response.json() if response.ok else {"error": "Couldn't connect"}
        file_id = data.get("fileID")
        
        if file_id:
            photo_model = cls(drive_photo_id=file_id)
            photo_model.save()
            return photo_model
        else:
            raise ValueError("Invalid Drive ID or Upload Failed")

class SellsPageUser(User):
    profile_picture =   models.ForeignKey("PhotoModel", related_name='profile_pics', on_delete=models.CASCADE,blank=True, null=True)
    cover_picture =   models.ForeignKey("PhotoModel", related_name='cover_pics', on_delete=models.CASCADE,blank=True, null=True)
    is_seller = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    date_of_birth = models.DateField(blank=True, null=True)
    contracts = models.OneToOneField("Contracts", on_delete=models.CASCADE, blank=True, null=True)
    promocode = models.CharField(max_length=20, blank=True, null=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def promo_from(self):
        return getFromPromoCode(self.promocode)
    def get_page(self, page_no: int = 1) -> dict:
        posts = self.listed_products.all().order_by("-id")
        paginator = Paginator(posts, 10)
        page = paginator.get_page(page_no)

        propsNeeded: list = [
            "id",
            "image",
            "title",
            "title",
            "price",
            "bought_by_count",
        ]
        
        return {
            "pageNo": page.number,
            "products": [
                {
                    **filter_dict(post.serialize(),propsNeeded),
                    "postedByCU": post.listed_by == self,
                    # todo "likesCU": post.likes.filter(liked_by=self).exists(),
                }
                for post in page.object_list
            ],
            "last": paginator.num_pages,
            "perPage": paginator.per_page,
            "arrayOfPages": list(paginator.page_range),
            "arrayOfPagesEllided": list(paginator.get_elided_page_range()),
            "nextPage": page.next_page_number() if page.has_next() else None,
            "previousPage": page.previous_page_number() if page.has_previous() else None,
        }

class Contracts(models.Model):
    whatsapp_phone = models.CharField(_("Whatsapp Phone Number"), max_length=20, blank=True, null=True)
    whatsapp_link = models.URLField(_("WhatsApp Link"), max_length=200, blank=True, null=True)
    imo_phone = models.CharField(_("IMO Phone Number"), max_length=20, blank=True, null=True)
    phone = models.CharField(_("Personal Phone Number"), max_length=20, blank=True, null=True)
    bkash_phone = models.CharField(_("Bkash Phone Number"), max_length=20, blank=True, null=True)
    nagad_phone = models.CharField(_("Nagad Phone Number"), max_length=20, blank=True, null=True)
    facebook_username = models.CharField(_("Facebook Username"), max_length=50, blank=True, null=True)
    messenger_username = models.CharField(_("Messenger Username"), max_length=50, blank=True, null=True)
    facebook_link = models.URLField(_("Facebook Link"), max_length=200, blank=True, null=True)
    messenger_link = models.URLField(_("Messenger Link"), max_length=200, blank=True, null=True)

class Promo(models.Model):
    holder = models.ForeignKey(SellsPageUser, related_name="my_promos", on_delete=models.CASCADE)
    promo_code = models.CharField(max_length=20, unique=True)
    interest_share_percent = models.PositiveSmallIntegerField()

    def __str__(self) -> str:
        return f"Promo from: {self.holder.full_name} <{self.holder.username}>"

    @classmethod
    def get_from_promo_code(cls, searched_promo_code: str):
        return cls.objects.filter(promo_code=searched_promo_code).first()

class Location(models.Model):
    location_str = models.CharField(max_length=200)

class Product(models.Model):
    title = models.CharField(max_length=50)
    main_image = models.ForeignKey(PhotoModel, verbose_name=_("Product Photo"), on_delete=models.CASCADE)
    price = models.FloatField()
    listed_by = models.ForeignKey(SellsPageUser, related_name="listed_products", on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)
    description = models.TextField(max_length=750, blank=True, null=True)
    long_description = models.TextField(max_length=1500, blank=True, null=True)
    product_type = models.CharField(max_length=20, choices=choiceListGen(productTypes), default=productTypes[0])
    # models.Choice(fsd=5)
    
    class Meta:
        ordering = ["-date_time", "title"]
        verbose_name = "Listing"
        verbose_name_plural = "Listings"

    def get_absolute_url(self):
        return reverse("listing_detail", args=[str(self.id)])

    def __str__(self):
        return f"{self.title} by {self.listed_by.username}"


    def serialize(self)-> dict: 
        return {
            "id": self.id,
            "title":self.title,
            "main_image":self.main_image.get_url(),
            "price":self.price,
            "listed_by":self.listed_by.username,
            "date_time":timestampFormatter(self.date_time),
            "is_available":self.is_available,
            "description":self.description,
            "long_description":self.long_description,
            "product_type":self.product_type, 
            "likes":"todo", 
            "comments":"todo", 
        
    }

class KeyFeatureOfProduct(models.Model):
    key = models.CharField(max_length=20)
    feature = models.CharField(max_length=100)
    product = models.ForeignKey(Product, related_name="key_features", on_delete=models.CASCADE)

class DescriptionPhoto(models.Model):
    product = models.ForeignKey(Product, related_name="description_photos", on_delete=models.CASCADE)
    photo = models.ForeignKey(PhotoModel, verbose_name=_("Description Photo"), on_delete=models.CASCADE)

class Order(models.Model):
    product = models.ForeignKey(Product, related_name="orders", on_delete=models.CASCADE)
    user = models.ForeignKey(SellsPageUser, related_name="orders", on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    product = models.ForeignKey(Product, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(SellsPageUser, related_name="comments", on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Wishlist(models.Model):
    user = models.ForeignKey(SellsPageUser, related_name="wishlists", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="wishlists", on_delete=models.CASCADE)

class Like(models.Model):
    user = models.ForeignKey(SellsPageUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} likes {self.product.title}"
