import edu.stanford.nlp.pipeline.*;
import edu.stanford.nlp.util.*;
import edu.stanford.nlp.ie.*;
import edu.stanford.nlp.ie.crf.*;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ie.AbstractSequenceClassifier;
import edu.stanford.nlp.ling.CoreAnnotations.AnswerAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.sequences.SeqClassifierFlags;
import edu.stanford.nlp.sequences.*;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;

import java.util.*;
import java.lang.reflect.Type;
class dudesCode{
	public static void main(String args []){
		List<String> configs = readConfig();
		HashMap<String, HashMap> probVect = returnVector(configs.get(0), configs.get(1)); 
		writeRes(probVect);

		//"dummy-ner-model.ser.gz"
		// for (String name: probVect.keySet()){
  //           String key = name.toString();
  //           String value = probVect.get(name).toString();  
  //           System.out.println(key + " " + value);  
		// }
	}
	public static HashMap<String,HashMap> returnVector(String txt, String modelName){
		HashMap<String, HashMap> probVect = new HashMap<String, HashMap>();

		CRFClassifier<CoreLabel> classifier = CRFClassifier.getClassifierNoExceptions(modelName);
		List<List<CoreLabel>> classifiedLabels = classifier.classify(txt);
		for (int l = 0; l < classifiedLabels.size(); l++){
			for (int m = 0; m < classifiedLabels.get(l).size(); m++){
				System.out.println(classifiedLabels.get(l).get(m));
				CRFCliqueTree<String> cliqueTree = classifier.getCliqueTree(classifiedLabels.get(l));
				CoreLabel wi = classifiedLabels.get(l).get(m);
				
				HashMap<String, Double> tmpMap = new HashMap<String, Double>();
			    for (Iterator<String> iter = classifier.classIndex.iterator(); iter.hasNext();) {
					String label = iter.next();
					int index = classifier.classIndex.indexOf(label);
					double prob = cliqueTree.prob(m, index);
					System.out.println("\t" + label + "(" + prob + ")");
					tmpMap.put(label, new Double(prob));
			    }
			    String tag = StringUtils.getNotNullString(wi.get(CoreAnnotations.AnswerAnnotation.class));
			    System.out.println("Class : " + tag);
				probVect.put(wi.toString(), tmpMap);
			}
		}
		return probVect;
	}
	private static void writeRes(HashMap<String, HashMap> map1) {
	    try(PrintWriter pw = new PrintWriter("probVect.txt")){
		    final Iterator<HashMap.Entry<String, HashMap>> mapIt
			= map1.entrySet().iterator();
		    while (mapIt.hasNext()) {
			final Map.Entry<String, HashMap> mapEntry = mapIt.next();
			mapIt.remove();
			pw.write(mapEntry.getKey()+" ");
			final Iterator<Map.Entry<String,Double>> fooIt 
			    = mapEntry.getValue().entrySet().iterator();
			while (fooIt.hasNext()) {
			    final Map.Entry<String,Double> fooEntry = fooIt.next();
			    fooIt.remove();
			    pw.write(fooEntry.getKey() +" " +fooEntry.getValue() + " ");
			}
			pw.write("\n");	
		    }
		System.out.println("Done");
	}catch(Exception e){}
	}
	private static List<String> readConfig(){
		List<String> sb = new ArrayList<String>();

		try (BufferedReader br = Files.newBufferedReader(Paths.get("config.txt"))) {

		    String line;
		    while ((line = br.readLine()) != null) {
		        sb.add(line);
		    }

		} catch (IOException e) {
		    System.err.format("IOException: %s%n", e);
		}

		return sb;
	}

}

