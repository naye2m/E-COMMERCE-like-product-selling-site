# from django.db import models
from typing import NoReturn
from django.urls import path,reverse,include
from django.db import models
from django.db.models import *
from django.contrib.auth.models import AbstractUser,AnonymousUser
from PIL import Image
import requests
import json as JSON
from django.utils.translation import gettext_lazy as _

from django.db.models import Q
from django.core.paginator import Page, Paginator
from django.core.serializers import serialize

import datetime as dt

from .utils import *
# Create your models here.
# banglaTxt = "আমার নাম নাঈম। কথা কম কাজ বেশি মানুশ আমি ভালোবাসি"
# TODOS
# Remember to add auto DateTimestamp
#serialize every models

class PhotoModel(Model):
    # TODO 

    drivePhotoID = CharField(max_length=256, editable=True, blank=True, null=True)

    # todo
    # make sure photo directly loaded in browser in src
    # try to use compression before upload
    
    # . get photo by id
    def asImageObject(self) -> Image: ...

    # . upload photo to drive and get id

    
    # def uploadPhoto(photo) -> int:
    #     """TODO: this should be an class Method for PhototModel"""
    @classmethod
    def uploadPhoto(cls,photo)  -> "PhotoModel":
        "get driveID and save Image"
        # photoModel = cls(drivePhotoID=1) # test
        # return photoModel # test
        url = "script.google"
        json: str = JSON.dumps({"hi": "hi"})
        data = None
        res: requests.Response = requests.post(url, data, json)
        dat: dict = res.json() if res.ok else {"err": "couldn;t connected"}
        fileID = dat.get("fileID", None)
        # TODO check valid driveID
        photoModel = cls(drivePhotoID=fileID)
        photoModel.save()
        return photoModel

    # . determine h and w
    
class User(AbstractUser):
    
    firstName = CharField(max_length=50, editable=True,blank=True, null=True)
    lastName = CharField(max_length=50, editable=True,blank=True, null=True)
    @property
    def fullName(self):
        "for getting full name"
        return self.firstName + self.lastName
    is_Seller = BooleanField(editable=True, blank=True, null=True)
    is_Customer = BooleanField(editable=True, blank=True, null=True)
    
    dateOfBirth = DateField(blank=True, null=True, editable=True)
    # phone = PhoneNumberField(editable=True)
    
    contracts = contracts = models.OneToOneField("sellspage.Contracts", on_delete=models.CASCADE)
    

    
    
    promocode = CharField(max_length=max_promo_length, blank=True, null=True)
    email = EmailField(blank=True, null=True, editable=True)

    @property
    def promoFrom(self):
        return getFromPromoCode(self.promocode)

    # @property
    # def totalSells(self):
    
    
    @property
    # def get_page( self:"User", posts:iter, pageNo: int = 1) -> dict:
    def get_page( self:"User",pageNo: int = 1) -> dict:
        posts = self.listed_products.all()
        if not user.is_authenticated:
            user = None
        post_list = posts.order_by("-id")
        pages = Paginator(post_list, 10)
        # pages.ELLIPSIS = "see all"
        if type(pageNo) is not int:
            try:
                pageNo = int(pageNo)
            except ValueError:
                pageNo = 1
        if pageNo > pages.num_pages:
            pageNo = pages.num_pages

        page: Page = pages.get_page(pageNo)
        return {
            "pageNo": page.number,
            "posts": [
                {
                    **post.serialize(),
                    "postedByCU": post.user == user,  # CU for current user
                    "likesCU": post.likes.filter(liked_by=user).first()
                    is not None,  # CU for current user
                    # **serialize("python", [post])[0],
                }
                for post in page.object_list
            ],
            "last": pages.num_pages,
            "perPage": pages.per_page
            # ,"total": pages.count
            ,
            "arrayOfPages": list(pages.page_range),
            "arrayOfPagesEllided": list(pages.get_elided_page_range()),
            "nextPage": page.next_page_number() if page.has_next() else False,
            "previousPage": (
                page.previous_page_number() if page.has_previous() else False
            ),
        }

