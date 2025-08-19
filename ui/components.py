import streamlit as st

def post_card(post):
    status_colors = {
        "posted": "green",
        "pending": "orange",
        "failed": "red"
    }
    color = status_colors.get(post.status, "gray")
    html = f"""
    <div style='border:1px solid #ddd; border-radius:8px; padding:16px; margin-bottom:12px;'>
        <b>Platform:</b> {post.platform}<br>
        <b>Content:</b> {post.content}<br>
        <b>Scheduled Time:</b> {post.scheduled_time}<br>
        <b>Status:</b> <span style='color:{color}'>{post.status.capitalize()}</span><br>
        {'<b>Engagement:</b><br>' if post.status == 'posted' else ''}
        {'Likes: ' + str(post.likes) + '<br>' if post.status == 'posted' else ''}
        {'Reposts: ' + str(post.reposts) + '<br>' if post.status == 'posted' else ''}
        {'Replies: ' + str(post.replies) + '<br>' if post.status == 'posted' else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def success_alert(msg):
    st.success(msg)

def error_alert(msg):
    st.error(msg)

def info_alert(msg):
    st.info(msg)
