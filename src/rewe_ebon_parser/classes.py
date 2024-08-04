# src/rewe_ebon_parser/classes.py
import math
from datetime import datetime
from typing import List, Optional
import pytz

class TaxCategory:
    """Represents different tax categories."""
    A = 'A'
    B = 'B'

class MarketAddress:
    """
    Represents a market address.

    Attributes:
        street (str): The street of the market.
        zip (str): The ZIP code of the market.
        city (str): The city where the market is located.
    """
    def __init__(self, street: str, zip: str, city: str):
        """
        Initializes a MarketAddress instance.

        Args:
            street (str): The street of the market.
            zip (str): The ZIP code of the market.
            city (str): The city where the market is located.
        """
        self.street = street
        self.zip = zip
        self.city = city
    
    def to_dict(self):
        """
        Converts the MarketAddress instance to a dictionary.

        Returns:
            dict: A dictionary representation of the MarketAddress instance.
        """
        return {
            'street': self.street,
            'zip': self.zip,
            'city': self.city
        }

class ReceiptItem:
    """
    Represents an item in a receipt.

    Attributes:
        tax_category (str): The tax category of the item.
        name (str): The name of the item.
        sub_total (float): The subtotal of the item.
        payback_qualified (bool): Whether the item qualifies for payback points.
        amount (float): The amount of the item.
        unit (Optional[str]): The unit of the item.
        price_per_unit (Optional[float]): The price per unit of the item.
    """
    def __init__(self, tax_category: str, name: str, sub_total: float, payback_qualified: bool, amount: float, unit: Optional[str] = None, price_per_unit: Optional[float] = None):
        self.tax_category = tax_category
        self.name = name
        self.sub_total = sub_total
        self.payback_qualified = payback_qualified
        self.amount = amount
        self.unit = unit
        self.price_per_unit = price_per_unit
    
    def to_dict(self):
        """
        Converts the ReceiptItem instance to a dictionary.

        Returns:
            dict: A dictionary representation of the ReceiptItem instance.
        """
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
    """
    Represents a payment in a receipt.

    Attributes:
        type (str): The type of payment.
        value (float): The value of the payment.
    """
    def __init__(self, type: str, value: float):
        self.type = type
        self.value = value
    
    def to_dict(self):
        """
        Converts the Payment instance to a dictionary.

        Returns:
            dict: A dictionary representation of the Payment instance.
        """
        return {
            'type': self.type,
            'value': self.value
        }

class TaxDetailsEntry:
    """
    Represents a tax details entry.

    Attributes:
        tax_percent (float): The tax percentage.
        net (float): The net amount.
        tax (float): The tax amount.
        gross (float): The gross amount.
    """
    def __init__(self, tax_percent: float, net: float, tax: float, gross: float):
        self.tax_percent = tax_percent
        self.net = net
        self.tax = tax
        self.gross = gross
    
    def to_dict(self):
        """
        Converts the TaxDetailsEntry instance to a dictionary.

        Returns:
            dict: A dictionary representation of the TaxDetailsEntry instance.
        """
        data = {
            'net': self.net,
            'tax': self.tax,
            'gross': self.gross
        }
        if not math.isnan(self.tax_percent):
            data['taxPercent'] = self.tax_percent
        return data

class TaxDetails:
    """
    Represents tax details for a receipt.

    Attributes:
        total (TaxDetailsEntry): The total tax details entry.
        A (Optional[TaxDetailsEntry]): The tax details entry for category A.
        B (Optional[TaxDetailsEntry]): The tax details entry for category B.
    """
    def __init__(self, total: TaxDetailsEntry, A: Optional[TaxDetailsEntry] = None, B: Optional[TaxDetailsEntry] = None):
        self.total = total
        self.A = A
        self.B = B
    
    def to_dict(self):
        """
        Converts the TaxDetails instance to a dictionary.

        Returns:
            dict: A dictionary representation of the TaxDetails instance.
        """
        data = {
            'total': self.total.to_dict()
        }
        if self.A is not None:
            data['A'] = self.A.to_dict()
        if self.B is not None:
            data['B'] = self.B.to_dict()
        return data

class PaybackCoupon:
    """
    Represents a payback coupon.

    Attributes:
        name (str): The name of the coupon.
        points (int): The points of the coupon.
    """
    def __init__(self, name: str, points: int):
        self.name = name
        self.points = points
    
    def to_dict(self):
        """
        Converts the PaybackCoupon instance to a dictionary.

        Returns:
            dict: A dictionary representation of the PaybackCoupon instance.
        """
        return {
            'name': self.name,
            'points': self.points
        }

class PaybackData:
    """
    Represents payback data for a receipt.

    Attributes:
        card (str): The payback card number.
        points_before (float): The points before the transaction.
        earned_points (int): The points earned in the transaction.
        used_coupons (List[PaybackCoupon]): The used payback coupons.
        used_rewe_credit (Optional[float]): The used REWE credit.
        new_rewe_credit (Optional[float]): The new REWE credit.
        payback_revenue (float): The payback revenue.
    """
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
        """
        Calculate the base points excluding coupon points.

        Returns:
            int: The base points.
        """
        return self.earned_points - self.coupon_points

    @property
    def coupon_points(self):
        """
        Calculate the total points from used coupons.

        Returns:
            int: The coupon points.
        """
        return sum(coupon.points for coupon in self.used_coupons)

    @property
    def qualified_revenue(self):
        """
        Get the qualified revenue for payback.

        Returns:
            float: The qualified revenue.
        """
        return self.payback_revenue
    
    def to_dict(self):
        """
        Converts the PaybackData instance to a dictionary.

        Returns:
            dict: A dictionary representation of the PaybackData instance.
        """
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
    """
    Represents a receipt.

    Attributes:
        date (datetime): The date of the receipt.
        market (str): The market of the receipt.
        market_address (Optional[MarketAddress]): The market address.
        cashier (str): The cashier of the receipt.
        checkout (str): The checkout number.
        vatin (str): The VAT identification number.
        items (List[ReceiptItem]): The items in the receipt.
        total (float): The total amount of the receipt.
        given (List[Payment]): The given payments.
        change (Optional[float]): The change returned.
        payout (Optional[float]): The payout amount.
        payback (Optional[PaybackData]): The payback data.
        tax_details (TaxDetails): The tax details.
    """
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
        """
        Converts the Receipt instance to a dictionary.

        Returns:
            dict: A dictionary representation of the Receipt instance.
        """
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