class Contracts(Model):
    id = BigAutoField(primary_key=True)
    whatsappPhone = models.CharField(_("Whatsapp_Phone_Number"), max_length=20,editable=True, blank=True, null=True)
    whatsappLink = models.URLField(_("WhatsAppLink"), max_length=200,editable=True, blank=True, null=True)
    imoPhone = models.CharField(_("imo_Phone_Number"), max_length=20,editable=True, blank=True, null=True)
    phone = models.CharField(_("Personal_Phone_Number"), max_length=20,editable=True, blank=True, null=True)
    bkashPhone = models.CharField(_("Bkash_Phone_Number"), max_length=20,editable=True, blank=True, null=True)
    nagadPhone = models.CharField(_("Nagad_Phone_Number"), max_length=20,editable=True, blank=True, null=True)
    facebookUsername = models.CharField(_("WhatsAppLink"), max_length=20,editable=True, blank=True, null=True)
    messengerUsername = models.CharField(_("WhatsAppLink"), max_length=20,editable=True, blank=True, null=True)
    facebookLink = models.URLField(_("WhatsAppLink"), max_length=200,editable=True, blank=True, null=True)
    messengerLink = models.URLField(_("WhatsAppLink"), max_length=200,editable=True, blank=True, null=True)
    
class Promo(Model):
    id = BigAutoField(primary_key=True)
    holder = ForeignKey(User, related_name=_("myPromo"), on_delete=models.CASCADE)
    # ForeignKey("app.Model", verbose_name=_(""), on_delete=models.CASCADE)
    promoCode = CharField(max_length=max_promo_length, unique=True)
    # intrestSherePercent = SmallIntegerField(max_length=100,min=0)
    intrestSherePercent = PositiveSmallIntegerField(max_length=100)
    # user = ForeignKey(User, related_name=_("thisPromo"), on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Promo from : {self.holder.fullName}<{self.holder.username}>"

    def __unicode__(self) -> str:
        return f"Promo from : {self.holder.fullName}<{self.holder.username}>"

    @classmethod
    def getFromPromoCode(cls,SearchedPromoCode):  # -> "Promo" | None: 
        # TODO : this should be a class method
        res: cls | None = cls.objects.filter(promoCode=SearchedPromoCode).first()
        return res or None

class Location(Model):
    id = BigAutoField(primary_key=True)
    # todo : text choices to all locations
    # location = TextChoices(choices=[
    #         ("Fashion", "Fashion"),
    #         ("Toys", "Toys"),
    #         ("Electronics", "Electronics"),
    #         ("Home", "Home"),
    #         ("Others", "Others"),
    #     ])
    # zila = CharField(max_length=50,editable=True)
    # upazila = CharField(max_length=50,editable=True)
    # union = CharField(max_length=50,editable=True)
    # unionNo = PositiveSmallIntegerField(editable=True)
    # wordNo = PositiveSmallIntegerField(editable=True)
    # postOffice = CharField(max_length=50,editable=True)
    # postCode = PositiveIntegerField(editable=True)
    # vill = CharField(max_length=50,editable=True)
    locationStr = CharField(max_length=200, editable=True)

