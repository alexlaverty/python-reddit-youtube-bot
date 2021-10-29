Errors to troubleshoot 

Video has exceeded background video length, need to loop background video 

```
MoviePy - Writing audio in qhb57o_To_people_who_ever_signed_up_for_one_of_those_hot_TEMP_MPY_wvf_snd.mp3
chunk:  90%|████████████████████████████████████████████████████████████████████████████████████▌         | 5732/6369 [00:07<00:00, 816.46it/s, now=None]Traceback (most recent call last):
  File "C:\Users\laverty\Documents\ttsvibelounge\app.py", line 70, in <module>
    main()
  File "C:\Users\laverty\Documents\ttsvibelounge\app.py", line 61, in main
    post_video = video.create(post)
  File "C:\Users\laverty\Documents\ttsvibelounge\video.py", line 188, in create
    post_video.write_videofile(video_filename)
  File "<decorator-gen-55>", line 2, in write_videofile
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\decorators.py", line 54, in requires_duration
    return f(clip, *a, **k)
  File "<decorator-gen-54>", line 2, in write_videofile
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\decorators.py", line 135, in use_clip_fps_by_default
    return f(clip, *new_a, **new_kw)
  File "<decorator-gen-53>", line 2, in write_videofile
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\decorators.py", line 22, in convert_masks_to_RGB
    return f(clip, *a, **k)
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\video\VideoClip.py", line 293, in write_videofile
    self.audio.write_audiofile(audiofile, audio_fps,
  File "<decorator-gen-45>", line 2, in write_audiofile
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\decorators.py", line 54, in requires_duration
    return f(clip, *a, **k)
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\audio\AudioClip.py", line 206, in write_audiofile
    return ffmpeg_audiowrite(self, filename, fps, nbytes, buffersize,
  File "<decorator-gen-9>", line 2, in ffmpeg_audiowrite
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\decorators.py", line 54, in requires_duration
    return f(clip, *a, **k)
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\audio\io\ffmpeg_audiowriter.py", line 166, in ffmpeg_audiowrite
    for chunk in clip.iter_chunks(chunksize=buffersize,
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\audio\AudioClip.py", line 85, in iter_chunks
    yield self.to_soundarray(tt, nbytes=nbytes, quantize=quantize,
  File "<decorator-gen-44>", line 2, in to_soundarray
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\decorators.py", line 54, in requires_duration
    return f(clip, *a, **k)
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\audio\AudioClip.py", line 127, in to_soundarray
    snd_array = self.get_frame(tt)
  File "<decorator-gen-11>", line 2, in get_frame
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\decorators.py", line 89, in wrapper
    return f(*new_a, **new_kw)
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\Clip.py", line 93, in get_frame
    return self.make_frame(t)
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\audio\AudioClip.py", line 296, in make_frame
    sounds = [c.get_frame(t - c.start)*np.array([part]).T
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\audio\AudioClip.py", line 296, in <listcomp>
    sounds = [c.get_frame(t - c.start)*np.array([part]).T
  File "<decorator-gen-11>", line 2, in get_frame
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\decorators.py", line 89, in wrapper
    return f(*new_a, **new_kw)
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\Clip.py", line 93, in get_frame
    return self.make_frame(t)
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\Clip.py", line 136, in <lambda>
    newclip = self.set_make_frame(lambda t: fun(self.get_frame, t))
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\audio\fx\volumex.py", line 19, in <lambda>
    return clip.fl(lambda gf, t: factor * gf(t),
  File "<decorator-gen-11>", line 2, in get_frame
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\decorators.py", line 89, in wrapper
    return f(*new_a, **new_kw)
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\Clip.py", line 93, in get_frame
    return self.make_frame(t)
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\audio\io\AudioFileClip.py", line 77, in <lambda>
    self.make_frame = lambda t: self.reader.get_frame(t)
  File "C:\Users\laverty\AppData\Local\Programs\Python\Python39\lib\site-packages\moviepy\audio\io\readers.py", line 170, in get_frame
    raise IOError("Error in file %s, "%(self.filename)+
OSError: Error in file backgrounds\ULTRAWAVE_i7jU0xDABGM.mp4, Accessing time t=262.42-262.46 seconds, with clip duration=262 seconds,
```