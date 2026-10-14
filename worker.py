"""Persistent engine subprocess. Protocol output is separated from model logs."""
import json
import os
from pathlib import Path
import sys
import traceback
import wave

protocol = sys.stdout
sys.stdout = sys.stderr
engine = sys.argv[1]
model = None
prompt = None
prompt_key = None


def generate(data):
    global model, prompt, prompt_key
    import soundfile as sf
    if engine == 'piper':
        from piper import PiperVoice, SynthesisConfig
        model_path = os.environ.get('PIPER_MODEL', '')
        if not model_path or not Path(model_path).is_file():
            raise ValueError('Chưa có PIPER_MODEL. Xem hướng dẫn tải giọng Piper.')
        if model is None:
            model = PiperVoice.load(model_path)
        with wave.open(data['output'], 'wb') as out:
            model.synthesize_wav(data['text'], out, syn_config=SynthesisConfig(length_scale=1 / data['speed'], speaker_id=data['speaker']))
        return
    import torch
    if not torch.cuda.is_available():
        raise ValueError('Engine clone cần GPU cho workflow này. Dùng Colab T4 GPU hoặc chọn Piper trên CPU.')
    if engine == 'omnivoice':
        from omnivoice import OmniVoice
        if model is None:
            model = OmniVoice.from_pretrained('k2-fsa/OmniVoice', device_map='cuda:0', dtype=torch.float16, load_asr=False)
        key = (data['sample_hash'], data['transcript'])
        with torch.inference_mode():
            if key != prompt_key:
                prompt = model.create_voice_clone_prompt(ref_audio=data['sample'], ref_text=data['transcript'])
                prompt_key = key
            audio = model.generate(text=data['text'], voice_clone_prompt=prompt, language=data['language'],
                                   speed=data['speed'], num_step=data['steps'])[0]
        sf.write(data['output'], audio, 24000)
    elif engine == 'coqui':
        if not data.get('license_consent'):
            raise ValueError('Cần đồng ý giấy phép XTTS cho sử dụng phi thương mại.')
        os.environ['COQUI_TOS_AGREED'] = '1'
        from TTS.api import TTS
        if model is None:
            model = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to('cuda')
        if data['language'] not in model.languages:
            raise ValueError('Model XTTS không hỗ trợ ngôn ngữ này.')
        model.tts_to_file(text=data['text'], speaker_wav=data['sample'], language=data['language'],
                          speed=data['speed'], file_path=data['output'])
    elif engine == 'chatterbox':
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS, SUPPORTED_LANGUAGES
        if data['language'] not in SUPPORTED_LANGUAGES:
            raise ValueError('Chatterbox không hỗ trợ ngôn ngữ này.')
        if model is None:
            model = ChatterboxMultilingualTTS.from_pretrained(device='cuda')
        audio = model.generate(data['text'], language_id=data['language'], audio_prompt_path=data['sample'],
                               exaggeration=data['emotion'], cfg_weight=0.5)
        sf.write(data['output'], audio.squeeze(0).detach().cpu().numpy(), model.sr)
    else:
        raise ValueError('Engine không hợp lệ')


for line in sys.stdin:
    try:
        data = json.loads(line)
        generate(data)
        reply = {'ok': True}
    except Exception as error:
        traceback.print_exc(file=sys.stderr)
        reply = {'ok': False, 'error': str(error)[:800]}
    protocol.write(json.dumps(reply) + '\n')
    protocol.flush()
