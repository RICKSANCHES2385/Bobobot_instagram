"""Dependency injection container for Telegram bot."""

from dataclasses import dataclass
from typing import Optional
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

# Application Layer Use Cases
from src.application.user_management.use_cases.register_user import RegisterUserUseCase
from src.application.user_management.use_cases.get_user import GetUserUseCase
from src.application.user_management.use_cases.activate_subscription import ActivateSubscriptionUseCase

from src.application.instagram_integration.use_cases.fetch_instagram_profile import FetchInstagramProfileUseCase
from src.application.instagram_integration.use_cases.fetch_instagram_stories import FetchInstagramStoriesUseCase
from src.application.instagram_integration.use_cases.fetch_instagram_posts import FetchInstagramPostsUseCase
from src.application.instagram_integration.use_cases.fetch_instagram_reels import FetchInstagramReelsUseCase
from src.application.instagram_integration.use_cases.fetch_instagram_highlights import FetchInstagramHighlightsUseCase
from src.application.instagram_integration.use_cases.fetch_instagram_highlight_stories import FetchInstagramHighlightStoriesUseCase
from src.application.instagram_integration.use_cases.fetch_instagram_followers import FetchInstagramFollowersUseCase
from src.application.instagram_integration.use_cases.fetch_instagram_following import FetchInstagramFollowingUseCase
from src.application.instagram_integration.use_cases.fetch_instagram_tagged_posts import FetchInstagramTaggedPostsUseCase

from src.application.content_tracking.use_cases.start_tracking import StartTrackingUseCase
from src.application.content_tracking.use_cases.stop_tracking import StopTrackingUseCase
from src.application.content_tracking.use_cases.pause_tracking import PauseTrackingUseCase
from src.application.content_tracking.use_cases.resume_tracking import ResumeTrackingUseCase
from src.application.content_tracking.use_cases.get_user_trackings import GetUserTrackingsUseCase

from src.application.subscription.use_cases.check_subscription_status import CheckSubscriptionStatusUseCase
from src.application.subscription.use_cases.get_subscription import GetSubscriptionUseCase
from src.application.subscription.use_cases.create_subscription import CreateSubscriptionUseCase

from src.application.payment.use_cases.create_payment import CreatePaymentUseCase
from src.application.payment.use_cases.process_payment import ProcessPaymentUseCase
from src.application.payment.use_cases.complete_payment import CompletePaymentUseCase
from src.application.payment.use_cases.get_payment_status import GetPaymentStatusUseCase
from src.application.payment.use_cases.create_cryptobot_invoice import CreateCryptoBotInvoiceUseCase
from src.application.payment.use_cases.check_cryptobot_payment import CheckCryptoBotPaymentUseCase

from src.application.notification.use_cases.create_notification import CreateNotificationUseCase
from src.application.notification.use_cases.send_notification import SendNotificationUseCase

from src.application.audience_tracking.use_cases.create_tracking import CreateAudienceTrackingUseCase
from src.application.audience_tracking.use_cases.get_tracking_status import GetAudienceTrackingStatusUseCase
from src.application.audience_tracking.use_cases.check_audience_changes import CheckAudienceChangesUseCase
from src.application.audience_tracking.use_cases.cancel_tracking import CancelAudienceTrackingUseCase
from src.application.audience_tracking.use_cases.renew_tracking import RenewAudienceTrackingUseCase
from src.application.audience_tracking.use_cases.calculate_price import CalculateAudienceTrackingPriceUseCase

from src.application.referral.use_cases.generate_referral_code import GenerateReferralCodeUseCase
from src.application.referral.use_cases.apply_referral_code import ApplyReferralCodeUseCase
from src.application.referral.use_cases.get_referral_stats import GetReferralStatsUseCase
from src.application.referral.use_cases.calculate_referral_reward import CalculateReferralRewardUseCase
from src.application.referral.use_cases.request_referral_payout import RequestReferralPayoutUseCase
from src.application.referral.use_cases.get_referral_link import GetReferralLinkUseCase
from src.application.referral.use_cases.process_referral_reward import ProcessReferralRewardUseCase
from src.application.referral.event_handlers.referral_reward_earned_handler import ReferralRewardEarnedHandler

# Infrastructure Layer
from src.infrastructure.persistence.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.infrastructure.persistence.repositories.sqlalchemy_subscription_repository import SQLAlchemySubscriptionRepository
from src.infrastructure.persistence.repositories.sqlalchemy_payment_repository import SQLAlchemyPaymentRepository
from src.infrastructure.persistence.repositories.sqlalchemy_content_tracking_repository import SQLAlchemyContentTrackingRepository
from src.infrastructure.persistence.repositories.sqlalchemy_notification_repository import SQLAlchemyNotificationRepository
from src.infrastructure.persistence.repositories.sqlalchemy_audience_tracking_repository import SqlAlchemyAudienceTrackingRepository
from src.infrastructure.persistence.repositories.sqlalchemy_referral_repository import SqlAlchemyReferralRepository

