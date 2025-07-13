use firsttest;
 CREATE TABLE  SC
 (
	Sno CHAR(9),
	Cno CHAR(4),
	Grade SMALLINT,
	Semester  CHAR(5),
	PRIMARY KEY (Sno, Cno),
	FOREIGN KEY(Sno) REFERENCES Student(Sno),
	FOREIGN KEY (Cno) REFERENCES Course(Cno)
);