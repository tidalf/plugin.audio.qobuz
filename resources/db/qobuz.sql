select * from tracks as t left join albums as a on t.album_id = a.album_id;
delete from tracks; delete from albums;

