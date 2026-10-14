"""Bounded-memory reference selection; activity is estimated from audio energy."""
import numpy as np
import soundfile as sf


def prepare_reference(path, manual_transcript=False):
    # libsndfile re-seeks after each read. Decode MP3 once before scanning PCM
    # blocks to avoid losing its bit reservoir at those seeks. MP3 sample rates
    # are bounded by the format; the duration cap bounds this allocation.
    with sf.SoundFile(path) as compressed:
        if compressed.format == 'MP3':
            if not 3 <= len(compressed) / compressed.samplerate <= 600:
                raise ValueError('Mẫu cần dài từ 3 giây đến 10 phút')
            if compressed.channels > 2 or compressed.samplerate > 48000:
                raise ValueError('MP3 tối đa 2 kênh và 48 kHz')
            decoded = compressed.read(dtype='float32', always_2d=True)
            sr = compressed.samplerate
        else:
            decoded = None
    if decoded is not None:
        if not np.isfinite(decoded).all():
            raise ValueError('Mẫu có dữ liệu âm thanh không hợp lệ')
        sf.write(path, decoded, sr, subtype='PCM_16')
        del decoded
    with sf.SoundFile(path) as source:
        duration = len(source) / source.samplerate
        sr = source.samplerate
        if not 3 <= duration <= 600:
            raise ValueError('Mẫu cần dài từ 3 giây đến 10 phút')
        if source.channels > 2 or sr > 192000:
            raise ValueError('Mẫu tối đa 2 kênh, sample rate tối đa 192 kHz')
        if manual_transcript and duration > 10.1:
            raise ValueError('Với mẫu dài, hãy bật AI tự chép lời để lời nhận dạng khớp đoạn được chọn')
        step = max(1, int(sr * .25))
        levels = []
        while True:
            block = source.read(step, dtype='float32', always_2d=True)
            if not len(block):
                break
            if not np.isfinite(block).all():
                raise ValueError('Mẫu có dữ liệu âm thanh không hợp lệ')
            mono = block.mean(axis=1)
            levels.append(float(np.sqrt(np.mean(mono**2))))
        if not levels or max(levels) < .0001:
            raise ValueError('Mẫu chỉ có im lặng hoặc âm lượng quá nhỏ')
        start = 0
        frames = len(source)
        trimmed = duration > 10.1
        if trimmed:
            # Prefer an 8s window with sustained activity, rather than leading silence.
            # This is not diarization/VAD; music and other speakers can also be active.
            width = 32
            levels = np.asarray(levels)
            threshold = max(.0001, float(np.max(levels)) * .08)
            active = (levels >= threshold).astype(float)
            energy = np.minimum(levels / max(threshold, .001), 2) * .01
            scores = np.convolve(active + energy, np.ones(width), mode='valid')
            start = int(np.argmax(scores)) * step
            frames = min(int(8 * sr), len(source) - start)
    # Reopen PCM for selecting the reference without retaining the full audio.
    with sf.SoundFile(path) as source:
        remaining = start
        while remaining:
            skip = min(remaining, step)
            source.read(skip, dtype='float32')
            remaining -= skip
        audio = source.read(frames, dtype='float32', always_2d=True).mean(axis=1)
    sf.write(path, audio, sr, subtype='PCM_16')
    return dict(original_duration=round(duration, 2), used_duration=round(len(audio)/sr, 2),
                start_seconds=round(start/sr, 2), auto_trimmed=trimmed)
