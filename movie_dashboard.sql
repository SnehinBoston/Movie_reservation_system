USE movie_project;

SET GLOBAL innodb_lock_wait_timeout = 5000; 
SET GLOBAL innodb_lock_wait_timeout = 5000; 

DELIMITER //

drop procedure if exists shows_display;
CREATE PROCEDURE shows_display(`day` varchar(100))
BEGIN
	# showId, startTime, endTime, weekday, movieId, hallId
    (select distinct theatreName, movieName, startTime, endTime
	from shows s 
	inner join movie m
	on s.movieId = m.movieId
	inner join hall h
	on s.hallId = h.hallId
	inner join theatre t
	on t.theatreId = h.theatreId
	where `weekday`=`day`
	order by theatreName,startTime);
	-- select * from display;
    -- drop table display;
END //
delimiter ;
call shows_display('Monday');

#drop table shows_display;

select * from shows_display;

DROP PROCEDURE if exists SELECT_SHOW;
delimiter //
CREATE PROCEDURE select_show(
	theName varchar(100),
	movName varchar(100),
	stTime time, 
	endTime time,
    `day` varchar(100)
)
BEGIN
	SET @movId = (SELECT movieId FROM movie WHERE movieName = 'Race');
	(select showId from shows where (startTime = stTime and endTime = endTime and `weekday` = `day` and movieId = @movId and hallId in (SELECT hallId FROM hall where theatreId = (SELECT theatreId FROM theatre WHERE theatreName = theName))));
END //
delimiter ;


delimiter //
drop procedure if exists book_tickets;
CREATE PROCEDURE book_tickets
( 	holdName varchar(100),
    shId int,
	booked_seat varchar(3),
    email varchar(100)
)
BEGIN
    update available_seats set availability = 0 where seatId = booked_seat and showId = shId;
    insert into ticket(holderName,showId,seatId,hallId,emailId) values(holdName, shId, booked_seat, (select hallId from shows where showId = shId),email);
END//
delimiter ;