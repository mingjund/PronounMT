/*  Copyright 2010, 2011 Semantic Web Research Center, KAIST

This file is part of JHanNanum.

JHanNanum is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

JHanNanum is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with JHanNanum.  If not, see <http://www.gnu.org/licenses/>   */

package kr.ac.kaist.swrc.jhannanum.demo;

import java.io.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

import kr.ac.kaist.swrc.jhannanum.hannanum.Workflow;
import kr.ac.kaist.swrc.jhannanum.plugin.MajorPlugin.MorphAnalyzer.ChartMorphAnalyzer.ChartMorphAnalyzer;
import kr.ac.kaist.swrc.jhannanum.plugin.MajorPlugin.PosTagger.HmmPosTagger.HMMTagger;
import kr.ac.kaist.swrc.jhannanum.plugin.SupplementPlugin.MorphemeProcessor.UnknownMorphProcessor.UnknownProcessor;
import kr.ac.kaist.swrc.jhannanum.plugin.SupplementPlugin.PlainTextProcessor.InformalSentenceFilter.InformalSentenceFilter;
import kr.ac.kaist.swrc.jhannanum.plugin.SupplementPlugin.PlainTextProcessor.SentenceSegmentor.SentenceSegmentor;

/**
 * This is a demo program of HanNanum that helps users to understand how to set up
 * HanNanum plug-ins manually for own purpose. It basically uses a work flow with
 * 5 plug-ins for morphological analysis and POS tagging, which is good for general
 * use, but you can test other work flows referring the commented codes. <br>
 * <br>
 * Used plug-ins: SentenceSegmentor, InformalSentenceFilter, ChartMorphAnalyzer, UnknownProcessor, and HMMTagger.<br>
 * <br>
 * It performs POS tagging for a Korean document with the following procedure:<br>
 * 		1. Create a work flow for morphological analysis and POS tagging with 5 plug-ins.<br>
 * 		2. Activate the work flow in multi-thread mode.<br>
 * 		3. Analyze a document that consists of several sentences.<br>
 * 		4. Print the result on the console.<br>
 * 		5. Repeats the procedure 3~4 with activated work flow.<br>
 * 		6. Close the work flow.<br>
 * <br>
 * @author Sangwon Park (hudoni@world.kaist.ac.kr), CILab, SWRC, KAIST
 */
public class TestWorkFlow {
    public static List<String> docs;

    public TestWorkFlow(List<String> docs){
        this.docs = docs;
    }

    /**
     * The main method of this demo program.
     */
    public static void run() {
        Workflow workflow = new Workflow();

        try {
            /* Setting up the work flow */
            /* Phase1. Supplement Plug-in for analyzing the plain text */
            workflow.appendPlainTextProcessor(new SentenceSegmentor(), null);
            workflow.appendPlainTextProcessor(new InformalSentenceFilter(), null);

            /* Phase2. Morphological Analyzer Plug-in and Supplement Plug-in for post processing */
            workflow.setMorphAnalyzer(new ChartMorphAnalyzer(), "plugin/MajorPlugin/MorphAnalyzer/ChartMorphAnalyzer.json");
            workflow.appendMorphemeProcessor(new UnknownProcessor(), null);

            /*
             * For simpler morphological analysis result with 22 tags, decomment the following line.
             * Notice: If you use SimpleMAResult22 plug-in, POSTagger will not work correctly.
             *         So don't add phase3 plug-ins after SimpleMAResult22.
             */
//			workflow.appendMorphemeProcessor(new SimpleMAResult22(), null);

            /*
             * For simpler morphological analysis result with 9 tags, decomment the following line.
             * Notice: If you use SimpleMAResult09 plug-in, POSTagger will not work correctly.
             *         So don't add phase3 plug-ins after SimpleMAResult09.
             */
//			workflow.appendMorphemeProcessor(new SimpleMAResult09(), null);

            /* Phase3. Part Of Speech Tagger Plug-in and Supplement Plug-in for post processing */
            workflow.setPosTagger(new HMMTagger(), "plugin/MajorPlugin/PosTagger/HmmPosTagger.json");

            /* For extracting nouns only, decomment the following line. */
//			workflow.appendPosProcessor(new NounExtractor(), null);

            /* For simpler POS tagging result with 22 tags, decomment the following line. */
//			workflow.appendPosProcessor(new SimplePOSResult22(), null);

            /* For simpler POS tagging result with 9 tags, decomment the following line. */
//			workflow.appendPosProcessor(new SimplePOSResult09(), null);

            /* Activate the work flow in the thread mode */
            workflow.activateWorkflow(true);

            FileWriter w = new FileWriter("./kor_pron.txt", true);
            BufferedWriter bf = new BufferedWriter(w);
            for (String line: docs){
                workflow.analyze(line);
                String result = workflow.getResultOfDocument();
                String[] results = result.split("\n");
                List<String> prons = new ArrayList<>();
                for(int i = 0; i < results.length; i++){
                    if(results[i].contains("npp")) {
                        String[] tokens = results[i].stripLeading().split("\\+");
                        for(String t : tokens){
                            if (t.contains("npp")){
                                String[] str = t.split("/");
                                prons.add(str[0]);
                            }
                        }
                    }
                }
                bf.write(String.join(" ", prons) + "\n");
            }
            bf.close();
            w.close();

            /* Close the work flow */
            workflow.close();

        } catch (FileNotFoundException e) {
            e.printStackTrace();
            System.exit(0);
        } catch (IOException e) {
            e.printStackTrace();
            System.exit(0);
        } catch (Exception e) {
            e.printStackTrace();
        }

        /* Shutdown the workflow */
        workflow.close();
    }
}


