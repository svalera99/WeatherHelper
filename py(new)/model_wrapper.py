import sys
import model
import cacheData
from importlib import reload
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
cache = None
if __name__=="__main__":
	while True:
		if not cache:
			cache = cacheData.cache()
		model.main(cache)
		print("Press enter to re-run the script, CTRL-C to exit")
		sys.stdin.readline()
		reload(model)
