package kr.ac.kaist.swrc.jhannanum.demo;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Scanner;

public class AnalyzeLongFile {

    public static void main(String[] args) {
        try{
            File f = new File("/Users/sherrywang/Desktop/Winter20/capstone/en-ko.txt/OpenSubtitles.en-ko.ko");
            File outF = new File("./kor_pos.txt");
            outF.createNewFile();
            Scanner reader = new Scanner(f);
            ArrayList<String> docs = new ArrayList<>();
            while(reader.hasNextLine()){
                String line = reader.nextLine();
                docs.add(line);
            }
            reader.close();
            TestWorkFlow testWorkFlow = new TestWorkFlow(docs);
//            TestWorkFlow testWorkFlow = new TestWorkFlow(docs.subList(0, 10));
            testWorkFlow.run();

        }catch (FileNotFoundException e) {
            e.printStackTrace();
            System.exit(0);
        } catch (IOException e) {
            e.printStackTrace();
            System.exit(0);
        } catch (Exception e) {
            e.printStackTrace();
        }

    }
}
