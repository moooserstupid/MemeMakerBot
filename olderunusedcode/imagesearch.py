import json
import os
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt
import requests
from dotenv import load_dotenv
import asyncio
import aiohttp
'''
This sample makes a call to the Bing Image Search API with a text query and returns relevant images with data.
Suggestions:
1: I need to find whether the different request calls are actually counted under my
query qouta and if they are, how I can reduce these calls to the least possible amount.
2: Why are the query results so goddamn slow
'''
async def get_image_urls(params, subscriptionKey, endpoint):
    #finds images based on the search param
    headers = {'Ocp-Apim-Subscription-Key': subscriptionKey}

    # Calls the API
    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint, headers=headers, params=params) as response:
            image_urls = []
            if response.status == 200:
                search_results = await response.json()
                image_urls = [img["contentUrl"] for img in search_results["value"][:5]]
            else:
                return None
            #image_objects = []
            #for i in range(5):
                
        # plt.show()
        #user_choice = 1
        #image_data = requests.get(content_urls[user_choice])
        #image_data.raise_for_status()
        #caption.add_caption(BytesIO(image_data.content), "I'm so tired", "oF bElieVinG")
        return image_urls
async def get_image_objects(image_urls, url_count):
    if image_urls is not None:
        async with aiohttp.ClientSession() as session:
            image_objects = []
            for i in range(url_count):
                async with session.get(image_urls[i]) as image_data:
                    if image_data.status == 200:
                        with Image.open(BytesIO(await image_data.read())) as image_bytes:
                            if image_bytes.mode != 'RGB': image_bytes.convert('RGB')
                            image_objects.append(image_bytes)
                    else:
                        image_objects.append("Error")
            return image_objects         
5
if __name__ == '__main__':
    load_dotenv()
    #Gets the Bing Image Search API subscription Key and endpoint from the .env file
    subscriptionKey = os.getenv('BS_API_KEY')
    endpoint = os.getenv('END_POINT') + "v7.0/images/search" #dont mess with this it will fuck everything up

    query = "Fry futurama take all my money"
    # Constructs a request
    mkt = 'en-US'
    params = {'q': query, 'mkt': mkt, 'count' : 5, 'safeSearch' : 'Moderate',
            'minHeight' : 120, 'minWidth' : 120,'maxHeight' : 1024, 'maxWidth' : 1024}
    #loop = asyncio.get_event_loop()
    #img_urls = loop.run_until_complete(get_image_urls(params=params, subscriptionKey=subscriptionKey, endpoint=endpoint))
    #print(img_urls)
    img_urls = ['https://i.pinimg.com/736x/b2/82/ec/b282ecedbb95a873ed9e3298673d34da--take-my-money-futurama.jpg', 'https://d2hg8ctx8thzji.cloudfront.net/faqs.com/wp-content/uploads/2019/04/Mr.-Fry-from-Futurama-and-his-shut-up-and-take-my-money.jpg', 'https://3dprintingindustry.com/wp-content/uploads/2016/08/futurama4.jpg', 'http://4.bp.blogspot.com/-J_fuziF-6Z4/UUJWLUCmqjI/AAAAAAAAO8M/Rxvx23tjBsA/w1200-h630-p-k-nu/futurama-fry-meme-shut-up-and-take-my-money.jpg', 'https://media.tenor.co/images/8922d2193965b055e35ece0c6dca4c42/tenor.gif']
    loop = asyncio.get_event_loop()
    img_objects = loop.run_until_complete(get_image_objects(img_urls, 5))
    for i in range(5):
        #print(img_objects[i])
        if img_objects[i] is not None:
            #if img_objects[i].mode != 'RGB': img_objects[i].convert('RGB')
            img_objects[i].save("images/" + str(i + 1) + ".jpg")
