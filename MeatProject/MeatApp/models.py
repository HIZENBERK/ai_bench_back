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
        주어진 비밀번호 등 개인정보로 User 인스턴스 생성
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




# 원료/발주
class Order(models.Model):
    OrderDate = models.DateTimeField(auto_now_add=True) #발주 일시
    OrderWorker = models.ForeignKey("User", on_delete=models.CASCADE, db_column="username") #발주자명(로그인한 계정명으로 가져올것, 기획서 ui에는 없는데 요구사항에는 있어서 넣음)
    ETA = models.DateField() #입고 예정일
    Client = models.ForeignKey("Client", on_delete=models.CASCADE, db_column="ClientName") #거래처
    OrderWeight = models.IntegerField(max_length=100)#발주 중량(KG)
    Part = models.CharField(max_length=100) #부위
    OderPrice = models.IntegerField(default=0) #발주 금액(발주 시 예삭 매입 금액)
    OrderNo = models.IntegerField(primary_key=True) #발주 번호
    OrderSituation = models.CharField(max_length=100) #상태
    OrderFix = models.BooleanField(default=False) #수정 여부(아마 o/x로 표시할듯, 아니면 수정 버튼이 되거나 일단 o/x로 했음)
    
    
    def __str__(self):
        return str(self.OrderNo)
    
    #def auto_generate_order_no(self):
    #    return self.OrderNo 발주번호 자동 생성_프라이머리키로 설정했기 때문에 오류를 우려하여 나중에 추가할 예정

    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)




# 원료/입고
class Stock(models.Model):
    OrderNo = models.ForeignKey("Order", on_delete=models.CASCADE, db_column="OrderNo") #발주 번호 (외래키, 이걸로 발주일시, 입고 예정일 등등 가져올것)
    StockDate = models.DateTimeField(auto_now_add=True) #입고 일시
    StockWorker = models.ForeignKey("User", on_delete=models.CASCADE, db_column="username") #입고자명(로그인한 계정명으로 가져올것)
    Stockitem = models.CharField(max_length=100) #입고 품목
    RealWeight = models.IntegerField(default=0) #실 중량
    RealPrice = models.IntegerField(default=0) #실 매입가
    MeterialNo = models.IntegerField(default=0) #이력 번호
    SlaugtherDate = models.DateField() #도축일
    UnitPrice = models.IntegerField(default=0) #입고단가(1KG당 가격)
    StockNo = models.IntegerField(primary_key=True) #입고 번호
    StockSituation = models.CharField(max_length=100) #상태
    StockFix = models.BooleanField(default=False) #수정 여부 (아마 o/x로 표시할듯, 아니면 수정 버튼이 되거나 일단 o/x로 했음)
    

    def __str__(self):
        return str(self.StockNo)
    
    # def auto_generate_stock_no(self):
    #     return self.StockNo 입고번호 자동 생성_프라이머리키로 설정했기 때문에 오류를 우려하여 나중에 추가할 예정

    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)




# 원료/2차 가공
class Product(models.Model):
    OrderNo = models.ForeignKey("Order", on_delete=models.CASCADE, db_column="OrderNo") #발주 번호 (외래키, 이걸로 발주일시, 입고 예정일 등등 가져올것)
    StockNo = models.ForeignKey("Stock", on_delete=models.CASCADE, db_column="StockNo") #입고 번호 (외래키, 이걸로 입고일시, 입고자명 등등 가져올것)
    ProductDate = models.DateTimeField(auto_now_add=True) #작업일(요일)
    ProductWorker = models.ForeignKey("User", on_delete=models.CASCADE, db_column="username") #작업자명(로그인한 계정명으로 가져올것)
    WeightAfterWork = models.IntegerField(default=0) #작업 후 중량(KG)
    LossWeight = models.IntegerField(default=0) #로스((실중량 - 작업 후 중량)/실중량 = 로스율)
    ProductPrice = models.IntegerField(default=0) #단가(작업 후 중량 기준으로 1000g/1kg당 가격)
    DiscountRate = models.IntegerField(default=0) #할인율(%)
    ProductNo = models.IntegerField(max_length=100, primary_key=True) #제품 번호
    ProductSituation = models.CharField(max_length=100) #상태
    ProductFix = models.BooleanField(default=False) #수정 여부 (아마 o/x로 표시할듯, 아니면 수정 버튼이 되거나 일단 o/x로 했음)
    Quantity = models.IntegerField(default=0) #수량(제품 수량, 제품 상세에 있어서 만듬)
    
    
    def __str__(self):
        return str(self.ProductNo)
    
    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)




