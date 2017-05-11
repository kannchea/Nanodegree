-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.


DROP TABLE Players CASCADE;
DROP TABLE Matches;
DROP VIEW Standings;
DROP VIEW SwissPairA;
DROP VIEW SwissPairB;

CREATE TABLE Players (
	ID SERIAL PRIMARY KEY,
	NAME TEXT
);


CREATE TABLE Matches (
	ID SERIAL PRIMARY KEY,
	Winner  INT references Players (ID) NOT NULL,
	Loser   INT references Players (ID) NOT NULL
);


CREATE VIEW Standings AS
SELECT Players.id, Players.name, 
( SELECT COUNT(winner) FROM Matches WHERE Players.id = Matches.winner ) AS wins, 
( SELECT COUNT(Matches.id) FROM Matches WHERE Players.id = Matches.winner OR Players.id = Matches.loser) AS matches 
FROM Players ORDER BY wins DESC;


CREATE VIEW SwissPairA AS
SELECT s.* FROM ( SELECT *, row_number() over(ORDER BY wins DESC) AS row FROM Standings ) s 
WHERE s.row % 2 = 0 ORDER BY wins DESC;


CREATE VIEW SwissPairB AS
SELECT s.* FROM ( SELECT *, row_number() over(ORDER BY wins DESC) AS row FROM Standings ) s 
WHERE (s.row + 1) % 2 = 0 ORDER BY wins DESC;


