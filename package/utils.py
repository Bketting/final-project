'''Utils for API'''
import accelerate
from llama_cpp import Llama
from transformers import AutoTokenizer
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings


def load_llm():
    '''Function to load LLM'''
    llm = Llama(
        model_path="model/nous-hermes-2-solar-10.7b.Q4_K_M.gguf",
        verbose=True,
        n_gpu_layers=-1,
        n_ctx=4096
    )
    return llm


def load_tokenizer():
    '''Function to load tokenizer'''
    tokenizer = AutoTokenizer.from_pretrained(
        "NousResearch/Nous-Hermes-2-SOLAR-10.7B"
    )
    return tokenizer


def load_embeddings():
    '''Function to load embedding tool'''
    model_name = "NousResearch/Nous-Hermes-2-SOLAR-10.7B"
    model_kwargs = {"device": "cuda"}
    encode_kwargs = {"normalize_embeddings": False}
    embed = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    return embed