# 제품/재고 현황
# class InventoryStatus(models.Model): 
# 보류

    

# 주문/주문 등록(order와 겹쳐서 purchase로 설정함)
class Purchase(models.Model):
    ProductNo = models.ForeignKey("Product", on_delete=models.CASCADE, db_column="ProductNo") #제품 번호 (외래키, 이걸로 제품명, 가격 등등 가져올것)
    PurchaseDate = models.DateTimeField(auto_now_add=True) #등록일(요일)
    # 구분이 뭔지 모르겠음
    Purchaser = models.ForeignKey("User", on_delete=models.CASCADE, db_column="username") #주문자(로그인한 계정명으로 가져올것)
    PurchaseAddress = models.CharField(max_length=100) #주소
    PurchasePhone = models.CharField(max_length=100) #연락처
    PurchaseNo = models.IntegerField(primary_key=True) #주문 번호
    Wrapping = models.BooleanField(default=False) #선물포장 여부
    # 수정/삭제의 경우 버튼으로 보여 따로 생성 안함
    
    
    def __str__(self):
        return str(self.PurchaseNo)
    
    # def auto_generate_purchase_no(self):
    #     return self.PurchaseNo 주문번호 자동 생성_프라이머리키로 설정했기 때문에 오류를 우려하여 나중에 추가할 예정

    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)



# 주문/작업지시서
# class WorkOrder(models.Model):
# 보류
    


# 주문/배송사고
class DeliveryAccident(models.Model):
    WaybillNo = models.CharField(max_length=100, primary_key=True) #운송장 번호
    Recipient = models.CharField(max_length=100) #받는 분
    TotalFreight = models.IntegerField(default=0) #총 운임
    ProductValue = models.IntegerField(default=0) #상품 가액
    Reimbursement = models.IntegerField(default=0) #변상요청금액
    #등록일자를 뭐로 할지 모르겠음. 배송사고 발생일자로 할지, 상품 등록일자로 할지
    ShippingDate = models.DateField() #발송일자
    
    
    
    
    def __str__(self):
        return str(self.WaybillNo)
    
    # def auto_generate_waybill_no(self):
    #     return self.WaybillNo 운송장번호 자동 생성_프라이머리키로 설정했기 때문에 오류를 우려하여 나중에 추가할 예정

    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)


# 기타/거래처 정보
class Client(models.Model):
    ClientType = models.CharField(max_length=100) #거래처 유형(매입, 매출 두가지)
    ClientName = models.CharField(max_length=100, primary_key=True) #거래처 이름 (기획서에는 없는데 필요할거 같아서 넣음)
    RepresentativeName = models.CharField(max_length=100) #대표자 명
    BusinessRegistrationNumber = models.CharField(max_length=100) #사업자 등록번호
    ClientAddress = models.CharField(max_length=100) #사업장 주소
    ClientPhone = models.CharField(max_length=100) #사업장 연락처
    PersonInCharge = models.CharField(max_length=100) #담당자(직급) 이름
    PersonInChargePhone = models.CharField(max_length=100) #담당자 연락처
    FirstTradeDate = models.DateField() #최초 거래일
    LastTradeDate = models.DateField() #최종 거래일
    Payment_Delivery = models.CharField(max_length=100) #납입/납품
    
    
    def __str__(self):
        return str(self.ClientName)
    
    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)