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

# from django.utils.translation import ugettext_lazy as _
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
        # user.is_staff = True  # 최상위 사용자가 staff 상태를 가지도록 설정
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    empNo = models.CharField(
        verbose_name=('Employee Number'),
        max_length=10,
        unique=True
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

    objects = UserManager()

    # id로 사용할 필드
    USERNAME_FIELD = 'empNo'
    # 필수 입력 필드
    REQUIRED_FIELDS = [
        'username',
        'Job'
        # ,'Position'
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
            prefix = '1' + get_random_string(length=5, allowed_chars='1234567890')
        elif self.Position == self.User:
            prefix = '2' + get_random_string(length=5, allowed_chars='1234567890')
        return prefix

    def generate_password(self):
        emp_no_str = str(self.empNo)
        if emp_no_str == 'Admin':
            random_part = '1234'
        else:
            random_part = get_random_string(length=3,
                                            allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') + get_random_string(
                length=3, allowed_chars='1234567890') + emp_no_str[4:]
        logger.debug(random_part)
        return random_part

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All superusers are staff
        return self.is_superuser


# 부위
class MeatPart(models.Model):
    name = models.CharField(verbose_name='Part name', max_length=100, unique=True)  # 부위 이름
    code = models.CharField(verbose_name='Part code', max_length=5, unique=True, blank=True)  # 부위 고유 번호

    def save(self, *args, **kwargs):
        if not self.code:
            max_code = MeatPart.objects.aggregate(models.Max('code'))['code__max']
            if max_code is None:  # 만약 데이터베이스에 아무 데이터도 없다면
                max_code = 100
                self.code = max_code
            else:
                self.code = str(int(max_code) + 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# 원료/발주
class Order(models.Model):
    ID = models.AutoField(primary_key=True)  # 번호
    OrderDate = models.DateField(auto_now=True)  # 발주 일시
    # 발주자명(로그인한 계정명으로 가져올것, 기획서 ui에는 없는데 요구사항에는 있어서 넣음) -> 이성재 변경 사항: 이름으로 가져올 시에 중복 문제가 발생할 수 있기에 사번으로 저장
    OrderWorker = models.ForeignKey(User,to_field='empNo',on_delete=models.CASCADE, db_column="OrderWorker")
    ETA = models.DateField()  # 입고 예정일
    Client = models.ForeignKey("Client", to_field='ClientName',on_delete=models.CASCADE, db_column="Client")  # 거래처
    OrderWeight = models.IntegerField()  # 발주 중량(KG)
    Part = models.ForeignKey("MeatPart",to_field='code', on_delete=models.CASCADE, db_column="Part")  # 부위
    OrderPrice = models.IntegerField(default=0)  # 발주 금액(발주 시 예삭 매입 금액)
    OrderNo = models.CharField(max_length=100, blank=True, unique=True)  # 발주 번호
    OrderSituation = models.CharField(max_length=10)  # 상태
    addDateTime = models.DateTimeField(auto_now=True, null=False)
    
    #발주번호는 발주가 등록되면 생성되면 발주번호 생성 규칙은 발주한 년/월/일/요일/부위 고유번호/ 발주업체 고유번호/ 당일 발주 순번 으로 한다. 
    #(y4/m2/d2/w1/p4/c4/0001)
    def save(self, *args, **kwargs):
        if not self.OrderNo:  # 발주번호가 없을 경우 자동 생성
            # 년/월/일/요일
            today = datetime.datetime.today()
            year = today.strftime('%Y')
            month = today.strftime('%m')
            day = today.strftime('%d')
            day_of_week = today.strftime('%w')  # 0(일)~6(토)
            # 부위 고유번호
            part_number = str(self.Part.code).zfill(4)
            # 발주업체 고유번호
            client_number = str(self.Client.ID).zfill(4)
            # 당일 발주 순번
            try:
                order_count = Order.objects.filter(OrderDate__year=year, OrderDate__month=today.month, OrderDate__day=today.day).count() + 1
            except Exception as e:
                order_count = 1

        #if self.instance is not None:
        #     self.instance = self.update(self.instance, validated_data= request.data)
        #     assert self.instance is not None, (
        #         '`update()` did not return an object instance.'
        #     )
        #else:
        #     self.instance = self.create(validated_data= request.data)
        #     assert self.instance is not None, (
        #         '`create()` did not return an object instance.'
        #     )
        #     return self.instance

            # 발주번호 생성
            self.OrderNo = f"{year}{month}{day}{day_of_week}{part_number}{client_number}{order_count:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.OrderNo)

    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)

    class Meta:
        ordering = ['-addDateTime']

    @classmethod
    def reset_order_count(cls):
        today = datetime.datetime.today()
        # 발주가 들어온 날짜가 오늘이 아닌 경우 발주번호 초기화
        if cls.objects.filter(OrderDate__year=today.year, OrderDate__month=today.month, OrderDate__day=today.day).count() == 0:
            cls.objects.all().update(OrderNo=None)


# 원료/입고
class Stock(models.Model):
    ID = models.AutoField(primary_key=True)  # 번호
    OrderNo = models.ForeignKey("Order", to_field='OrderNo', on_delete=models.CASCADE, db_column="OrderNo", unique=True)  # 발주 번호 (외래키, 이걸로 발주일시, 입고 예정일 등등 가져올것)
    StockDate = models.DateField() # 입고 일시
    StockWorker = models.ForeignKey(User,to_field='empNo',on_delete=models.CASCADE, db_column="StockWorker")  # 입고자명(로그인한 계정명으로 가져올것)
    Stockitem = models.CharField(max_length=100)  # 입고 품목
    RealWeight = models.IntegerField(default=0)  # 실 중량
    RealPrice = models.IntegerField(default=0)  # 실 매입가
    MeterialNo = models.IntegerField(default=0)  # 이력 번호
    SlaugtherDate = models.DateField()  # 도축일
    UnitPrice = models.IntegerField(default=0)  # 입고단가(1KG당 가격)
    StockNo = models.CharField(max_length=100, blank=True, unique=True)  # 입고 번호
    StockSituation = models.CharField(max_length=100)  # 상태
    
    def save(self, *args, **kwargs):
        if not self.StockNo:
            try:
                order_date = Order.objects.get(OrderNo=self.OrderNo).OrderDate
                
                if isinstance(order_date, datetime.datetime):
                    order_date = order_date.date()
            
                stock_date = self.StockDate
                diff = stock_date - order_date # 날짜 차이 계산
                
                self.StockNo = str(self.OrderNo) + str(diff.days).zfill(4)
            
            except Order.DoesNotExist:
                raise ValueError("참조된 발주번호가 존재하지 않습니다. 발주번호를 확인해주세요.")
        super().save(*args, **kwargs)
        
    def __str__(self):
        return str(self.StockNo)

    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)


# 원료/2차 가공
class Product(models.Model):
    ID = models.AutoField(primary_key=True)  # 번호
    StockNo = models.ForeignKey("Stock",to_field='StockNo', on_delete=models.CASCADE, db_column="StockNo")  # 입고 번호 (외래키, 이걸로 입고일시, 입고자명 등등 가져올것)
    ProductDate = models.DateTimeField(auto_now=True)  # 작업일(요일)
    ProductWorker = models.ForeignKey(User,to_field='empNo',on_delete=models.CASCADE, db_column="ProductWorker")  # 작업자명(로그인한 계정명으로 가져올것)
    WeightAfterWork = models.IntegerField(default=0)  # 작업 후 중량(KG)
    LossWeight = models.IntegerField(default=0)  # 로스((실중량 - 작업 후 중량)/실중량 = 로스율) #프론트에서 계산 할 수도 있음
    ProductPrice = models.IntegerField(default=0)  # 단가(작업 후 중량 기준으로 1000g/1kg당 가격)
    DiscountRate = models.IntegerField(default=0)  # 할인율(%)
    ProductNo = models.CharField(max_length=100, blank=True, unique=True)  # 제품 번호
    ProductSituation = models.CharField(max_length=100)  # 상태
    Quantity = models.IntegerField(default=0)  # 수량(제품 수량, 제품 상세에 있어서 만듬)
    PurchaseNo = models.ForeignKey("Purchase", to_field='PurchaseNo', on_delete=models.SET_NULL,null=True, db_column="PurchaseNo", blank=True)
    def __str__(self):
        return str(self.ProductNo)
    
    # 제품 번호 = 입고번호 + 카운트 1씩 증가
    def save(self, *args, **kwargs):
        if not self.ProductNo:  # 제품 번호가 비어 있는 경우에만 새로운 번호 생성
            last_product = Product.objects.filter(StockNo=self.StockNo).order_by('-ProductNo').first()
            if last_product:
                last_number = int(last_product.ProductNo[-4:])
                new_number = str(last_number + 1).zfill(4) # 4자리 숫자로 변환
            else:
                new_number = "0001"
            self.ProductNo = f"{self.StockNo}{new_number}"
        super().save(*args, **kwargs)
        
    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)
    class Meta:
        ordering = ['-ProductDate']

