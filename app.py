import os
import os.path
from youtube_dl.utils import DownloadError
import streamlit as st
import re, requests, subprocess, urllib.parse, urllib.request
from bs4 import BeautifulSoup
import inspect
from pprint import pprint
import json
from streamlit_player import st_player
import downloader

DEFAULT_PAGE_SIZE=20

def init_folders():
    ''' ensure needed folders exist'''
    try:
        os.mkdir('./temp')
    except OSError as error:
        pass #print(error)

def setup_page():
    ''' streamlit page config, app title etc'''
    st.set_page_config(
        page_title = "Music and Lyrics",
        layout="wide",
        initial_sidebar_state="expanded",
        page_icon="🎶",
        menu_items={
            "About": "Music & Lyrics app, by Leon van Dyk 2021"
        }
    )
    st.title('Music and Lyrics v 0.1🎶')
    st.subheader("Search Youtube for Music, then pair with lyrics and translation!")

def name_and_args():
    ''' inspect function arguments '''
    caller = inspect.stack()[1][0]
    args, _, _, values = inspect.getargvalues(caller)
    return [(i, values[i]) for i in args]

@st.cache
def submit_youtube_query(music_name):
    '''
    put search query to youtube and return results
    '''
    query_string = urllib.parse.urlencode({"search_query": music_name})

    # perform the yt search 
    formatUrl = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
    return re.findall(r"watch\?v=(\S{11})", formatUrl.read().decode())

@st.cache
def get_youtube_links(search_results, page_size): #, prog_bar):
    '''
    return dict of yt urls keyed on title
    '''
    yt_urls={}
    with st.spinner("get youtube links..."):
        for index in range(0, page_size):
            clip_url = "https://www.youtube.com/watch?v=" + "{}".format(search_results[index])
            clip = requests.get(clip_url)

            inspect = BeautifulSoup(clip.content, "html.parser")
            if index==0:
                with open('inspect.html','wt') as outfile:
                    pprint(inspect, stream=outfile)
            

            yt_title = inspect.find_all("meta", property="og:title")

            yt_title_friendly = yt_title[0]['content']
            # build hash lookup of yt urls keyed on friendly titles
            yt_urls[yt_title_friendly] = clip_url

    return yt_urls

# def get_video(videos_url):
#     print(name_and_args())    
#     #print(videos_url[0][1])
#     #st_player(yt_urls[chosen])

def search_form_callback():
    ''' executed when form is submitted and before re-run '''

    if st.session_state.music_query == '':
        return

    if not hasattr(st.session_state,'title_radio'):
        return

    chosen_title = st.session_state.title_radio 
    # dont download title already in the player
    most_recently_download = hasattr(st.session_state,'current_playee') and chosen_title == st.session_state.current_playee

    download_url = st.session_state.yt_urls[chosen_title]
    if not most_recently_download:
        with st.spinner(f"Downloading and extracting audio from '{chosen_title}' youtube video ..."):
            placeholder = st.empty()
            completion_state = downloader.retrieve(download_url, placeholder)
            if completion_state is not None:
                if isinstance(completion_state, DownloadError):
                    st.error(f'This video ({chosen_title}) may only being played on Youtube itself')
                    print(completion_state)
                elif isinstance(completion_state,FileNotFoundError):
                    st.error('File not found - title may contain disallowed characters...')
                else:
                    st.exception(completion_state)
            else:
                st.markdown(f'** {chosen_title} **')

    # youtube_dl alters some filename chars, so
    # ensure certain disallowed characters in filenames get 
    # substituted in the same way that youtube_dl does them
    scrubbed_title = re.sub(r'[\|/\\]', '_', chosen_title)
    # double quotes become single
    scrubbed_title = re.sub(r'"', "'", scrubbed_title)
    # : becomes -
    scrubbed_title = re.sub(r':', "-", scrubbed_title)

    playee_fn = f'./temp/{scrubbed_title}.mp3'
    if os.path.isfile(playee_fn):
        st.session_state.current_playee = chosen_title
        # place audio player - hopefully the file will be an mp3:
        st.audio(playee_fn, format='audio/ogg')
        st.write(f'Watch video on Youtube {download_url}')
    else:
        st.error(f'Unable to find or play {playee_fn} - the audio player cannot load it due to irregular titling.')
            

###################################
# START with a search box and button
init_folders()
setup_page()

#get help on any widget this way
#st.help(st.selectbox)

with st.expander("options"):
    results_size = int(st.number_input('number of results to fetch',min_value=1, max_value=100, value=DEFAULT_PAGE_SIZE))
    video_links_only = st.checkbox('get youtube videos links only',value=False, help='check this if you only want to watch videos, as opposed to the normal pairing of audio with lyrics')

with st.form('search_form'):
    #results_size = DEFAULT_PAGE_SIZE        
    music_query = st.text_input("Artist and|or name of song video to search for", key='music_query', help='Artist AND song OR just artist OR just song. To begin a new search, clear this text box and click submit below')    
    if not music_query:
        submit_button = st.form_submit_button('search')
        st.warning('please enter a search term eg Αντώνης Ρέμος')
        st.stop()
    else:
        search_results = submit_youtube_query(music_query)
        # inspect search results and extract video urls
        st.session_state.yt_urls=get_youtube_links(search_results, results_size)

        if video_links_only:
            # show only youtube links in a list
            for title,link in st.session_state.yt_urls.items():
                st.markdown(f'[{title}]({link})')
        else:
            # intended default mode
            st.radio('Choose a title to download and play', st.session_state.yt_urls.keys(), key='title_radio')
        
        submit_button = st.form_submit_button(label='submit', on_click=search_form_callback)


                

