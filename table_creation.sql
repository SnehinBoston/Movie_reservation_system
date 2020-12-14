drop database movie_project;
create database movie_project;
use movie_project;
-- drop table `admin`;
create table `admin`(
	emailId varchar(100) not null,
    `name` varchar(100) not null,
    phone varchar(10),
    `password` text(100) not null,
    primary key(emailId)
);

create table theatre(
	theatreId int AUTO_INCREMENT,
    theatreName varchar(100) unique not null,
    primary key(theatreId) 
);

create table hall(
	hallId int auto_increment,
    hallName varchar(100) unique not null,
    theatreId int not null,
    primary key(hallId),
    foreign key (theatreId) references theatre(theatreId) on delete cascade
);

create table movie(
	movieId int auto_increment,
    movieName varchar(200) unique not null,
    director text(100) not null,
    actors text(400) not null,
    primary key(movieId)
);

create table shows(
	showId int auto_increment,
    startTime time not null, 
    endTime time not null,
    `weekday` varchar(15) not null,
    movieId int not null,
    hallId int not null,
    unique(startTime,endTime,`weekday`,hallId),
    primary key(showId),
    foreign key(hallId) references hall(hallId) on update cascade on delete cascade,
    foreign key(movieId) references movie(movieId) on update cascade on delete cascade
);

-- drop table seats, available_seats, ticket;
create table seats(
	seatId varchar(100),
    price int not null,
    primary key(seatId)
);

-- drop table available_seats;
create table available_seats(
	showId int,
    seatId varchar(100),
    availability boolean not null,
    primary key(showId,seatId),
    foreign key(showId) references shows(showId) on update cascade on delete cascade,
    foreign key(seatId) references seats(seatId) on update cascade on delete cascade
);

create table `user`(
	emailId varchar(100) not null,
    `name` varchar(100) not null,
    phone varchar(10),
    `password` text(100) not null,
    primary key(emailId)
);

create table ticket(
	ticketId int auto_increment,
    holderName text(100),
    showId int not null,
    seatId varchar(100) not null,
    hallId int not null,
    emailId varchar(100),
    primary key(ticketId),
    foreign key(showId) references shows(showId) on update cascade on delete cascade,
    foreign key(seatId) references seats(seatId) on update cascade on delete cascade,
    foreign key(hallId) references hall(hallId) on update cascade on delete cascade,
    foreign key(emailId) references `user`(emailId) on update cascade on delete cascade
);