# 제품/재고 현황
# class InventoryStatus(models.Model):
# 보류 굳이 안 팔요할듯 함


# 주문/주문 등록(order와 겹쳐서 purchase로 설정함)
class Purchase(models.Model):
    ID = models.AutoField(primary_key=True)  # 번호
    PurchaseDate = models.DateTimeField(auto_now_add=True)  # 등록일(요일)
    PurchaseStep = models.CharField(max_length=10)  # 구분
    Purchaser = models.CharField(max_length=100)  # 주문자
    PurchaseAddress = models.CharField(max_length=100)  # 주소
    PurchaseAddressDetail = models.CharField(max_length=100)  # 상세 주소
    PurchasePhone = models.CharField(max_length=15)  # 연락처
    PurchaseNo = models.CharField(max_length=10, blank=True, unique=True)  # 주문 번호
    Wrapping = models.BooleanField(max_length=10)  # 선물포장 여부
    PurchaserName = models.CharField(max_length=100, blank=True, null=True) # 제품명
    PurchaserPrice = models.CharField(max_length=100, blank=True, null=True) # 가격


    def __str__(self):
        return str(self.PurchaseNo)

    def save(self, *args, **kwargs):
        if not self.PurchaseNo:
            last_purchase = Purchase.objects.order_by('-ID').first()
            if last_purchase and last_purchase.PurchaseNo.isdigit():
                next_number = str(int(last_purchase.PurchaseNo) + 1).zfill(5)
            else:
                next_number = '00001'
            self.PurchaseNo = next_number
        super(Purchase, self).save(*args, **kwargs)

