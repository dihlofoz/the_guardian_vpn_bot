from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Float, Boolean, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, nullable=False, unique=True)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ref_code = Column(String, unique=True, nullable=True)
    referred_by = Column(String, nullable=True)
    active_discount_code = Column(String, nullable=True)
    active_discount_value = Column(Integer, nullable=True)
    bonus_days_balance = Column(Integer, default=0)
    rp_days_balance = Column(Integer, default=0)   # накопленные дни
    rp_gb_balance = Column(Float, default=0.0)    # накопленные GB
    rp_days_limit = Column(Integer, default=30)   # максимум дней
    rp_gb_limit = Column(Float, default=45.0)
    devices_included = Column(Integer, default=2)  # базовое количество
    devices_extra = Column(Integer, default=0) # докупленные устройства

    # 🔹 Обратные связи
    trial_subscriptions = relationship(
        "TrialSubscription",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    referrals = relationship(
        "Referral",
        back_populates="referrer",
        foreign_keys="[Referral.referrer_id]",
        cascade="all, delete-orphan"
    )
    referred = relationship(
        "Referral",
        back_populates="referred_user",
        foreign_keys="[Referral.referred_id]",
        cascade="all, delete-orphan"
    )
    subscriptions = relationship(
        "Subscriptions",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    

class TrialSubscription(Base):
    __tablename__ = "trial_subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    activated_at = Column(DateTime(timezone=True), nullable=False)
    trial_reminder_sent = Column(Boolean, default=False)

    user = relationship(
        "User",
        back_populates="trial_subscriptions"
    )


class Subscriptions(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, ForeignKey("users.tg_id", ondelete="CASCADE"), nullable=False)

    # --- BASE VPN ---
    base_plan_name = Column(String, nullable=True)
    base_amount = Column(Float, nullable=True)
    base_start_date = Column(DateTime(timezone=True), nullable=True)
    base_expire_date = Column(DateTime(timezone=True), nullable=True)
    base_active = Column(Boolean, default=False)

    # --- BYPASS / WHITELIST ---
    bypass_plan_name = Column(String, nullable=True)
    bypass_amount = Column(Float, nullable=True)
    bypass_start_date = Column(DateTime(timezone=True), nullable=True)
    bypass_expire_date = Column(DateTime(timezone=True), nullable=True)
    bypass_active = Column(Boolean, default=False)

    # --- MULTI ---
    multi_plan_name = Column(String, nullable=True)
    multi_amount = Column(Float, nullable=True)
    multi_start_date = Column(DateTime(timezone=True), nullable=True)
    multi_expire_date = Column(DateTime(timezone=True), nullable=True)
    multi_active = Column(Boolean, default=False)

    user = relationship("User", back_populates="subscriptions")

class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    referrer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    referred_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    referrer = relationship(
        "User",
        foreign_keys=[referrer_id],
        back_populates="referrals"
    )
    referred_user = relationship(
        "User",
        foreign_keys=[referred_id],
        back_populates="referred"
    )


class PromoDiscount(Base):
    __tablename__ = "promo_discount_codes"

    id = Column(Integer, primary_key=True)
    promo_code = Column(String, unique=True, nullable=False)
    discount_percent = Column(Integer, nullable=False)   # процент скидки
    max_uses = Column(Integer, nullable=False)
    active_uses = Column(Integer, default=0)


class PromoBonusDays(Base):
    __tablename__ = "promo_bonus_codes"

    id = Column(Integer, primary_key=True)
    promo_code = Column(String, unique=True, nullable=False)
    bonus_days = Column(Integer, nullable=False)         # сколько бонусных дней даёт
    max_uses = Column(Integer, nullable=False)
    active_uses = Column(Integer, default=0)

class PromoUse(Base):
    __tablename__ = "promo_uses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    promo_id = Column(Integer, nullable=False)  # В твоих промо-таблицах есть id
    used_at = Column(DateTime, default=datetime.utcnow)

class ExpiredSubscriptionNotification(Base):
    __tablename__ = "expired_subscription_notifications"

    telegram_id = Column(BigInteger, primary_key=True)

    notified_trial = Column(Boolean, default=False)
    notified_paid = Column(Boolean, default=False)
    notified_special = Column(Boolean, default=False)


class NotificationMeta(Base):
    __tablename__ = "notification_meta"

    id = Column(Integer, primary_key=True)
    last_reset_at = Column(DateTime, nullable=False)