class ListingProduct(Model):
    """    Model for a listing in an online auction.
    """

    __all_prop__ : list = [
        "listed_by",
        "title",
        "price",
        "ProducType",
        "mainImage",
        "description_photos",
        "description",
        "longDescription",
        "timestamp",
        "isAvailable",#default true
        "Soldto",
        "date_time",
        ]
    
    def __init__(self, ):
        ...
        
    #  TODO: Define fields here
    title = CharField(max_length=50, editable=True, blank=True, null=True)
    mainImage = models.ForeignKey(PhotoModel, verbose_name=_("productsPhoto"), on_delete=models.CASCADE)
    price = FloatField(editable=True, blank=True, null=True)
    listed_by = ForeignKey(User,related_name="listed_products", on_delete=models.CASCADE)
    # mainImage = URLField(max_length=200, blank=True, null=True)
    date_time = DateTimeField(auto_now_add=True)  # Only set on creation
    isAvailable: bool = BooleanField(default=False,editable=True)
    description = CharField(max_length=750, editable=True, blank=True, null=True)
    longDescription = CharField(max_length=1500, editable=True, blank=True, null=True)
    timestamp = DateTimeField(auto_now_add=True,auto_created=True,auto_now=True)
    ProducType  = models.CharField(max_length=20, blank=True, null=True, choices=choiceListGen(productTypes),default=productTypes[0])
    # description_photos foreignkey
    # Soldto = IntegerField(editable=True,blank=True, null=True)
    @property
    def soldTo(self)->int:
        return self.s 

    photo = OneToOneField(
        PhotoModel,
        verbose_name=("products"),
        on_delete=models.CASCADE,
        editable=True,
        blank=True,
        null=True,
    )
    # photo = ForeignKey(Photo, verbose_name=("products"), on_delete=models.CASCADE,editable=True, blank=True, null=True)

    @property
    def staticUrl():
        return
    @staticUrl.getter
    def _():
        ...
    @staticUrl.setter
    def _() -> NoReturn:
        raise ValueError("Static URL cant be set")

    def getWatchlist(self):
        return self.watchlists if self.watchlists.exists() else None

    def new_comment(self, user: User, text: float) -> bool:
        try:
            b = Comment(listing=self, text=text, commented_by=user)
            b.save()
        except:
            return False
        return True
    def mark_as_sold(self, user:User) -> bool:
        try:
            if self.seller == user:
                self.isSold = True 
                self.save(update_fields=["isSold"])
            else:
                raise UserWarning
        except:
            return False
        return True

    def new_watchlist(self, user: User) -> bool:
        if user is self.seller:
            return False
        try:
            b = Watchlist(listing=self, user=user)
            b.save()
        except:
            return False
        return True
    def edit_details(self,user:User, details:str):
        if self.isSold or user != self.seller :
            return False
        try:
            self.details = details
            self.save(update_fields=["details"])
        except:
            return False
        return True
    class Meta:
        ordering = ["-date_time", "name"]  # Newest listings first
        verbose_name = "Listing"  # Improves admin interface display
        verbose_name_plural = "Listings"  # Improves admin interface display

    def get_absolute_url(self):
        """
        Dynamic URL based on listing ID
        Returns the URL for a specific listing detail view.   
        """
        return reverse(
            "listing_detail", args=[str(self.id)]
        )
    def __str__(self):
        return f"{self.name} by {self.seller.username}"  # More informative string representation

class keyFeatureOfProduct(Model):
    id = BigAutoField(primary_key=True)
    key = models.CharField(max_length=20)
    feature = models.CharField(max_length=100)
    product = models.ForeignKey(ListingProduct, verbose_name=_("keyFeatures"),related_name=_("keyFeatures"), on_delete=models.CASCADE)

