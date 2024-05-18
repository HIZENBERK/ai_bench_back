from typing import Any, Iterable
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
import datetime


# 회원정보
class EmpInfo(models.Model):
    EmpNo = models.CharField(max_length=6, primary_key=True, editable=False) #직원 번호
    EmpName = models.CharField(max_length=20) #직원 이름
    
    OrderManager = 'OM'
    DissectionManager = 'DM'
    WarehouseManger = 'WM'
    Admin = 'A'
    Manager = 'M'
    User = 'U'
    
    JobList = [ #직무
        (OrderManager, '주문담당자'),
        (DissectionManager, '해체담당자'),
        (WarehouseManger, '입고담당자'),
    ]
    Job = models.CharField(max_length=100, choices=JobList, default=OrderManager)  #직무
    
    PositionList = [ #직위
        (Admin, '관리자'),
        (Manager, '매니저'),
        (User, '사용자'),
    ]
    Position = models.CharField(max_length=100, choices=PositionList, default=User) #직위
    
    # 사원번호 랜덤 생성 / 앞의 1자리 권한번호 뒤의 랜덤 5자리  total 6자리
    # 중복 적용 안함을 아직 구현하지 않음 ------해결 필요
    
    def save(self, *args, **kwargs):
        if self.Position == self.Admin:
            self.EmpNo = '0' + get_random_string(length=5, allowed_chars='1234567890')
        elif self.Position == self.Manager:
            self.EmpNo = '1' + get_random_string(length=5, allowed_chars='1234567890')
        elif self.Position == self.User:
            self.EmpNo = '2' + get_random_string(length=5, allowed_chars='1234567890')
        super(EmpInfo, self).save(*args, **kwargs)
    
    def is_jobselect(self):
        return self.Position in {self.OrderManager, self.DissectionManager, self.WarehouseManger}
    
    def is_positionselect(self):
        return self.Position in {self.Admin, self.Manager, self.User}
    
    def __str__(self):
        return str(self.EmpNo)

    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)

# 로그인 정보
class LoginInfo(models.Model):
    EmpNo = models.ForeignKey("EmpInfo", on_delete=models.CASCADE, db_column="EmpNo") #직원 번호
    PassWord = models.CharField(max_length=8, editable=False) #비밀번호
    
    # 비밀번호는 앞의 3자리는 영문 대소문자, 중간 3자리는 숫자, 뒤의 2자리는 해당 직원의 사원번호(EmpNo) 뒤의 2자리
    # 비밀번호의 경우 중복은 상관 없음
    def save(self, *args, **kwargs):
        emp_no_str = str(self.EmpNo)
        self.PassWord = get_random_string(length=3, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') + get_random_string(length=3, allowed_chars='1234567890') + emp_no_str[4:]
        super(LoginInfo, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.PassWord)
    
    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)
    
    # 회원가입을 api로 확인시 django의 auto id생성이 확인됨 id를 사용하지 않고 EmpNo를 사용하도록 수정 필요

# 발주 정보
class Order(models.Model):
    EmpNo = models.ForeignKey("EmpInfo", on_delete=models.CASCADE, db_column="EmpNo") #직원 번호
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
    EmpNo = models.ForeignKey("EmpInfo", on_delete=models.CASCADE, db_column="EmpNo") #직원 번호
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
    EmpNo = models.ForeignKey("EmpInfo", on_delete=models.CASCADE, db_column="EmpNo")#직원 번호
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
    
