
import java.io.*;
import java.nio.file.*;
import java.util.*;

class Student {
    private int id;
    private String name;
    private String department;

    public Student(int id, String name, String department) {
        this.id = id;
        this.name = name;
        this.department = department;
    }

    public int getId() { return id; }
    public String getName() { return name; }
    public String getDepartment() { return department; }
}

class Attendance {
    private int studentId;
    private String date;
    private String status;

    public Attendance(int studentId, String date, String status) {
        this.studentId = studentId;
        this.date = date;
        this.status = status;
    }

    public int getStudentId() { return studentId; }
    public String getDate() { return date; }
    public String getStatus() { return status; }
}

class StudentManager {
    private final Path file = Paths.get("data", "students.txt");

    public StudentManager() throws IOException {
        Files.createDirectories(file.getParent());
        if (!Files.exists(file)) Files.createFile(file);
    }

    public void addStudent(Student s) throws IOException {
        if (getStudents().stream().anyMatch(
            x -> x.getId() == s.getId())) {
            throw new IllegalArgumentException("Student ID already exists");
        }

        String line = s.getId() + "|" + s.getName()
                + "|" + s.getDepartment();

        Files.writeString(file, line + System.lineSeparator(),
                StandardOpenOption.APPEND);
    }

    public List<Student> getStudents() throws IOException {
        List<Student> result = new ArrayList<>();

        for (String line : Files.readAllLines(file)) {
            String[] p = line.split("\\|", -1);
            if (p.length == 3) {
                result.add(new Student(
                    Integer.parseInt(p[0]), p[1], p[2]));
            }
        }
        return result;
    }
}

class AttendanceManager {
    private final Path file = Paths.get("data", "attendance.txt");

    public AttendanceManager() throws IOException {
        Files.createDirectories(file.getParent());
        if (!Files.exists(file)) Files.createFile(file);
    }

    public void markAttendance(Attendance a) throws IOException {
        if (!a.getStatus().equals("Present")
                && !a.getStatus().equals("Absent")) {
            throw new IllegalArgumentException("Invalid status");
        }

        List<String> lines = Files.readAllLines(file);
        String updated = a.getStudentId() + "|" +
                a.getDate() + "|" + a.getStatus();

        boolean found = false;

        for (int i = 0; i < lines.size(); i++) {
            String[] p = lines.get(i).split("\\|", -1);

            if (p.length == 3
                    && p[0].equals(String.valueOf(a.getStudentId()))
                    && p[1].equals(a.getDate())) {
                lines.set(i, updated);
                found = true;
                break;
            }
        }

        if (!found) lines.add(updated);

        Files.write(file, lines);
    }

    public List<Attendance> getRecords() throws IOException {
        List<Attendance> result = new ArrayList<>();

        for (String line : Files.readAllLines(file)) {
            String[] p = line.split("\\|", -1);

            if (p.length == 3) {
                result.add(new Attendance(
                    Integer.parseInt(p[0]), p[1], p[2]));
            }
        }
        return result;
    }
}

public class Main {

    public static void main(String[] args) {

        try {
            StudentManager sm = new StudentManager();
            AttendanceManager am = new AttendanceManager();

            if (args.length == 0) {
                System.out.println("Java Backend Ready");
                return;
            }

            switch (args[0]) {

                case "add":
                    if (args.length != 4) throw new IllegalArgumentException("Usage: add ID NAME DEPARTMENT");

                    if (args[2].contains("|") || args[3].contains("|")
                            || args[2].contains("\n") || args[3].contains("\n")) {
                        throw new IllegalArgumentException("Invalid text");
                    }

                    sm.addStudent(new Student(
                        Integer.parseInt(args[1]), args[2], args[3]));

                    System.out.println("SUCCESS");
                    break;

                case "list":
                    for (Student s : sm.getStudents()) {
                        System.out.println(s.getId() + "|" +
                            s.getName() + "|" + s.getDepartment());
                    }
                    break;

                case "mark":
                    if (args.length != 4) throw new IllegalArgumentException("Usage: mark ID DATE STATUS");

                    am.markAttendance(new Attendance(
                        Integer.parseInt(args[1]), args[2], args[3]));

                    System.out.println("SUCCESS");
                    break;

                case "records":
                    for (Attendance a : am.getRecords()) {
                        System.out.println(a.getStudentId() + "|" +
                            a.getDate() + "|" + a.getStatus());
                    }
                    break;

                default:
                    throw new IllegalArgumentException("Unknown command");
            }

        } catch (Exception e) {
            System.out.println("ERROR: " + e.getMessage());
            System.exit(1);
        }
    }
}
