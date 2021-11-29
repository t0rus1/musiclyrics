import streamlit as st
import re, requests, subprocess, urllib.parse, urllib.request
from bs4 import BeautifulSoup
import inspect
import pprint
from streamlit_player import st_player

PAGE_SIZE=10

# how to imbed an iframe to play (only) official videos
# '''
# <iframe width="1904" height="782" src="https://www.youtube.com/embed/h_QgZoohP2E" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
# '''

# def name_and_args():
#     caller = inspect.stack()[1][0]
#     args, _, _, values = inspect.getargvalues(caller)
#     return [(i, values[i]) for i in args]

def perform_yt_user_search(music_name):
    '''
    put search query to youtube and return results
    '''
    query_string = urllib.parse.urlencode({"search_query": music_name})

    # perform the yt search 
    formatUrl = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
    return re.findall(r"watch\?v=(\S{11})", formatUrl.read().decode())

def extract_yt_urls(search_results): #, prog_bar):
    '''
    return hash of yt urls keyed on title
    '''

    yt_urls={}
    with st.spinner("searching youtube ..."):
        for index in range(0, PAGE_SIZE+1):
            clip_url = "https://www.youtube.com/watch?v=" + "{}".format(search_results[index])
            clip = requests.get(clip_url)

            inspect = BeautifulSoup(clip.content, "html.parser")
            yt_title = inspect.find_all("meta", property="og:title")

            yt_title_friendly = yt_title[0]['content']
            # build hash lookup of yt urls keyed on friendly titles
            yt_urls[yt_title_friendly] = clip_url
            #prog_bar.progress(index/PAGE_SIZE)

    return yt_urls

###################################
# START with a search box and button
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
st.header("Search Youtube for Music")

music_search = st.text_input("Artist and name of song video to search for eg Αντώνης Ρέμος Εμείς","")
#if not music_search:
submit1 = st.button('Search')
if not music_search:
    st.warning('Please input a search term above eg Αντώνης Ρέμος Εμείς')
    st.stop()


with st.form(key='f1'):
    # music_search = st.text_input("Artist and name of song video to search for eg Αντώνης Ρέμος Εμείς","")
    # if not music_search:
    #     submit1 = st.form_submit_button('Search')
    #     st.warning('Please input a search term above eg Αντώνης Ρέμος Εμείς')
    #     st.stop()

    # put search to youtube
    search_results = perform_yt_user_search(music_search)

    # inspect search results and extract video urls
    progress_bar = st.progress(0)
    yt_urls=extract_yt_urls(search_results) #, progress_bar)

    # build a select box of first PAGE_SIZE results (only)
    chosen = st.selectbox(label=f'first {PAGE_SIZE} results', options=yt_urls.keys(), index=0, ) #, on_change=track_chosen)
    submit1 = st.form_submit_button(f"get youtube link")

if submit1:
    st.write(chosen)
    st.write(f'{yt_urls[chosen]}')
    st_player(yt_urls[chosen])

