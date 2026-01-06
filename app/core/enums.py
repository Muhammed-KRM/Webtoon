"""
Application Enums
"""
from enum import IntEnum, Enum


class TranslateType(IntEnum):
    """Translation type enumeration"""
    AI = 1  # OpenAI GPT-4o-mini (paid, high quality)
    FREE = 2  # Free translation (Google Translate/DeepL free tier)


class TranslationMode(IntEnum):
    """Translation processing mode"""
    CLEAN = 1  # Clean mode: remove original text and replace
    OVERLAY = 2  # Overlay mode: add translation on top


class JobStatus(IntEnum):
    """Translation job status"""
    PENDING = 1
    PROCESSING = 2
    COMPLETED = 3
    FAILED = 4


class SeriesStatus(str, Enum):
    """Series publication status"""
    ONGOING = "ongoing"
    COMPLETED = "completed"
    HIATUS = "hiatus"


class TranslationStatus(str, Enum):
    """Chapter translation status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PlanType(str, Enum):
    """Subscription plan type"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"


class PaymentStatus(str, Enum):
    """Payment status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class ReactionType(str, Enum):
    """Reaction type"""
    EMOJI = "emoji"
    GIF = "gif"
    MEMOJI = "memoji"


class NotificationType(str, Enum):
    """Notification type"""
    TRANSLATION_COMPLETED = "translation_completed"
    NEW_CHAPTER = "new_chapter"
    COMMENT_REPLY = "comment_reply"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    SUBSCRIPTION_EXPIRED = "subscription_expired"


class ProperNounType(str, Enum):
    """Proper noun detection type"""
    AUTO = "auto"  # Automatically detected
    YES = "yes"  # Manually confirmed as proper noun
    NO = "no"  # Manually marked as not proper noun


class UserRole(str, Enum):
    """User role"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    PREMIUM = "premium"


class Theme(str, Enum):
    """UI theme"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class Quality(str, Enum):
    """Translation quality"""
    HIGH = "high"
    FAST = "fast"

