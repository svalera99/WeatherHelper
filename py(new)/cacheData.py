from gensim.models import FastText, KeyedVectors

def cache():
	google_model = KeyedVectors.load_word2vec_format('~/Documents/GoogleNews-vectors-negative300.bin.gz', binary=True, limit=500000) 
	wikipedia_model = KeyedVectors.load_word2vec_format('~/Documents/wiki_model.bin', binary=True, limit=500000)
	print("works!")
	return [google_model, wikipedia_model]