from src.infrastructure.external_services.hiker_api.hiker_api_adapter import HikerAPIAdapter
from src.infrastructure.messaging.telegram_notification_sender import TelegramNotificationSender
from src.infrastructure.payment.adapters.cryptobot_adapter import CryptoBotAdapter
from src.infrastructure.cache.cache_service import CacheService
from src.infrastructure.cache.rate_limit_service import RateLimitService
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork, IUnitOfWork


@dataclass
class UseCaseContainer:
    """Container for all use cases."""
    
    # User Management
    register_user: RegisterUserUseCase
    get_user: GetUserUseCase
    activate_subscription: ActivateSubscriptionUseCase
    
    # Instagram Integration
    fetch_instagram_profile: FetchInstagramProfileUseCase
    fetch_instagram_stories: FetchInstagramStoriesUseCase
    fetch_instagram_posts: FetchInstagramPostsUseCase
    fetch_instagram_reels: FetchInstagramReelsUseCase
    fetch_instagram_highlights: FetchInstagramHighlightsUseCase
    fetch_instagram_highlight_stories: FetchInstagramHighlightStoriesUseCase
    fetch_instagram_followers: FetchInstagramFollowersUseCase
    fetch_instagram_following: FetchInstagramFollowingUseCase
    fetch_instagram_tagged_posts: FetchInstagramTaggedPostsUseCase
    
    # Content Tracking
    start_tracking: StartTrackingUseCase
    stop_tracking: StopTrackingUseCase
    pause_tracking: PauseTrackingUseCase
    resume_tracking: ResumeTrackingUseCase
    get_user_trackings: GetUserTrackingsUseCase
    
    # Subscription
    check_subscription_status: CheckSubscriptionStatusUseCase
    get_subscription: GetSubscriptionUseCase
    create_subscription: CreateSubscriptionUseCase
    
    # Payment
    create_payment: CreatePaymentUseCase
    process_payment: ProcessPaymentUseCase
    complete_payment: CompletePaymentUseCase
    get_payment_status: GetPaymentStatusUseCase
    create_cryptobot_invoice: CreateCryptoBotInvoiceUseCase
    check_cryptobot_payment: CheckCryptoBotPaymentUseCase
    
    # Notification
    create_notification: CreateNotificationUseCase
    send_notification: SendNotificationUseCase
    
    # Audience Tracking
    create_audience_tracking: CreateAudienceTrackingUseCase
    get_audience_tracking_status: GetAudienceTrackingStatusUseCase
    check_audience_changes: CheckAudienceChangesUseCase
    cancel_audience_tracking: CancelAudienceTrackingUseCase
    renew_audience_tracking: RenewAudienceTrackingUseCase
    calculate_audience_tracking_price: CalculateAudienceTrackingPriceUseCase
    
    # Referral
    generate_referral_code: GenerateReferralCodeUseCase
    apply_referral_code: ApplyReferralCodeUseCase
    get_referral_stats: GetReferralStatsUseCase
    calculate_referral_reward: CalculateReferralRewardUseCase
    request_referral_payout: RequestReferralPayoutUseCase
    get_referral_link: GetReferralLinkUseCase
    process_referral_reward: ProcessReferralRewardUseCase


