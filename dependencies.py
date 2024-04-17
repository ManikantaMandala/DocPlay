import os
import streamlit as st
# import streamlit_authenticator as stauth
import datetime
import re
from deta import Deta
from dotenv import dotenv_values
import pymongo
import bcrypt

config = dotenv_values(".env")
database_url = config['DATABASE_URL']

def connection():
    try:
        client = pymongo.MongoClient(database_url)
        db = client['DocPlay']
        collection = db['users']
    except Exception as e:
        print(e)

def insert_user(email, username, password):
    """
    Inserts Users into the DB
    :param email:
    :param username:
    :param password:
    :return User Upon successful Creation:
    """
    date_joined = str(datetime.datetime.now())
    try:
        client = pymongo.MongoClient(database_url)
        db = client['DocPlay']
        collection = db['users']
        is_inserted = collection.insert_one({
            'email': email,
            'username': username,
            'password': password, 'date_joined': date_joined
        })
        return is_inserted
    except Exception as e:
        print(e)


def fetch_users():
    """
    Fetch Users
    :return Dictionary of Users:
    """
    try:
        client = pymongo.MongoClient(database_url)
        db = client['DocPlay']
        collection = db['users']
        users = collection.find()
        return users
    except Exception as e:
        print(e)
    # users = 
    # return users.items

def check_in_emails(email):
    """
    Check if email exists
    :param email:
    :return True if email exists else False:
    """
    try:
        client = pymongo.MongoClient(database_url)
        db = client['DocPlay']
        collection = db['users']
        user = collection.find_one({'email': email})
        if user:
            return False
        return True
    except Exception as e:
        print(e)

def get_user_emails():
    """
    Fetch User Emails
    :return List of user emails:
    """
    try:
        client = pymongo.MongoClient(database_url)
        db = client['DocPlay']
        collection = db['users']
        users = collection.find()
        emails = []
        for user in users.items:
            emails.append(user['email'])
        return emails
    except Exception as e:
        print(e)

def check_in_usernames(username):
    """
    Check if username exists
    :param username:
    :return True if username exists else False:
    """
    try:
        client = pymongo.MongoClient(database_url)
        db = client['DocPlay']
        collection = db['users']
        user = collection.find_one({'username': username})
        if user:
            return False
        return True
    except Exception as e:
        print(e)

def get_usernames():
    """
    Fetch Usernames
    :return List of user usernames:
    """
    try:
        client = pymongo.MongoClient(database_url)
        db = client['DocPlay']
        collection = db['users']
        users = collection.find()
        usernames = []
        for user in users.items:
            usernames.append(user['key'])
        return usernames
    except Exception as e:
        print(e)


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


def hash(password: str) -> str:
    """
    Hashes the plain text password.

    Parameters
    ----------
    password: str
        The plain text password to be hashed.
    Returns
    -------
    str
        The hashed password.
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def sign_up():
    with st.form(key='signUpForProject', clear_on_submit=True):
        st.subheader('Sign Up')
        email = st.text_input(':blue[Email]', placeholder='Enter Your Email')
        username = st.text_input(':blue[Username]', placeholder='Enter Your Username')
        password1 = st.text_input(':blue[Password]', placeholder='Enter Your Password', type='password')
        password2 = st.text_input(':blue[Confirm Password]', placeholder='Confirm Your Password', type='password')

        if email:
            if validate_email(email):
                if check_in_emails(email):
                    if validate_username(username):
                        if check_in_usernames(username):
                            if len(username) >= 2:
                                if len(password1)>=6:
                                    if password1 == password2:
                                        
                                        #Adding the user
                                        # hashed_password = stauth.Hasher(password2).generator();
                                        # hashed_password = hash(password2)
                                        insert_user(email,username, hash(password2))
                                        st.success('Account has been created Successfully!!')
                                        # st.balloons()
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
