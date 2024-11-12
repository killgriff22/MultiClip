from classes import *
#
#
vc: discord.voice_client.VoiceClient | None = None
instances:list[Instance] = []


def update_queue(queue=queue):
    open("queue.txt", "w").write(str(queue))


def read_queue():
    return eval(open("queue.txt").read())


@user.event
async def on_ready():
    global vc
    print(f'{user.user.name} has connected to Discord!')
    user_prompt_timeout.start()
    status.start()
    queue_loop.start()
    instance_loop.start()
    voice_channel = user.get_guild(
        1173496575771807805).get_channel(1173496575771807809)
    vc = await voice_channel.connect()


@user.event
async def on_message(message: discord.Message):
    global vc, queue, paused, loop
    if message.author == user.user:  # dont respond to our own messages
        if message.attachments:
            for file in message.attachments:
                for root, dirs, files in os.walk("Downloads"):
                    for file_ in files:
                        if file.filename in file_:
                            os.remove(os.path.join(root, file_))
    if not message.content.startswith('!'):  # check for the prefix
        return
        
    # this next chunk of code does some file fuckery and adds a status
    # one of the aliases for this command is !s. why? Dont ask me! i just work here!
    for _ in [""]:  # allows me to skip this entire chunk of code if i try to stop the queue
        if any(cmd in message.content for cmd in ['!status', '!s']):
            if "!s" in message.content:
                if any(cmd in message.content for cmd in ['!stop', '!skip']):
                    break
            split = message.content.split(' ')
            with open('statuses.txt', 'a') as f:
                add = ' '.join(split[1:])
                f.write(f"{add}\n")
            with open('statuses.txt', 'r') as f:
                length = len(f.readlines())
            await message.channel.send(f"Added {add} to statuses ({length})")
            return
    # this bot runs in a server with my friends and thats it, i dont want to clog chat so i whitlelist 2 channels
    if not message.channel.id in [1215317925049667594, 1164386048407781457,1173496575771807808,1174005255189569587,1217604526270316636]:
            return
    split = message.content.split(' ')
    if message.author.id == 976512674806501397: #Commands for the bot owner
        match split[0]:
            case '!logout':
                await user.close()
            case '!lookup':
                search_terms = split[1:]
                await message.channel.send(f"searching for {' '.join(split[1:])}")
                #os.walk "/media/skye/New Volume/Music/Backup/Heap" in search of any of the search terms
                if not any(term in file for term in search_terms for file in os.listdir("/media/skye/New Volume/Music/Skye's/Backup/Heap")):
                    await message.channel.send("No results found")
                for file in tqdm(os.listdir("/media/skye/New Volume/Music/Skye's/Backup/Heap")):
                        if any(term in file for term in search_terms):
                            await message.channel.send(file,files=[discord.File(os.path.join("/media/skye/New Volume/Music/Skye's/Backup/Heap", file))])
            case '!deposit':
                if message.attachments:
                    for file in message.attachments:
                        await file.save(os.path.join("/media/skye/New Volume/Music/Skye's/Backup/temp",file.filename))
            case '!retrive':
                #do the above search, for temp instead of Heap
                search_terms = split[1:]
                await message.channel.send(f"searching for {' '.join(split[1:])}")
                if not any(term in file for term in search_terms for file in os.listdir("/media/skye/New Volume/Music/Skye's/Backup/temp")):
                    await message.channel.send("No results found")
                    return
                #os.walk "/media/skye/New Volume/Music/Backup/temp" in search of any of the search terms
                for file in tqdm(os.listdir("/media/skye/New Volume/Music/Skye's/Backup/temp")):
                    if any(term in file for term in search_terms):
                        await message.channel.send(file,files=[discord.File(os.path.join("/media/skye/New Volume/Music/Skye's/Backup/temp", file))])

    if not vc:
        return
    match split[0]:  # Music Bot Commands. Dependent on a active voice channel.
        case '!r' | '!remove':
            index = split[1]
            if index.is_digit():
                if int(index) < len(queue):
                    queue.pop(int(index)-1 if int(index)-1 < 0 else int(index))
        case '!queue' | '!q':
            desc = "".join(
                [f"{i}: {file.split('/')[-1].split('.')[0]}\n" for i, file in enumerate(queue)])
            await message.channel.send(
                embed=discord.Embed(
                    title="QUEUE",
                    color=discord.Color.blurple(),
                    description=desc
                )
            )
        case '!pause' | '!paws':
            if not paused:
                vc.pause()
                paused = True
        case '!resume' | '!res':
            if paused:
                vc.resume()
                paused = False
        case '!c' | '!clear' | '!stop' | '!end':
            vc.stop()
            queue = []
            update_queue()
        case '!skip' | '!next':
            vc.stop()
            queue.pop(0)
        case '!loop' | '!l':
            loop = not loop
            await message.reply(f"loop {'on' if loop else 'off'}")
        case '!play' | '!p':
            paused = False
            if len(split) >= 2:
                url = split[1]
                if url in playlists:
                    print(split)
                    if len(split) >= 3:
                        name = " ".join(split[2:])
                        for song in playlists[url]:
                            if name == song:
                                queue.append(song)
                                break
                            artist_song = song.split("/")[-1].split(".mp3")[0].split(" - ")
                            print(artist_song)
                            song_name = artist_song[1] if len(artist_song) == 2 else artist_song[0] if len(artist_song) == 1 else " - ".join(artist_song[1:])
                            if song_name.lower() == name.lower():
                                queue.append(song)
                                print(queue)
                                print(song)
                                break
                    else:
                        import copy
                        pl = copy.deepcopy(playlists[url])
                        random.shuffle(pl)
                        queue=pl
                        print(queue)
                    update_queue(queue)
            elif message.attachments:
                if not any("mp3" in file.filename for file in message.attachments):
                    return
                before_download = set(os.listdir(Discord_path))
                os.chdir(Discord_path)
                for file in message.attachments:
                    if "mp3" in file.filename:
                        if not file.filename in before_download:
                            await file.save(file.filename)
                        else:
                            files.append(file.filename)
                os.chdir(root)
                after_download = set(os.listdir(Discord_path))
                files = list(set(after_download) - set(before_download))
                for i, file in enumerate(files.copy()):
                    files[i] = os.path.join(Discord_path, file)
                queue += files
                update_queue()
            elif paused:
                vc.resume()
                paused = False
        case '!disconnect' | '!dc':
            await vc.disconnect()
            vc = None


