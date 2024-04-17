import os
import streamlit as st
import streamlit_authenticator as stauth
import datetime
import re
from deta import Deta
from dotenv import dotenv_values
config = dotenv_values(".env")

deta = Deta(config['DETA_PROJECT_KEY'])

db = deta.Base('StreamlitAuth')

def insert_user(email, username, password):
    """
    Inserts Users into the DB
    :param email:
    :param username:
    :param password:
    :return User Upon successful Creation:
    """
    date_joined = str(datetime.datetime.now())

    return db.put({'key': email, 'username': username, 'password': password, 'date_joined': date_joined})

def fetch_users():
    """
    Fetch Users
    :return Dictionary of Users:
    """
    users = db.fetch()
    return users.items


def get_user_emails():
    """
    Fetch User Emails
    :return List of user emails:
    """
    users = db.fetch()
    emails = []
    for user in users.items:
        emails.append(user['key'])
    return emails


def get_usernames():
    """
    Fetch Usernames
    :return List of user usernames:
    """
    users = db.fetch()
    usernames = []
    for user in users.items:
        usernames.append(user['key'])
    return usernames


def validate_email(email):
    """
    Check Email Validity
    :param email:
    :return True if email is valid else False:
    """
    pattern = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$" #tesQQ12@gmail.com

    if re.match(pattern, email):
        return True
    return False


def validate_username(username):
    """
    Checks Validity of userName
    :param username:
    :return True if username is valid else False:
    """

    pattern = "^[a-zA-Z0-9]*$"
    if re.match(pattern, username):
        return True
    return False

def sign_up():
    with st.form(key='signUpForProject', clear_on_submit=True):
        st.subheader('Sign Up')
        email = st.text_input(':blue[Email]', placeholder='Enter Your Email')
        username = st.text_input(':blue[Username]', placeholder='Enter Your Username')
        password1 = st.text_input(':blue[Password]', placeholder='Enter Your Password', type='password')
        password2 = st.text_input(':blue[Confirm Password]', placeholder='Confirm Your Password', type='password')

        if email:
            if validate_email(email):
                if email not in get_user_emails():
                    if validate_username(username):
                        if username not in get_usernames():
                            if len(username) >= 2:
                                if len(password1)>=6:
                                    if password1 == password2:
                                        
                                        #Adding the user
                                        hashed_password = stauth.Hasher([password2]).generate()
                                        print(insert_user(email,username, hashed_password[0]))
                                        st.success('Account has been created Successfully!!')
                                        st.balloons()
                                    else:
                                        st.warning('Passwords do not match')
                                else:
                                    st.warning('Password is too short')
                            else:
                                st.warning('Username Too Short')
                        else:
                            st.warning('Username already exists')
                    else:
                        st.warning('Invalid Username')
                else:
                    st.warning('Email Already exists')
            else:
                st.warning('Invalid Email')

        btn1, btn2, btn3, btn4, btn5 = st.columns(5)
        with btn3:
            st.form_submit_button('Sign Up')

sign_up()
