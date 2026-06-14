SELECT RM.RoomNumber, RT.TypeName, RT.PricePerNight
FROM ROOM RM
JOIN ROOMTYPE RT ON RM.RoomTypeID = RT.RoomTypeID;