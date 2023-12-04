from .models import JoinRequestChannel


def add_join_request_channel(channel_id: int, channel_title: str, invite_link: str, welcome_text: str) -> None:
    JoinRequestChannel.create(
        channel_id=channel_id, channel_title=channel_title,
        invite_link=invite_link, welcome_text=welcome_text
    )


def get_join_request_channel_or_none(channel_id: int) -> JoinRequestChannel | None:
    return JoinRequestChannel.get_or_none(JoinRequestChannel.channel_id == channel_id)


def get_all_join_request_channels() -> list[JoinRequestChannel]:
    return JoinRequestChannel.select()


def update_invite_link(channel_id: int, new_link: str) -> bool:
    channel = JoinRequestChannel.get_or_none(JoinRequestChannel.channel_id == channel_id)
    if not channel:
        return False

    channel.invite_link = new_link
    channel.save()
    return True


def update_welcome_text(channel_id: int, new_welcome: str) -> bool:
    channel = JoinRequestChannel.get_or_none(JoinRequestChannel.channel_id == channel_id)
    if not channel:
        return False

    channel.welcome_text = new_welcome
    channel.save()
    return True


def increase_requests_approved_count(channel_id: int) -> bool:
    """ Увеличить счётчик одобренных заявок """
    channel = JoinRequestChannel.get_or_none(JoinRequestChannel.channel_id == channel_id)
    if not channel:
        return False

    channel.approved_requests_count += 1
    channel.save()
    return True


def delete_join_request_channel(channel_id: int) -> bool:
    """ Удалить  """
    channel = JoinRequestChannel.get_or_none(JoinRequestChannel.channel_id == channel_id)
    if not channel:
        return False

    channel.delete_instance()
    return True
