import streamlit as st
from streamlit_navigation_bar import st_navbar
import logic

# Setting app width to max
st.set_page_config(layout='wide')

# Showing movies list to user
st.title("Movie Recommendation System")
selected_movie_name = st.selectbox(
    'Please Select a Movie to get Recommendation',
    logic.movies_list['title'].values
)

btn_placeholder = st.empty()
if btn_placeholder.button('Recommend', key='before_recommend_btn'):
    btn_placeholder.button('Searching...', disabled=True, key='searching_btn')
    recommended_movies = logic.recommend(selected_movie_name)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        movie = recommended_movies[0]
        st.image(movie['poster_path'])
        st.markdown(f'**{movie['name']}** ({movie['release_year']})')
    with col2:
        movie = recommended_movies[1]
        st.image(movie['poster_path'])
        st.markdown(f'**{movie['name']}** ({movie['release_year']})')
    with col3:
        movie = recommended_movies[2]
        st.image(movie['poster_path'])
        st.markdown(f'**{movie['name']}** ({movie['release_year']})')
    with col4:
        movie = recommended_movies[3]
        st.image(movie['poster_path'])
        st.markdown(f'**{movie['name']}** ({movie['release_year']})')
    with col5:
        movie = recommended_movies[4]
        st.image(movie['poster_path'])
        st.markdown(f'**{movie['name']}** ({movie['release_year']})')
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        movie = recommended_movies[5]
        st.image(movie['poster_path'])
        st.markdown(f'**{movie['name']}** ({movie['release_year']})')
    with col2:
        movie = recommended_movies[6]
        st.image(movie['poster_path'])
        st.markdown(f'**{movie['name']}** ({movie['release_year']})')
    with col3:
        movie = recommended_movies[7]
        st.image(movie['poster_path'])
        st.markdown(f'**{movie['name']}** ({movie['release_year']})')
    with col4:
        movie = recommended_movies[8]
        st.image(movie['poster_path'])
        st.markdown(f'**{movie['name']}** ({movie['release_year']})')
    with col5:
        movie = recommended_movies[9]
        st.image(movie['poster_path'])
        st.markdown(f'**{movie['name']}** ({movie['release_year']})')

    btn_placeholder.button('Recommend', disabled=False, key='after_recommend_btn')

