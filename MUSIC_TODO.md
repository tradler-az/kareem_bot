# Music Playback Feature Implementation TODO

## Step 1: Update requirements.txt
- [x] Add yt-dlp dependency

## Step 2: Create music_player.py module
- [x] Created bosco_os/capabilities/system/music_player.py
- [x] Implemented play_song() - parse "song by artist" format
- [x] Used yt-dlp to get YouTube audio stream
- [x] Used mpv to play audio
- [x] Implemented controls: pause, resume, stop

## Step 3: Update main.py
- [x] Import music functions
- [x] Add music intent handling in process_command()
- [x] Parse song/artist from voice command

## Step 4: Install Dependencies (USER NEEDS TO DO)
- [ ] pip install yt-dlp (run: pip install yt-dlp)
- [ ] sudo apt install mpv (run: sudo apt install mpv)

## Step 5: Test
- [ ] Test "play [song] by [artist]" command

## Usage Examples:
- "Bosco play fear by NF"
- "Bosco play shape of you"
- "Bosco stop music"
- "Bosco pause music"
- "Bosco resume"
- "Bosco what's playing"

