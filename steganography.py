import numpy as np
import wave

def hide_message(input_wav, output_wav, message):
    # Open the original WAV file
    with wave.open(input_wav, 'rb') as wav:
        params = wav.getparams()
        frames = wav.readframes(params.nframes)
    
    # Convert frames to numpy array and create a writable copy
    audio_data = np.frombuffer(frames, dtype=np.int16).copy()
    
    # Prepare the message
    message_bytes = message.encode('utf-8')
    message_bits = ''.join(format(byte, '08b') for byte in message_bytes)
    
    # Embed the message in the audio data
    for i in range(len(message_bits)):
        if i < len(audio_data):
            audio_data[i] = (audio_data[i] & ~1) | int(message_bits[i])
    
    # Write the modified audio data to a new WAV file
    with wave.open(output_wav, 'wb') as wav_out:
        wav_out.setparams(params)
        wav_out.writeframes(audio_data.tobytes())

def extract_message(input_wav, message_length):
    # Open the WAV file
    with wave.open(input_wav, 'rb') as wav:
        frames = wav.readframes(wav.getnframes())
    
    # Convert frames to numpy array
    audio_data = np.frombuffer(frames, dtype=np.int16)
    
    # Extract the message bits
    extracted_bits = []
    for i in range(message_length * 8):  # Each character is 8 bits
        if i < len(audio_data):
            extracted_bits.append(audio_data[i] & 1)
    
    # Convert bits to bytes
    message_bytes = bytearray()
    for i in range(0, len(extracted_bits), 8):
        byte = extracted_bits[i:i+8]
        message_bytes.append(int(''.join(map(str, byte)), 2))
    
    return message_bytes.decode('utf-8', errors='ignore')

"""# Example usage
if __name__ == "__main__":
    # Hide a message in the WAV file
    hide_message_in_wav('input.wav', 'output.wav', 'Hello, this is a secret message!')
    
    # Extract the message from the WAV file
    extracted_message = extract_message_from_wav('output.wav', 40)  # Adjust length as needed
    print('Extracted Message:', extracted_message)"""