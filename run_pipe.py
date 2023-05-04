from transcriber import transcribe
from downloader import download

def run_pipe():
    print("Pipeline started...")

    ## Download videos
    do_download = False
    if do_download:
        try:
            download(reset=False)
        except:
            print("Pipe failed, running again.")
            run_pipe()
        finally:
            print("Download finished!")

    ## Transcribe
    do_transcribe = False
    if do_transcribe:
        transcribe()

    print("Pipeline finished!")


if __name__ == "__main__":
    run_pipe()