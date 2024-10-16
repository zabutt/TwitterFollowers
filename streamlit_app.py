import streamlit as st
import tweepy
import pandas as pd
import plotly.express as px

# Twitter API credentials (replace with actual values)
consumer_key = "YOUR_TWITTER_CONSUMER_KEY"
consumer_secret = "YOUR_TWITTER_CONSUMER_SECRET"
access_token = "YOUR_TWITTER_ACCESS_TOKEN"
access_token_secret = "YOUR_TWITTER_ACCESS_TOKEN_SECRET"

# Authenticate with Twitter (assuming credentials are configured in Streamlit Secrets)
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Function to geocode locations (replace with your actual implementation using a geocoding service)
def geocode_location(location_text):
    # Implement logic to use a geocoding API and return latitude and longitude
    return None, None  # Placeholder for now

def get_followers_locations(username):
    try:
        followers = api.get_followers(screen_name=username)
        locations = [follower.location for follower in followers if follower.location]
        return pd.DataFrame(locations, columns=['Location']), None
    except tweepy.TweepError as e:
        if 'Rate limit exceeded' in str(e):
            time.sleep(60 * 15)  # Wait for 15 minutes before retrying
            return get_followers_locations(username)  # Retry the function
        elif 'User not found' in str(e):
            return None, "Error: User not found. Please check the username and try again."
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

            # Geocode locations using a geocoding service
            for index, row in followers_df.iterrows():
                location_text = row['Location']
                latitude, longitude = geocode_location(location_text)
                if latitude and longitude:
                    followers_df.at[index, 'lat'] = latitude
                    followers_df.at[index, 'lon'] = longitude

            # Plot the map (assuming geocoding is successful)
            if 'lat' in followers_df.columns and 'lon' in followers_df.columns:
                fig = px.scatter_geo(followers_df, lat='lat', lon='lon', hover_name='Location')
                st.plotly_chart(fig)
            else:
                st.warning("Geocoding failed for all locations. Consider retrying later.")
        else:
            st.warning("No followers with location data found for this user.")

if __name__ == "__main__":
    main()
