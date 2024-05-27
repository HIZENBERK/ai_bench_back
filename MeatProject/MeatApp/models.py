from typing import Any, Iterable
from venv import logger

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin, User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.crypto import get_random_string
import datetime

#from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token


class UserManager(BaseUserManager):
    def create_user(self, empNo, username, Position, Job=None, password=None):
        """
        주어진 이메일, 닉네임, 비밀번호 등 개인정보로 User 인스턴스 생성
        """
        if not empNo:
            raise ValueError('Users must have an employee number')

        user = self.model(
            empNo=empNo,
            username=username,
            Position=Position,
            Job=Job,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, empNo, username, password, Position='A', Job='OM'):
        """
        주어진 이메일, 닉네임, 비밀번호 등 개인정보로 User 인스턴스 생성
        단, 최상위 사용자이므로 권한을 부여한다.
        """
        user = self.create_user(
            empNo=empNo,
            username=username,
            Position=Position,
            Job=Job,
            password=password,
        )

        user.is_superuser = True
        #user.is_staff = True  # 최상위 사용자가 staff 상태를 가지도록 설정
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    empNo = models.CharField(
        verbose_name=('Employee Number'),
        max_length=10,
        unique=True,
    )
    username = models.CharField(
        verbose_name=('User name'),
        max_length=30,
        unique=True
    )
    is_active = models.BooleanField(
        verbose_name=('Is active'),
        default=True
    )
    date_joined = models.DateTimeField(
        verbose_name=('Date joined'),
        default=timezone.now
    )
    OrderManager = 'OM'
    DissectionManager = 'DM'
    WarehouseManager = 'WM'
    Admin = 'A'
    Manager = 'M'
    User = 'U'
    JobList = [  # 직무
        (OrderManager, '주문담당자'),
        (DissectionManager, '해체담당자'),
        (WarehouseManager, '입고담당자'),
    ]
    Job = models.CharField(
        max_length=50,
        choices=JobList,
        default=OrderManager
    )

    PositionList = [
        (Admin, '관리자'),
        (Manager, '매니저'),
        (User, '사용자'),
    ]
    Position = models.CharField(
        max_length=20,
        choices=PositionList,
        default=User
    )  # 직위

    # 이 필드는 레거시 시스템 호환을 위해 추가할 수도 있다.
    # salt = models.CharField(
    #     verbose_name=_('Salt'),
    #     max_length=10,
    #     blank=True
    # )

    objects = UserManager()

    # id로 사용할 필드
    USERNAME_FIELD = 'empNo'
    # 필수 입력 필드
    REQUIRED_FIELDS = [
        'username',
        'Job'
        #,'Position'
    ]

    # class Meta:
    #     verbose_name = _('empNo')
    #     verbose_name_plural = _('users')
    #     ordering = ('-date_joined',)

    def __str__(self):
        return self.username

    def generate_emp_no(self):
        prefix = ''
        if self.Position == self.Admin:
            prefix = 'admin'
        elif self.Position == self.Manager:
            prefix = '1'+ get_random_string(length=5, allowed_chars='1234567890')
        elif self.Position == self.User:
            prefix = '2'+ get_random_string(length=5, allowed_chars='1234567890')
        return prefix

    def generate_password(self):
        emp_no_str = str(self.empNo)
        if emp_no_str == 'Admin':
            random_part = '1234'
        else:
            random_part = get_random_string(length=3,allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') + get_random_string(length=3, allowed_chars='1234567890')+ emp_no_str[4:]
        logger.debug(random_part)
        return random_part

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All superusers are staff
        return self.is_superuser



# class CustomUserManager(BaseUserManager):
#     def create_user(self, username, EmpNo, Position, password=None, **extra_fields):
#         if not EmpNo:
#             raise ValueError('The EmpNo field must be set')
#         user = self.model(username=username, EmpNo=EmpNo, Position=Position, **extra_fields)
#         if password:
#             user.set_password(password)
#         else:
#             user.set_password(self.generate_password())
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(self, username, EmpNo, Position, password=None, **extra_fields):
#         extra_fields.setdefault('is_admin', True)
#         extra_fields.setdefault('is_superuser', True)
#         return self.create_user(username, EmpNo, Position, password, **extra_fields)

# class CustomUser(AbstractBaseUser, PermissionsMixin):
#     username = models.CharField(max_length=6, unique=True)
#     EmpNo = models.CharField(max_length=6, unique=True, editable=False)
#
#     OrderManager = 'OM'
#     DissectionManager = 'DM'
#     WarehouseManager = 'WM'
#     Admin = 'A'
#     Manager = 'M'
#     User = 'U'
#
#     JobList = [  # 직무
#         (OrderManager, '주문담당자'),
#         (DissectionManager, '해체담당자'),
#         (WarehouseManager, '입고담당자'),
#     ]
#     Job = models.CharField(max_length=100, choices=JobList, default=OrderManager)
#
#     PositionList = [
#         (Admin, '관리자'),
#         (Manager, '매니저'),
#         (User, '사용자'),
#     ]
#     Position = models.CharField(max_length=100, choices=PositionList, default=User)  # 직위
#     is_active = models.BooleanField(default=True) #계정 사용가능 여부
#     is_admin = models.BooleanField(default=False)#항상 관리자로 유지하는지
#     is_anonymous = models.BooleanField(default=False)#항상 로그아웃을 유지할지
#     is_authenticated = models.BooleanField(default=False)#항상 로그인을 유지할지
#     #id로 사용할 필드
#     USERNAME_FIELD = 'EmpNo'
#     #필수 입력 필드
#     REQUIRED_FIELDS = ['username', 'Position']
#
#     objects = CustomUserManager()
#
#     def save(self, *args, **kwargs):
#         if not self.EmpNo:
#             self.EmpNo = self.generate_emp_no()
#         if not self.password:
#             self.set_password(self.generate_password())
#             #self.set_password(self.password)
#         super().save(*args, **kwargs)
#
#     def generate_emp_no(self):
#         prefix = ''
#         if self.Position == self.Admin:
#             prefix = 'admin'
#         elif self.Position == self.Manager:
#             prefix = '1'+ get_random_string(length=5, allowed_chars='1234567890')
#         elif self.Position == self.User:
#             prefix = '2'+ get_random_string(length=5, allowed_chars='1234567890')
#         return prefix
#
#     def generate_password(self):
#         emp_no_str = str(self.EmpNo)
#         if emp_no_str == 'Admin':
#             random_part = '1234'
#         else:
#             random_part = get_random_string(length=3,allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') + get_random_string(length=3, allowed_chars='1234567890')+ emp_no_str[4:]
#         logger.debug(random_part)
#         return random_part
#
#     def was_published_recently(self):
#         return self.date_joined >= timezone.now() - datetime.timedelta(days=1)



# 회원정보
# class EmpInfo(models.Model):
#     EmpNo = models.CharField(max_length=6, primary_key=True, editable=False) #직원 번호
#     EmpName = models.ForeignKey("User", on_delete=models.CASCADE, db_column="username") #직원 이름
#     Job = models.ForeignKey("User", on_delete=models.CASCADE,db_column="Job")  #직무
#     Position = models.ForeignKey("User", on_delete=models.CASCADE,db_column="Position") #직위
#
#     def save(self, *args, **kwargs):
#         if self.Position == self.Admin:
#             self.EmpNo = '0' + get_random_string(length=5, allowed_chars='1234567890')
#         elif self.Position == self.Manager:
#             self.EmpNo = '1' + get_random_string(length=5, allowed_chars='1234567890')
#         elif self.Position == self.User:
#             self.EmpNo = '2' + get_random_string(length=5, allowed_chars='1234567890')
#         super(EmpInfo, self).save(*args, **kwargs)
#
#     def __str__(self):
#         return str(self.EmpNo)
#
#     def was_published_recently(self):
#         return self.created_at >= timezone.now() - datetime.timedelta(days=1)
#     # 사원번호 랜덤 생성 / 앞의 1자리 권한번호 뒤의 랜덤 5자리  total 6자리
#     # 중복 적용 안함을 아직 구현하지 않음 ------해결 필요
#
#
#
# # 로그인 정보
# class LoginInfo(models.Model):
#     EmpNo = models.ForeignKey("EmpInfo", on_delete=models.CASCADE, db_column="EmpNo") #직원 번호
#     PassWord = models.CharField(max_length=8, editable=False) #비밀번호
#
#     # 비밀번호는 앞의 3자리는 영문 대소문자, 중간 3자리는 숫자, 뒤의 2자리는 해당 직원의 사원번호(EmpNo) 뒤의 2자리
#     # 비밀번호의 경우 중복은 상관 없음
#     def save(self, *args, **kwargs):
#         emp_no_str = str(self.EmpNo)
#         self.PassWord = get_random_string(length=3, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') + get_random_string(length=3, allowed_chars='1234567890') + emp_no_str[4:]
#         super(LoginInfo, self).save(*args, **kwargs)
#
#     def __str__(self):
#         return str(self.PassWord)
#
#     def was_published_recently(self):
#         return self.created_at >= timezone.now() - datetime.timedelta(days=1)
    
    # 회원가입을 api로 확인시 django의 auto id생성이 확인됨 id를 사용하지 않고 EmpNo를 사용하도록 수정 필요

# 발주 정보
class Order(models.Model):
    EmpNo = models.ForeignKey("User", on_delete=models.CASCADE, db_column="EmpNo") #직원 번호
    OrderNo = models.IntegerField(primary_key=True) #발주 번호
    OrderDate = models.DateTimeField(auto_now_add=True) #발주 일자
    OrderWeight = models.CharField(max_length=100) #발주 중량
    ETA = models.DateField() #입고 예정일
    Part = models.CharField(max_length=100) #부위
    Client = models.CharField(max_length=100) #업체
    OderPrice = models.IntegerField(default=0) #발주 금액
    
    def __str__(self):
        return str(self.OrderNo)

    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)
    
