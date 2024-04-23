from typing import Iterable
from django.db import models
from django.utils import timezone
import datetime

#----------------intigerfield의 경우 primary_key가 없을시 제대로 출력되지 않음 수정해야함!----------------
#----------------단, char의 경우 정상 출력되긴 함----------------

# 회원정보
class EmpInfo(models.Model):
    EmpNo = models.IntegerField(primary_key=True) #직원 번호
    EmpName = models.CharField(max_length=100) #직원 이름
    
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
    Job = models.CharField(max_length=100, choices=JobList, default=OrderManager)  # 직무
    
    PositionList = [ #직위
        (Admin, '관리자'),
        (Manager, '매니저'),
        (User, '사용자'),
    ]
    Position = models.CharField(max_length=100, choices=PositionList, default=User) # 직위
    
    
    
    def is_jobselect(self):
        return self.Position in {self.OrderManager, self.DissectionManager, self.WarehouseManger}
    
    def is_positionselect(self):
        return self.Position in {self.Admin, self.Manager, self.User} 
    
    def __str__(self):
        return self.EmpNo

    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)

# 로그인 정보
class LoginInfo(models.Model):
    EmpNo = models.ForeignKey("EmpInfo", on_delete=models.CASCADE, db_column="EmpNo")#직원 번호
    PassWord = models.CharField(max_length=100) #비밀번호

    def __str__(self):
        return self.EmpNo

    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)

# 발주 정보
class Order(models.Model):
    EmpNo = models.ForeignKey("EmpInfo", on_delete=models.CASCADE, db_column="EmpNo")#직원 번호
    OrderNo = models.IntegerField(primary_key=True) #발주 번호
    OrderDate = models.DateTimeField(auto_now_add=True) #발주 일자
    OrderWeight = models.CharField(max_length=100) #발주 중량
    ETA = models.DateField() #입고 예정일
    Part = models.CharField(max_length=100) #부위
    Client = models.CharField(max_length=100) #업체
    OderPrice = models.IntegerField(default=0) #발주 금액

    def __str__(self):
        return self.OrderNo

    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)
    

# 원료 정보    
class Stock(models.Model):
    StockNo = models.IntegerField(primary_key=True) #입고 번호
    EmpNo = models.ForeignKey("EmpInfo", on_delete=models.CASCADE, db_column="EmpNo")#직원 번호
    OrderNo = models.ForeignKey("Order", on_delete=models.CASCADE, db_column="OrderNo")#발주 번호
    StockDate = models.DateTimeField(auto_now_add=True) #입고 일
    RealWeight = models.IntegerField(default=0) #실중량
    MeterialNo = models.IntegerField(default=0) #이력 번호
    SlaugtherDate = models.DateField() #도축 일자
    UnitPrice = models.IntegerField(default=0) #단가
    SaleApply = models.BooleanField(default=False) #할인 적용 여부
    FinalPrice = models.IntegerField(default=0) #실제 구매 금액

    def __str__(self):
        return self.StockNo

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