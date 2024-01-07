import grequests
import requests
import re
from tqdm import tqdm
session=requests.session()

# Base URL for animepahe.ru
url = "https://animepahe.ru/"

def search_apahe(query: str) -> list:
    """
    Search animepahe.ru for anime matching the given query.
    
    Parameters:
        query (str): The search query.
    
    Returns:
        A list of lists, where each inner list contains the following information
        about a search result:
            - Title
            - Type (e.g. TV, movie)
            - Number of episodes
            - Status (e.g. completed, airing)
            - Year
            - Score
            - Session ID
    """
    global url
    search_url = url + "api?m=search&q=" + query
    response = session.get(search_url)
    data = response.json()
    clean_data = []
    for i in data["data"]:
        hmm = []
        hmm.append(i['title'])
        hmm.append(i['type'])
        hmm.append(i['episodes'])
        hmm.append(i['status'])
        hmm.append(i['year'])
        hmm.append(i['score'])
        hmm.append(i['session'])
        clean_data.append(hmm)
    return clean_data

#print(search_apahe("horimiya"))

def mid_apahe(session_id: str , episode_range: list) -> list:
    """
    Retrieve a list of episode IDs for the specified session ID within a given range.
    
    Parameters:
        session_id (str): The unique session ID.
        episode_range (list): A list containing the start and end episode IDs within the range.
    
    Returns:
        list: A list of episode IDs.
    """
    # episode_range[0]=int(episode_range[0])
    # episode_range[1]=int(episode_range[1])
    pages=[1,2]
    pages[0]+=(episode_range[0]//30)
    pages[1]+=(episode_range[1]//30)
    global url
    data = []
    for page in range(pages[0],pages[1]):
        url2 = url + "api?m=release&id=" + session_id + "&sort=episode_asc&page="+ str(page)
        r = session.get(url2)
        for i in (r.json())['data']:
            s = str(i['session'])
            data.append(s)
    return data[(episode_range[0]%30)-1:30*(pages[1]-pages[0]-1)+episode_range[1]%30]

#print(mid_apahe("e8e5a274-b2a0-ae45-de26-803004f3299b",[29,31]))
def dl_apahe1(anime_id: str, episode_ids: list) -> dict:
    """
    Get a list of download links for the given episode IDs asynchronously.
    
    Parameters:
        anime_id (str): The anime ID.
        episode_ids (list): List of episode IDs.
    
    Returns:
        A dictionary where keys are episode indices and values are lists of download link information.
    """
    global url
    urls = [f'{url}/play/{anime_id}/{episode_id}' for episode_id in episode_ids]
    response_futures = grequests.map((grequests.get(url) for url in urls), size=10)

    data_dict = {}
    for index, response in enumerate(response_futures):
        if response is not None and response.status_code == 200:
            text = response.text
            data = re.findall(r'href="(?:([^\"]+)" target="_blank" class="dropdown-item">(?:[^\&]+)&middot; ([^\<]+))(?:<span class="badge badge-primary">(?:[^\&]+)</span> <span class="badge badge-warning text-capitalize">([^\<]+))?', text)
            data_dict[index] = data
        else:
            print(f"Episode {episode_ids[index]} could not be fetched.")

    return data_dict

#print(dl_apahe1("13e4f8aa-169f-41cc-b7a1-218c88e3b8d2",["9ea4686f8cd114f3d9c065ab113b49a637f8b23dda5bebcf3c7a1aca20e8e371","d8c696836ba4bbdaff7ad3ca5450b410bbf7eec81832f167c3f7d8231eeaa5e1"]))
# print(dl_apahe1("13e4f8aa-169f-41cc-b7a1-218c88e3b8d2","d8c696836ba4bbdaff7ad3ca5450b410bbf7eec81832f167c3f7d8231eeaa5e1"))

def dl_apahe2(url: str) -> str:
    """
    Follow a redirect link to get the final download link.
    
    Parameters:
        url (str): The redirect link.
    
    Returns:
        The final download link.
    """
    r = requests.get(url)
    redirect_link = (re.findall(r'(https://kwik\.cx/[^"]+)', r.text))[0]
    return redirect_link

#print(dl_apahe2("https://pahe.win/HVLTy"))

def download_file(url, destination):
    if os.path.exists(destination):
        file_size = os.path.getsize(destination)
    else:
        file_size = 0

    headers = {'Range': f'bytes={file_size}-'} if file_size else None
    response = requests.get(url, headers=headers, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    if response.status_code == 206:
        print("Downloading resumed successfully.")
    elif response.status_code == 200:
        print("Downloading")

    with open(destination, 'ab') as file, tqdm(
        desc=destination,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=69420):
            bar.update(len(data))
            file.write(data)
