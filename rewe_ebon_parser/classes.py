# classes.py
import math
from datetime import datetime
from typing import List, Optional
import pytz

class TaxCategory:
    A = 'A'
    B = 'B'

class MarketAddress:
    def __init__(self, street: str, zip: str, city: str):
        self.street = street
        self.zip = zip
        self.city = city
    
    def to_dict(self):
        return {
            'street': self.street,
            'zip': self.zip,
            'city': self.city
        }

class ReceiptItem:
    def __init__(self, tax_category: str, name: str, sub_total: float, payback_qualified: bool, amount: float, unit: Optional[str] = None, price_per_unit: Optional[float] = None):
        self.tax_category = tax_category
        self.name = name
        self.sub_total = sub_total
        self.payback_qualified = payback_qualified
        self.amount = amount
        self.unit = unit
        self.price_per_unit = price_per_unit
    
    def to_dict(self):
        data = {
            'taxCategory': self.tax_category,
            'name': self.name,
            'amount': self.amount,
            'subTotal': self.sub_total,
            'paybackQualified': self.payback_qualified
        }
        if self.unit is not None:
            data['unit'] = self.unit
        if self.price_per_unit is not None:
            data['pricePerUnit'] = self.price_per_unit
        return data

class Payment:
    def __init__(self, type: str, value: float):
        self.type = type
        self.value = value
    
    def to_dict(self):
        return {
            'type': self.type,
            'value': self.value
        }

class TaxDetailsEntry:
    def __init__(self, tax_percent: float, net: float, tax: float, gross: float):
        self.tax_percent = tax_percent
        self.net = net
        self.tax = tax
        self.gross = gross
    
    def to_dict(self):
        data = {
            'net': self.net,
            'tax': self.tax,
            'gross': self.gross
        }
        if not math.isnan(self.tax_percent):
            data['taxPercent'] = self.tax_percent
        return data

class TaxDetails:
    def __init__(self, total: TaxDetailsEntry, A: Optional[TaxDetailsEntry] = None, B: Optional[TaxDetailsEntry] = None):
        self.total = total
        self.A = A
        self.B = B
    
    def to_dict(self):
        data = {
            'total': self.total.to_dict()
        }
        if self.A is not None:
            data['A'] = self.A.to_dict()
        if self.B is not None:
            data['B'] = self.B.to_dict()
        return data

class PaybackCoupon:
    def __init__(self, name: str, points: int):
        self.name = name
        self.points = points
    
    def to_dict(self):
        return {
            'name': self.name,
            'points': self.points
        }

class PaybackData:
    def __init__(self, card: str, points_before: float, earned_points: int, used_coupons: List[PaybackCoupon], used_rewe_credit: Optional[float], new_rewe_credit: Optional[float], payback_revenue: float):
        self.card = card
        self.points_before = points_before
        self.earned_points = earned_points
        self.used_coupons = used_coupons
        self.used_rewe_credit = used_rewe_credit
        self.new_rewe_credit = new_rewe_credit
        self.payback_revenue = payback_revenue

    @property
    def base_points(self):
        return self.earned_points - self.coupon_points

    @property
    def coupon_points(self):
        return sum(coupon.points for coupon in self.used_coupons)

    @property
    def qualified_revenue(self):
        return self.payback_revenue
    
    def to_dict(self):
        data = {
            'card': self.card,
            'pointsBefore': self.points_before,
            'earnedPoints': self.earned_points,
            'basePoints': self.base_points,
            'couponPoints': self.coupon_points,
            'qualifiedRevenue': self.qualified_revenue,
            'usedCoupons': [coupon.to_dict() for coupon in self.used_coupons]
        }
        if self.used_rewe_credit is not None:
            data['usedREWECredit'] = self.used_rewe_credit
        if self.new_rewe_credit is not None:
            data['newREWECredit'] = self.new_rewe_credit
        return data

class Receipt:
    def __init__(self, date: datetime, market: str, market_address: Optional[MarketAddress], cashier: str, checkout: str, vatin: str, items: List[ReceiptItem], total: float, given: List[Payment], change: Optional[float], payout: Optional[float], payback: Optional[PaybackData], tax_details: TaxDetails):
        self.date = date
        self.market = market
        self.market_address = market_address
        self.cashier = cashier
        self.checkout = checkout
        self.vatin = vatin
        self.items = items
        self.total = total
        self.given = given
        self.change = change
        self.payout = payout
        self.payback = payback
        self.tax_details = tax_details
    
    def to_dict(self):
        data = {
            'datetime_local': self.date.isoformat(timespec='seconds'),
            'datetime_utc': self.date.astimezone(pytz.utc).isoformat(),
            'market': self.market,
            'marketAddress': self.market_address.to_dict() if self.market_address else None,
            'cashier': self.cashier,
            'checkout': self.checkout,
            'vatin': self.vatin,
            'items': [item.to_dict() for item in self.items],
            'total': self.total,
            'given': [payment.to_dict() for payment in self.given],
            'taxDetails': self.tax_details.to_dict()
        }
        if self.change is not None:
            data['change'] = self.change
        if self.payback is not None:
            data['payback'] = self.payback.to_dict()
        if self.payout is not None:
            data['payout'] = self.payout
        return data
