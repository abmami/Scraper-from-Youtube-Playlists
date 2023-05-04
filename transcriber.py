
from faster_whisper import WhisperModel
import os 
import json
import time

def get_audio_files():
    with open('dataset/data.json', 'r') as f:
        audio_paths = []
        data = json.load(f)
        total_length = 0
        for playlist_id, playlist_data in data.items():
            for video_id, video_data in playlist_data.items():
                audio_path = f"dataset/{playlist_id}/{video_id}/{video_id}.mp3"
                audio_paths.append(audio_path)

        return audio_paths


def transcribe_audio(model, path_to_audio):
    print("Transcribing", path_to_audio)
    # cal exec time 
    etime = time.time()

    segments,_ = model.transcribe(path_to_audio, beam_size=5, vad_filter=True)
    text = {}
    for i,segment in enumerate(segments):
        text[i] = {"start": segment.start, "end": segment.end, "text": segment.text}

    print("Transcribed in %.2fs" % (time.time() - etime))

    ## remove .mp3 from path
    path_to_audio = path_to_audio[:-4]
    ## load json file and add text
    with open(f"{path_to_audio}.json", 'r') as f:
        data = json.load(f)
        data["transcript"] = text
        
    ## save json file
    with open(f"{path_to_audio}.json", 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Added transcription for {path_to_audio}.json")
        

def build_transcribed_dataset():

    folders = os.listdir("dataset")
    final_data = {}
    for playlist in folders:
        ## if not folder skip
        if not os.path.isdir(f"dataset/{playlist}"):
            continue
        final_data[playlist] = {}
        videos = os.listdir(f"dataset/{playlist}")
        for video in videos:
            ## get json file
            json_file = f"dataset/{playlist}/{video}/{video}.json"
            ## load json file            
            with open(json_file, 'r') as f:
                data = json.load(f)
                final_data[playlist][video] = data
     
    ## Save to json file

    with open("dataset/final_data.json", 'w') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
        print(f"Saved {len(final_data)} playlists to dataset/final_data.json")


def transcribe():
    print("Transcription started...")

    ## Load model
    model = WhisperModel("small", device="cuda", compute_type="int8")

    ## Transcribe 
    files = get_audio_files()
    for file in files:
        transcribe_audio(model, file)
        
    ## Save to json file
    build_transcribed_dataset()
    print("Transcription finished!")

