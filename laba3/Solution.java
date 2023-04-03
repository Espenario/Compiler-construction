import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.io.BufferedReader;
import java.util.Collections;
import java.util.ArrayList;
import java.util.List;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;


public class Solution
{
    public static void main(String[] args) {
        ArrayList<Token> buff = new ArrayList();
        try {
            File file = new File("file.txt");
            //создаем объект FileReader для объекта File
            FileReader fr = new FileReader(file);
            //создаем BufferedReader с существующего FileReader для построчного считывания
            BufferedReader reader = new BufferedReader(fr);
            // считаем сначала первую строку
            String line = reader.readLine();
            int line_count = 1;
            while (line != null) {
                String[] lexems = line.split("\\s");
                if (lexems.length == 1) {
                    lexems[0] += "\n";
                    line += "\n";
                }
                for (int i = 0; i < lexems.length; i++) {
                    //System.out.print(lexems[i] + " ");
                    ArrayList<Token> mini_buf = new ArrayList();
                    buff = match(lexems[i], line_count, buff);
                    //System.out.println(buff.size());
                    //System.out.println(position);
                }
                //match(line);
                // считываем остальные строки в цикле
                line = reader.readLine();
                line_count +=  1;
            }
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
        for (int i = 0; i < buff.size(); i ++) {
            System.out.println(buff.get(i));
        }
    }

    static class Token {
        String tag;
        int line, col;
        String value;

        public @Override String toString() {
            return tag + " (" + line + ", " + col + "): " + value;
        }
    }

    public static ArrayList<Token> match(String text, int line, ArrayList<Token> arr1) {
        // Регулярные выражения
        String numbers = "<\\d+>";
        String operations = "<=|==|=";
        String ident = "([A-Za-z]*|\\d*)\\d$";
        String pattern = "(?<numbers>"+ numbers +")|(?<operations>"+ operations +")|(?<ident>"+ ident +")";
        // Компиляция регулярного выражения
        Pattern p = Pattern.compile(pattern);
        // Сопоставление текста с регулярным выражением
        Matcher m = p.matcher(text);
        //arr1.add(text);
        int flag = 0;
        while (m.find()) {
            if (m.group("ident") != null) {
                int start = m.start();
                //System.out.print("Идентификатор " + start + " "  + end);
                Token t = new Token();
                t.line = line;
                t.col = start;
                t.tag = "Ident";
                t.value = m.group("ident");
                arr1.add(t);
                if (start == 0) flag = 1;
            } else if (m.group("numbers") != null) {
                int start = m.start();
                Token t = new Token();
                t.line = line;
                t.col = start;
                t.tag = "numbers";
                t.value = m.group("numbers");
                arr1.add(t);
                if (start == 0) flag = 1;
            } else {
                int start = m.start();
                //System.out.print("Операции " + start);
                Token t = new Token();
                t.line = line;
                t.col = start;
                t.tag = "operation";
                t.value = m.group("operations");
                arr1.add(t);
                if (start == 0) flag = 1;
            }
        }
        if (flag == 0) {
            Token t = new Token();
            //System.out.print("Ошибка");
            t.line = line;
            t.col = 0;
            t.tag = "error";
            t.value = text;
            arr1.add(t);
        }
        
        return arr1;
    }
}