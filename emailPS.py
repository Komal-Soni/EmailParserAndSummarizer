import streamlit as st
from emailparsersummarizer import major
st.title("Email Parser and Summarizer")
form = st.form(key="my_form")
email = form.text_input(label="Email ID")
password = form.text_input(label="Password")
submit = form.form_submit_button(label="Read summary")
ReadBody = form.form_submit_button(label="Read Body")
if submit:
    op = major(email, password)
    st.header("Results")
    for i in range(1,len(op)):
        st.write("From: "+ op['From'][i])
        st.write("Subject: "+ op['Subject'][i])
        st.write("Summary: "+ op['Summary'][i])
        st.write("="*86)
else:
    op = major(email, password)
    st.header("Results")
    for i in range(1,len(op)):
        st.write("From: "+ op['From'][i])
        st.write("Subject: "+ op['Subject'][i])
        st.write("Body: "+ op['Body'][i])
        st.write("="*86)