# 원료 정보
class Stock(models.Model):
    StockNo = models.IntegerField(primary_key=True) #입고 번호
    EmpNo = models.ForeignKey("User", on_delete=models.CASCADE, db_column="EmpNo") #직원 번호
    OrderNo = models.ForeignKey("Order", on_delete=models.CASCADE, db_column="OrderNo") #발주 번호
    StockDate = models.DateTimeField(auto_now_add=True) #입고 일
    RealWeight = models.IntegerField(default=0) #실중량
    MeterialNo = models.IntegerField(default=0) #이력 번호
    SlaugtherDate = models.DateField() #도축 일자
    UnitPrice = models.IntegerField(default=0) #단가
    SaleApply = models.BooleanField(default=False) #할인 적용 여부
    FinalPrice = models.IntegerField(default=0) #실제 구매 금액

    def __str__(self):
        return str(self.StockNo)

    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)
    
# 실제품, 2차가공
class Product(models.Model):
    ProductNo = models.IntegerField(primary_key=True) #제품 번호
    EmpNo = models.ForeignKey("User", on_delete=models.CASCADE, db_column="EmpNo")#직원 번호
    StockNo = models.ForeignKey("Stock", on_delete=models.CASCADE, db_column="StockNo")#입고 번호
    ProductDate = models.DateTimeField(auto_now_add=True) #제품 생산일
    AfterProduceWeight = models.IntegerField(default=0) #손질 후 중량
    RemainWeight = models.IntegerField(default=0) #잔여량
    ProduceAmount = models.IntegerField(default=0) #생산량(팩)
    SalePrice = models.IntegerField(default=0) #제품 가격
    
    def __str__(self):
        return str(self.ProductNo)
    
    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)
    
