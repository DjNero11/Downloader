from flask import Flask, redirect, request, render_template, send_file
from pytube import YouTube
import os
import instaloader
import shutil

# Configuration of app
app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        form_id = request.form.get('form_id')
        
        if form_id == 'form1':
            return youtube_download()
        elif form_id == 'form2':
            return instagram_download()
        
    else:
        return render_template("index.html")


def youtube_download():
    #get link to the video form webiste
        try:
            link = request.form.get("yt_link")
            yt = YouTube(link)
        except:
            print("Enter valid Link")
            return render_template("index.html")

        audio_only = request.form.get('audio_only')
        if audio_only:
            try:
                audio_only_stream = yt.streams.filter(only_audio=True, mime_type="audio/mp4").order_by("abr").desc()
                file = audio_only_stream.first().download()
            except:
                print("Error occured during audio download.")
                return render_template("index.html")
        else:
            #download video(only up to 720p) Higher resolution requires more work.
            try:
                video = yt.streams.get_highest_resolution()
                file = video.download()
            except:
                print("Error occured during video download.")
                return render_template("index.html")
        try:
            response = send_file(file, as_attachment=True)
            os.remove(file)
            return response
        except:
            print("Error when sending file.")
            return render_template("index.html")
        
def instagram_download():
    link = request.form.get("ig_link")
    try:
        # get info about post 
        loader = instaloader.Instaloader()
        post = instaloader.Post.from_shortcode(loader.context, link.split('/')[-2])
        # download files and create a folder 
        loader.download_post(post,"ig_file")
        #zip folder
        shutil.make_archive("ig_download_files", 'zip', "ig_file")
        #send the file to user 
        response = send_file("ig_download_files.zip", as_attachment=True)
        #remove files from the serer
        shutil.rmtree("ig_file")
        os.remove("ig_download_files.zip")
        return response
    except:
            try:
                shutil.rmtree("ig_file")
            except:
                print("error removing file")
            try:
                os.remove("ig_download_files.zip")
            except:
                print("error removing file")
            print("Error when sending or downloadnig.")
            return redirect("/")