class Post(Model):
    """Model definition for Post."""

    # TODO: Define fields here
    user = ForeignKey(User,related_name="posts", on_delete=models.CASCADE)
    timestamp = DateTimeField(auto_now_add=True)
    title = CharField(max_length=50, editable=True, blank=True, null=True)
    price = FloatField(editable=True, blank=True, null=True)
    # Soldto = IntegerField(editable=True,blank=True, null=True)
    description = CharField(max_length=750, editable=True, blank=True, null=True)
    longDescription = CharField(max_length=1500, editable=True, blank=True, null=True)
    ProducType = models.CharField(_("Type_Of_Product"), max_length=50,choices=choiceListGen(productTypes),default=productTypes[0])
    photo = OneToOneField(
        PhotoModel,
        verbose_name=("products"),
        on_delete=models.CASCADE,
        editable=True,
        blank=True,
        null=True,
    )
    # photo = ForeignKey(Photo, verbose_name=("products"), on_delete=models.CASCADE,editable=True, blank=True, null=True)

    @property
    def staticUrl():
        return
    @staticUrl.getter
    def _():
        ...
    @staticUrl.getter
    def _() -> NoReturn:
        raise ValueError("Static URL cant be set")

    class Meta:
        """Meta definition for Post."""

        ordering:list = [
            "-id",
        ]
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self) -> str:
        """Unicode representation of Post."""
        return f"Post : #{self.id} - {self.caption}"

    def edit(self, user: User, new_caption: str) -> bool:
        """Must remember to check the user is user who commented"""
        if user != self.user:
            return False
        try:
            self.caption = new_caption
            self.save()
            return True
        except:
            return False

    # def new_post(user: User, caption: str):
    #     # try:
    #         post = Post(user=user, caption=caption)
    #         post.save()
    #         return True
    #     # except:
    #         # return False

    def add_comment(self, commented_by: User, comment):
        try:
            comment = Comment(commented_by=commented_by, post=self, comment=comment)
            comment.save()
            return True
        except:
            return False

    def add_like(self, liked_by: User, isadd=True):
        try:
            if isadd:
                like = Like.objects.filter(post=self, liked_by=liked_by).first()
                if like:
                    return True
                like_obj = Like(liked_by=liked_by, post=self)
                like_obj.save()
            else:
                like = Like.objects.filter(post=self, liked_by=liked_by).first()
                if like:
                    like.delete()
            return True
        except:
            return False

    def serialize(self, numberOfComment=5) -> dict:
        return {
            "id": self.id,
            "user": self.user.username,
            "caption": self.caption,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes": self.likes.values("liked_by").distinct().count(),
            "comments": [
                com.get_dict()
                for com in self.comments.all().order_by("-id")[:numberOfComment]
            ],
        }

    def get_page(user:User, posts:iter, pageNo: int = 1) -> dict:
        print(user)
        if not user.is_authenticated:
            user = None
        post_list = posts.order_by("-id")
        pages = Paginator(post_list, 10)
        # pages.ELLIPSIS = "see all"
        if type(pageNo) is not int:
            try:
                pageNo = int(pageNo)
            except:
                pageNo = 1
        if pageNo > pages.num_pages:
            pageNo = pages.num_pages

        page: Page = pages.get_page(pageNo)
        return {
            "pageNo": page.number,
            "posts": [
                {
                    **post.serialize(),
                    "postedByCU": post.user == user,  # CU for current user
                    "likesCU": post.likes.filter(liked_by=user).first()
                    is not None,  # CU for current user
                    # **serialize("python", [post])[0],
                }
                for post in page.object_list
            ],
            "last": pages.num_pages,
            "perPage": pages.per_page
            # ,"total": pages.count
            ,
            "arrayOfPages": list(pages.page_range),
            "arrayOfPagesEllided": list(pages.get_elided_page_range()),
            "nextPage": page.next_page_number() if page.has_next() else False,
            "previousPage": (
                page.previous_page_number() if page.has_previous() else False
            ),
        }

class Product(Model):

    title = CharField(max_length=50, editable=True, blank=True, null=True)
    price = FloatField(editable=True, blank=True, null=True)
    # Soldto = IntegerField(editable=True,blank=True, null=True)
    description = CharField(max_length=750, editable=True, blank=True, null=True)
    longDescription = CharField(max_length=1500, editable=True, blank=True, null=True)
    photo = OneToOneField(
        PhotoModel,
        verbose_name=("products"),
        on_delete=models.CASCADE,
        editable=True,
        blank=True,
        null=True,
    )
    # photo = ForeignKey(Photo, verbose_name=("products"), on_delete=models.CASCADE,editable=True, blank=True, null=True)

    @property
    def staticUrl():
        return
    @staticUrl.getter
    def _():
        ...
    @staticUrl.getter
    def _() -> NoReturn:
        raise ValueError("Static URL cant be set")

class descriptionPhoto(Model):
# TODO rename this model
    product = ForeignKey(
        Product, related_name=_("description_photos"), on_delete=models.CASCADE
    )
    photo = models.ForeignKey(PhotoModel, verbose_name=_("description_photos"), on_delete=models.CASCADE)

class Order(Model):
    id = BigAutoField(primary_key=True)
    product = ForeignKey(
        Product, related_name=_("orders"), on_delete=models.CASCADE
    )
    User = ForeignKey(User, related_name=_("Orders"), on_delete=models.CASCADE)
    ...

class Comment(Model):
    id = BigAutoField(primary_key=True)
    product = ForeignKey(
        Product, related_name=_("descriptionPhotos"), on_delete=models.CASCADE
    )
    User = ForeignKey(User, related_name=_("comments"), on_delete=models.CASCADE)
    ...

class Wishlist(Model):
    id = BigAutoField(primary_key=True)
    User = ForeignKey(User, related_name=_("wishlists"), on_delete=models.CASCADE)
    product = ForeignKey(
        Product, related_name=_("descriptionPhotos"), on_delete=models.CASCADE
    )
    ...
