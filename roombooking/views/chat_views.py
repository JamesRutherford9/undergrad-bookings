from django.shortcuts import render, redirect
from django.urls import reverse

def chatbot(request):

        return render(request, 'roombooking/chatbot/chatbot.html')