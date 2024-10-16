import streamlit as st
import tweepy
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twitter API credentials
consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Authenticate with Twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

def get_followers_locations(username):
    try:
        followers = api.get_followers(screen_name=username)
        locations = [follower.location for follower in followers if follower.location]
        return pd.DataFrame(locations, columns=['Location']), None
    except tweepy.TweepError as e:
        if 'User not found' in str(e):
            return None, "Error: User not found. Please check the username and try again."
        elif 'Rate limit exceeded' in str(e):
            return None, "Error: Twitter API rate limit exceeded. Please try again later."
        else:
            return None, f"An unexpected error occurred: {str(e)}"

def main():
    st.title("Twitter Followers Map")
    
    username = st.text_input("Enter Twitter username:")
    
    if st.button("Generate Map"):
        with st.spinner("Fetching follower data..."):
            followers_df, error_message = get_followers_locations(username)
        
        if error_message:
            st.error(error_message)
        elif followers_df is not None and not followers_df.empty:
            st.success(f"Successfully fetched data for {len(followers_df)} followers with locations.")
            
            # Here you would need to geocode the locations
            # This is a placeholder for demonstration
            followers_df['lat'] = [0] * len(followers_df)
            followers_df['lon'] = [0] * len(followers_df)
            
            fig = px.scatter_geo(followers_df, lat='lat', lon='lon', hover_name='Location')
            st.plotly_chart(fig)
        else:
            st.warning("No followers with location data found for this user.")

if __name__ == "__main__":
    main()
