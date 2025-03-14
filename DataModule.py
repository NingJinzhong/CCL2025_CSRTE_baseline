import os
import torch
import random
import librosa
import json
import numpy as np
import lightning as L
from torch.utils.data import ConcatDataset,StackDataset,random_split
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import Dataset, DataLoader, TensorDataset
from transformers import WhisperProcessor,\
                        WhisperFeatureExtractor,\
                        WhisperTokenizer

class CSRTE_Dataset(Dataset):
    def __init__(self, data_type,hypernum=None):
        super().__init__()
        self.hypernum = hypernum
        self.data_path = hypernum.train_file_dir
        self.audio_file = hypernum.train_audio_files_dir
        self.data_type = data_type
        self.all_data,entities_types,relations_types = self.get_alldata()

        self.order_map = dict(h = '<head_entity>',r = '<relation_type>',t = '<tail_entity>')
        self.order_to_id = {'<head_entity>':0,'<relation_type>':1,'<tail_entity>':2}
        self.id_to_order = {0:'<head_entity>',1:'<relation_type>',2:'<tail_entity>'}
        

    def __getitem__(self, index):
        data_item  = self.all_data[index]
        target,decoder_input_text,entity_list,relation_list = self.get_target(data_item,self.order_view)

        audio_id = data_item["audio_id"]
        if "conll04" in self.data_path.lower() or "retracred" in self.data_path.lower():
            speechfiledir = os.path.join(self.audio_file, audio_id+".wav")
        else:
            if "tts" in self.audio_file:
                speechfiledir = os.path.join(self.audio_file, "tts_"+audio_id+".wav")
            else:
                speechfiledir = os.path.join(self.audio_file, audio_id+".npy")
        if ".wav" in speechfiledir:
            try:
                waveform, sampling_rate = librosa.load(speechfiledir, sr=16000)
            except Exception as e:
                target = "There is no audio input."
                waveform = np.zeros(500)
                sampling_rate = 16000
        else:
            waveform = np.load(speechfiledir)
            sampling_rate = 16000

        
        return waveform,sentence,target,decoder_input_text,entity_list,relation_list,self.data_type
    def get_alldata(self):
        data_file_path = self.data_path
        dataset_info_file_path = self.hypernum.dataset_info_file_path

        with open(data_file_path, "r",encoding='utf-8') as f:
            all_data = json.load(f)
        with open(dataset_info_file_path, "r",encoding='utf-8') as f:
            dataset_info = json.load(f)
        entities_types = entities_types = [e_item if e_item.startswith("<") else '<'+e_item+'>' for e_item in dataset_info["entities_type"]]

        relations_types = [r_item if r_item.startswith("<") else '<'+r_item+'>' for r_item in dataset_info["relations_type"]]
        
        return all_data,entities_types,relations_types
    def __len__(self):
        return len(self.all_data)
    def get_target(self,data_item):

if __name__ == "__main__":
    class Hypernum:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    hypernum = Hypernum(
    train_file_dir = r"/root/autodl-tmp/data1/train.json",
    train_audio_files_dir = r"/root/autodl-tmp/data1/train_audio",
    dataset_info_file_path = "./SRTE_Chinese_info.json"
                )
    dataset = CSRTE_Dataset('train',hypernum)
    for item in dataset:
        print(item)
        
    