# 주문/작업지시서
# class WorkOrder(models.Model):
# 보류 굳이 안 팔요할듯 함


# 주문/배송사고
class DeliveryAccident(models.Model):
    WaybillNo = models.CharField(max_length=100, primary_key=True)  # 운송장 번호
    Recipient = models.CharField(max_length=100)  # 받는 분
    TotalFreight = models.IntegerField(default=0)  # 총 운임
    ProductValue = models.IntegerField(default=0)  # 상품 가액
    Reimbursement = models.IntegerField(default=0)  # 변상요청금액
    PurchaseDate = models.ForeignKey("Purchase", on_delete=models.CASCADE, db_column="PurchaseDate")  # 등록 일자
    ShippingDate = models.DateField()  # 발송일자

    def __str__(self):
        return str(self.WaybillNo)

    # def auto_generate_waybill_no(self):
    #     return self.WaybillNo 운송장번호 자동 생성_프라이머리키로 설정했기 때문에 오류를 우려하여 나중에 추가할 예정
    #     - 성재:운송장은 우체국에서 던져주는 거라 필요할 지? https://blog.naver.com/okuk81/221516678226 이런 api로 송장번호 생성하는 듯

    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)


# 주문/ 매입,매출
# 살짝 에매함 원료 테이블 쪽에서 가져오려면 다 가져올 수 있긴 함. 각 단품을 합산하면 결과적으로 월 매입,매출이 나올 수 있음
class InOutCome(models.Model):
    ID = models.AutoField(primary_key=True)  # 번호
    Part = models.ForeignKey("Order", on_delete=models.CASCADE, db_column="Part")  # 부위(외래키, 이걸로 발주번호, 발주일시, 입고 예정일 등등 가져올것)
    IncomePrice = models.IntegerField(default=0)  # 매입가
    OutcomePrice = models.IntegerField(default=0)  # 매출가
    IncomeAmount = models.IntegerField(default=0)  # 매입량
    OutcomeAmount = models.IntegerField(default=0)  # 매출량
    IncomeDate = models.DateField()  # 매입일시/월별
    OutcomeDate = models.DateField()  # 매출일시/월별
    Gifts = models.IntegerField(default=0)  # 사은품

    def __str__(self):
        return str(self.InOutComeNo)

    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)


# 기타/거래처 정보
class Client(models.Model):
    ID = models.AutoField(primary_key=True)  # 번호
    ClientType = models.CharField(max_length=100)  # 거래처 유형(매입, 매출 두가지)
    ClientName = models.CharField(max_length=100, unique=True)  # 거래처 이름 (기획서에는 없는데 필요할거 같아서 넣음)
    RepresentativeName = models.CharField(max_length=100)  # 대표자 명
    BusinessRegistrationNumber = models.CharField(max_length=100)  # 사업자 등록번호
    ClientAddress = models.CharField(max_length=100)  # 사업장 주소
    ClientPhone = models.CharField(max_length=100)  # 사업장 연락처
    PersonInCharge = models.CharField(max_length=100)  # 담당자(직급) 이름
    PersonInChargePhone = models.CharField(max_length=100)  # 담당자 연락처
    FirstTradeDate = models.DateField()  # 최초 거래일
    LastTradeDate = models.DateField()  # 최종 거래일
    Payment_Delivery = models.CharField(max_length=100)  # 납입/납품

    def __str__(self):
        return str(self.ClientName)

    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)


# 기타/기타비용
class OtherCost(models.Model):
    ID = models.AutoField(primary_key=True)  # 번호
    Category = models.CharField(max_length=100)  # 유형
    SubsidiaryMaterial = models.CharField(max_length=100)  # 부자재 명
    Quntity = models.IntegerField(default=0)  # 수량
    Price = models.IntegerField(default=0)  # 단가
    TotalPrice = models.IntegerField(default=0)  # 금액
    Client = models.ForeignKey("Client", to_field='ClientName',on_delete=models.CASCADE, db_column="Client")  # 거래처
    CostSituation = models.CharField(max_length=100)  # 상태

    def __str__(self):
        return str(self.SubsidiaryMaterial)

    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)


# 기타/지육, 제품 추가 이건 성재랑 상의좀 하자
