token=""

spotipy_creds = {
    "client_id": "f48cc50681534c1c8b557bd9f6e1d2eb",
    "client_secret": "87bf6165687941afb9120e44c6fa5fbc",
    #    "redirect_uri": "https://example.com/callback"
}
configffmpeg_path = "c:/Users/kilgr/.spotdl/ffmpeg.exe"
music_library = "c:/USers/kilgr/Music"
playlists= {}
import os
for root, dirs, files in os.walk(music_library):
    for file in files:
        if not ".m3u" in file:
            continue
        print(file)
        playlist_name = file.split(".")[0]
        playlists[playlist_name]=[]
        with open(os.path.join(root,file),"r") as f:
            for line in f.read().split("\n"):
                if line.startswith("#"):
                    continue
                print(line)
                playlists[playlist_name].append(line)
