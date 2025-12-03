import streamlit as st

st.title('hello from streamlit app made by lomash choudhary')
st.subheader('Brewed with streamlit')
st.text('welcome to your first interactive app')
st.write('choose your favorite language')

choosedLanguage = st.selectbox('Your Favorite language : ', ['','java', 'python', 'javascript', 'rust', 'c++'])

st.subheader(f"You choosed : {choosedLanguage}, Excellent choince")

st.success(f"Your languaged has been choosen as {choosedLanguage}")