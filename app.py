import os
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
        print(error)

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
    st.title('Music and Lyrics 🎶')
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
def get_youtube_titles(search_results, page_size): #, prog_bar):
    '''
    return dict of yt urls keyed on title
    '''

    yt_urls={}
    with st.spinner("getting youtube titles..."):
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
    chosen_title = st.session_state.title_radio
    download_url = st.session_state.yt_urls[chosen_title]
    with st.spinner(f'downloading audio for {chosen_title}'):
        completion_state = downloader.download(download_url)
        if completion_state is not None:
            st.exception(completion_state)
        else:
            st.success(f'audio for {chosen_title} successfully downloaded!')
    st.audio(f'./temp/{chosen_title}.mp3')
            

###################################
# START with a search box and button
init_folders()
setup_page()

#get help on any widget this way
#st.help(st.selectbox)

with st.form('search_form'):
    music_query = st.text_input("Artist and name of song video to search for")
    if not music_query:
        submit_button = st.form_submit_button('search')
        st.warning('please enter a search term eg Αντώνης Ρέμος')
        st.stop()
    else:
        #results_page_size = st.number_input('Number of results:',min_value=1, max_value=100, value=DEFAULT_PAGE_SIZE, key='pagesize_input')
        results_page_size = DEFAULT_PAGE_SIZE
        search_results = submit_youtube_query(music_query)
        # inspect search results and extract video urls
        st.session_state.yt_urls=get_youtube_titles(search_results, results_page_size)

        # with st.container():
        #     for option in yt_urls.keys():
        #         st.write(f'{option}')
        #         downloader.download(yt_urls[option])

        st.radio('Choose a title to download and play', st.session_state.yt_urls.keys(), key='title_radio')
        submit_button = st.form_submit_button(label='submit', on_click=search_form_callback)


                

