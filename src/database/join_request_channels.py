from .models import JoinRequestChannel


def add_join_request_channel(channel_id: int, channel_title: str, welcome_text: str, goodbye_text: str) -> None:
    JoinRequestChannel.create(
        channel_id=channel_id, channel_title=channel_title,
        welcome_text=welcome_text, goodbye_text=goodbye_text
    )


def get_join_request_channel_or_none(channel_id: int) -> JoinRequestChannel | None:
    return JoinRequestChannel.get_or_none(JoinRequestChannel.channel_id == channel_id)


def get_all_join_request_channels() -> list[JoinRequestChannel]:
    return JoinRequestChannel.select()


def update_allow_joins_approving(channel_id: int, accept: bool) -> bool:
    channel: JoinRequestChannel = JoinRequestChannel.get_or_none(JoinRequestChannel.channel_id == channel_id)
    if not channel:
        return False

    channel.allow_approving = accept
    channel.save()
    return True


def update_welcome_text(channel_id: int, new_welcome: str) -> bool:
    channel = JoinRequestChannel.get_or_none(JoinRequestChannel.channel_id == channel_id)
    if not channel:
        return False

    channel.welcome_text = new_welcome
    channel.save()
    return True


def update_goodbye_text(channel_id: int, new_goodbye: str) -> bool:
    channel = JoinRequestChannel.get_or_none(JoinRequestChannel.channel_id == channel_id)
    if not channel:
        return False

    channel.goodbye_text = new_goodbye
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
