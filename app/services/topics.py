"""
Module containing topic-related functionality including a list of topics
and utility functions to work with them.
"""

import random

TOPICS = [
    "Love Quotes",
    "Friendship Quotes",
    "Inspirational Quotes",
    "Motivational Quotes",
    "Life Quotes",
    "Happiness Quotes",
    "Positive Quotes",
    "Hope Quotes",
    "Faith & Spiritual Quotes",
    "Success Quotes",
    "Funny Quotes",
    "Wisdom Quotes",
    "Leadership Quotes",
    "Family Quotes",
    "Self-Love Quotes",
    "Confidence Quotes",
    "Attitude Quotes",
    "Courage Quotes",
    "Perseverance Quotes",
    "Dream Quotes",
    "Mindfulness Quotes",
    "Gratitude Quotes",
    "Kindness Quotes",
    "Teamwork Quotes",
    "Hard Work Quotes",
    "Change Quotes",
    "Patience Quotes",
    "Failure Quotes",
    "Forgiveness Quotes",
    "Equality & Unity Quotes",
    "Resilience Quotes",
    "Nature Quotes",
    "Philosophical (Deep) Quotes",
    "Education & Knowledge Quotes",
    "Travel Quotes",
    "Adventure Quotes",
    "Fitness Quotes",
    "Mental Health Quotes",
    "Creativity Quotes",
    "Business & Entrepreneur Quotes",
    "Compassion Quotes",
    "Humility Quotes",
    "Self-Improvement Quotes",
    "Sad/Heartbreak Quotes",
    "Freedom Quotes",
    "Time Quotes",
    "Trust & Loyalty Quotes",
    "Integrity & Honesty Quotes",
    "Peace Quotes",
    "Live in the Moment (Carpe Diem) Quotes"
]


def get_random_topic():
    """
    Returns a random topic from the TOPICS list.
    
    Returns:
        str: A randomly selected topic
    """
    return random.choice(TOPICS)