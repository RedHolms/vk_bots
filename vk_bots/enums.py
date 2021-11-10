from .types import Enum

class HandlerType(Enum):
    """
    Handlers arguments format:
    --------------------------
    Cycle Handler:
    ```
    def HANDLER(self: Bot):
        # Some code...
        return
    ```
    
    Event Handler:
    ```
    def HANDLER(self: Bot, eventObject: dict):
        # Some code...
        return
    ```

    InvalidParamsHandler:
    ```
    def HANDLER(self: Bot, messageObject: dict, receivedParams: list, expectedParams: list, invalidParamIndex: int):
        # Some code...
        return
    ```
    """
    CycleHandler = "cycle"
    EventHandler = "event"
    InvalidParamsHandler = "params_error"

class Event(Enum):
    class Message(Enum):
        New = "message_new"
        Reply = "message_reply"
        Edit = "message_edit"
        Allow = "message_allow"
        Deny = "message_deny"
        TypingStateChange = "message_typing_state"
    class CallbackButton(Enum):
        Press = "message_event"
    class Photo(Enum):
        New = "photo_new"
        class Comment(Enum):
            New = "photo_comment_new"
            Edit = "photo_comment_edit"
            Delete = "photo_comment_delete"
            Restore = "photo_comment_restore"
    class Audio(Enum):
        New = "audio_new"
    class Video(Enum):
        New = "video_new"
        class Comment(Enum):
            New = "video_comment_new"
            Edit = "video_comment_edit"
            Delete = "video_comment_delete"
            Restore = "video_comment_restore"
    class Wall(Enum):
        class Post(Enum):
            New = "wall_post_new"
            Repost = "wall_repost"
            class Comment(Enum):
                New = "wall_reply_new"
                Edit = "wall_reply_edit"
                Delete = "wall_reply_delete"
                Restore = "wall_reply_restore"
        class Like(Enum):
            Add = "like_add"
            Remove = "like_remove"
    class BoardPost(Enum):
        New = "board_post_new"
        Edit = "board_post_edit"
        Delete = "board_post_delete"
        Restore = "board_post_restore"
    class Market(Enum):
        class Order(Enum):
            New = "market_order_new"
            Edit = "market_order_edit"
        class Comment(Enum):
            New = "market_comment_new"
            Edit = "market_comment_edit"
            Delete = "market_comment_delete"
            Restore = "market_comment_restore"
    class Follower(Enum):
        Join = "group_join"
        Leave = "group_leave"
        Ban = "user_block"
        Unban = "user_unblock"
    class Poll(Enum):
        NewVote = "poll_vote_new"
    class Group(Enum):
        SettingsChange = "group_change_settings"
        OfficersListEdit = "group_officers_edit"
        PhotoChange = "group_change_photo"
    class VKPay(Enum):
        Transaction = "vkpay_transaction"
    class VKMiniApps(Enum):
        Event = "app_payload"
    class VKDonut(Enum):
        class Subscription(Enum):
            New = "donut_subscription_create"
            Prolong = "donut_subscription_prolonged"
            Expire = "donut_subscription_expired"
            Cancel = "donut_subscription_cancelled"
            PriceChange = "donut_subscription_price_changed"
        class MoneyWithdraw(Enum):
            Successful = "donut_money_withdraw"
            Error = "donut_money_withdraw_error"