@tasks.loop(seconds=1)
async def user_prompt_timeout():  # Controls user prompt timeouts...
    for user_ in users.copy():
        if user_.timeout > 0:
            user_.timeout -= 1
        else:
            users.remove(user_)
            await user.get_channel(1174005255189569587).send(f"{user_.user.name} timed out")


@tasks.loop(seconds=20)
async def status():  # manages the random status
    with open('statuses.txt', 'r') as f:
        statuses = f.readlines()
        for i, status in enumerate(statuses.copy()):
            statuses[i] = status.strip()
    await user.change_presence(activity=Custom_listening_activity(name=random.choice(statuses)))


@tasks.loop(seconds=1)
async def queue_loop():  # manages the queue
    if not vc:  # dont run any of this if vc is None
        return
    if paused:  # if the pause flag is set, pause the stream, the always return until unpaused
        if vc.is_playing():
            vc.pause()
        else:
            return
    global queue
    queue = read_queue()
    if not queue:  # if the queue is empty, do nothing
        return
    music_channel = user.get_guild(
        1173496575771807805).get_channel(1174005255189569587)
    while queue:  # while we have a queue, play the first item from the queue
        if not vc.is_playing():
            vc.play(discord.FFmpegPCMAudio(executable=ffmpeg_path,
                    source=queue[0]))
            await music_channel.send(f"Now playing {queue[0].split('/')[-1].split('.')[0]}")
        else:
            continue
        if not loop:  # if we arent looping, remove the file, and the entry, then update the queue file
            queue.pop(0)
            #update_queue()
        else:  # otherwise, send the firs item to the back and update the queue file
            queue.append(queue.pop(0))
            #update_queue()
    # when the queue is empty, say it!
    await music_channel.send("Queue has ended")


@tasks.loop(seconds=4)
async def instance_loop():
    global instances
    for instance in instances.copy():
        if instance.poll() != None:
            print("Instance finished")
            instances.remove(instance)
            msg = await instance.channel.send(f"Downloaded {instance.url}")
            await msg.edit(suppress=True)
    # os.walk through the downloads folder and send all mp3s to the music channel
            for root, dirs, files in os.walk("Downloads"):
                for file in files:
                    if "mp3" in file:
                        await instance.channel.send(files=[discord.File(os.path.join(root, file))])
                        os.remove(os.path.join(root, file))
            del instance