class DependencyContainer:
    """Main dependency injection container."""
    
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        hiker_api_key: str,
        telegram_bot_token: str,
        cryptobot_token: Optional[str] = None,
        cache_service: Optional[CacheService] = None,
    ):
        self.session_factory = session_factory
        self.hiker_api_key = hiker_api_key
        self.telegram_bot_token = telegram_bot_token
        self.cryptobot_token = cryptobot_token
        self.cache_service = cache_service
        self._use_cases: Optional[UseCaseContainer] = None
        self._rate_limit_service: Optional[RateLimitService] = None
    
    async def get_session(self) -> AsyncSession:
        """Get database session."""
        return self.session_factory()
    
    @asynccontextmanager
    async def get_uow(self):
        """Get Unit of Work with automatic transaction management."""
        async with self.session_factory() as session:
            uow = SQLAlchemyUnitOfWork(session)
            try:
                yield uow
                await uow.commit()
            except Exception:
                await uow.rollback()
                raise
    
    def get_use_cases(self) -> UseCaseContainer:
        """Get use cases container (lazy initialization)."""
        if self._use_cases is None:
            self._use_cases = self._create_use_cases()
        return self._use_cases
    
    def get_rate_limit_service(self) -> RateLimitService:
        """Get rate limit service (lazy initialization)."""
        if self._rate_limit_service is None:
            if self.cache_service is None:
                raise RuntimeError("CacheService not provided to container")
            self._rate_limit_service = RateLimitService(cache_service=self.cache_service)
        return self._rate_limit_service
    
    def _create_use_cases(self) -> UseCaseContainer:
        """Create and wire all use cases."""
        
        # Create external services
        hiker_api = HikerAPIAdapter(api_key=self.hiker_api_key)
        telegram_service = TelegramNotificationSender(bot_token=self.telegram_bot_token)
        
        # User Management Use Cases - pass session_factory, they'll create session inside
        register_user = RegisterUserUseCase(session_factory=self.session_factory)
        get_user = GetUserUseCase(session_factory=self.session_factory)
        activate_subscription = ActivateSubscriptionUseCase(session_factory=self.session_factory)
        
        # Instagram Integration Use Cases
        fetch_instagram_profile = FetchInstagramProfileUseCase(instagram_api_client=hiker_api)
        fetch_instagram_stories = FetchInstagramStoriesUseCase(instagram_api_client=hiker_api)
        fetch_instagram_posts = FetchInstagramPostsUseCase(instagram_api_client=hiker_api)
        fetch_instagram_reels = FetchInstagramReelsUseCase(instagram_api_client=hiker_api)
        fetch_instagram_highlights = FetchInstagramHighlightsUseCase(instagram_api_client=hiker_api)
        fetch_instagram_highlight_stories = FetchInstagramHighlightStoriesUseCase(instagram_api_client=hiker_api)
        fetch_instagram_followers = FetchInstagramFollowersUseCase(instagram_api_client=hiker_api)
        fetch_instagram_following = FetchInstagramFollowingUseCase(instagram_api_client=hiker_api)
        fetch_instagram_tagged_posts = FetchInstagramTaggedPostsUseCase(instagram_api_client=hiker_api)
        
        # Content Tracking Use Cases - TODO: Update to use session_factory
        start_tracking = None  # StartTrackingUseCase(tracking_repository=tracking_repo, instagram_adapter=hiker_api)
        stop_tracking = None  # StopTrackingUseCase(tracking_repository=tracking_repo)
        pause_tracking = None  # PauseTrackingUseCase(tracking_repository=tracking_repo)
        resume_tracking = None  # ResumeTrackingUseCase(tracking_repository=tracking_repo)
        get_user_trackings = None  # GetUserTrackingsUseCase(tracking_repository=tracking_repo)
        
        # Subscription Use Cases - TODO: Update to use session_factory
        check_subscription_status = None  # CheckSubscriptionStatusUseCase(subscription_repository=subscription_repo)
        get_subscription = None  # GetSubscriptionUseCase(subscription_repository=subscription_repo)
        create_subscription = None  # CreateSubscriptionUseCase(subscription_repository=subscription_repo)
        
        # Payment Use Cases - TODO: Update to use session_factory
        create_payment = None  # CreatePaymentUseCase(payment_repository=payment_repo)
        process_payment = None  # ProcessPaymentUseCase(payment_repository=payment_repo)
        complete_payment = None  # CompletePaymentUseCase(payment_repository=payment_repo)
        get_payment_status = None  # GetPaymentStatusUseCase(payment_repository=payment_repo)
        
        # CryptoBot Payment Use Cases (optional)
        create_cryptobot_invoice = None
        check_cryptobot_payment = None
        if self.cryptobot_token:
            cryptobot_adapter = CryptoBotAdapter(api_token=self.cryptobot_token)
            create_cryptobot_invoice = CreateCryptoBotInvoiceUseCase(
                cryptobot_adapter=cryptobot_adapter
            )
            check_cryptobot_payment = CheckCryptoBotPaymentUseCase(
                cryptobot_adapter=cryptobot_adapter
            )
        
        # Notification Use Cases - TODO: Update to use session_factory
        create_notification = None  # CreateNotificationUseCase(notification_repository=notification_repo)
        send_notification = None  # SendNotificationUseCase(notification_repository=notification_repo, notification_sender=telegram_service)
        
        # Audience Tracking Use Cases - TODO: Update to use session_factory
        create_audience_tracking = None  # CreateAudienceTrackingUseCase(tracking_repository=audience_tracking_repo, instagram_service=hiker_api)
        get_audience_tracking_status = None  # GetAudienceTrackingStatusUseCase(tracking_repository=audience_tracking_repo)
        check_audience_changes = None  # CheckAudienceChangesUseCase(tracking_repository=audience_tracking_repo, instagram_service=hiker_api)
        cancel_audience_tracking = None  # CancelAudienceTrackingUseCase(tracking_repository=audience_tracking_repo)
        renew_audience_tracking = None  # RenewAudienceTrackingUseCase(tracking_repository=audience_tracking_repo)
        calculate_audience_tracking_price = CalculateAudienceTrackingPriceUseCase()
        
        # Referral Use Cases - TODO: Update to use session_factory
        generate_referral_code = None  # GenerateReferralCodeUseCase(referral_repository=referral_repo)
        apply_referral_code = None  # ApplyReferralCodeUseCase(referral_repository=referral_repo)
        get_referral_stats = None  # GetReferralStatsUseCase(referral_repository=referral_repo)
        calculate_referral_reward = CalculateReferralRewardUseCase()
        request_referral_payout = None  # RequestReferralPayoutUseCase(referral_repository=referral_repo)
        get_referral_link = None  # GetReferralLinkUseCase(referral_repository=referral_repo, bot_username="your_bot_username")
        
        # Referral Event Handlers
        referral_reward_earned_handler = None  # ReferralRewardEarnedHandler(send_notification_use_case=send_notification)
        
        # Process Referral Reward with event handler
        process_referral_reward = None  # ProcessReferralRewardUseCase(referral_repository=referral_repo, referral_reward_earned_handler=referral_reward_earned_handler)
        
        return UseCaseContainer(
            # User Management
            register_user=register_user,
            get_user=get_user,
            activate_subscription=activate_subscription,
            # Instagram Integration
            fetch_instagram_profile=fetch_instagram_profile,
            fetch_instagram_stories=fetch_instagram_stories,
            fetch_instagram_posts=fetch_instagram_posts,
            fetch_instagram_reels=fetch_instagram_reels,
            fetch_instagram_highlights=fetch_instagram_highlights,
            fetch_instagram_highlight_stories=fetch_instagram_highlight_stories,
            fetch_instagram_followers=fetch_instagram_followers,
            fetch_instagram_following=fetch_instagram_following,
            fetch_instagram_tagged_posts=fetch_instagram_tagged_posts,
            # Content Tracking
            start_tracking=start_tracking,
            stop_tracking=stop_tracking,
            pause_tracking=pause_tracking,
            resume_tracking=resume_tracking,
            get_user_trackings=get_user_trackings,
            # Subscription
            check_subscription_status=check_subscription_status,
            get_subscription=get_subscription,
            create_subscription=create_subscription,
            # Payment
            create_payment=create_payment,
            process_payment=process_payment,
            complete_payment=complete_payment,
            get_payment_status=get_payment_status,
            create_cryptobot_invoice=create_cryptobot_invoice,
            check_cryptobot_payment=check_cryptobot_payment,
            # Notification
            create_notification=create_notification,
            send_notification=send_notification,
            # Audience Tracking
            create_audience_tracking=create_audience_tracking,
            get_audience_tracking_status=get_audience_tracking_status,
            check_audience_changes=check_audience_changes,
            cancel_audience_tracking=cancel_audience_tracking,
            renew_audience_tracking=renew_audience_tracking,
            calculate_audience_tracking_price=calculate_audience_tracking_price,
            # Referral
            generate_referral_code=generate_referral_code,
            apply_referral_code=apply_referral_code,
            get_referral_stats=get_referral_stats,
            calculate_referral_reward=calculate_referral_reward,
            request_referral_payout=request_referral_payout,
            get_referral_link=get_referral_link,
            process_referral_reward=process_referral_reward,
        )


# Global container instance (will be initialized in bot.py)
_container: Optional[DependencyContainer] = None


def init_container(
    session_factory: async_sessionmaker[AsyncSession],
    hiker_api_key: str,
    telegram_bot_token: str,
    cryptobot_token: Optional[str] = None,
    cache_service: Optional[CacheService] = None,
) -> DependencyContainer:
    """Initialize global dependency container."""
    global _container
    _container = DependencyContainer(
        session_factory=session_factory,
        hiker_api_key=hiker_api_key,
        telegram_bot_token=telegram_bot_token,
        cryptobot_token=cryptobot_token,
        cache_service=cache_service,
    )
    return _container


def get_container() -> DependencyContainer:
    """Get global dependency container."""
    if _container is None:
        raise RuntimeError("Container not initialized. Call init_container() first.")
    return _container
