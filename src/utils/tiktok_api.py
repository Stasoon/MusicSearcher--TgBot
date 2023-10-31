# # from .pyktok import save_tiktok
# from aiotiktok import Client
#
#
# async def get_video(url: str):
#     # save_tiktok(video_url=url, browser_name='chrome')
#     # print('finish')
#     tiktok = Client()
#     try:
#         data = await tiktok.video_data(url=url)
#     except Exception as e:
#         print('Error!', e)
#     else:
#         print("video data: ", data)


# from tiktokapipy.async_api import AsyncTikTokAPI
#
#
# async def get_video(video_link):
#     async with AsyncTikTokAPI() as api:
#         video = await api.video(video_link)
#     print(video)
#     return video

